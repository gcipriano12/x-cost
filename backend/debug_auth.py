#!/usr/bin/env python3
"""
Script para debug de autenticação
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import get_database
from app.credential_models import User, UserRole
from app.auth_security import security_manager

# Context para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_password_hash():
    """Testa o hash de senha"""
    password = "test123"
    hashed = pwd_context.hash(password)
    print(f"Password: {password}")
    print(f"Hashed: {hashed}")
    print(f"Verify: {pwd_context.verify(password, hashed)}")

def create_simple_user():
    """Cria um usuário simples para teste"""
    db = next(get_database())
    
    # Deletar usuário se existe
    existing = db.query(User).filter(User.username == "test").first()
    if existing:
        db.delete(existing)
        db.commit()
    
    # Criar novo usuário
    password = "test123"
    hashed_password = pwd_context.hash(password)
    
    user = User(
        username="test",
        email="test@test.com",
        hashed_password=hashed_password,
        role=UserRole.ADMIN,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    
    print(f"Usuário criado: {user.username}")
    print(f"Senha: {password}")
    print(f"Hash: {hashed_password}")
    
    # Testar verificação
    verify_result = pwd_context.verify(password, hashed_password)
    print(f"Verificação: {verify_result}")
    
    return user

def test_authenticate():
    """Testa autenticação"""
    db = next(get_database())
    
    username = "test"
    password = "test123"
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"Usuário {username} não encontrado")
        return
    
    print(f"Usuário encontrado: {user.username}")
    print(f"Hash armazenado: {user.hashed_password}")
    
    # Testar verificação de senha
    verify_result = pwd_context.verify(password, user.hashed_password)
    print(f"Verificação de senha: {verify_result}")
    
    # Testar com security manager
    try:
        auth_user = security_manager.authenticate_user(db, username, password)
        print(f"Autenticação via security_manager: {auth_user is not None}")
    except Exception as e:
        print(f"Erro na autenticação: {e}")

if __name__ == "__main__":
    print("=== Debug de Autenticação ===")
    
    print("\n1. Testando hash de senha:")
    test_password_hash()
    
    print("\n2. Criando usuário simples:")
    user = create_simple_user()
    
    print("\n3. Testando autenticação:")
    test_authenticate()
