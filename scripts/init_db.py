#!/usr/bin/env python3
"""
Script para inicializar banco de dados e criar usuário admin padrão
"""

import os
import sys
from pathlib import Path

# Adicionar app ao path
app_path = Path(__file__).parent.parent / "app"
sys.path.append(str(app_path))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from models import Base as OriginalBase
from credential_models import Base as CredentialBase, User, UserRole
from auth_security import security_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database_url():
    """Criar URL do banco a partir das variáveis de ambiente"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://finops_user:finops_password@localhost:5432/finops_db"
    )

def init_database():
    """Inicializar banco de dados"""
    try:
        database_url = create_database_url()
        engine = create_engine(database_url)
        
        # Criar schema finops se não existir
        logger.info("Criando schema finops se não existir...")
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS finops"))
            conn.commit()
        
        logger.info("Criando tabelas do schema original...")
        OriginalBase.metadata.create_all(bind=engine)
        
        logger.info("Criando tabelas do schema de credenciais...")
        CredentialBase.metadata.create_all(bind=engine)
            
        logger.info("Banco de dados inicializado com sucesso!")
        return engine
        
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

def create_admin_user(engine):
    """Criar usuário admin padrão"""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Verificar se já existe admin
            existing_admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
            if existing_admin:
                logger.info(f"Usuário admin já existe: {existing_admin.username}")
                return existing_admin
            
            # Criar usuário admin
            admin_password = os.getenv("ADMIN_PASSWORD", "ChangeMe123!")
            hashed_password = security_manager.get_password_hash(admin_password)
            
            admin_user = User(
                username="admin",
                email="admin@finops.local",
                hashed_password=hashed_password,
                role=UserRole.ADMIN,
                is_active=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            logger.info(f"Usuário admin criado: {admin_user.username}")
            logger.warning(f"IMPORTANTE: Altere a senha padrão '{admin_password}' em produção!")
            
            return admin_user
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao criar usuário admin: {e}")
        raise

def create_sample_data(engine):
    """Criar dados de exemplo para desenvolvimento"""
    try:
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        try:
            # Criar usuários de exemplo
            sample_users = [
                {
                    "username": "finops_admin",
                    "email": "finops@company.com",
                    "password": "Password123!",
                    "role": UserRole.FINOPS_ADMIN
                },
                {
                    "username": "operator",
                    "email": "operator@company.com", 
                    "password": "Password123!",
                    "role": UserRole.OPERATOR
                },
                {
                    "username": "viewer",
                    "email": "viewer@company.com",
                    "password": "Password123!",
                    "role": UserRole.VIEWER
                }
            ]
            
            for user_data in sample_users:
                existing = db.query(User).filter(User.username == user_data["username"]).first()
                if not existing:
                    hashed_password = security_manager.get_password_hash(user_data["password"])
                    user = User(
                        username=user_data["username"],
                        email=user_data["email"],
                        hashed_password=hashed_password,
                        role=user_data["role"],
                        is_active=True
                    )
                    db.add(user)
                    logger.info(f"Criado usuário de exemplo: {user_data['username']}")
            
            db.commit()
            logger.info("Dados de exemplo criados com sucesso!")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Erro ao criar dados de exemplo: {e}")
        raise

def main():
    """Função principal"""
    logger.info("Iniciando configuração do banco de dados...")
    
    try:
        # Inicializar banco
        engine = init_database()
        
        # Criar usuário admin
        create_admin_user(engine)
        
        # Criar dados de exemplo se em desenvolvimento
        if os.getenv("ENVIRONMENT", "development") == "development":
            create_sample_data(engine)
        
        logger.info("Configuração do banco de dados concluída!")
        
    except Exception as e:
        logger.error(f"Falha na configuração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()