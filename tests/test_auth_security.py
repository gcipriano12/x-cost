"""
Implementação de teste do módulo auth_security para SQLite
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import logging
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Header
from tests.test_models import User, UserRole

logger = logging.getLogger(__name__)

# Reuse some settings from the original module
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "test-secret-key-for-unit-testing")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Context para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_current_token(authorization: str = Header(None)) -> str:
    """Extrair token do header de autorização"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

class SecurityManagerTest:
    """Versão de teste do SecurityManager que trabalha com SQLite sem schema"""
    
    def get_current_token(self, authorization: str = Header(None)) -> str:
        """Extrair token do header de autorização - método da classe"""
        return get_current_token(authorization)
    
    def get_current_active_user(self, db, token: str) -> Optional[User]:
        """Obter usuário atual ativo a partir do token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            
            user = db.query(User).filter(User.username == username).first()
            if user is None or not user.is_active:
                return None
                
            return user
        except Exception as e:
            logger.error(f"Erro ao decodificar token: {e}")
            return None
    
    def authenticate_user(self, db, username: str, password: str) -> Optional[User]:
        """Autenticar usuário com banco SQLite sem schema"""
        try:
            # Usar os modelos de teste sem schema
            user = db.query(User).filter(User.username == username).first()
            
            if not user:
                logger.warning(f"Usuário não encontrado: {username}")
                return None
                
            if not self.verify_password(password, user.hashed_password):
                logger.warning(f"Senha inválida para usuário: {username}")
                return None
                
            if not user.is_active:
                logger.warning(f"Usuário inativo: {username}")
                return None
                
            # Atualizar último login
            user.last_login = datetime.utcnow()
            db.commit()
            
            return user
        except Exception as e:
            logger.error(f"Error in authenticate_user: {e}")
            return None
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha com hash"""
        return pwd_context.verify(plain_password, hashed_password)
        
    def get_password_hash(self, password: str) -> str:
        """Criar hash de senha"""
        return pwd_context.hash(password)
        
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Criar token JWT de acesso"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Criar token JWT de refresh"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
        
    def _get_client_ip(self, request: Any) -> str:
        """Obter IP do cliente"""
        return request.client.host if request.client and hasattr(request.client, "host") else "unknown"

# Instância única para uso nos testes
security_manager_test = SecurityManagerTest()
