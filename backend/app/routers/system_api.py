"""
System API Router

Endpoints para monitoramento, saúde do sistema e gerenciamento de cache
"""

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_cache, health_check, SessionLocal
from app.credential_models import (
    User, CloudCredentialConfig, CredentialAuditLog, CloudProviderType
)
from app.auth_security import get_current_active_user, security_manager
from app.secrets_manager import get_secrets_manager_hybrid
from app.utils.response_helpers import StandardResponse

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1", tags=["System"])


@router.get("/health", tags=["System Health"])
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
        
        status_code = 200 if health["overall"] else 503
        
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


@router.get("/system/status", tags=["System Health"])
async def get_system_status(
    current_user: User = Depends(get_current_active_user)
):
    """Obtém status detalhado do sistema"""
    try:
        # Verificar permissões
        if not security_manager.check_permission(current_user.role, "system:admin"):
            return StandardResponse.success({
                "system_status": "operational",
                "user_role": current_user.role.value,
                "access_level": "basic"
            })
        
        # Status completo para admins
        health = health_check()
        
        # Usar SessionLocal diretamente
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
            
            return StandardResponse.success({
                "system_health": health,
                "credential_stats": {
                    "total": credential_stats,
                    "active": active_credentials,
                    "inactive": credential_stats - active_credentials
                },
                "user_stats": user_stats,
                "recent_activities": activities_list,
                "generated_at": datetime.utcnow()
            })
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/status", tags=["Cloud Providers"])
async def get_providers_status(
    current_user: User = Depends(get_current_active_user)
):
    """Obtém status dos provedores de nuvem configurados"""
    try:
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
            
            return StandardResponse.success({
                "providers": provider_status,
                "total_configured": sum(1 for p in provider_status.values() if p["active_credentials"] > 0),
                "checked_at": datetime.utcnow()
            })
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error getting providers status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cache/clear", tags=["System Management"])
async def clear_cache(
    pattern: Optional[str] = "*",
    current_user: User = Depends(get_current_active_user),
    cache = Depends(get_cache)
):
    """Limpa cache do sistema"""
    try:
        # Verificar permissões
        if not security_manager.check_permission(current_user.role, "system:admin"):
            raise HTTPException(
                status_code=403,
                detail="Admin privileges required to clear cache"
            )
        
        cleared_count = cache.clear_pattern(pattern)
        
        return StandardResponse.success({
            "message": "Cache cleared successfully",
            "pattern": pattern,
            "cleared_keys": cleared_count,
            "cleared_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system/metrics", tags=["System Health"])
async def get_system_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """Obtém métricas básicas do sistema"""
    try:
        # Verificar permissões
        if not security_manager.check_permission(current_user.role, "system:admin"):
            raise HTTPException(status_code=403, detail="Admin privileges required")
        
        db = SessionLocal()
        try:
            # Métricas básicas
            metrics = {
                "database": {
                    "total_users": db.query(User).count(),
                    "active_users": db.query(User).filter(User.is_active == True).count(),
                    "total_credentials": db.query(CloudCredentialConfig).count(),
                    "active_credentials": db.query(CloudCredentialConfig).filter(
                        CloudCredentialConfig.status == "active"
                    ).count()
                },
                "timestamp": datetime.utcnow()
            }
            
            return StandardResponse.success(metrics)
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias para compatibilidade
system_router = router