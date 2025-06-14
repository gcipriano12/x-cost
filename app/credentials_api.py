from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Response
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.database import get_database, db_manager, get_db_session
from app.credential_models import (
    CloudCredentialConfig, User, CloudProviderType, CredentialStatus,
    CredentialConfigCreate, CredentialConfigUpdate, CredentialConfigResponse,
    CredentialValidationResult, CredentialTestRequest, CredentialQueryParams,
    AuditQueryParams, AuditLogResponse, CredentialError, UserCreate, UserResponse,
    TokenResponse, AuditAction, LoginRequest
)
from app.auth_security import (
    get_current_active_user, require_finops_admin, require_admin, 
    get_audit_logger, AuditLogger, security_manager, create_user
)
from app.secrets_manager import get_secrets_manager, SecretsManagerSimple
from sqlalchemy import and_, or_, desc

logger = logging.getLogger(__name__)

# Router para endpoints de credenciais
credentials_router = APIRouter(prefix="/api/v1/credentials", tags=["Credentials Management"])

# Router para endpoints de autenticação
auth_router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Router para endpoints de auditoria
audit_router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])

# ============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# ============================================================================

@auth_router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_database)
):
    """Autentica usuário e retorna tokens"""
    try:        
        # Autenticar usuário
        user = security_manager.authenticate_user(db, login_data.username, login_data.password)
        
        if not user:
            # Log tentativa de login falhada
            try:
                audit_logger = AuditLogger(db)
                audit_logger.log_credential_action(
                    user=None,
                    action=AuditAction.VIEW,
                    ip_address=security_manager._get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    success=False,
                    error_message="Invalid credentials"
                )
            except Exception as audit_error:
                logger.warning(f"Failed to log failed login attempt: {audit_error}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Criar tokens
        access_token = security_manager.create_access_token(
            data={"sub": user.username, "role": user.role.value}
        )
        refresh_token = security_manager.create_refresh_token(
            data={"sub": user.username}
        )
        
        # Log login bem-sucedido
        try:
            audit_logger = AuditLogger(db)
            audit_logger.log_credential_action(
                user=user,
                action=AuditAction.VIEW,
                ip_address=security_manager._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                details={"action": "login"},
                success=True
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log successful login: {audit_error}")
        
        # Converter UUID para string antes de criar o UserResponse
        user_response_data = {
            "id": str(user.id),  # Converter UUID para string
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login
        }
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=3600,  # 1 hora
            user=UserResponse(**user_response_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )

@auth_router.post("/users", response_model=UserResponse)
async def create_new_user(
    user_data: UserCreate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_database)
):
    """Cria novo usuário (apenas admins)"""
    try:
        new_user = create_user(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password.get_secret_value(),
            role=user_data.role
        )
        
        # Log criação de usuário
        try:
            audit_logger = AuditLogger(db)
            audit_logger.log_credential_action(
                user=current_user,
                action=AuditAction.CREATE,
                ip_address=security_manager._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                details={"action": "create_user", "target_user": new_user.username},
                success=True
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log user creation: {audit_error}")
        
        return UserResponse.from_orm(new_user)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"User creation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

# ============================================================================
# ENDPOINTS DE GERENCIAMENTO DE CREDENCIAIS
# ============================================================================

@credentials_router.post("", response_model=CredentialConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_credentials(
    credential_data: CredentialConfigCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_finops_admin),
    db: Session = Depends(get_database),
    secrets_manager: SecretsManagerSimple = Depends(get_secrets_manager)
):
    """Cria nova configuração de credenciais"""
    try:
        # Verificar se nome já existe para o provedor
        existing = db.query(CloudCredentialConfig).filter(
            and_(
                CloudCredentialConfig.name == credential_data.name,
                CloudCredentialConfig.provider_type == credential_data.provider_type
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Credential name '{credential_data.name}' already exists for {credential_data.provider_type.value}"
            )
        
        # Armazenar credenciais no Secrets Manager
        secret_arn, secret_name = secrets_manager.store_credentials(
            credential_name=credential_data.name,
            provider_type=credential_data.provider_type,
            credentials=credential_data.credentials,
            description=credential_data.description,
            expires_at=credential_data.expires_at
        )
        
        # Extrair account_id se disponível
        account_id = None
        if credential_data.provider_type == CloudProviderType.AWS:
            account_id = credential_data.credentials.account_id
        elif credential_data.provider_type == CloudProviderType.AZURE:
            account_id = credential_data.credentials.subscription_id
        elif credential_data.provider_type == CloudProviderType.GCP:
            account_id = credential_data.credentials.project_id
        
        # Criar registro no banco de dados
        db_credential = CloudCredentialConfig(
            name=credential_data.name,
            description=credential_data.description,
            provider_type=credential_data.provider_type,
            secret_arn=secret_arn,
            secret_name=secret_name,
            account_id=account_id,
            additional_config=credential_data.additional_config,
            expires_at=credential_data.expires_at,
            created_by=current_user.id,
            status=CredentialStatus.ACTIVE
        )
        
        db.add(db_credential)
        db.commit()
        db.refresh(db_credential)
        
        # Log da criação
        try:
            audit_logger = AuditLogger(db)
            audit_logger.log_credential_action(
                user=current_user,
                action=AuditAction.CREATE,
                credential_id=str(db_credential.id),
                ip_address=security_manager._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                details={
                    "provider_type": credential_data.provider_type.value,
                    "credential_name": credential_data.name
                },
                success=True
            )
        except Exception as audit_error:
            logger.warning(f"Audit log error (non-critical): {audit_error}")
        
        # Validar credenciais em background
        background_tasks.add_task(
            validate_credentials_background,
            str(db_credential.id),
            secret_arn,
            current_user.id
        )
        
        # Preparar resposta
        response = CredentialConfigResponse(
            id=str(db_credential.id),
            name=db_credential.name,
            description=db_credential.description,
            provider_type=db_credential.provider_type,
            account_id=db_credential.account_id,
            region_preference=db_credential.region_preference,
            status=db_credential.status,
            last_validated=db_credential.last_validated,
            validation_error=db_credential.validation_error,
            expires_at=db_credential.expires_at,
            created_by=current_user.username,
            created_at=db_credential.created_at,
            updated_at=db_credential.updated_at
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating credentials: {e}")
        
        # Log erro - usar uma nova sessão para evitar problemas
        try:
            with db_manager.get_session() as audit_db:
                audit_logger = AuditLogger(audit_db)
                audit_logger.log_credential_action(
                    user=current_user,
                    action=AuditAction.CREATE,
                    ip_address=security_manager._get_client_ip(request),
                    user_agent=request.headers.get("user-agent"),
                    success=False,
                    error_message=str(e)
                )
        except Exception as audit_error:
            logger.warning(f"Failed to log error: {audit_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create credentials"
        )

@credentials_router.get("", response_model=List[CredentialConfigResponse])
async def list_credentials(
    params: CredentialQueryParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Lista configurações de credenciais"""
    try:
        query = db.query(CloudCredentialConfig).join(User)
        
        # Aplicar filtros
        if params.provider_type:
            query = query.filter(CloudCredentialConfig.provider_type == params.provider_type)
        if params.status:
            query = query.filter(CloudCredentialConfig.status == params.status)
        if params.name_contains:
            query = query.filter(CloudCredentialConfig.name.ilike(f"%{params.name_contains}%"))
        if params.expires_before:
            query = query.filter(CloudCredentialConfig.expires_at <= params.expires_before)
        
        # Ordenação e paginação
        results = query.order_by(
            desc(CloudCredentialConfig.created_at)
        ).offset(params.offset).limit(params.limit).all()
        
        # Converter para response
        response_list = []
        for credential in results:
            response_list.append(CredentialConfigResponse(
                id=str(credential.id),
                name=credential.name,
                description=credential.description,
                provider_type=credential.provider_type,
                account_id=credential.account_id,
                region_preference=credential.region_preference,
                status=credential.status,
                last_validated=credential.last_validated,
                validation_error=credential.validation_error,
                expires_at=credential.expires_at,
                created_by=credential.created_by_user.username,
                created_at=credential.created_at,
                updated_at=credential.updated_at
            ))
        
        return response_list
        
    except Exception as e:
        logger.error(f"Error listing credentials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list credentials"
        )

@credentials_router.get("/{credential_id}", response_model=CredentialConfigResponse)
async def get_credential(
    credential_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém configuração específica de credencial"""
    try:
        credential = db.query(CloudCredentialConfig).join(User).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        return CredentialConfigResponse(
            id=str(credential.id),
            name=credential.name,
            description=credential.description,
            provider_type=credential.provider_type,
            account_id=credential.account_id,
            region_preference=credential.region_preference,
            status=credential.status,
            last_validated=credential.last_validated,
            validation_error=credential.validation_error,
            expires_at=credential.expires_at,
            created_by=credential.created_by_user.username,
            created_at=credential.created_at,
            updated_at=credential.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get credential"
        )

@credentials_router.delete("/{credential_id}")
async def delete_credential(
    credential_id: str,
    request: Request,
    current_user: User = Depends(require_finops_admin),
    db: Session = Depends(get_database),
    secrets_manager: SecretsManagerSimple = Depends(get_secrets_manager),
    force: bool = False
):
    """Remove configuração de credencial"""
    try:
        credential = db.query(CloudCredentialConfig).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        # Remover do Secrets Manager
        secrets_manager.delete_credentials(
            secret_arn=credential.secret_arn,
            force_delete=force
        )
        
        # Remover do banco de dados
        credential_name = credential.name
        provider_type = credential.provider_type.value
        
        db.delete(credential)
        db.commit()
        
        # Log da remoção
        try:
            audit_logger = AuditLogger(db)
            audit_logger.log_credential_action(
                user=current_user,
                action=AuditAction.DELETE,
                credential_id=credential_id,
                ip_address=security_manager._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                details={
                    "credential_name": credential_name,
                    "provider_type": provider_type,
                    "force_delete": force
                },
                success=True
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log credential deletion: {audit_error}")
        
        return Response(status_code=204)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete credential"
        )

@credentials_router.post("/{credential_id}/validate", response_model=CredentialValidationResult)
async def validate_credential(
    credential_id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database),
    secrets_manager: SecretsManagerSimple = Depends(get_secrets_manager)
):
    """Valida credencial específica"""
    try:
        credential = db.query(CloudCredentialConfig).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        # Validar credenciais
        validation_result = secrets_manager.validate_credentials(credential.secret_arn)
        
        # Atualizar status no banco
        if validation_result['is_valid']:
            credential.status = CredentialStatus.ACTIVE
            credential.validation_error = None
        else:
            credential.status = CredentialStatus.VALIDATION_FAILED
            credential.validation_error = validation_result.get('error_message')
        
        credential.last_validated = datetime.utcnow()
        db.commit()
        
        # Log da validação
        try:
            audit_logger = AuditLogger(db)
            audit_logger.log_credential_action(
                user=current_user,
                action=AuditAction.VALIDATE,
                credential_id=credential_id,
                ip_address=security_manager._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                details={"validation_result": validation_result['is_valid']},
                success=validation_result['is_valid'],
                error_message=validation_result.get('error_message')
            )
        except Exception as audit_error:
            logger.warning(f"Failed to log credential validation: {audit_error}")
        
        return CredentialValidationResult(**validation_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate credential"
        )

@credentials_router.post("/test", response_model=CredentialValidationResult)
async def test_credentials(
    test_request: CredentialTestRequest,
    request: Request,
    current_user: User = Depends(require_finops_admin),
    secrets_manager: SecretsManagerSimple = Depends(get_secrets_manager)
):
    """Testa credenciais sem salvá-las"""
    try:
        # Criar um secret temporário para teste
        temp_name = f"temp-test-{datetime.utcnow().timestamp()}"
        
        try:
            # Armazenar temporariamente
            secret_arn, _ = secrets_manager.store_credentials(
                credential_name=temp_name,
                provider_type=test_request.provider_type,
                credentials=test_request.credentials,
                description="Temporary test credential"
            )
            
            # Validar
            validation_result = secrets_manager.validate_credentials(secret_arn)
            
            # Remover secret temporário
            secrets_manager.delete_credentials(secret_arn, force_delete=True)
            
            return CredentialValidationResult(**validation_result)
            
        except Exception as cleanup_error:
            logger.warning(f"Failed to cleanup test credential: {cleanup_error}")
            # Ainda retornar o resultado da validação se possível
            if 'validation_result' in locals():
                return CredentialValidationResult(**validation_result)
            raise
            
    except Exception as e:
        logger.error(f"Error testing credentials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to test credentials"
        )

# ============================================================================
# ENDPOINTS DE AUDITORIA
# ============================================================================

@audit_router.get("/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    params: AuditQueryParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Obtém logs de auditoria"""
    try:
        from app.credential_models import CredentialAuditLog
        
        query = db.query(CredentialAuditLog).join(User)
        
        # Aplicar filtros
        if params.credential_id:
            query = query.filter(CredentialAuditLog.credential_id == params.credential_id)
        if params.user_id:
            query = query.filter(CredentialAuditLog.user_id == params.user_id)
        if params.action:
            query = query.filter(CredentialAuditLog.action == params.action)
        if params.start_date:
            query = query.filter(CredentialAuditLog.timestamp >= params.start_date)
        if params.end_date:
            query = query.filter(CredentialAuditLog.timestamp <= params.end_date)
        if params.success_only is not None:
            query = query.filter(CredentialAuditLog.success == params.success_only)
        
        # Ordenação e paginação
        results = query.order_by(
            desc(CredentialAuditLog.timestamp)
        ).offset(params.offset).limit(params.limit).all()
        
        # Converter para response
        response_list = []
        for log in results:
            # Obter nome da credencial se disponível
            credential_name = None
            if log.credential_id:
                credential = db.query(CloudCredentialConfig).filter(
                    CloudCredentialConfig.id == log.credential_id
                ).first()
                if credential:
                    credential_name = credential.name
            
            response_list.append(AuditLogResponse(
                id=str(log.id),
                credential_id=str(log.credential_id) if log.credential_id else None,
                credential_name=credential_name,
                user_username=log.user.username,
                action=log.action,
                ip_address=log.ip_address,
                success=log.success,
                error_message=log.error_message,
                timestamp=log.timestamp,
                details=log.details
            ))
        
        return response_list
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get audit logs"
        )

# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

async def validate_credentials_background(
    credential_id: str,
    secret_arn: str,
    user_id: str
):
    """Valida credenciais em background"""
    try:
        logger.info(f"Starting background validation for credential {credential_id}")
        
        with db_manager.get_session() as db:
            secrets_manager = get_secrets_manager()
            
            # Validar credenciais
            validation_result = secrets_manager.validate_credentials(secret_arn)
            
            # Atualizar status no banco
            credential = db.query(CloudCredentialConfig).filter(
                CloudCredentialConfig.id == credential_id
            ).first()
            
            if credential:
                if validation_result['is_valid']:
                    credential.status = CredentialStatus.ACTIVE
                    credential.validation_error = None
                else:
                    credential.status = CredentialStatus.VALIDATION_FAILED
                    credential.validation_error = validation_result.get('error_message')
                
                credential.last_validated = datetime.utcnow()
                
                logger.info(f"Background validation completed for credential {credential_id}: {validation_result['is_valid']}")
            
    except Exception as e:
        logger.error(f"Background validation failed for credential {credential_id}: {e}")

# Função para obter credenciais para uso interno (pelos extractors)
def get_provider_credentials(provider_type: CloudProviderType, credential_name: str = None) -> Dict[str, Any]:
    """
    Função utilitária para obter credenciais de um provedor específico
    Para uso pelos extractors de dados
    """
    try:
        with db_manager.get_session() as db:
            query = db.query(CloudCredentialConfig).filter(
                and_(
                    CloudCredentialConfig.provider_type == provider_type,
                    CloudCredentialConfig.status == CredentialStatus.ACTIVE
                )
            )
            
            if credential_name:
                query = query.filter(CloudCredentialConfig.name == credential_name)
            
            credential = query.first()
            
            if not credential:
                raise ValueError(f"No active credentials found for {provider_type.value}")
            
            # Obter credenciais do Secrets Manager
            secrets_manager = get_secrets_manager()
            cred_data = secrets_manager.retrieve_credentials(credential.secret_arn)
            
            return cred_data['credentials']
            
    except Exception as e:
        logger.error(f"Error getting provider credentials: {e}")
        raise