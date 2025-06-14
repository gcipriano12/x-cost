from app.secrets_manager import get_secrets_manager_hybrid
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import logging
import os
from contextlib import asynccontextmanager

# Imports existentes
from app.database import get_database, get_cache, db_manager, cache_manager, init_database, health_check
from app.models import (
    FocusCostDataResponse, CostAnalysisResponse, BudgetResponse,
    CostQueryParams, AnalysisQueryParams, FocusCostDataCreate,
    BudgetCreate, CostSummary, MonthlyCostResponse, CostForecast,
    DashboardSummary
)
from app.cost_analytics import CostAnalyzer, BudgetAnalyzer
from app.cloud_connectors import CloudConnectorFactory, extract_all_providers_data
from app.data_ingestion import DataIngestionService

# Novos imports para gerenciamento de credenciais
from app.credential_models import User, CloudCredentialConfig
from app.auth_security import get_current_active_user, security_manager
from app.credentials_api import credentials_router, auth_router, audit_router, get_provider_credentials
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

# Criar aplicação FastAPI
app = FastAPI(
    title="X Cost API",
    description="API completa para gerenciamento de custos multi-cloud",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
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

# === ENDPOINTS EXISTENTES DE DADOS DE CUSTO (mantidos) ===

@app.get("/api/v1/costs", response_model=List[FocusCostDataResponse])
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

@app.post("/api/v1/data/secure-ingest")
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

@app.get("/api/v1/health")
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


@app.get("/api/v1/system/status")
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

@app.get("/api/v1/providers/status")
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

@app.delete("/api/v1/cache/clear")
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

@app.get("/api/v1/analytics/trend")
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

@app.get("/api/v1/analytics/by-service")
async def get_cost_by_service(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    top_n: Optional[int] = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém breakdown de custos por serviço AWS"""
    try:
        # Calcular período baseado nos dias
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        analyzer = CostAnalyzer(db)
        
        # Por enquanto, vamos usar provider_name como None se credential_id for fornecido
        # Em uma implementação completa, você mapearia credential_id para provider_name
        provider_name = None
        if credential_id:
            # Aqui você poderia buscar o provider_name baseado no credential_id
            # Por enquanto, vamos simular com dados existentes
            pass
        
        service_data = analyzer.analyze_by_service(
            provider_name=provider_name,
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )
        
        return {
            "service_breakdown": service_data,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
            "filters": {
                "credential_id": credential_id,
                "top_n": top_n
            },
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error calculating service breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/dashboard/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    period_days: int = 30,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém resumo consolidado para o dashboard"""
    try:
        from app.cost_analytics import DashboardAnalyzer
        
        dashboard_analyzer = DashboardAnalyzer(db)
        summary = dashboard_analyzer.get_dashboard_summary(period_days=period_days)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/by-region")
async def get_cost_by_region(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    top_n: Optional[int] = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém breakdown de custos por região AWS"""
    try:
        # Calcular período baseado nos dias
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        analyzer = CostAnalyzer(db)
        
        # Por enquanto, vamos usar provider_name como None se credential_id for fornecido
        # Em uma implementação completa, você mapearia credential_id para provider_name
        provider_name = None
        if credential_id:
            # Aqui você poderia buscar o provider_name baseado no credential_id
            # Por enquanto, vamos simular com dados existentes
            pass
        
        region_data = analyzer.analyze_by_region(
            provider_name=provider_name,
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )
        
        return {
            "region_breakdown": region_data,
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": days
            },
            "filters": {
                "credential_id": credential_id,
                "top_n": top_n
            },
            "requested_by": current_user.username
        }
        
    except Exception as e:
        logger.error(f"Error calculating region breakdown: {str(e)}")
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

@app.get("/api/v1/security/info")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )