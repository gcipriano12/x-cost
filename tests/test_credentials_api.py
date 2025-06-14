"""
Versão de teste do credentials_api.py sem referência a schema para uso com SQLite
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, Header
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from pydantic import BaseModel, Field, validator, SecretStr

from tests.test_models import User, UserRole, CloudProvider, CloudCredential
from tests.test_config import get_test_database
from tests.test_auth_security import security_manager_test

# Modelos Pydantic para API
class LoginRequest(BaseModel):
    """Requisição de login"""
    username: str
    password: str

class TokenResponse(BaseModel):
    """Resposta de token de autenticação"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Dict[str, Any] = None

class UserCreate(BaseModel):
    """Modelo para criação de usuários"""
    username: str
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=8)
    role: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one number')
        return v

class UserResponse(BaseModel):
    """Resposta de usuário"""
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

class CredentialConfigResponse(BaseModel):
    """Resposta de configuração de credenciais"""
    id: int
    name: str
    provider_type: str
    description: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_validated: Optional[datetime] = None
    expires_at: Optional[datetime] = None

class CredentialCreate(BaseModel):
    """Modelo para criação de credenciais"""
    name: str = Field(..., min_length=1, max_length=100)
    provider_type: str = Field(..., pattern="^(AWS|Azure|GCP)$")
    description: Optional[str] = Field(None, max_length=255)
    credentials: Dict[str, Any] = Field(..., min_items=1)
    expires_at: Optional[datetime] = None
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    # Validação mais rigorosa de credenciais
    @validator('credentials')
    def validate_credentials(cls, v, values):
        if not v:
            raise ValueError('Credentials cannot be empty')
        
        provider_type = values.get('provider_type')
        if provider_type == 'AWS':
            required_fields = ['access_key_id', 'secret_access_key']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Missing required field for AWS: {field}')
                
            # Validar formato de access_key_id
            if not v['access_key_id'].startswith('AKIA'):
                raise ValueError('Invalid AWS access key ID format')
                
            # Validar tamanho mínimo de secret_access_key
            if len(v['secret_access_key']) < 20:
                raise ValueError('AWS secret access key too short')
                
        elif provider_type == 'Azure':
            required_fields = ['subscription_id', 'client_id', 'client_secret', 'tenant_id']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Missing required field for Azure: {field}')
            
            # Validar formato de GUIDs do Azure
            import re
            guid_pattern = re.compile('^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
            for field in ['subscription_id', 'client_id', 'tenant_id']:
                if not guid_pattern.match(v[field]):
                    raise ValueError(f'Invalid Azure {field} format')
    
        return v

class CredentialUpdate(BaseModel):
    """Modelo para atualização de credenciais"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    expires_at: Optional[datetime] = None

class AuditLogResponse(BaseModel):
    """Resposta de log de auditoria"""
    id: int
    action: str
    username: str
    timestamp: datetime
    success: bool
    details: Optional[Dict[str, Any]] = None

logger = logging.getLogger(__name__)

# Routers para testes
credentials_router_test = APIRouter(prefix="/api/v1/credentials", tags=["Credentials Management"])
auth_router_test = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
audit_router_test = APIRouter(prefix="/api/v1/audit", tags=["Audit"])

# Função auxiliar para obter usuário atual
async def get_current_user(authorization: str = Header(None), 
                          db: Session = Depends(get_test_database)):
    """Obter usuário atual a partir do token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = security_manager_test.get_current_token(authorization)
    user = security_manager_test.get_current_active_user(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# ============================================================================
# ENDPOINTS DE AUTENTICAÇÃO
# ============================================================================

@auth_router_test.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_test_database)
):
    """Autentica usuário e retorna tokens"""
    try:        
        # Autenticar usuário
        user = security_manager_test.authenticate_user(db, login_data.username, login_data.password)
        
        if not user:
            # Log tentativa de login falhada (simplificado para testes)
            logger.warning(f"Login falhou para usuário: {login_data.username}")
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Criar tokens
        access_token = security_manager_test.create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        refresh_token = security_manager_test.create_refresh_token(
            data={"sub": user.username}
        )
        
        # Log login bem-sucedido (simplificado para testes)
        logger.info(f"Login bem-sucedido para usuário: {login_data.username}")
        
        # Criar resposta de usuário para testes
        user_response_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user_response_data
        )
    
    except HTTPException:
        # Re-raise HTTPExceptions (como 401) sem modificar
        raise
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login error: {str(e)}"
        )

