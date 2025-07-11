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
from app.credentials.compatibility_adapter import CompatibilityAdapter

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
            status=CredentialStatus.ACTIVE,
            # Campos estendidos
            access_pattern=credential_data.access_pattern,
            credential_type=credential_data.credential_type,
            api_role_arn=credential_data.api_role_arn,
            data_role_arn=credential_data.data_role_arn,
            external_id=credential_data.external_id,
            session_duration=credential_data.session_duration
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
            updated_at=db_credential.updated_at,
            access_pattern=db_credential.access_pattern,
            credential_type=db_credential.credential_type,
            api_role_arn=db_credential.api_role_arn,
            data_role_arn=db_credential.data_role_arn,
            external_id=db_credential.external_id,
            session_duration=db_credential.session_duration
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
                updated_at=credential.updated_at,
                access_pattern=credential.access_pattern,
                credential_type=credential.credential_type,
                api_role_arn=credential.api_role_arn,
                data_role_arn=credential.data_role_arn,
                external_id=credential.external_id,
                session_duration=credential.session_duration
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
            updated_at=credential.updated_at,
            access_pattern=credential.access_pattern,
            credential_type=credential.credential_type,
            api_role_arn=credential.api_role_arn,
            data_role_arn=credential.data_role_arn,
            external_id=credential.external_id,
            session_duration=credential.session_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get credential"
        )

