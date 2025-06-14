from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import jwt
import logging
from functools import wraps
import ipaddress
import os

from app.credential_models import User, UserRole, CredentialAuditLog, AuditAction, SecurityContext, PermissionCheck
from app.database import get_database

logger = logging.getLogger(__name__)

# Configurações de segurança
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
if SECRET_KEY == "your-secret-key-change-in-production":
    logger.warning("AVISO DE SEGURANÇA: Usando chave secreta padrão, defina JWT_SECRET_KEY em produção!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Context para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()

class AuthenticationError(Exception):
    """Erro de autenticação"""
    pass

class AuthorizationError(Exception):
    """Erro de autorização"""
    pass

class SecurityManager:
    """Gerenciador de segurança para autenticação e autorização"""
    
    def __init__(self):
        self.pwd_context = pwd_context
        self.secret_key = SECRET_KEY
        self.algorithm = ALGORITHM
        
        # Definir permissões por role
        self.role_permissions = {
            UserRole.ADMIN: [
                "credentials:create", "credentials:read", "credentials:update", "credentials:delete",
                "credentials:validate", "credentials:rotate", "users:create", "users:read", 
                "users:update", "users:delete", "audit:read", "system:admin"
            ],
            UserRole.FINOPS_ADMIN: [
                "credentials:create", "credentials:read", "credentials:update", "credentials:delete",
                "credentials:validate", "credentials:rotate", "audit:read"
            ],
            UserRole.OPERATOR: [
                "credentials:read", "credentials:validate", "data:ingest"
            ],
            UserRole.VIEWER: [
                "credentials:read", "audit:read"
            ]
        }
        
        # IPs permitidos (opcional - configure conforme necessário)
        self.allowed_ip_ranges = [
            ipaddress.ip_network("10.0.0.0/8"),      # Private networks
            ipaddress.ip_network("172.16.0.0/12"),
            ipaddress.ip_network("192.168.0.0/16"),
            ipaddress.ip_network("127.0.0.0/8"),     # Localhost
        ]
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica senha"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Gera hash da senha"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Cria token de acesso JWT"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access_token"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Cria token de refresh"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh_token"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifica e decodifica token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.JWTError:
            raise AuthenticationError("Invalid token")
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Autentica usuário"""
        try:
            # Verificar se db é realmente uma Session
            if not hasattr(db, 'query'):
                logger.error(f"Invalid session object: {type(db)}")
                return None
                
            user = db.query(User).filter(User.username == username).first()
            if not user:
                logger.warning(f"User not found: {username}")
                return None
                
            if not user.is_active:
                logger.warning(f"User is inactive: {username}")
                return None
                
            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Invalid password for user: {username}")
                return None
            
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.commit()
            
            logger.info(f"User authenticated successfully: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error in authenticate_user: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_user_permissions(self, user_role: UserRole) -> List[str]:
        """Obtém permissões do usuário baseado no role"""
        return self.role_permissions.get(user_role, [])
    
    def check_permission(self, user_role: UserRole, required_permission: str) -> bool:
        """Verifica se usuário tem permissão específica"""
        user_permissions = self.get_user_permissions(user_role)
        return required_permission in user_permissions
    
    def check_ip_allowed(self, ip_address: str) -> bool:
        """Verifica se IP está na lista de permitidos (opcional)"""
        if not self.allowed_ip_ranges:
            return True  # Se não há restrições, permite todos
        
        try:
            client_ip = ipaddress.ip_address(ip_address)
            return any(client_ip in network for network in self.allowed_ip_ranges)
        except ValueError:
            logger.warning(f"Invalid IP address: {ip_address}")
            return False
    
    def create_security_context(
        self, 
        request: Request, 
        user: User,
        required_permissions: List[str] = None
    ) -> SecurityContext:
        """Cria contexto de segurança para a requisição"""
        
        # Obter IP do cliente
        client_ip = self._get_client_ip(request)
        
        # Verificar permissões
        permissions = []
        if required_permissions:
            for permission in required_permissions:
                allowed = self.check_permission(user.role, permission)
                permissions.append(PermissionCheck(
                    action=permission,
                    resource="credentials",
                    allowed=allowed,
                    reason=None if allowed else "Insufficient privileges"
                ))
        
        return SecurityContext(
            user_id=str(user.id),
            username=user.username,
            role=user.role,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent", ""),
            permissions=permissions
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Obtém IP real do cliente considerando proxies"""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback para IP direto
        return request.client.host if request.client else "unknown"

# Instância global do gerenciador de segurança
security_manager = SecurityManager()

# Dependency functions para main
# Substitua as funções de dependency em app/auth_security.py

# Dependency functions para FastAPI
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_database)
) -> User:
    """Dependency para obter usuário autenticado"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Verificar token
        payload = security_manager.verify_token(credentials.credentials)
        username: str = payload.get("sub")
        
        if username is None:
            logger.warning("Token payload missing 'sub' field")
            raise credentials_exception
            
    except Exception as e:
        logger.warning(f"Token verification failed: {e}")
        raise credentials_exception
    
    # Buscar usuário no banco usando SessionLocal diretamente
    from app.database import SessionLocal
    
    db_session = SessionLocal()
    try:
        user = db_session.query(User).filter(User.username == username).first()
        if user is None:
            logger.warning(f"User not found in database: {username}")
            raise credentials_exception
            
        if not user.is_active:
            logger.warning(f"User is inactive: {username}")
            raise credentials_exception
        
        logger.info(f"User authenticated successfully via token: {username}")
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Database error in get_current_user: {e}")
        raise credentials_exception
    finally:
        db_session.close()

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency para garantir que usuário está ativo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Versões simplificadas para roles específicos
async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency que exige role ADMIN"""
    if current_user.role != UserRole.ADMIN:
        logger.warning(f"Access denied for user {current_user.username}: requires admin role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def require_finops_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency que exige role FINOPS_ADMIN ou superior"""
    allowed_roles = [UserRole.ADMIN, UserRole.FINOPS_ADMIN]
    if current_user.role not in allowed_roles:
        logger.warning(f"Access denied for user {current_user.username}: requires finops_admin role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FinOps Admin privileges required"
        )
    return current_user

async def require_operator(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency que exige role OPERATOR ou superior"""
    allowed_roles = [UserRole.ADMIN, UserRole.FINOPS_ADMIN, UserRole.OPERATOR]
    if current_user.role not in allowed_roles:
        logger.warning(f"Access denied for user {current_user.username}: requires operator role")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator privileges required"
        )
    return current_user

# # Função para obter logger de auditoria sem dependency injection
# def get_audit_logger_direct() -> AuditLogger:
#     """Obter logger de auditoria sem dependency injection"""
#     from app.database import SessionLocal
#     db = SessionLocal()
#     return AuditLogger(db)

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency para garantir que usuário está ativo"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_permissions(required_permissions: List[str]):
    """Decorator para exigir permissões específicas"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair user da função (assumindo que é um dependency)
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependency not found"
                )
            
            # Verificar permissões
            for permission in required_permissions:
                if not security_manager.check_permission(current_user.role, permission):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Insufficient permissions: {permission} required"
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(required_roles: List[UserRole]):
    """Decorator para exigir roles específicos"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication dependency not found"
                )
            
            if current_user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required roles: {[role.value for role in required_roles]}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Dependencies específicos por role
async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency que exige role ADMIN"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def require_finops_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency que exige role FINOPS_ADMIN ou superior"""
    allowed_roles = [UserRole.ADMIN, UserRole.FINOPS_ADMIN]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="FinOps Admin privileges required"
        )
    return current_user

