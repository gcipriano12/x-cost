#!/usr/bin/env python3
"""
Script para criar todas as tabelas no banco de dados
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.database import DATABASE_URL
from app.credential_models import Base
from app.models import Base as ModelsBase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_all_tables():
    """Cria todas as tabelas no banco de dados"""
    try:
        # Usar a URL do banco diretamente
        logger.info(f"Conectando ao banco: {DATABASE_URL}")
        
        # Criar engine
        engine = create_engine(DATABASE_URL, echo=True)  # Adicionar echo para debug
        
        # Verificar conexão
        with engine.connect() as conn:
            logger.info("✅ Conexão com banco estabelecida")
        
        # Criar todas as tabelas
        logger.info("Criando tabelas dos modelos de credenciais...")
        logger.info(f"Tabelas a serem criadas: {list(Base.metadata.tables.keys())}")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Criando tabelas dos outros modelos...")
        logger.info(f"Tabelas a serem criadas: {list(ModelsBase.metadata.tables.keys())}")
        ModelsBase.metadata.create_all(bind=engine)
        
        logger.info("✅ Todas as tabelas foram criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = create_all_tables()
    sys.exit(0 if success else 1)