@credentials_router.put("/{credential_id}", response_model=CredentialConfigResponse)
async def update_credential(
    credential_id: str,
    credential_data: CredentialConfigUpdate,
    request: Request,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(require_finops_admin),
    db: Session = Depends(get_database),
    secrets_manager: SecretsManagerSimple = Depends(get_secrets_manager)
):
    """Atualiza configuração de credencial existente"""
    try:
        # Buscar credencial existente
        db_credential = db.query(CloudCredentialConfig).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not db_credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        # Verificar se nome já existe para outro registro
        if credential_data.name and credential_data.name != db_credential.name:
            existing = db.query(CloudCredentialConfig).filter(
                and_(
                    CloudCredentialConfig.name == credential_data.name,
                    CloudCredentialConfig.provider_type == db_credential.provider_type,
                    CloudCredentialConfig.id != credential_id
                )
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Credential name '{credential_data.name}' already exists for {db_credential.provider_type.value}"
                )
        
        # Atualizar credenciais no Secrets Manager se fornecidas
        if credential_data.credentials:
            secrets_manager.update_credentials(
                secret_arn=db_credential.secret_arn,
                credentials=credential_data.credentials,
                description=credential_data.description or db_credential.description
            )
            
            # Atualizar account_id se mudou o provider
            if db_credential.provider_type == CloudProviderType.AWS:
                db_credential.account_id = credential_data.credentials.account_id
            elif db_credential.provider_type == CloudProviderType.AZURE:
                db_credential.account_id = credential_data.credentials.subscription_id
            elif db_credential.provider_type == CloudProviderType.GCP:
                db_credential.account_id = credential_data.credentials.project_id
        
        # Atualizar campos do modelo
        if credential_data.name is not None:
            db_credential.name = credential_data.name
        if credential_data.description is not None:
            db_credential.description = credential_data.description
        if credential_data.status is not None:
            db_credential.status = credential_data.status
        if credential_data.expires_at is not None:
            db_credential.expires_at = credential_data.expires_at
        if credential_data.additional_config is not None:
            db_credential.additional_config = credential_data.additional_config
            
        # Atualizar campos estendidos
        if credential_data.access_pattern is not None:
            db_credential.access_pattern = credential_data.access_pattern
        if credential_data.credential_type is not None:
            db_credential.credential_type = credential_data.credential_type
        if credential_data.api_role_arn is not None:
            db_credential.api_role_arn = credential_data.api_role_arn
        if credential_data.data_role_arn is not None:
            db_credential.data_role_arn = credential_data.data_role_arn
        if credential_data.external_id is not None:
            db_credential.external_id = credential_data.external_id
        if credential_data.session_duration is not None:
            db_credential.session_duration = credential_data.session_duration
        
        # Resetar validação se credenciais mudaram
        if credential_data.credentials:
            db_credential.last_validated = None
            db_credential.validation_error = None
        
        db_credential.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_credential)
        
        # Log da atualização
        try:
            audit_logger = AuditLogger(db)
            audit_logger.log_credential_action(
                user=current_user,
                action=AuditAction.UPDATE,
                credential_id=str(db_credential.id),
                ip_address=security_manager._get_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                details={
                    "provider_type": db_credential.provider_type.value,
                    "credential_name": db_credential.name,
                    "updated_fields": [field for field, value in credential_data.dict(exclude_unset=True).items() if value is not None]
                },
                success=True
            )
        except Exception as audit_error:
            logger.warning(f"Audit log error (non-critical): {audit_error}")
        
        # Re-validar credenciais em background se mudaram
        if credential_data.credentials:
            background_tasks.add_task(
                validate_credentials_background,
                str(db_credential.id),
                db_credential.secret_arn,
                db_credential.provider_type
            )
        
        return CredentialConfigResponse(
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
            created_by=db_credential.creator.username if db_credential.creator else "unknown",
            created_at=db_credential.created_at,
            updated_at=db_credential.updated_at,
            access_pattern=db_credential.access_pattern,
            credential_type=db_credential.credential_type,
            api_role_arn=db_credential.api_role_arn,
            data_role_arn=db_credential.data_role_arn,
            external_id=db_credential.external_id,
            session_duration=db_credential.session_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update credential"
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
# ENDPOINTS PARA SISTEMA DUAL DE CREDENCIAIS (NOVO)
# ============================================================================

def get_enhanced_connector(credential_id: str, db: Session) -> Any:
    """
    Obter connector usando novo sistema (para uso futuro)
    """
    credential = db.query(CloudCredentialConfig).filter(
        CloudCredentialConfig.id == credential_id
    ).first()
    
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    adapter = CompatibilityAdapter(credential)
    return adapter.get_connector()

@credentials_router.get("/{credential_id}/enhanced-test")
async def test_enhanced_connector_get(
    credential_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Testar novo sistema de credenciais com validação abrangente (GET)
    """
    try:
        # Verificar se credencial existe
        credential = db.query(CloudCredentialConfig).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        
        # Criar adapter
        adapter = CompatibilityAdapter(credential)
        
        # Verificar se estratégia foi criada com sucesso
        if not adapter.strategy:
            return {
                "credential_id": credential_id,
                "test_type": "Enhanced Validation",
                "status": "ERROR",
                "message": f"Strategy not available for provider {credential.provider_type}",
                "timestamp": datetime.utcnow().isoformat(),
                "data_access": {"status": "NOT_AVAILABLE"},
                "api_access": {"status": "NOT_AVAILABLE"},
                "role_validation": {"status": "NOT_AVAILABLE"}
            }
        
        # Fazer teste básico da estratégia
        test_result = adapter.strategy.test_connection()
        
        if test_result.get("success"):
            return {
                "credential_id": credential_id,
                "test_type": "Enhanced Validation",
                "status": "SUCCESS",
                "message": "Basic connection test passed",
                "timestamp": datetime.utcnow().isoformat(),
                "data_access": {"status": "BASIC_SUCCESS"},
                "api_access": {"status": "BASIC_SUCCESS"},
                "role_validation": {"status": "NOT_TESTED"}
            }
        else:
            error_msg = test_result.get("error", "Connection test failed")
            return {
                "credential_id": credential_id,
                "test_type": "Enhanced Validation", 
                "status": "FAILED",
                "message": error_msg,
                "timestamp": datetime.utcnow().isoformat(),
                "data_access": {"status": "FAILED", "error": error_msg},
                "api_access": {"status": "FAILED", "error": error_msg},
                "role_validation": {"status": "FAILED", "error": error_msg}
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced connector test: {e}")
        return {
            "credential_id": credential_id,
            "test_type": "Enhanced Validation",
            "status": "ERROR", 
            "message": f"Unexpected error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "data_access": {"status": "ERROR", "error": str(e)},
            "api_access": {"status": "ERROR", "error": str(e)},
            "role_validation": {"status": "ERROR", "error": str(e)}
        }

@credentials_router.post("/{credential_id}/enhanced-test")
async def test_enhanced_connector_post(
    credential_id: str,
    request_data: Optional[dict] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database),
    secrets_manager: SecretsManagerSimple = Depends(get_secrets_manager)
):
    """
    Testar novo sistema de credenciais com configuração específica (POST)
    Aceita dados de validação do frontend para teste de roles
    """
    try:
        # Verificar se credencial existe
        credential = db.query(CloudCredentialConfig).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        
        # Obter credenciais do Secrets Manager
        try:
            credential_data = secrets_manager.get_credentials(credential.secret_arn)
        except Exception as e:
            logger.error(f"Failed to retrieve credentials from Secrets Manager: {e}")
            return {
                "credential_id": credential_id,
                "test_type": "Enhanced Validation",
                "status": "ERROR",
                "message": f"Failed to retrieve credentials: {str(e)}",
                "timestamp": datetime.utcnow().isoformat(),
                "data_access": {"status": "FAILED", "error": str(e)},
                "api_access": {"status": "FAILED", "error": str(e)},
                "role_validation": {"status": "FAILED", "error": str(e)}
            }
        
        # Criar adapter para compatibilidade
        adapter = CompatibilityAdapter(credential)
        
        # Inicializar resultado
        result = {
            "credential_id": credential_id,
            "test_type": "Enhanced Validation",
            "status": "SUCCESS",
            "message": "Validation completed",
            "timestamp": datetime.utcnow().isoformat(),
            "data_access": {"status": "NOT_TESTED"},
            "api_access": {"status": "NOT_TESTED"},
            "role_validation": {"status": "NOT_TESTED"},
            "permissions": {},
            "account_info": {}
        }
        
        # Se configuração enhanced foi fornecida, usar para validação específica
        if request_data:
            # Extrair configurações de role se fornecidas
            api_role_arn = request_data.get('api_role_arn') or credential.api_role_arn
            data_role_arn = request_data.get('data_role_arn') or credential.data_role_arn
            external_id = request_data.get('external_id') or credential.external_id
            session_duration = request_data.get('session_duration') or credential.session_duration or 3600
            
            # Testar acesso aos dados (Cost Explorer, Billing)
            if credential.provider_type == CloudProviderType.AWS:
                try:
                    data_result = await _test_aws_data_access(
                        credential_data,
                        data_role_arn,
                        external_id,
                        session_duration
                    )
                    result["data_access"] = data_result
                except Exception as e:
                    result["data_access"] = {
                        "status": "FAILED",
                        "error": str(e),
                        "services": []
                    }
                
                # Testar acesso à API (assumir roles)
                try:
                    api_result = await _test_aws_api_access(
                        credential_data,
                        api_role_arn,
                        external_id,
                        session_duration
                    )
                    result["api_access"] = api_result
                except Exception as e:
                    result["api_access"] = {
                        "status": "FAILED",
                        "error": str(e),
                        "capabilities": []
                    }
                
                # Testar validação de roles
                try:
                    role_result = await _test_aws_role_validation(
                        credential_data,
                        api_role_arn,
                        data_role_arn,
                        external_id
                    )
                    result["role_validation"] = role_result
                except Exception as e:
                    result["role_validation"] = {
                        "status": "FAILED",
                        "error": str(e),
                        "roles_tested": []
                    }
                
                # Obter informações da conta
                try:
                    account_info = await _get_aws_account_info(credential_data)
                    result["account_info"] = account_info
                except Exception as e:
                    result["account_info"] = {"error": str(e)}
        else:
            # Fazer teste básico sem roles específicas
            if adapter.strategy:
                test_result = adapter.strategy.test_connection()
                if test_result.get("success"):
                    result["status"] = "SUCCESS"
                    result["message"] = "Basic connection test passed"
                    result["data_access"] = {"status": "BASIC_SUCCESS"}
                    result["api_access"] = {"status": "BASIC_SUCCESS"}
                else:
                    result["status"] = "FAILED"
                    result["message"] = test_result.get("error", "Connection test failed")
                    result["data_access"] = {"status": "FAILED", "error": result["message"]}
                    result["api_access"] = {"status": "FAILED", "error": result["message"]}
        
        # Determinar status geral
        data_ok = result["data_access"].get("status") in ["SUCCESS", "BASIC_SUCCESS"]
        api_ok = result["api_access"].get("status") in ["SUCCESS", "BASIC_SUCCESS"]
        
        if data_ok and api_ok:
            result["status"] = "SUCCESS"
            result["message"] = "All validations passed"
        elif data_ok or api_ok:
            result["status"] = "PARTIAL"
            result["message"] = "Some validations failed"
        else:
            result["status"] = "FAILED"
            result["message"] = "All validations failed"
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in enhanced connector test: {e}")
        return {
            "credential_id": credential_id,
            "test_type": "Enhanced Validation",
            "status": "ERROR",
            "message": f"Unexpected error: {str(e)}",
            "timestamp": datetime.utcnow().isoformat(),
            "data_access": {"status": "ERROR", "error": str(e)},
            "api_access": {"status": "ERROR", "error": str(e)},
            "role_validation": {"status": "ERROR", "error": str(e)}
        }

# Funções auxiliares para validação AWS
async def _test_aws_data_access(credential_data: dict, role_arn: str = None, external_id: str = None, session_duration: int = 3600):
    """Testa acesso aos dados AWS (Cost Explorer, Billing)"""
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
        
        # Criar cliente com credenciais base
        if 'aws_access_key_id' in credential_data:
            session = boto3.Session(
                aws_access_key_id=credential_data['aws_access_key_id'],
                aws_secret_access_key=credential_data['aws_secret_access_key'],
                region_name=credential_data.get('region', 'us-east-1')
            )
        else:
            session = boto3.Session()
        
        # Se role_arn fornecida, assumir role
        if role_arn:
            sts_client = session.client('sts')
            assume_role_kwargs = {
                'RoleArn': role_arn,
                'RoleSessionName': 'xcost-data-validation',
                'DurationSeconds': session_duration
            }
            if external_id:
                assume_role_kwargs['ExternalId'] = external_id
                
            response = sts_client.assume_role(**assume_role_kwargs)
            credentials = response['Credentials']
            
            session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=credential_data.get('region', 'us-east-1')
            )
        
        services_tested = []
        
        # Testar Cost Explorer
        try:
            ce_client = session.client('ce', region_name='us-east-1')  # Cost Explorer é global
            ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': '2024-01-01',
                    'End': '2024-01-02'
                },
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            services_tested.append({"service": "Cost Explorer", "status": "SUCCESS"})
        except ClientError as e:
            services_tested.append({
                "service": "Cost Explorer", 
                "status": "FAILED", 
                "error": str(e)
            })
        except Exception as e:
            services_tested.append({
                "service": "Cost Explorer", 
                "status": "ERROR", 
                "error": str(e)
            })
        
        # Testar S3 (para Cost and Usage Reports)
        try:
            s3_client = session.client('s3')
            s3_client.list_buckets()
            services_tested.append({"service": "S3", "status": "SUCCESS"})
        except ClientError as e:
            services_tested.append({
                "service": "S3", 
                "status": "FAILED", 
                "error": str(e)
            })
        except Exception as e:
            services_tested.append({
                "service": "S3", 
                "status": "ERROR", 
                "error": str(e)
            })
        
        # Determinar status geral
        success_count = len([s for s in services_tested if s["status"] == "SUCCESS"])
        if success_count == len(services_tested):
            status = "SUCCESS"
        elif success_count > 0:
            status = "PARTIAL"
        else:
            status = "FAILED"
        
        return {
            "status": status,
            "services": services_tested,
            "role_used": role_arn or "base_credentials"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "services": []
        }

async def _test_aws_api_access(credential_data: dict, role_arn: str = None, external_id: str = None, session_duration: int = 3600):
    """Testa acesso às APIs AWS (IAM, Organizations)"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Criar cliente com credenciais base
        if 'aws_access_key_id' in credential_data:
            session = boto3.Session(
                aws_access_key_id=credential_data['aws_access_key_id'],
                aws_secret_access_key=credential_data['aws_secret_access_key'],
                region_name=credential_data.get('region', 'us-east-1')
            )
        else:
            session = boto3.Session()
        
        # Se role_arn fornecida, assumir role
        if role_arn:
            sts_client = session.client('sts')
            assume_role_kwargs = {
                'RoleArn': role_arn,
                'RoleSessionName': 'xcost-api-validation',
                'DurationSeconds': session_duration
            }
            if external_id:
                assume_role_kwargs['ExternalId'] = external_id
                
            response = sts_client.assume_role(**assume_role_kwargs)
            credentials = response['Credentials']
            
            session = boto3.Session(
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=credential_data.get('region', 'us-east-1')
            )
        
        capabilities_tested = []
        
        # Testar STS (identidade)
        try:
            sts_client = session.client('sts')
            identity = sts_client.get_caller_identity()
            capabilities_tested.append({
                "capability": "STS Identity", 
                "status": "SUCCESS",
                "details": {
                    "account": identity.get('Account'),
                    "user_id": identity.get('UserId'),
                    "arn": identity.get('Arn')
                }
            })
        except ClientError as e:
            capabilities_tested.append({
                "capability": "STS Identity", 
                "status": "FAILED", 
                "error": str(e)
            })
        
        # Testar IAM (listar roles - permissão comum)
        try:
            iam_client = session.client('iam')
            iam_client.list_roles(MaxItems=1)
            capabilities_tested.append({"capability": "IAM ListRoles", "status": "SUCCESS"})
        except ClientError as e:
            capabilities_tested.append({
                "capability": "IAM ListRoles", 
                "status": "FAILED", 
                "error": str(e)
            })
        
        # Testar Organizations (se disponível)
        try:
            org_client = session.client('organizations')
            org_client.describe_organization()
            capabilities_tested.append({"capability": "Organizations", "status": "SUCCESS"})
        except ClientError as e:
            if e.response['Error']['Code'] == 'AWSOrganizationsNotInUseException':
                capabilities_tested.append({
                    "capability": "Organizations", 
                    "status": "NOT_APPLICABLE", 
                    "message": "Account not part of organization"
                })
            else:
                capabilities_tested.append({
                    "capability": "Organizations", 
                    "status": "FAILED", 
                    "error": str(e)
                })
        
        # Determinar status geral
        success_count = len([c for c in capabilities_tested if c["status"] == "SUCCESS"])
        if success_count >= 1:  # Pelo menos STS deve funcionar
            status = "SUCCESS"
        else:
            status = "FAILED"
        
        return {
            "status": status,
            "capabilities": capabilities_tested,
            "role_used": role_arn or "base_credentials"
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "capabilities": []
        }

async def _test_aws_role_validation(credential_data: dict, api_role_arn: str = None, data_role_arn: str = None, external_id: str = None):
    """Valida se as roles podem ser assumidas"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        # Criar cliente base
        if 'aws_access_key_id' in credential_data:
            session = boto3.Session(
                aws_access_key_id=credential_data['aws_access_key_id'],
                aws_secret_access_key=credential_data['aws_secret_access_key'],
                region_name=credential_data.get('region', 'us-east-1')
            )
        else:
            session = boto3.Session()
        
        sts_client = session.client('sts')
        roles_tested = []
        
        # Testar API role
        if api_role_arn:
            try:
                assume_role_kwargs = {
                    'RoleArn': api_role_arn,
                    'RoleSessionName': 'xcost-api-role-test',
                    'DurationSeconds': 900  # Mínimo para teste
                }
                if external_id:
                    assume_role_kwargs['ExternalId'] = external_id
                
                response = sts_client.assume_role(**assume_role_kwargs)
                roles_tested.append({
                    "role_type": "API",
                    "role_arn": api_role_arn,
                    "status": "SUCCESS",
                    "session_duration": 900
                })
            except ClientError as e:
                roles_tested.append({
                    "role_type": "API",
                    "role_arn": api_role_arn,
                    "status": "FAILED",
                    "error": str(e)
                })
        
        # Testar Data role
        if data_role_arn and data_role_arn != api_role_arn:
            try:
                assume_role_kwargs = {
                    'RoleArn': data_role_arn,
                    'RoleSessionName': 'xcost-data-role-test',
                    'DurationSeconds': 900
                }
                if external_id:
                    assume_role_kwargs['ExternalId'] = external_id
                
                response = sts_client.assume_role(**assume_role_kwargs)
                roles_tested.append({
                    "role_type": "DATA",
                    "role_arn": data_role_arn,
                    "status": "SUCCESS",
                    "session_duration": 900
                })
            except ClientError as e:
                roles_tested.append({
                    "role_type": "DATA",
                    "role_arn": data_role_arn,
                    "status": "FAILED",
                    "error": str(e)
                })
        
        # Determinar status geral
        if not roles_tested:
            return {
                "status": "NOT_APPLICABLE",
                "message": "No roles configured for testing",
                "roles_tested": []
            }
        
        success_count = len([r for r in roles_tested if r["status"] == "SUCCESS"])
        if success_count == len(roles_tested):
            status = "SUCCESS"
        elif success_count > 0:
            status = "PARTIAL"
        else:
            status = "FAILED"
        
        return {
            "status": status,
            "roles_tested": roles_tested
        }
        
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e),
            "roles_tested": []
        }

async def _get_aws_account_info(credential_data: dict):
    """Obtém informações da conta AWS"""
    try:
        import boto3
        from botocore.exceptions import ClientError
        
        if 'aws_access_key_id' in credential_data:
            session = boto3.Session(
                aws_access_key_id=credential_data['aws_access_key_id'],
                aws_secret_access_key=credential_data['aws_secret_access_key'],
                region_name=credential_data.get('region', 'us-east-1')
            )
        else:
            session = boto3.Session()
        
        sts_client = session.client('sts')
        identity = sts_client.get_caller_identity()
        
        return {
            "account_id": identity.get('Account'),
            "user_id": identity.get('UserId'),
            "arn": identity.get('Arn'),
            "region": credential_data.get('region', 'us-east-1')
        }
        
    except Exception as e:
        return {"error": str(e)}

@credentials_router.get("/{credential_id}/enhanced-info")
async def get_enhanced_credential_info(
    credential_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Obter informações sobre capacidades estendidas da credencial
    """
    try:
        credential = db.query(CloudCredentialConfig).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        
        # Informações sobre estratégias disponíveis
        from app.credentials.strategies.factory import CredentialStrategyFactory
        
        supported_providers = CredentialStrategyFactory.get_supported_providers()
        provider_supported = credential.provider_type.value in supported_providers
        
        return {
            "credential_id": credential_id,
            "provider_type": credential.provider_type.value,
            "provider_supported": provider_supported,
            "supported_providers": supported_providers,
            "enhanced_features_available": provider_supported
        }
        
    except Exception as e:
        logger.error(f"Enhanced info failed for credential {credential_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))

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

@credentials_router.post("/{credential_id}/configure-enhanced")
async def configure_enhanced_credential(
    credential_id: str,
    enhanced_config: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Configurar credencial com recursos estendidos (roles, external_id, etc.)
    """
    try:
        # Verificar se credencial existe
        credential = db.query(CloudCredentialConfig).filter(
            CloudCredentialConfig.id == credential_id
        ).first()
        
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        
        # Validar configuração estendida
        from app.credentials.models.credential_config import ExtendedCredentialConfigWrapper
        from app.credentials.strategies.base import AccessPattern, CredentialType
        
        wrapper = ExtendedCredentialConfigWrapper(credential)
        
        # Aplicar configurações
        if 'access_pattern' in enhanced_config:
            try:
                pattern = AccessPattern(enhanced_config['access_pattern'])
                wrapper.set_access_pattern(pattern)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid access_pattern")
        
        if 'credential_type' in enhanced_config:
            try:
                cred_type = CredentialType(enhanced_config['credential_type'])
                wrapper.set_credential_type(cred_type)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid credential_type")
        
        # Configurar roles se fornecidos
        wrapper.add_role_config(
            data_role_arn=enhanced_config.get('data_role_arn'),
            api_role_arn=enhanced_config.get('api_role_arn'),
            external_id=enhanced_config.get('external_id')
        )
        
        # Validar configuração
        strategy_config = wrapper.get_strategy_config()
        
        # Tentar criar estratégia com nova configuração
        adapter = CompatibilityAdapter(credential)
        
        if adapter.strategy:
            # Testar nova configuração
            test_result = adapter.strategy.validate_comprehensive_access()
            
            # Salvar configuração estendida como JSON na credencial
            # (em implementação futura, isso seria salvo em campo específico)
            enhanced_info = {
                "enhanced_config": enhanced_config,
                "validation_result": test_result,
                "configured_at": datetime.utcnow().isoformat()
            }
            
            return {
                "credential_id": credential_id,
                "enhanced_config_applied": True,
                "config_summary": {
                    "access_pattern": wrapper.enhanced.access_pattern.value,
                    "credential_type": wrapper.enhanced.credential_type.value,
                    "has_data_role": bool(wrapper.enhanced.data_role_arn),
                    "has_api_role": bool(wrapper.enhanced.api_role_arn),
                    "has_external_id": bool(wrapper.enhanced.external_id)
                },
                "validation_result": test_result
            }
        else:
            return {
                "credential_id": credential_id,
                "enhanced_config_applied": False,
                "error": "Strategy not available for this provider"
            }
        
    except Exception as e:
        logger.error(f"Enhanced configuration failed for credential {credential_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))