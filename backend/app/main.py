"""
X-Cost API - Main Application (Completely Modular)

Arquivo principal completamente refatorado com arquitetura modular.
Todos os endpoints foram extraídos para routers específicos.
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from collections import defaultdict

# Carregar variáveis de ambiente do arquivo .env
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

# Database and core imports
from app.database import get_database, db_manager, cache_manager, init_database, health_check
from app.models import DashboardSummary

# Cloud Native Optimization imports
from app.cloud_native_optimization import get_optimization_service

# Security and authentication
from app.credential_models import User, UserRole
from app.auth_security import get_current_active_user, create_user, security_manager

# Router imports - All endpoints are now in dedicated routers
from app.credentials_api import credentials_router, auth_router, audit_router
from app.budget_api import budget_router
from app.routers.analytics_api import router as analytics_router
from app.routers.optimization_api import optimization_router
from app.routers.services_api import router as services_router
from app.routers.team_costs import router as team_costs_router
from app.routers.kpi_api import router as kpi_router
from app.virtual_tags_api import router as virtual_tags_router

# Utilities
from app.utils.response_helpers import StandardResponse

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
    logger.info("Starting X Cost API (Modular Architecture)...")
    
    # Inicializar banco de dados
    if not init_database():
        logger.error("Failed to initialize database")
        raise RuntimeError("Database initialization failed")
    
    # Inicializar tabelas de credenciais
    from app.credential_models import Base
    Base.metadata.create_all(bind=db_manager.engine)
    
    # Criar usuário admin padrão se não existir
    try:
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
    
    # Inicializar serviço de otimização
    await init_optimization_service()
    
    logger.info("X Cost API (Modular) started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down X Cost API...")
    if db_manager:
        db_manager.close()
    if cache_manager:
        cache_manager.close()
    logger.info("X Cost API shutdown complete")


async def init_optimization_service():
    """Inicializa o serviço de otimização cloud native"""
    try:
        service = get_optimization_service()
        logger.info("Cloud Native Optimization Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize optimization service: {e}")
        # Não parar a aplicação por causa disso
        pass


# Tags metadata para documentação da API
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Autenticação e autorização de usuários"
    },
    {
        "name": "Credentials",
        "description": "Gerenciamento de credenciais cloud"
    },
    {
        "name": "Budgets",
        "description": "Gerenciamento de orçamentos e alertas"
    },
    {
        "name": "Analytics", 
        "description": "Análises e relatórios de custos"
    },
    {
        "name": "Team Costs",
        "description": "Análise de custos por equipe baseada em tags"
    },
    {
        "name": "Virtual Tags",
        "description": "Gerenciamento de Virtual Tags para alocação dinâmica de custos"
    },
    {
        "name": "Dashboard", 
        "description": "Resumo executivo e métricas principais"
    },
    {
        "name": "Cloud Native Optimization",
        "description": "Otimização de custos cloud native, anomalias e recomendações"
    },
    {
        "name": "System Health",
        "description": "Monitoramento da saúde do sistema"
    },
    {
        "name": "Audit",
        "description": "Logs de auditoria e rastreamento"
    }
]


# Criar aplicação FastAPI
app = FastAPI(
    title="X Cost API",
    description="API completa para gerenciamento de custos multi-cloud (Arquitetura Modular)",
    version="3.0.0",
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
async def security_middleware(request: Request, call_next):
    """Middleware de segurança para headers adicionais"""
    response = await call_next(request)
    
    # Adicionar headers de segurança
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logging detalhado de requisições"""
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds()
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    return response


# ===== INCLUIR TODOS OS ROUTERS MODULARES =====

# Routers de autenticação e credenciais
app.include_router(auth_router)
app.include_router(credentials_router)
app.include_router(audit_router)

# Router de orçamentos
app.include_router(budget_router)

# Routers de analytics e otimização (novos)
app.include_router(analytics_router)
app.include_router(optimization_router)

# Router de KPIs
app.include_router(kpi_router)

# Router de services
app.include_router(services_router)

# Router de team costs
app.include_router(team_costs_router)

# Router de Virtual Tags
app.include_router(virtual_tags_router)


# ===== ENDPOINTS BÁSICOS E ESSENCIAIS =====

@app.get("/", tags=["System Health"])
async def root():
    """Endpoint raiz da API"""
    return StandardResponse.success({
        "message": "X Cost API - Modular Architecture",
        "version": "3.0.0",
        "status": "running",
        "architecture": "modular",
        "documentation": "/docs",
        "health_check": "/health"
    })


@app.get("/health", tags=["System Health"])
async def health_endpoint():
    """Endpoint de verificação de saúde simplificado"""
    try:
        health = health_check()
        status_code = 200 if health["overall"] else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "healthy" if health["overall"] else "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "3.0.0",
                "components": health
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@app.get("/api/v1/system/info", tags=["System Health"])
async def get_system_info(
    current_user: User = Depends(get_current_active_user)
):
    """Informações básicas do sistema (requer autenticação)"""
    try:
        # Verificar se é admin para informações completas
        is_admin = security_manager.check_permission(current_user.role, "system:admin")
        
        basic_info = {
            "api_version": "3.0.0",
            "architecture": "modular",
            "user": {
                "username": current_user.username,
                "role": current_user.role.value,
                "is_admin": is_admin
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if is_admin:
            # Informações completas para admins
            health = health_check()
            basic_info.update({
                "system_health": health,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "database_status": health.get("database", False),
                "cache_status": health.get("cache", False)
            })
        
        return StandardResponse.success(basic_info)
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== EXCEPTION HANDLERS =====

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


# ===== STARTUP MESSAGE =====

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting X Cost API with modular architecture...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")