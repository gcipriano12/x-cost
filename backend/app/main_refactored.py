"""
X-Cost API Main Application (Refactored)

Aplicação principal refatorada usando arquitetura modular
"""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

# Imports de configuração
from app.database import init_database, health_check, db_manager
from app.credential_models import Base, User, UserRole

# Imports de middleware
from app.middleware.security import (
    configure_cors_middleware, 
    comprehensive_security_middleware
)
from app.middleware.rate_limiting import rate_limit_middleware

# Imports de routers
from app.routers.system_api import router as system_router
from app.routers.cost_data_api import router as cost_data_router  
from app.routers.data_ingestion_api import router as data_ingestion_router

# Imports de routers existentes
from app.credentials_api import credentials_router, auth_router, audit_router
from app.budget_api import budget_router

# Imports para otimização
from app.cloud_native_optimization import get_optimization_service

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Tags para documentação da API
tags_metadata = [
    {
        "name": "Authentication",
        "description": "Endpoints para autenticação e autorização"
    },
    {
        "name": "System",
        "description": "Monitoramento e status do sistema"
    },
    {
        "name": "Cost Data", 
        "description": "Recuperação de dados de custo básicos"
    },
    {
        "name": "Data Ingestion",
        "description": "Ingestão segura de dados de múltiplos provedores"
    },
    {
        "name": "Analytics",
        "description": "Análise avançada de custos e trends"
    },
    {
        "name": "Optimization",
        "description": "Otimização de custos e recomendações"
    },
    {
        "name": "Credentials",
        "description": "Gerenciamento de credenciais cloud"
    },
    {
        "name": "Budget Management",
        "description": "Gerenciamento de orçamentos e alertas"
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    # Startup
    logger.info("Starting X Cost API (Refactored)...")
    
    # Inicializar banco de dados
    if not init_database():
        logger.error("Failed to initialize database")
        raise RuntimeError("Database initialization failed")
    
    # Inicializar tabelas de credenciais
    Base.metadata.create_all(bind=db_manager.engine)
    
    # Criar usuário admin padrão se não existir
    try:
        from app.auth_security import create_user
        
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
    
    logger.info("X Cost API (Refactored) started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down X Cost API...")


async def init_optimization_service():
    """Inicializa o serviço de otimização cloud"""
    try:
        import redis
        
        # Configurar Redis (usando configurações padrão para desenvolvimento)
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
        # Inicializar serviço de otimização
        optimization_service = get_optimization_service(redis_client)
        logger.info("Cloud Native Optimization Service initialized successfully")
        
        return optimization_service
        
    except Exception as e:
        logger.warning(f"Cloud Native Optimization Service initialization failed: {e}")
        # Não falhar o startup se o serviço de otimização falhar


# Criar aplicação FastAPI
app = FastAPI(
    title="X Cost API (Refactored)",
    description="API completa para gerenciamento de custos multi-cloud - Arquitetura Modular",
    version="2.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata
)

# Configurar CORS
configure_cors_middleware(app)

# Adicionar middleware de segurança e logging
app.middleware("http")(comprehensive_security_middleware)
app.middleware("http")(rate_limit_middleware)

# Incluir routers refatorados
app.include_router(system_router)
app.include_router(cost_data_router)
app.include_router(data_ingestion_router)

# Incluir routers existentes
app.include_router(auth_router)
app.include_router(credentials_router)
app.include_router(audit_router)
app.include_router(budget_router)

# TODO: Adicionar analytics_router e optimization_router quando refatorados
# app.include_router(analytics_router)
# app.include_router(optimization_router)


# ============================================================================
# Global Exception Handler
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handler global para HTTPExceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handler global para exceções não tratadas"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# Security Information Endpoint
# ============================================================================

@app.get("/api/v1/security/info", tags=["System"])
async def get_security_info():
    """
    Obtém informações de segurança da API
    
    Retorna informações sobre autenticação, autorização e políticas de segurança
    sem expor detalhes sensíveis.
    """
    return {
        "authentication": {
            "method": "JWT Bearer Token",
            "token_endpoint": "/api/v1/auth/token",
            "registration_endpoint": "/api/v1/auth/register"
        },
        "authorization": {
            "model": "Role-Based Access Control (RBAC)",
            "roles": ["admin", "user", "viewer"],
            "permissions": [
                "data:read", "data:write", "data:ingest",
                "credentials:read", "credentials:write", "credentials:delete",
                "system:admin", "budget:manage"
            ]
        },
        "security_features": [
            "HTTPS Required",
            "JWT Token Authentication", 
            "Role-Based Authorization",
            "Rate Limiting",
            "Security Headers",
            "Input Validation",
            "Audit Logging"
        ],
        "data_protection": {
            "encryption_at_rest": "AES-256",
            "encryption_in_transit": "TLS 1.3",
            "credential_storage": "AWS Secrets Manager / Encrypted Local Storage",
            "audit_logging": "All credential and sensitive operations logged"
        }
    }


# ============================================================================
# API Root Endpoint
# ============================================================================

@app.get("/", tags=["System"])
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "X-Cost API - Refactored Architecture",
        "version": "2.1.0",
        "status": "operational",
        "documentation": "/docs",
        "redoc": "/redoc",
        "health_check": "/api/v1/health",
        "architecture": "modular",
        "features": [
            "Multi-cloud cost management",
            "Secure credential storage", 
            "Real-time optimization",
            "Budget management",
            "Audit logging",
            "Role-based access control"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    # Configuração para desenvolvimento
    uvicorn.run(
        "main_refactored:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )