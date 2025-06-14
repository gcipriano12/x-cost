"""
Modelos para testes com SQLite (sem schema)
"""
import sys
import os
from pathlib import Path
import enum
from datetime import datetime

# Importações SQLAlchemy
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Float
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

# Base para todos os modelos de teste
TestBase = declarative_base()

# Enum de roles de usuário
class UserRole(enum.Enum):
    """Roles de usuários"""
    ADMIN = "admin"
    FINOPS_ADMIN = "finops_admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

# Modelos de tabela sem schema para SQLite
class User(TestBase):
    """Usuários do sistema"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime)
    
    # Relações
    credentials = relationship("CloudCredential", back_populates="owner")
    
    def __init__(self, username, email, hashed_password, role, is_active=True):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.role = role if isinstance(role, str) else role.value
        self.is_active = is_active


class CloudProvider(TestBase):
    """Provedores de nuvem"""
    __tablename__ = "cloud_providers"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    provider_type = Column(String(20), nullable=False)
    description = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    credentials = relationship("CloudCredential", back_populates="provider")
class CloudCredential(TestBase):
    """Credenciais de provedores de nuvem"""
    __tablename__ = "cloud_credentials"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    provider_type = Column(String(20), nullable=False)
    provider_id = Column(Integer, ForeignKey("cloud_providers.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String(255))
    secret_arn = Column(String(255))
    secret_name = Column(String(255))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_validated = Column(DateTime)
    expires_at = Column(DateTime)
    account_id = Column(String(50))
    region_preference = Column(String(50))
    validation_error = Column(String(255))
    created_by = Column(String(50), default="admin")  # Simplificado para testes
    
    # Relacionamentos
    provider = relationship("CloudProvider", back_populates="credentials")
    owner = relationship("User", back_populates="credentials")