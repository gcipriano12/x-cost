"""
Data Ingestion API Router

Endpoints para ingestão segura de dados de múltiplos provedores cloud
"""

import logging
from datetime import datetime
from typing import List, Optional, Dict

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

from app.database import db_manager, SessionLocal
from app.credential_models import (
    User, CloudCredentialConfig, CloudProviderType, AuditAction
)
from app.auth_security import get_current_active_user, security_manager, AuditLogger
from app.credentials_api import get_provider_credentials
from app.cloud_connectors import CloudConnectorFactory
from app.data_ingestion import DataIngestionService
from app.utils.response_helpers import StandardResponse, calculate_processing_time
from app.utils.validators import validate_date_range

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1/data", tags=["Data Ingestion"])


@router.post("/secure-ingest")
@calculate_processing_time
async def trigger_secure_data_ingestion(
    background_tasks: BackgroundTasks,
    providers: Optional[List[str]] = None,
    credential_names: Optional[Dict[str, str]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    Inicia processo de ingestão de dados usando credenciais armazenadas
    
    Este endpoint permite iniciar a coleta de dados de custos de múltiplos
    provedores de nuvem de forma segura, usando credenciais previamente
    configuradas no sistema.
    
    Args:
        providers: Lista de provedores (aws, azure, gcp, oracle)
        credential_names: Mapeamento de nomes específicos de credenciais por provedor
        start_date: Data inicial para coleta (padrão: início do dia atual)
        end_date: Data final para coleta (padrão: agora)
    """
    try:
        # Verificar permissões de ingestão
        if not security_manager.check_permission(current_user.role, "data:ingest"):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions for data ingestion"
            )
        
        # Definir datas padrão se não fornecidas
        if not start_date:
            start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        if not end_date:
            end_date = datetime.now()
        
        # Validar range de datas
        validate_date_range(start_date.date(), end_date.date(), max_days=365)
        
        # Se não especificou provedores, usar todos os ativos
        if not providers:
            db = SessionLocal()
            try:
                active_credentials = db.query(CloudCredentialConfig).filter(
                    CloudCredentialConfig.status == "active"
                ).all()
                providers = list(set([cred.provider_type.value for cred in active_credentials]))
            finally:
                db.close()
        
        # Validar provedores
        supported_providers = ["aws", "azure", "gcp", "oracle"]
        invalid_providers = [p for p in providers if p not in supported_providers]
        if invalid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported providers: {invalid_providers}. "
                       f"Supported: {supported_providers}"
            )
        
        # Adicionar tarefa em background
        background_tasks.add_task(
            run_secure_data_ingestion,
            start_date=start_date,
            end_date=end_date,
            providers=providers,
            credential_names=credential_names or {},
            user_id=str(current_user.id)
        )
        
        return StandardResponse.success({
            "message": "Secure data ingestion started",
            "start_date": start_date,
            "end_date": end_date,
            "providers": providers,
            "initiated_by": current_user.username,
            "status": "processing"
        })
        
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
    """
    Executa ingestão de dados usando credenciais seguras
    
    Esta função é executada em background e realiza:
    1. Obtenção de credenciais seguras para cada provedor
    2. Conexão e extração de dados de custo
    3. Transformação para formato FOCUS
    4. Inserção em massa no banco de dados
    5. Log de auditoria da operação
    """
    try:
        logger.info(f"Starting secure data ingestion for {providers} by user {user_id}")
        
        all_data = {}
        extraction_errors = {}
        
        # Extrair dados de cada provedor
        for provider_name in providers:
            try:
                # Obter credenciais seguras para o provedor
                credential_name = credential_names.get(provider_name)
                
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
                
                # Extrair e transformar dados
                raw_data = connector.extract_cost_data(start_date, end_date)
                focus_data = connector.transform_to_focus(raw_data)
                all_data[provider_name] = focus_data
                
                logger.info(f"Successfully extracted {len(focus_data)} records from {provider_name}")
                
            except Exception as provider_error:
                error_msg = f"Failed to extract data from {provider_name}: {str(provider_error)}"
                logger.error(error_msg)
                extraction_errors[provider_name] = error_msg
                all_data[provider_name] = []
        
        # Salvar dados no banco
        total_inserted = 0
        insertion_results = {}
        
        with db_manager.get_session() as db:
            ingestion_service = DataIngestionService(db)
            
            for provider_name, focus_data in all_data.items():
                if focus_data:
                    try:
                        inserted_count = ingestion_service.bulk_insert_focus_data(focus_data)
                        total_inserted += inserted_count
                        insertion_results[provider_name] = inserted_count
                        logger.info(f"Inserted {inserted_count} records for {provider_name}")
                    except Exception as insert_error:
                        logger.error(f"Failed to insert data for {provider_name}: {insert_error}")
                        insertion_results[provider_name] = 0
                else:
                    insertion_results[provider_name] = 0
        
        # Determinar sucesso geral
        operation_success = total_inserted > 0 or len(extraction_errors) == 0
        
        logger.info(
            f"Secure data ingestion completed. "
            f"Total records: {total_inserted}, "
            f"Errors: {len(extraction_errors)}"
        )
        
        # Log de auditoria
        await _log_ingestion_audit(
            user_id=user_id,
            providers=providers,
            start_date=start_date,
            end_date=end_date,
            total_inserted=total_inserted,
            insertion_results=insertion_results,
            extraction_errors=extraction_errors,
            success=operation_success
        )
        
    except Exception as e:
        logger.error(f"Secure data ingestion failed: {str(e)}")
        
        # Log do erro
        await _log_ingestion_audit(
            user_id=user_id,
            providers=providers,
            start_date=start_date,
            end_date=end_date,
            success=False,
            error_message=str(e)
        )


async def _log_ingestion_audit(
    user_id: str,
    providers: List[str],
    start_date: datetime,
    end_date: datetime,
    total_inserted: int = 0,
    insertion_results: Dict[str, int] = None,
    extraction_errors: Dict[str, str] = None,
    success: bool = True,
    error_message: str = None
):
    """Log de auditoria para operações de ingestão"""
    try:
        with db_manager.get_session() as db:
            audit_logger = AuditLogger(db)
            user = db.query(User).filter(User.id == user_id).first()
            
            if user:
                audit_details = {
                    "action": "data_ingestion",
                    "providers": providers,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
                
                if success:
                    audit_details.update({
                        "records_inserted": total_inserted,
                        "insertion_results": insertion_results or {},
                        "extraction_errors": extraction_errors or {}
                    })
                
                audit_logger.log_credential_action(
                    user=user,
                    action=AuditAction.VIEW,  # Usando VIEW para operações de extração
                    details=audit_details,
                    success=success,
                    error_message=error_message
                )
    except Exception as audit_error:
        logger.warning(f"Failed to log ingestion audit: {audit_error}")


@router.get("/ingestion/status")
async def get_ingestion_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém status das últimas operações de ingestão
    """
    try:
        # Verificar permissões
        if not security_manager.check_permission(current_user.role, "data:view"):
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to view ingestion status"
            )
        
        db = SessionLocal()
        try:
            # Buscar últimas atividades de ingestão nos logs de auditoria
            from app.credential_models import CredentialAuditLog
            
            recent_ingestions = db.query(CredentialAuditLog).filter(
                CredentialAuditLog.details.op('->>')('action') == 'data_ingestion'
            ).order_by(CredentialAuditLog.timestamp.desc()).limit(10).all()
            
            status_list = []
            for log in recent_ingestions:
                details = log.details or {}
                status_list.append({
                    "timestamp": log.timestamp,
                    "user": log.user.username,
                    "providers": details.get("providers", []),
                    "success": log.success,
                    "records_inserted": details.get("records_inserted", 0),
                    "error": log.error_message if not log.success else None
                })
            
            return StandardResponse.success({
                "recent_ingestions": status_list,
                "total_found": len(status_list)
            })
            
        finally:
            db.close()
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting ingestion status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers/active")
async def get_active_providers(
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém lista de provedores ativos disponíveis para ingestão
    """
    try:
        db = SessionLocal()
        try:
            # Buscar credenciais ativas
            active_credentials = db.query(CloudCredentialConfig).filter(
                CloudCredentialConfig.status == "active"
            ).all()
            
            providers_info = {}
            for cred in active_credentials:
                provider = cred.provider_type.value
                if provider not in providers_info:
                    providers_info[provider] = {
                        "provider": provider,
                        "credentials_count": 0,
                        "credential_names": [],
                        "last_validated": None
                    }
                
                providers_info[provider]["credentials_count"] += 1
                providers_info[provider]["credential_names"].append(cred.name)
                
                # Atualizar data de última validação
                if (not providers_info[provider]["last_validated"] or 
                    (cred.last_validated and 
                     cred.last_validated > providers_info[provider]["last_validated"])):
                    providers_info[provider]["last_validated"] = cred.last_validated
            
            return StandardResponse.success({
                "active_providers": list(providers_info.values()),
                "total_providers": len(providers_info)
            })
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error getting active providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias para compatibilidade
data_ingestion_router = router