from app.secrets_manager import get_secrets_manager_hybrid
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import logging
import os
import time
import functools
from collections import defaultdict
from contextlib import asynccontextmanager

# Imports existentes
from app.database import get_database, get_cache, db_manager, cache_manager, init_database, health_check
from app.models import (
    FocusCostDataResponse, CostAnalysisResponse, BudgetResponse,
    CostQueryParams, AnalysisQueryParams, FocusCostDataCreate,
    BudgetCreate, CostSummary, MonthlyCostResponse, CostForecast,
    DashboardSummary
)
# Cloud Native Optimization imports
from app.cloud_native_optimization import (
    CloudNativeOptimizationService,
    AnomalyType,
    SeverityLevel,
    RecommendationType,
    CloudAnomaly,
    SavingsOpportunity,
    OptimizationRecommendation,
    create_optimization_service
)
from app.cost_analytics import CostAnalyzer, BudgetAnalyzer
from app.cloud_connectors import CloudConnectorFactory, extract_all_providers_data
from app.data_ingestion import DataIngestionService

# Novos imports para gerenciamento de credenciais
from app.credential_models import User, CloudCredentialConfig
from app.auth_security import get_current_active_user, security_manager
from app.credentials_api import credentials_router, auth_router, audit_router, get_provider_credentials
from app.budget_api import budget_router
from app.secrets_manager import get_secrets_manager_hybrid

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    # Startup
    logger.info("Starting X Cost API...")
    
    # Inicializar banco de dados
    if not init_database():
        logger.error("Failed to initialize database")
        raise RuntimeError("Database initialization failed")
    
    # Inicializar tabelas de credenciais
    from app.credential_models import Base
    Base.metadata.create_all(bind=db_manager.engine)
    
    # Criar usuário admin padrão se não existir
    try:
        from app.auth_security import create_user
        from app.credential_models import UserRole
        
        with db_manager.get_session() as db:
            existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if not existing_admin:
                admin_user = create_user(
                    db=db,
                    username="admin",
                    email="admin@finops.local",
                    password="ChangeMe123!",  # MUDE ISSO EM PRODUÇÃO
                    role=UserRole.ADMIN
                )
                logger.warning(f"Created default admin user: {admin_user.username} (CHANGE PASSWORD!)")
    except Exception as e:
        logger.error(f"Failed to create default admin user: {e}")
    
    # Verificar conexões
    health = health_check()
    if not health["overall"]:
        logger.error(f"Health check failed: {health}")



        raise RuntimeError("System health check failed")
    
    logger.info("X Cost API started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down X Cost API...")

# Metadados das tags para organização no Swagger
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Endpoints para autenticação e autorização"
    },
    {
        "name": "Credentials Management", 
        "description": "Gerenciamento de credenciais cloud"
    },
    {
        "name": "Budget Management",
        "description": "Gerenciamento de orçamentos e controle de gastos"
    },
    {
        "name": "Cost Analytics",
        "description": "Análises e relatórios de custos"
    },
    {
        "name": "Dashboard", 
        "description": "Resumo executivo e métricas principais"
    },
    {
        "name": "Data Ingestion",
        "description": "Ingestão e sincronização de dados"
    },
    {
        "name": "Cost Data",
        "description": "Dados brutos de custos e consumo"
    },
    {
        "name": "Cloud Providers",
        "description": "Status e configuração de provedores cloud"
    },
    {
        "name": "Security",
        "description": "Informações e configurações de segurança"
    },
    {
        "name": "System Health",
        "description": "Monitoramento da saúde do sistema"
    },
    {
        "name": "System Management",
        "description": "Operações administrativas do sistema"
    },
    {
        "name": "Audit",
        "description": "Logs de auditoria e rastreamento"
    },
    {
        "name": "Cloud Native Optimization",
        "description": "Otimização de custos cloud native, anomalias e recomendações"
    }
]

# Criar aplicação FastAPI
app = FastAPI(
    title="X Cost API",
    description="API completa para gerenciamento de custos multi-cloud",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure adequadamente em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para adicionar headers de segurança
@app.middleware("http")
async def security_middleware(request, call_next):
    """Middleware de segurança para headers adicionais"""
    response = await call_next(request)
    
    # Adicionar headers de segurança
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response

# Incluir routers de credenciais
app.include_router(auth_router)
app.include_router(credentials_router)
app.include_router(audit_router)
app.include_router(budget_router)

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    return response

# Rate limiting storage (em produção, usar Redis)
_rate_limit_storage = defaultdict(lambda: defaultdict(list))

def rate_limit(max_requests: int, window_minutes: int = 1):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum number of requests allowed
        window_minutes: Time window in minutes
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Encontrar o request e current_user nos argumentos
            request = None
            current_user = None
            
            for arg in args:
                if hasattr(arg, 'method') and hasattr(arg, 'url'):  # Request object
                    request = arg
                elif hasattr(arg, 'username'):  # User object
                    current_user = arg
                    
            for value in kwargs.values():
                if hasattr(value, 'method') and hasattr(value, 'url'):  # Request object
                    request = value
                elif hasattr(value, 'username'):  # User object
                    current_user = value
            
            if current_user:
                user_id = current_user.username
                endpoint = func.__name__
                now = time.time()
                window_start = now - (window_minutes * 60)
                
                # Limpar requests antigos
                _rate_limit_storage[user_id][endpoint] = [
                    req_time for req_time in _rate_limit_storage[user_id][endpoint]
                    if req_time > window_start
                ]
                
                # Verificar limite
                if len(_rate_limit_storage[user_id][endpoint]) >= max_requests:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_minutes} minute(s)"
                    )
                
                # Registrar request atual
                _rate_limit_storage[user_id][endpoint].append(now)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# === ENDPOINTS EXISTENTES DE DADOS DE CUSTO (mantidos) ===