@auth_router_test.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_data: UserCreate,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Criar novo usuário (simplificado para testes)"""
    try:
        # Verificar se usuário atual é admin
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        # Verificar se usuário já existe
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already exists"
            )
        
        # Criar hash da senha
        hashed_password = security_manager_test.get_password_hash(user_data.password)
        
        # Criar novo usuário
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            role=new_user.role,
            is_active=new_user.is_active,
            created_at=new_user.created_at
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Erro ao criar usuário: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

# ============================================================================
# ENDPOINTS DE CREDENCIAIS
# ============================================================================

@credentials_router_test.post("", response_model=CredentialConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_credential(
    credential_data: CredentialCreate,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Criar nova credencial (simplificada para testes)"""
    try:
        # Verificar se usuário pode criar credenciais
        if current_user.role not in ["admin", "finops_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # Verificar se o nome já existe
        existing = db.query(CloudCredential).filter(CloudCredential.name == credential_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Credential with this name already exists"
            )
        
        # Verificar se o provedor existe, senão criar
        provider = db.query(CloudProvider).filter(
            CloudProvider.provider_name == credential_data.provider_type
        ).first()
        
        if not provider:
            provider = CloudProvider(
                provider_name=credential_data.provider_type,
                api_endpoint=None,
                is_active=True
            )
            db.add(provider)
            db.commit()
        
        # Criar credencial
        new_credential = CloudCredential(
            name=credential_data.name,
            provider_type=credential_data.provider_type,
            provider_id=provider.id,
            description=credential_data.description,
            status="active",
            expires_at=credential_data.expires_at
        )
        
        db.add(new_credential)
        db.commit()
        db.refresh(new_credential)
        
        return CredentialConfigResponse(
            id=new_credential.id,
            name=new_credential.name,
            provider_type=new_credential.provider_type,
            description=new_credential.description,
            status=new_credential.status,
            created_at=new_credential.created_at,
            updated_at=new_credential.updated_at,
            last_validated=new_credential.last_validated,
            expires_at=new_credential.expires_at
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Erro ao criar credencial: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating credential: {str(e)}"
        )

@credentials_router_test.get("", response_model=List[CredentialConfigResponse])
async def list_credentials(
    provider_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Listar credenciais com suporte a filtros"""
    query = db.query(CloudCredential)
    
    # Aplicar filtros
    if provider_type:
        query = query.filter(CloudCredential.provider_type == provider_type)
    if status:
        query = query.filter(CloudCredential.status == status)
    
    credentials = query.all()
    return credentials

@credentials_router_test.get("/{credential_id}", response_model=CredentialConfigResponse)
async def get_credential(
    credential_id: str,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Obter uma credencial específica"""
    credential = db.query(CloudCredential).filter(CloudCredential.id == credential_id).first()
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )
    
    return credential

@credentials_router_test.put("/{credential_id}", response_model=CredentialConfigResponse)
async def update_credential(
    credential_id: str,
    credential_data: CredentialUpdate,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Atualizar uma credencial"""
    credential = db.query(CloudCredential).filter(CloudCredential.id == credential_id).first()
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )
    
    # Atualizar apenas campos fornecidos
    if credential_data.name is not None:
        credential.name = credential_data.name
    if credential_data.description is not None:
        credential.description = credential_data.description
    if credential_data.status is not None:
        credential.status = credential_data.status
    if credential_data.expires_at is not None:
        credential.expires_at = credential_data.expires_at
    
    credential.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(credential)
    
    return credential

@credentials_router_test.delete("/{credential_id}")
async def delete_credential(
    credential_id: int,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Deletar credencial"""
    try:
        # Verificar permissões
        if current_user.role not in ["admin", "finops_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # Buscar credencial
        credential = db.query(CloudCredential).filter(CloudCredential.id == credential_id).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        # Deletar credencial
        db.delete(credential)
        db.commit()
        
        return {"message": "Credential deleted successfully"}
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Erro ao deletar credencial: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting credential: {str(e)}"
        )

@credentials_router_test.post("/{credential_id}/validate")
async def validate_credential(
    credential_id: int,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Validar credencial (simulado para testes)"""
    try:
        credential = db.query(CloudCredential).filter(CloudCredential.id == credential_id).first()
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found"
            )
        
        # Simular validação bem-sucedida
        credential.last_validated = datetime.utcnow()
        credential.status = "active"
        db.commit()
        
        return {
            "is_valid": True,
            "provider_type": credential.provider_type,
            "validation_timestamp": credential.last_validated.isoformat(),
            "account_info": {"account_id": "123456789012"},
            "permissions_check": {"cost_explorer": True}
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Erro ao validar credencial: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error validating credential: {str(e)}"
        )

class CredentialTest(BaseModel):
    """Modelo para teste de credenciais"""
    provider_type: str = Field(..., pattern="^(AWS|Azure|GCP)$")
    credentials: Dict[str, Any] = Field(..., min_items=1)

@credentials_router_test.post("/test", status_code=status.HTTP_200_OK)
async def validate_credentials_endpoint(
    credential_data: CredentialTest,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Testar credenciais sem salvar"""
    try:
        # Simular validação para testes
        return {
            "is_valid": True,
            "provider_type": credential_data.provider_type,
            "validation_timestamp": datetime.utcnow().isoformat(),
            "details": {
                "permissions_check": {"cost_explorer": True},
                "account_info": {"account_id": "123456789012"}
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

class StatusUpdate(BaseModel):
    """Modelo para atualização de status"""
    status: str = Field(..., pattern="^(active|inactive)$")

@credentials_router_test.patch("/{credential_id}/status", response_model=CredentialConfigResponse)
async def update_credential_status(
    credential_id: str,
    status_data: StatusUpdate,
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user)
):
    """Atualizar status de uma credencial"""
    credential = db.query(CloudCredential).filter(CloudCredential.id == credential_id).first()
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credential not found"
        )
    
    # Verificar permissões
    if current_user.role not in [UserRole.ADMIN.value, UserRole.FINOPS_ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    credential.status = status_data.status
    credential.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(credential)
    
    return credential

# ============================================================================
# ENDPOINTS DE AUDITORIA
# ============================================================================

@audit_router_test.get("", response_model=List[AuditLogResponse])
async def list_audit_logs(
    db: Session = Depends(get_test_database),
    current_user: User = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """Listar logs de auditoria (simplificado para testes)"""
    # Simplificado para testes (sem audit logs reais)
    # Retornar alguns logs de exemplo
    return [
        AuditLogResponse(
            id=1,
            action="login",
            username=current_user.username,
            timestamp=datetime.utcnow(),
            success=True,
            details={"ip": "127.0.0.1"}
        )
    ]