async def require_operator(current_user: User = Depends(get_current_active_user)) -> User:
    """Dependency que exige role OPERATOR ou superior"""
    allowed_roles = [UserRole.ADMIN, UserRole.FINOPS_ADMIN, UserRole.OPERATOR]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator privileges required"
        )
    return current_user

class AuditLogger:
    """Logger para auditoria de operações com credenciais"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_credential_action(
        self,
        user: Optional[User],
        action: AuditAction,
        credential_id: Optional[str] = None,
        ip_address: str = None,
        user_agent: str = None,
        details: Dict[str, Any] = None,
        success: bool = True,
        error_message: str = None
    ):
        """Registra ação de auditoria"""
        try:
            # Verificar se usuário é None
            if user is None:
                # Log de tentativa sem usuário autenticado
                logger.warning(f"Tentativa de ação {action.value} sem usuário autenticado")
                return
            
            # Verificar se db é um generator (problema comum)
            if hasattr(self.db, '__next__'):
                logger.error("Database session is a generator object, not a Session")
                return
                
            audit_log = CredentialAuditLog(
                credential_id=credential_id,
                user_id=user.id,
                action=action,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details or {},
                success=success,
                error_message=error_message
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
            logger.info(
                f"Audit log created: {action.value} by {user.username} "
                f"(success={success}) for credential {credential_id}"
            )
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            try:
                self.db.rollback()
            except Exception as rollback_error:
                logger.error(f"Failed to rollback after audit log error: {rollback_error}")

def get_audit_logger(db: Session = Depends(get_database)) -> AuditLogger:
    """Dependency para obter logger de auditoria"""
    # Extrair a sessão real se for um generator
    if hasattr(db, '__next__'):
        try:
            db = next(db)
        except StopIteration:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get database session"
            )
    
    return AuditLogger(db)

def get_audit_logger(db: Session = Depends(get_database)) -> AuditLogger:
    """Dependency para obter logger de auditoria"""
    return AuditLogger(db)

# Middleware de segurança
class SecurityMiddleware:
    """Middleware para verificações de segurança adicionais"""
    
    def __init__(self):
        self.security_manager = security_manager
    
    async def __call__(self, request: Request, call_next):
        """Processa requisição com verificações de segurança"""
        
        # Verificar IP apenas se a verificação estiver ativada
        if self._should_check_ip():
            client_ip = self.security_manager._get_client_ip(request)
            if not self.security_manager.check_ip_allowed(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied from this IP address"
                )
        
        # Adicionar headers de segurança
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    def _should_check_ip(self) -> bool:
        """Determina se deve verificar IP (baseado no ambiente)"""
        import os
        return os.getenv("ENVIRONMENT") == "production"

# Funções utilitárias
def create_user(
    db: Session, 
    username: str, 
    email: str, 
    password: str, 
    role: UserRole = UserRole.VIEWER
) -> User:
    """Cria novo usuário"""
    
    # Verificar se usuário já existe
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        raise ValueError("Username or email already exists")
    
    # Criar usuário
    hashed_password = security_manager.get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        role=role
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info(f"Created user: {username} with role {role.value}")
    return user

def change_user_password(db: Session, user: User, new_password: str) -> bool:
    """Altera senha do usuário"""
    try:
        user.hashed_password = security_manager.get_password_hash(new_password)
        db.commit()
        
        logger.info(f"Password changed for user: {user.username}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to change password for user {user.username}: {e}")
        db.rollback()
        return False