@app.get("/api/v1/costs", response_model=List[FocusCostDataResponse], tags=["Cost Data"])
async def get_costs(
    params: CostQueryParams = Depends(),
    cache = Depends(get_cache),
    current_user: User = Depends(get_current_active_user)
):
    """Obtém dados de custo com filtros opcionais"""
    try:
        # Gerar chave de cache
        cache_key = f"costs:{hash(str(params.dict()))}"
        
        # Tentar obter do cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        # Usar SessionLocal diretamente
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Construir query
            from app.models import FocusCostData
            query = db.query(FocusCostData)
            
            # Aplicar filtros
            if params.provider_name:
                query = query.filter(FocusCostData.provider_name == params.provider_name)
            if params.service_name:
                query = query.filter(FocusCostData.service_name == params.service_name)
            if params.resource_type:
                query = query.filter(FocusCostData.resource_type == params.resource_type)
            if params.start_date:
                query = query.filter(FocusCostData.billing_period_start >= params.start_date)
            if params.end_date:
                query = query.filter(FocusCostData.billing_period_end <= params.end_date)
            
            # Filtros por tags
            if params.tags:
                for key, value in params.tags.items():
                    query = query.filter(FocusCostData.tags[key].astext == value)
            
            # Paginação e ordenação
            results = query.order_by(
                FocusCostData.billing_period_start.desc()
            ).offset(params.offset).limit(params.limit).all()
            
            # Converter para response model
            response_data = [FocusCostDataResponse.from_orm(result) for result in results]
            
            # Cachear resultado
            cache.set(cache_key, response_data, ttl=900)  # 15 minutos
            
            return response_data
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error fetching costs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === NOVOS ENDPOINTS PARA INGESTÃO SEGURA ===

