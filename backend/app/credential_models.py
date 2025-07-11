from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pydantic import BaseModel, Field, SecretStr, validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum as PyEnum
import uuid
import re

Base = declarative_base()

# Enums
class CloudProviderType(str, PyEnum):
    AWS = "AWS"
    AZURE = "Azure"
    GCP = "GCP"
    ORACLE_CLOUD = "Oracle Cloud"

class CredentialStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    VALIDATION_FAILED = "validation_failed"

class UserRole(str, PyEnum):
    ADMIN = "admin"
    FINOPS_ADMIN = "finops_admin"
    VIEWER = "viewer"
    OPERATOR = "operator"

class AuditAction(str, PyEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VIEW = "view"
    VALIDATE = "validate"
    ROTATE = "rotate"

# SQLAlchemy Models
class User(Base):
    """Modelo de usuário para autenticação e autorização"""
    __tablename__ = "users"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relacionamentos
    credential_configs = relationship("CloudCredentialConfig", back_populates="created_by_user")

class CloudCredentialConfig(Base):
    """Configuração de credenciais (metadados apenas, não as credenciais sensíveis)"""
    __tablename__ = "cloud_credential_configs"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)  # Nome amigável dado pelo usuário
    description = Column(Text)
    provider_type = Column(Enum(CloudProviderType), nullable=False, index=True)
    
    # Referência ao secret no AWS Secrets Manager
    secret_arn = Column(String(500), nullable=False, unique=True)
    secret_name = Column(String(100), nullable=False, unique=True, index=True)
    
    # Metadados não-sensíveis específicos do provedor
    account_id = Column(String(50))  # AWS Account ID, Azure Subscription ID, etc.
    region_preference = Column(String(50))  # Região preferencial
    additional_config = Column(JSONB)  # Configurações extras não-sensíveis
    
    # Campos estendidos para sistema de duplas credenciais
    access_pattern = Column(String(20))  # DATA_ONLY, API_ONLY, HYBRID
    credential_type = Column(String(20))  # ROLE_BASED, PROGRAMMATIC
    api_role_arn = Column(String(500))  # ARN da role para acesso à API
    data_role_arn = Column(String(500))  # ARN da role para acesso aos dados
    external_id = Column(String(100))  # External ID para assume role
    session_duration = Column(Integer, default=3600)  # Duração da sessão em segundos
    
    # Status e validação
    status = Column(Enum(CredentialStatus), default=CredentialStatus.ACTIVE, index=True)
    last_validated = Column(DateTime)
    validation_error = Column(Text)
    expires_at = Column(DateTime)  # Para credenciais temporárias
    
    # Auditoria
    created_by = Column(UUID(as_uuid=True), ForeignKey("finops.users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    created_by_user = relationship("User", back_populates="credential_configs")

class CredentialAuditLog(Base):
    """Log de auditoria para operações com credenciais"""
    __tablename__ = "credential_audit_logs"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credential_id = Column(UUID(as_uuid=True), ForeignKey("finops.cloud_credential_configs.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("finops.users.id"), nullable=False)
    action = Column(Enum(AuditAction), nullable=False)
    
    # Detalhes da operação
    ip_address = Column(String(45))  # IPv6 support
    user_agent = Column(String(500))
    details = Column(JSONB)  # Detalhes específicos da ação
    
    # Resultado
    success = Column(Boolean, nullable=False)
    error_message = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

# Pydantic Models para API

# Modelos base para cada provedor
class AWSCredentials(BaseModel):
    """Credenciais AWS"""
    access_key_id: str = Field(..., min_length=16, max_length=32)
    secret_access_key: SecretStr = Field(..., min_length=40)
    region: Optional[str] = Field(default="us-east-1")
    account_id: Optional[str] = Field(default=None, pattern=r'^\d{12}$')
    role_arn: Optional[str] = Field(default=None)  # Para assume role
    external_id: Optional[str] = Field(default=None)  # Para cross-account access
    
    @validator('access_key_id')
    def validate_access_key_format(cls, v):
        if not re.match(r'^AKIA[0-9A-Z]{16}$|^ASIA[0-9A-Z]{16}$', v):
            raise ValueError('Invalid AWS Access Key ID format')
        return v

class AzureCredentials(BaseModel):
    """Credenciais Azure"""
    subscription_id: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    client_id: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
    client_secret: SecretStr = Field(..., min_length=1)
    tenant_id: str = Field(..., pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

class GCPCredentials(BaseModel):
    """Credenciais GCP"""
    project_id: str = Field(..., min_length=6, max_length=30)
    service_account_key: Dict[str, Any] = Field(...)  # JSON key file content
    
    @validator('service_account_key')
    def validate_service_account_key(cls, v):
        required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in v:
                raise ValueError(f'Missing required field in service account key: {field}')
        if v.get('type') != 'service_account':
            raise ValueError('Invalid service account key type')
        return v

class OracleCloudCredentials(BaseModel):
    """Credenciais Oracle Cloud"""
    user_ocid: str = Field(..., pattern=r'^ocid1\.user\.oc1\.\.[a-zA-Z0-9]+$')
    tenancy_ocid: str = Field(..., pattern=r'^ocid1\.tenancy\.oc1\.\.[a-zA-Z0-9]+$')
    region: str = Field(...)
    fingerprint: str = Field(..., pattern=r'^[a-f0-9]{2}(:[a-f0-9]{2}){15}$')
    private_key: SecretStr = Field(..., min_length=100)

# Union type para todas as credenciais
ProviderCredentials = Union[AWSCredentials, AzureCredentials, GCPCredentials, OracleCloudCredentials]

# Request/Response Models
class CredentialConfigCreate(BaseModel):
    """Modelo para criação de configuração de credencial"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    provider_type: CloudProviderType
    credentials: ProviderCredentials
    expires_at: Optional[datetime] = Field(default=None)
    additional_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Campos estendidos para sistema de duplas credenciais
    access_pattern: Optional[str] = Field(default=None, description="Padrão de acesso: DATA_ONLY, API_ONLY, ou HYBRID")
    credential_type: Optional[str] = Field(default=None, description="Tipo de credencial: ROLE_BASED ou PROGRAMMATIC")
    api_role_arn: Optional[str] = Field(default=None, description="ARN da role para acesso à API")
    data_role_arn: Optional[str] = Field(default=None, description="ARN da role para acesso aos dados")
    external_id: Optional[str] = Field(default=None, description="External ID para assume role")
    session_duration: Optional[int] = Field(default=3600, description="Duração da sessão em segundos")

class CredentialConfigUpdate(BaseModel):
    """Modelo para atualização de configuração de credencial"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    credentials: Optional[ProviderCredentials] = Field(default=None)
    status: Optional[CredentialStatus] = Field(default=None)
    expires_at: Optional[datetime] = Field(default=None)
    additional_config: Optional[Dict[str, Any]] = Field(default=None)
    
    # Campos estendidos para sistema de duplas credenciais
    access_pattern: Optional[str] = Field(default=None, description="Padrão de acesso: DATA_ONLY, API_ONLY, ou HYBRID")
    credential_type: Optional[str] = Field(default=None, description="Tipo de credencial: ROLE_BASED ou PROGRAMMATIC")
    api_role_arn: Optional[str] = Field(default=None, description="ARN da role para acesso à API")
    data_role_arn: Optional[str] = Field(default=None, description="ARN da role para acesso aos dados")
    external_id: Optional[str] = Field(default=None, description="External ID para assume role")
    session_duration: Optional[int] = Field(default=None, description="Duração da sessão em segundos")

class CredentialConfigResponse(BaseModel):
    """Modelo de resposta para configuração de credencial (sem dados sensíveis)"""
    id: str
    name: str
    description: Optional[str]
    provider_type: CloudProviderType
    account_id: Optional[str]
    region_preference: Optional[str]
    status: CredentialStatus
    last_validated: Optional[datetime]
    validation_error: Optional[str]
    expires_at: Optional[datetime]
    created_by: str  # Username
    created_at: datetime
    updated_at: datetime
    
    # Campos estendidos para sistema de duplas credenciais
    access_pattern: Optional[str] = Field(default=None, description="Padrão de acesso: DATA_ONLY, API_ONLY, ou HYBRID")
    credential_type: Optional[str] = Field(default=None, description="Tipo de credencial: ROLE_BASED ou PROGRAMMATIC")
    api_role_arn: Optional[str] = Field(default=None, description="ARN da role para acesso à API")
    data_role_arn: Optional[str] = Field(default=None, description="ARN da role para acesso aos dados")
    external_id: Optional[str] = Field(default=None, description="External ID para assume role")
    session_duration: Optional[int] = Field(default=None, description="Duração da sessão em segundos")
    
    class Config:
        from_attributes = True

class CredentialValidationResult(BaseModel):
    """Resultado da validação de credenciais"""
    is_valid: bool
    provider_type: CloudProviderType
    account_info: Optional[Dict[str, Any]] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    validation_timestamp: datetime
    permissions_check: Optional[Dict[str, bool]] = Field(default=None)

class CredentialTestRequest(BaseModel):
    """Request para teste de credenciais"""
    provider_type: CloudProviderType
    credentials: ProviderCredentials
    test_permissions: bool = Field(default=True)

# User Management Models
class UserCreate(BaseModel):
    """Modelo para criação de usuário"""
    username: str = Field(..., min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: SecretStr = Field(..., min_length=8)
    role: UserRole = Field(default=UserRole.VIEWER)

class UserResponse(BaseModel):
    """Modelo de resposta do usuário"""
    id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Resposta de autenticação"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

# Query Parameters
class CredentialQueryParams(BaseModel):
    """Parâmetros de consulta para credenciais"""
    provider_type: Optional[CloudProviderType] = Field(default=None)
    status: Optional[CredentialStatus] = Field(default=None)
    name_contains: Optional[str] = Field(default=None)
    expires_before: Optional[datetime] = Field(default=None)
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class AuditQueryParams(BaseModel):
    """Parâmetros de consulta para logs de auditoria"""
    credential_id: Optional[str] = Field(default=None)
    user_id: Optional[str] = Field(default=None)
    action: Optional[AuditAction] = Field(default=None)
    start_date: Optional[datetime] = Field(default=None)
    end_date: Optional[datetime] = Field(default=None)
    success_only: Optional[bool] = Field(default=None)
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class AuditLogResponse(BaseModel):
    """Resposta do log de auditoria"""
    id: str
    credential_id: Optional[str]
    credential_name: Optional[str]
    user_username: str
    action: AuditAction
    ip_address: Optional[str]
    success: bool
    error_message: Optional[str]
    timestamp: datetime
    details: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True

# Error Models
class CredentialError(BaseModel):
    """Modelo de erro para operações com credenciais"""
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = Field(default=None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Security Models
class PermissionCheck(BaseModel):
    """Verificação de permissões"""
    action: str
    resource: str
    allowed: bool
    reason: Optional[str] = Field(default=None)

class SecurityContext(BaseModel):
    """Contexto de segurança da requisição"""
    user_id: str
    username: str
    role: UserRole
    ip_address: str
    user_agent: str
    permissions: List[PermissionCheck]

class LoginRequest(BaseModel):
    """Modelo para request de login"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)