@app.post("/api/v1/data/secure-ingest", tags=["Data Ingestion"])
async def trigger_secure_data_ingestion(
    background_tasks: BackgroundTasks,
    providers: Optional[List[str]] = None,
    credential_names: Optional[Dict[str, str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Inicia processo de ingestão de dados usando credenciais armazenadas"""
    try:
        # Verificar permissões
        from app.auth_security import security_manager
        if not security_manager.check_permission(current_user.role, "data:ingest"):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions for data ingestion"
            )
        
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = datetime.now()
        
        # Se não especificou provedores, usar todos os ativos
        if not providers:
            from app.database import SessionLocal
            
            db = SessionLocal()
            try:
                active_credentials = db.query(CloudCredentialConfig).filter(
                    CloudCredentialConfig.status == "active"
                ).all()
                providers = list(set([cred.provider_type.value for cred in active_credentials]))
            finally:
                db.close()
        
        # Adicionar tarefa em background
        background_tasks.add_task(
            run_secure_data_ingestion,
            start_date=start_date,
            end_date=end_date,
            providers=providers,
            credential_names=credential_names or {},
            user_id=str(current_user.id)
        )
        
        return {
            "message": "Secure data ingestion started",
            "start_date": start_date,
            "end_date": end_date,
            "providers": providers,
            "initiated_by": current_user.username,
            "status": "processing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering secure data ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_secure_data_ingestion(
    start_date: datetime,
    end_date: datetime,
    providers: List[str],
    credential_names: Dict[str, str],
    user_id: str
):
    """Executa ingestão de dados usando credenciais seguras"""
    try:
        logger.info(f"Starting secure data ingestion for {providers} by user {user_id}")
        
        all_data = {}
        
        for provider_name in providers:
            try:
                # Obter credenciais seguras para o provedor
                credential_name = credential_names.get(provider_name)
                
                from app.credential_models import CloudProviderType
                provider_type = CloudProviderType(provider_name)
                
                credentials = get_provider_credentials(
                    provider_type=provider_type,
                    credential_name=credential_name
                )
                
                # Criar conector com credenciais
                connector = CloudConnectorFactory.create_connector(
                    provider_name.lower(),
                    **credentials
                )
                
                # Extrair dados
                raw_data = connector.extract_cost_data(start_date, end_date)
                focus_data = connector.transform_to_focus(raw_data)
                all_data[provider_name] = focus_data
                
                logger.info(f"Successfully extracted {len(focus_data)} records from {provider_name}")
                
            except Exception as provider_error:
                logger.error(f"Failed to extract data from {provider_name}: {str(provider_error)}")
                all_data[provider_name] = []
        
        # Salvar no banco de dados
        total_inserted = 0
        with db_manager.get_session() as db:
            ingestion_service = DataIngestionService(db)
            
            for provider_name, focus_data in all_data.items():
                if focus_data:
                    inserted_count = ingestion_service.bulk_insert_focus_data(focus_data)
                    total_inserted += inserted_count
                    logger.info(f"Inserted {inserted_count} records for {provider_name}")
        
        logger.info(f"Secure data ingestion completed successfully. Total records: {total_inserted}")
        
        # Log da operação de ingestão
        try:
            from app.auth_security import AuditLogger
            from app.credential_models import AuditAction
            
            with db_manager.get_session() as db:
                audit_logger = AuditLogger(db)
                user = db.query(User).filter(User.id == user_id).first()
                
                if user:
                    audit_logger.log_credential_action(
                        user=user,
                        action=AuditAction.VIEW,  # Usando VIEW para operações de extração
                        details={
                            "action": "data_ingestion",
                            "providers": providers,
                            "records_inserted": total_inserted,
                            "start_date": start_date.isoformat(),
                            "end_date": end_date.isoformat()
                        },
                        success=True
                    )
        except Exception as audit_error:
            logger.warning(f"Failed to log ingestion audit: {audit_error}")
        
    except Exception as e:
        logger.error(f"Secure data ingestion failed: {str(e)}")
        
        # Log do erro
        try:
            with db_manager.get_session() as db:
                audit_logger = AuditLogger(db)
                user = db.query(User).filter(User.id == user_id).first()
                
                if user:
                    audit_logger.log_credential_action(
                        user=user,
                        action=AuditAction.VIEW,
                        details={
                            "action": "data_ingestion",
                            "providers": providers
                        },
                        success=False,
                        error_message=str(e)
                    )
        except:
            pass

# === ENDPOINTS DE MONITORAMENTO ATUALIZADOS ===

@app.get("/api/v1/health", tags=["System Health"])
async def health_check_endpoint():
    """Endpoint para verificação de saúde do sistema"""
    try:
        # Chamar health_check do database.py
        health = health_check()
        
        # Verificação com Secrets Manager (versão corrigida para macOS/LocalStack)
        try:
            secrets_manager = get_secrets_manager_hybrid()
            sm_health = secrets_manager.health_check()
            
            if sm_health["status"] == "healthy":
                health["secrets_manager"] = True
                health["secrets_manager_details"] = {
                    "status": "connected",
                    "is_localstack": sm_health.get("is_localstack", False),
                    "endpoint": sm_health.get("endpoint", "unknown"),
                    "method": sm_health.get("method", "hybrid"),
                    "region": sm_health.get("region", "us-east-1")
                }
                logger.info(f"✅ Secrets Manager OK (método: {sm_health.get('method', 'unknown')})")
                
                # Teste adicional: tentar criar secret de teste
                try:
                    test_arn = secrets_manager.create_test_secret("health-check")
                    health["secrets_manager_details"]["test_secret"] = "created"
                    logger.info("✅ Teste de criação de secret bem-sucedido")
                except Exception as test_error:
                    if 'already exists' in str(test_error).lower():
                        health["secrets_manager_details"]["test_secret"] = "exists"
                        logger.info("✅ Secret de teste já existe")
                    else:
                        health["secrets_manager_details"]["test_secret"] = f"failed: {test_error}"
                        logger.warning(f"⚠️ Teste de criação falhou: {test_error}")
                
            else:
                health["secrets_manager"] = False
                health["secrets_manager_details"] = {
                    "status": "error",
                    "error": sm_health.get("error", "unknown"),
                    "method": sm_health.get("method", "unknown")
                }
                
                # Em desenvolvimento, não falhar o health check geral
                environment = os.getenv("ENVIRONMENT", "production").lower()
                if environment in ["development", "dev", "local"]:
                    logger.warning(f"⚠️ Secrets Manager falhou em desenvolvimento: {sm_health.get('error')}")
                    logger.warning("💡 Health check continuará OK para desenvolvimento")
                else:
                    health["overall"] = False
                    
        except Exception as e:
            logger.error(f"❌ Secrets Manager inicialização falhou: {e}")
            
            # Em desenvolvimento, continuar sem falhar
            environment = os.getenv("ENVIRONMENT", "production").lower()
            if environment in ["development", "dev", "local"]:
                logger.warning("⚠️ Continuando sem Secrets Manager em desenvolvimento")
                health["secrets_manager"] = False
                health["secrets_manager_details"] = {
                    "status": "disabled_in_dev",
                    "reason": f"Initialization failed: {str(e)}",
                    "method": "none"
                }
            else:
                health["secrets_manager"] = False
                health["overall"] = False
        
        status_code = 200 if health["overall"] else 503;
        
        return JSONResponse(
            status_code=status_code,
            content=health
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={"error": str(e), "overall": False}
        )


@app.get("/api/v1/system/status", tags=["System Health"])
async def get_system_status(
    current_user: User = Depends(get_current_active_user)
):
    """Obtém status detalhado do sistema"""
    try:
        # Verificar permissões
        from app.auth_security import security_manager
        if not security_manager.check_permission(current_user.role, "system:admin"):
            return {
                "system_status": "operational",
                "user_role": current_user.role.value,
                "access_level": "basic"
            }
        
        # Status completo para admins
        health = health_check()
        
        # Usar SessionLocal diretamente
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Estatísticas de credenciais
            credential_stats = db.query(CloudCredentialConfig).count()
            active_credentials = db.query(CloudCredentialConfig).filter(
                CloudCredentialConfig.status == "active"
            ).count()
            
            # Estatísticas de usuários
            user_stats = {
                "total_users": db.query(User).count(),
                "active_users": db.query(User).filter(User.is_active == True).count(),
                "admin_users": db.query(User).filter(User.role == "admin").count()
            }
            
            # Últimas atividades de auditoria
            try:
                from app.credential_models import CredentialAuditLog
                recent_activities = db.query(CredentialAuditLog).order_by(
                    CredentialAuditLog.timestamp.desc()
                ).limit(5).all()
                
                activities_list = []
                for activity in recent_activities:
                    activities_list.append({
                        "action": activity.action.value,
                        "user": activity.user.username,
                        "timestamp": activity.timestamp,
                        "success": activity.success
                    })
            except Exception as audit_error:
                logger.warning(f"Error getting audit logs: {audit_error}")
                activities_list = []
            
            return {
                "system_health": health,
                "credential_stats": {
                    "total": credential_stats,
                    "active": active_credentials,
                    "inactive": credential_stats - active_credentials
                },
                "user_stats": user_stats,
                "recent_activities": activities_list,
                "generated_at": datetime.utcnow()
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINTS PARA CONFIGURAÇÃO DE PROVEDORES ===

@app.get("/api/v1/providers/status", tags=["Cloud Providers"])
async def get_providers_status(
    current_user: User = Depends(get_current_active_user)
):
    """Obtém status dos provedores de nuvem configurados"""
    try:
        from app.credential_models import CloudProviderType
        from app.database import SessionLocal
        
        provider_status = {}
        
        db = SessionLocal()
        try:
            for provider_type in CloudProviderType:
                # Contar credenciais por provedor
                total_creds = db.query(CloudCredentialConfig).filter(
                    CloudCredentialConfig.provider_type == provider_type
                ).count()
                
                active_creds = db.query(CloudCredentialConfig).filter(
                    CloudCredentialConfig.provider_type == provider_type,
                    CloudCredentialConfig.status == "active"
                ).count()
                
                # Última validação
                last_credential = db.query(CloudCredentialConfig).filter(
                    CloudCredentialConfig.provider_type == provider_type
                ).order_by(CloudCredentialConfig.last_validated.desc()).first()
                
                provider_status[provider_type.value] = {
                    "total_credentials": total_creds,
                    "active_credentials": active_creds,
                    "status": "configured" if active_creds > 0 else "not_configured",
                    "last_validated": last_credential.last_validated if last_credential else None,
                    "last_validation_success": (
                        last_credential.status == "active" if last_credential else None
                    )
                }
            
            return {
                "providers": provider_status,
                "total_configured": sum(1 for p in provider_status.values() if p["active_credentials"] > 0),
                "checked_at": datetime.utcnow()
            }
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error getting providers status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINTS DE UTILITÁRIOS ATUALIZADOS ===

@app.delete("/api/v1/cache/clear", tags=["System Management"])
async def clear_cache(
    pattern: Optional[str] = "*",
    current_user: User = Depends(get_current_active_user),
    cache = Depends(get_cache)
):
    """Limpa cache do sistema"""
    try:
        # Verificar permissões
        from app.auth_security import security_manager
        if not security_manager.check_permission(current_user.role, "system:admin"):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required to clear cache"
            )
        
        cleared_count = cache.clear_pattern(pattern)
        
        return {
            "message": "Cache cleared successfully",
            "pattern": pattern,
            "cleared_keys": cleared_count,
            "cleared_by": current_user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === ENDPOINTS EXISTENTES MANTIDOS (com autenticação adicionada) ===

# Todos os endpoints existentes de analytics, budgets, etc. são mantidos
# mas agora requerem autenticação via get_current_active_user

@app.get("/api/v1/analytics/trend", tags=["Cost Analytics"])
async def get_cost_trend(
    provider_name: Optional[str] = None,
    service_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    period: str = "daily",
    current_user: User = Depends(get_current_active_user),  # Autenticação adicionada
    db: Session = Depends(get_database)
):
    """Obtém tendência de custos (agora requer autenticação)"""
    try:
        analyzer = CostAnalyzer(db)
        trend_data = analyzer.calculate_cost_trend(
            provider_name=provider_name,
            service_name=service_name,
            start_date=start_date.date() if start_date else None,
            end_date=end_date.date() if end_date else None,
            period=period
        )
        
        return {
            "trend_data": trend_data,
            "period": period,
            "filters": {
                "provider_name": provider_name,
                "service_name": service_name,
                "start_date": start_date,
                "end_date": end_date
            },
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error calculating trend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/by-service", tags=["Cost Analytics"])
async def get_cost_by_service(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_n: Optional[int] = 10,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém breakdown de custos por serviço AWS"""
    try:
        # Determinar período: usar start_date/end_date se fornecidos, senão usar 'days'
        if start_date and end_date:
            # Validar que end_date > start_date
            if end_date <= start_date:
                raise HTTPException(status_code=400, detail="end_date must be greater than start_date")
            
            period_start = start_date
            period_end = end_date
            period_days = (end_date - start_date).days + 1
        else:
            # Usar lógica existente baseada em 'days'
            period_end = date.today()
            period_start = period_end - timedelta(days=days-1)  # -1 para incluir o dia atual
            period_days = days
        
        analyzer = CostAnalyzer(db)
        
        # Usar provider_name passado como parâmetro, se fornecido
        effective_provider_name = provider_name
        if credential_id and not provider_name:
            # Aqui você poderia buscar o provider_name baseado no credential_id
            # Por enquanto, vamos manter como None para buscar todos os providers
            effective_provider_name = None
        
        service_data = analyzer.analyze_by_service(
            provider_name=effective_provider_name,
            start_date=period_start,
            end_date=period_end,
            top_n=top_n
        )
        
        return {
            "service_breakdown": service_data,
            "period": {
                "start_date": period_start,
                "end_date": period_end,
                "days": period_days
            },
            "filters": {
                "credential_id": credential_id,
                "provider_name": effective_provider_name,
                "top_n": top_n
            },
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error calculating service breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dashboard/summary", response_model=DashboardSummary, tags=["Dashboard"])
async def get_dashboard_summary(
    period_days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém resumo consolidado para o dashboard"""
    try:
        from app.cost_analytics import DashboardAnalyzer
        
        # Determinar período: usar start_date/end_date se fornecidos, senão usar 'period_days'
        if start_date and end_date:
            # Validar que end_date > start_date
            if end_date <= start_date:
                raise HTTPException(status_code=400, detail="end_date must be greater than start_date")
            
            calculated_days = (end_date - start_date).days + 1
        else:
            # Usar lógica existente baseada em 'period_days'
            calculated_days = period_days
        
        dashboard_analyzer = DashboardAnalyzer(db)
        summary = dashboard_analyzer.get_dashboard_summary(
            period_days=calculated_days,
            provider_name=provider_name
        )
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/by-region", tags=["Cost Analytics"])
async def get_cost_by_region(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_n: Optional[int] = 10,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém breakdown de custos por região AWS"""
    try:
        # Determinar período: usar start_date/end_date se fornecidos, senão usar 'days'
        if start_date and end_date:
            # Validar que end_date > start_date
            if end_date <= start_date:
                raise HTTPException(status_code=400, detail="end_date must be greater than start_date")
            
            period_start = start_date
            period_end = end_date
            period_days = (end_date - start_date).days + 1
        else:
            # Usar lógica existente baseada em 'days'
            period_end = date.today()
            period_start = period_end - timedelta(days=days-1)  # -1 para incluir o dia atual
            period_days = days
        
        analyzer = CostAnalyzer(db)
        
        # Usar provider_name passado como parâmetro, se fornecido
        effective_provider_name = provider_name
        if credential_id and not provider_name:
            # Aqui você poderia buscar o provider_name baseado no credential_id
            # Por enquanto, vamos manter como None para buscar todos os providers
            effective_provider_name = None
        
        region_data = analyzer.analyze_by_region(
            provider_name=effective_provider_name,
            start_date=period_start,
            end_date=period_end,
            top_n=top_n
        )
        
        return {
            "region_breakdown": region_data,
            "period": {
                "start_date": period_start,
                "end_date": period_end,
                "days": period_days
            },
            "filters": {
                "credential_id": credential_id,
                "provider_name": effective_provider_name,
                "top_n": top_n
            },
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error calculating region breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/by-category", tags=["Cost Analytics"])
async def get_cost_by_category(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_n: Optional[int] = 10,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém breakdown de custos por categoria de serviço"""
    try:
        # Determinar período: usar start_date/end_date se fornecidos, senão usar 'days'
        if start_date and end_date:
            # Validar que end_date > start_date
            if end_date <= start_date:
                raise HTTPException(status_code=400, detail="end_date must be greater than start_date")
            
            period_start = start_date
            period_end = end_date
            period_days = (end_date - start_date).days + 1
        else:
            # Usar lógica existente baseada em 'days'
            period_end = date.today()
            period_start = period_end - timedelta(days=days-1)  # -1 para incluir o dia atual
            period_days = days
        
        analyzer = CostAnalyzer(db)
        
        # Usar provider_name diretamente se fornecido
        category_data = analyzer.analyze_by_category(
            provider_name=provider_name,
            start_date=period_start,
            end_date=period_end,
            top_n=top_n
        )
        
        # Calcular total de custos para o período
        total_cost = sum(item['total_cost'] for item in category_data)
        
        return {
            "category_breakdown": category_data,
            "period": {
                "start_date": period_start,
                "end_date": period_end,
                "days": period_days
            },
            "total_cost": total_cost,
            "filters": {
                "credential_id": credential_id,
                "top_n": top_n
            },
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error calculating category breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# === MIDDLEWARE DE TRATAMENTO DE ERROS ATUALIZADO ===

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global para exceções"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Não expor detalhes técnicos em produção
    import os
    debug_mode = os.getenv("ENVIRONMENT", "production") != "production"
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if debug_mode else "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# === ENDPOINT DE DOCUMENTAÇÃO DE SEGURANÇA ===

@app.get("/api/v1/security/info", tags=["Security"])
async def get_security_info():
    """Retorna informações públicas sobre segurança da API"""
    return {
        "authentication": {
            "method": "JWT Bearer Token",
            "endpoint": "/api/v1/auth/login",
            "token_expiry": "1 hour"
        },
        "authorization": {
            "method": "Role-Based Access Control (RBAC)",
            "roles": ["admin", "finops_admin", "operator", "viewer"]
        },
        "encryption": {
            "in_transit": "TLS 1.3",
            "at_rest": "AWS KMS + AES-256",
            "credentials": "Multi-layer encryption"
        },
        "audit": {
            "logging": "Complete audit trail",
            "retention": "2 years",
            "endpoint": "/api/v1/audit/logs"
        },
        "compliance": [
            "OWASP Top 10",
            "NIST Cybersecurity Framework",
            "SOC 2 ready"
        ]
    }


# === CLOUD NATIVE OPTIMIZATION ENDPOINTS ===

# Global optimization service instance
optimization_service: Optional[CloudNativeOptimizationService] = None

@app.on_event("startup")
async def init_optimization_service():
    """Initialize optimization service on startup"""
    global optimization_service
    try:
        from app.cloud_native_optimization import load_config_from_env
        import redis
        
        # Criar cliente Redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        # Carregar configuração
        config = load_config_from_env()
        
        # Criar serviço
        optimization_service = create_optimization_service(redis_client, config)
        logger.info("Cloud Native Optimization Service initialized successfully")
    except Exception as e:
        logger.warning(f"Cloud Native Optimization Service initialization failed: {e}")
        # Don't fail startup if optimization service fails


def get_optimization_service() -> CloudNativeOptimizationService:
    """Dependency to get optimization service instance"""
    if optimization_service is None:
        raise HTTPException(status_code=503, detail="Optimization service not available")
    return optimization_service


@app.get("/api/v1/anomalies", tags=["Cloud Native Optimization"])
@rate_limit(max_requests=100, window_minutes=1)
async def get_anomalies(
    provider: Optional[str] = Query(None, description="Cloud provider (AWS, Azure, GCP, Oracle) or None for all"),
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    severity: Optional[str] = Query(None, description="Filter by severity: high, medium, low"),
    force_refresh: bool = Query(False, description="Force refresh from cache"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Get cost anomalies from specified cloud providers
    
    **Query Parameters:**
    - `provider`: Cloud provider to analyze (AWS, Azure, GCP, Oracle) or None for all providers
    - `days`: Number of days to analyze (1-365, default: 30)
    - `severity`: Filter by severity level (high, medium, low)
    - `force_refresh`: Skip cache and get fresh data
    
    **Returns:**
    List of detected cost anomalies with severity levels, cost impact, and metadata.
    
    **Rate Limiting:** 100 requests per minute per user
    """
    try:
        start_time = datetime.utcnow()
        
        # Validar severity se fornecido
        if severity and severity.lower() not in ['high', 'medium', 'low']:
            raise HTTPException(
                status_code=400, 
                detail="Invalid severity. Must be 'high', 'medium', or 'low'"
            )
        
        # Mapear provider para formato interno
        provider_name = provider.lower() if provider else None
        
        # Buscar anomalias
        anomalies = await service.get_anomalies_by_provider(provider_name=provider_name)
        
        # Filtrar por severidade se especificado
        if severity:
            anomalies = [a for a in anomalies if hasattr(a, 'severity') and a.severity.lower() == severity.lower()]
        
        # Calcular métricas
        total_cost_impact = sum(a.cost_impact for a in anomalies if hasattr(a, 'cost_impact'))
        severity_count = {}
        for anomaly in anomalies:
            if hasattr(anomaly, 'severity'):
                severity_level = anomaly.severity
                severity_count[severity_level] = severity_count.get(severity_level, 0) + 1
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Retrieved {len(anomalies)} anomalies for user {current_user.username}")
        
        return {
            "data": anomalies,
            "metadata": {
                "total_count": len(anomalies),
                "total_cost_impact": round(total_cost_impact, 2),
                "severity_breakdown": severity_count,
                "filters": {
                    "provider": provider,
                    "days": days,
                    "severity": severity
                },
                "last_updated": end_time.isoformat(),
                "processing_time_seconds": round(processing_time, 3),
                "requested_by": current_user.username
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get anomalies: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve anomalies")

@app.get("/api/v1/savings-opportunities", tags=["Cloud Native Optimization"])
@rate_limit(max_requests=100, window_minutes=1)
async def get_savings_opportunities(
    provider: Optional[str] = Query(None, description="Cloud provider (AWS, Azure, GCP, Oracle) or None for all"),
    min_savings: Optional[float] = Query(None, description="Minimum monthly savings threshold in USD"),
    category: Optional[str] = Query(None, description="Filter by category: rightsizing, unused_resources, reserved_instances, etc."),
    force_refresh: bool = Query(False, description="Force refresh from cache"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Get cost savings opportunities from specified cloud providers
    
    **Query Parameters:**
    - `provider`: Cloud provider to analyze (AWS, Azure, GCP, Oracle) or None for all providers
    - `min_savings`: Minimum monthly savings threshold in USD
    - `category`: Filter by opportunity category (rightsizing, unused_resources, reserved_instances, etc.)
    - `force_refresh`: Skip cache and get fresh data
    
    **Returns:**
    List of identified savings opportunities with potential impact, confidence levels, and implementation guidance.
    
    **Rate Limiting:** 100 requests per minute per user
    """
    try:
        start_time = datetime.utcnow()
        
        # Mapear provider para formato interno
        provider_name = provider.lower() if provider else None
        
        # Buscar oportunidades
        opportunities = await service.get_savings_opportunities_by_provider(provider_name=provider_name)
        
        # Filtrar por valor mínimo se especificado
        if min_savings is not None:
            opportunities = [o for o in opportunities if hasattr(o, 'potential_savings') and o.potential_savings >= min_savings]
        
        # Filtrar por categoria se especificado
        if category:
            opportunities = [o for o in opportunities if hasattr(o, 'category') and category.lower() in o.category.lower()]
        
        # Calcular métricas
        total_potential_savings = sum(o.potential_savings for o in opportunities if hasattr(o, 'potential_savings'))
        category_breakdown = {}
        effort_breakdown = {}
        
        for opportunity in opportunities:
            if hasattr(opportunity, 'category'):
                cat = opportunity.category
                category_breakdown[cat] = category_breakdown.get(cat, 0) + 1
            
            if hasattr(opportunity, 'effort_level'):
                effort = opportunity.effort_level
                effort_breakdown[effort] = effort_breakdown.get(effort, 0) + 1
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Retrieved {len(opportunities)} savings opportunities for user {current_user.username}")
        
        return {
            "data": opportunities,
            "metadata": {
                "total_count": len(opportunities),
                "total_potential_savings": round(total_potential_savings, 2),
                "category_breakdown": category_breakdown,
                "effort_breakdown": effort_breakdown,
                "filters": {
                    "provider": provider,
                    "min_savings": min_savings,
                    "category": category
                },
                "last_updated": end_time.isoformat(),
                "processing_time_seconds": round(processing_time, 3),
                "requested_by": current_user.username
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get savings opportunities: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve savings opportunities")


@app.get("/api/v1/optimization/recommendations", response_model=List[OptimizationRecommendation], tags=["Cloud Native Optimization"])
async def get_optimization_recommendations(
    provider_name: Optional[str] = Query(None, description="Cloud provider to check"),
    recommendation_type: Optional[RecommendationType] = Query(None, description="Type of recommendations to include"),
    force_refresh: bool = Query(False, description="Force refresh from cache"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Get comprehensive optimization recommendations
    
    Returns prioritized list of optimization recommendations based on anomalies and savings opportunities.
    """
    try:
        recommendations = await service.get_unified_recommendations(provider_name=provider_name)
        logger.info(f"Retrieved {len(recommendations)} recommendations for user {current_user.username}")
        return recommendations
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recommendations")


@app.get("/api/v1/optimization/summary", tags=["Cloud Native Optimization"])
@rate_limit(max_requests=50, window_minutes=1)
async def get_optimization_summary(
    provider: Optional[str] = Query(None, description="Cloud provider (AWS, Azure, GCP, Oracle) or None for all"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
) -> Dict[str, Any]:
    """
    Get comprehensive optimization summary
    
    **Query Parameters:**
    - `provider`: Cloud provider to analyze (AWS, Azure, GCP, Oracle) or None for all providers
    
    **Returns:**
    Aggregated statistics and metrics for anomalies, savings opportunities, and recommendations.
    Includes optimization score, total potential impact, and prioritized insights.
    
    **Rate Limiting:** 50 requests per minute per user
    """
    try:
        start_time = datetime.utcnow()
        
        # Mapear provider para formato interno
        provider_name = provider.lower() if provider else None
        
        # Chamar métodos individuais e consolidar
        anomalies = await service.get_anomalies_by_provider(provider_name)
        opportunities = await service.get_savings_opportunities_by_provider(provider_name)
        recommendations = await service.get_unified_recommendations(provider_name)
        
        # Calcular métricas agregadas
        total_cost_impact = sum(a.cost_impact for a in anomalies if hasattr(a, 'cost_impact'))
        total_potential_savings = sum(o.potential_savings for o in opportunities if hasattr(o, 'potential_savings'))
        
        # Breakdown por severidade de anomalias
        anomaly_severity_breakdown = {}
        for anomaly in anomalies:
            if hasattr(anomaly, 'severity'):
                severity = anomaly.severity
                anomaly_severity_breakdown[severity] = anomaly_severity_breakdown.get(severity, 0) + 1
        
        # Breakdown por tipo de recomendação
        recommendation_type_breakdown = {}
        for rec in recommendations:
            if hasattr(rec, 'type'):
                rec_type = rec.type
                recommendation_type_breakdown[rec_type] = recommendation_type_breakdown.get(rec_type, 0) + 1
        
        # Calcular optimization score (0-100)
        optimization_score = 100
        if anomalies:
            optimization_score -= min(50, len(anomalies) * 5)  # Penalizar anomalias
        if opportunities:
            optimization_score += min(20, len(opportunities) * 2)  # Bonificar oportunidades identificadas
        optimization_score = max(0, min(100, optimization_score))
        
        # Top insights
        top_anomaly = max(anomalies, key=lambda x: getattr(x, 'cost_impact', 0)) if anomalies else None
        top_opportunity = max(opportunities, key=lambda x: getattr(x, 'potential_savings', 0)) if opportunities else None
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        summary = {
            "anomalies": {
                "total_count": len(anomalies),
                "total_cost_impact": round(total_cost_impact, 2),
                "severity_breakdown": anomaly_severity_breakdown,
                "top_anomaly": {
                    "description": getattr(top_anomaly, 'description', None),
                    "cost_impact": getattr(top_anomaly, 'cost_impact', 0),
                    "severity": getattr(top_anomaly, 'severity', None)
                } if top_anomaly else None
            },
            "savings_opportunities": {
                "total_count": len(opportunities),
                "total_potential_savings": round(total_potential_savings, 2),
                "top_opportunity": {
                    "description": getattr(top_opportunity, 'description', None),
                    "potential_savings": getattr(top_opportunity, 'potential_savings', 0),
                    "category": getattr(top_opportunity, 'category', None)
                } if top_opportunity else None
            },
            "recommendations": {
                "total_count": len(recommendations),
                "type_breakdown": recommendation_type_breakdown,
                "high_priority_count": len([r for r in recommendations if hasattr(r, 'priority') and r.priority in ['high', 'critical']])
            },
            "optimization_metrics": {
                "optimization_score": round(optimization_score, 1),
                "total_potential_impact": round(total_cost_impact + total_potential_savings, 2),
                "health_status": "excellent" if optimization_score >= 90 else 
                               "good" if optimization_score >= 70 else 
                               "needs_attention" if optimization_score >= 50 else "critical"
            },
            "metadata": {
                "provider": provider,
                "analysis_scope": "all_providers" if not provider else f"{provider}_only",
                "last_updated": end_time.isoformat(),
                "processing_time_seconds": round(processing_time, 3),
                "requested_by": current_user.username
            }
        }
        
        logger.info(f"Generated optimization summary for user {current_user.username}")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get optimization summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve optimization summary")


@app.post("/api/v1/optimization/cache/invalidate", tags=["Cloud Native Optimization"])
async def invalidate_optimization_cache(
    pattern: str = Query("*", description="Cache pattern to invalidate"),
    current_user: User = Depends(get_current_active_user),
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    """
    Invalidate cache entries matching the specified pattern
    
    Useful for forcing refresh of optimization data when cloud configurations change.
    """
    try:
        # Verificar permissões de admin
        from app.auth_security import security_manager
        if not security_manager.check_permission(current_user.role, "system:admin"):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required to invalidate cache"
            )
        
        await service.invalidate_cache(pattern)
        logger.info(f"Cache invalidated for pattern: {pattern} by user {current_user.username}")
        return {"message": f"Cache invalidated for pattern: {pattern}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to invalidate cache")


@app.get("/api/v1/optimization/providers", tags=["Cloud Native Optimization"])
async def get_supported_providers():
    """Get list of supported cloud providers for optimization"""
    return {
        "providers": ["aws", "azure", "gcp", "oracle"],
        "descriptions": {
            "aws": "Amazon Web Services",
            "azure": "Microsoft Azure", 
            "gcp": "Google Cloud Platform",
            "oracle": "Oracle Cloud Infrastructure"
        }
    }


@app.get("/api/v1/optimization/types", tags=["Cloud Native Optimization"])
async def get_optimization_types():
    """Get list of supported optimization types"""
    return {
        "types": list(RecommendationType),
        "descriptions": {
            RecommendationType.RIGHTSIZING: "Rightsizing recommendations for compute resources",
            RecommendationType.RESERVED_INSTANCES: "Reserved instance recommendations",
            RecommendationType.SPOT_INSTANCES: "Spot instance recommendations",
            RecommendationType.STORAGE_OPTIMIZATION: "Storage optimization recommendations",
            RecommendationType.NETWORK_OPTIMIZATION: "Network optimization recommendations",
            RecommendationType.IDLE_RESOURCES: "Idle resource identification",
            RecommendationType.SCHEDULING: "Resource scheduling optimizations"
        }
    }


# === END CLOUD NATIVE OPTIMIZATION ENDPOINTS ===