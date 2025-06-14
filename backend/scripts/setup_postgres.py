#!/usr/bin/env python3
"""
Script para configurar e verificar o banco PostgreSQL 
antes de popular com dados de teste.

Este script:
- Verifica se o PostgreSQL está acessível
- Cria o schema finops se não existir
- Executa migrations se necessário
- Verifica integridade das tabelas

Uso:
    python scripts/setup_postgres.py
"""

import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.credential_models import Base as CredentialBase

# Configurações do banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finops_user:finops_password@localhost:5432/finops_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_USER = os.getenv("POSTGRES_USER", "finops_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "finops_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "finops_db")

def create_database_if_not_exists():
    """Cria o banco de dados se não existir"""
    try:
        # Conectar ao PostgreSQL (sem especificar database)
        conn = psycopg2.connect(
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database="postgres"  # Conectar ao banco padrão
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Verificar se o banco existe
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{POSTGRES_DB}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"📦 Criando banco de dados: {POSTGRES_DB}")
            cursor.execute(f"CREATE DATABASE {POSTGRES_DB}")
            print(f"✅ Banco {POSTGRES_DB} criado com sucesso")
        else:
            print(f"✅ Banco {POSTGRES_DB} já existe")
            
        cursor.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Erro ao conectar/criar banco: {e}")
        return False
    
    return True

def create_schema_and_tables():
    """Cria o schema finops e as tabelas"""
    try:
        engine = create_engine(DATABASE_URL)
        
        # Criar schema finops
        with engine.connect() as conn:
            conn.execute(text("CREATE SCHEMA IF NOT EXISTS finops"))
            conn.commit()
            print("✅ Schema 'finops' verificado/criado")
        
        # Criar todas as tabelas
        print("📋 Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        CredentialBase.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas/verificadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar schema/tabelas: {e}")
        return False

def insert_default_providers():
    """Insere os provedores padrão"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Verificar se os provedores já existem
            result = conn.execute(text("SELECT COUNT(*) FROM finops.cloud_providers"))
            count = result.scalar()
            
            if count == 0:
                print("📦 Inserindo provedores de nuvem padrão...")
                providers_sql = """
                INSERT INTO finops.cloud_providers (provider_name, api_endpoint, is_active) VALUES 
                ('AWS', 'https://aws.amazon.com', true),
                ('Azure', 'https://azure.microsoft.com', true),
                ('GCP', 'https://cloud.google.com', true),
                ('Oracle Cloud', 'https://oracle.com/cloud', true)
                ON CONFLICT (provider_name) DO NOTHING
                """
                conn.execute(text(providers_sql))
                conn.commit()
                print("✅ Provedores inseridos")
            else:
                print(f"✅ Provedores já existem ({count} registros)")
                
        return True
        
    except Exception as e:
        print(f"❌ Erro ao inserir provedores: {e}")
        return False

def verify_database_structure():
    """Verifica a estrutura do banco"""
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Verificar tabelas existentes
            tables_sql = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'finops'
            ORDER BY table_name
            """
            result = conn.execute(text(tables_sql))
            tables = [row[0] for row in result.fetchall()]
            
            expected_tables = [
                'budgets', 
                'cloud_credential_configs',  # Nome real da tabela
                'cloud_providers',
                'cost_analysis',
                'credential_audit_logs',  # Nome real da tabela
                'focus_cost_data',
                'users'
            ]
            
            print(f"\n📋 Tabelas encontradas no schema 'finops':")
            for table in tables:
                status = "✅" if table in expected_tables else "⚠️"
                print(f"  {status} {table}")
            
            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                print(f"\n⚠️  Tabelas faltando: {', '.join(missing_tables)}")
                return False
            
            print(f"\n✅ Estrutura do banco verificada ({len(tables)} tabelas)")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura: {e}")
        return False

def test_database_connection():
    """Testa a conexão com o banco"""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Conexão PostgreSQL OK: {version.split(',')[0]}")
            return True
    except Exception as e:
        print(f"❌ Falha na conexão: {e}")
        return False

def print_connection_info():
    """Imprime informações de conexão"""
    print("\n" + "="*60)
    print("🔧 CONFIGURAÇÃO DO BANCO DE DADOS")
    print("="*60)
    print(f"Host: {POSTGRES_HOST}")
    print(f"Porta: {POSTGRES_PORT}")
    print(f"Usuário: {POSTGRES_USER}")
    print(f"Banco: {POSTGRES_DB}")
    print(f"URL: postgresql://finops_user:finops_password@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    print("="*60)

def main():
    """Função principal"""
    print("🚀 Configurando ambiente PostgreSQL...")
    
    print_connection_info()
    
    # 1. Testar conexão
    print("\n🔍 Testando conexão...")
    if not test_database_connection():
        print("\n❌ Configure o PostgreSQL e tente novamente")
        print("\n💡 Comandos para configurar PostgreSQL:")
        print("  # Docker:")
        print(f"  docker run -d --name postgres-finops \\")
        print(f"    -e POSTGRES_USER={POSTGRES_USER} \\")
        print(f"    -e POSTGRES_PASSWORD={POSTGRES_PASSWORD} \\")
        print(f"    -e POSTGRES_DB={POSTGRES_DB} \\")
        print(f"    -p {POSTGRES_PORT}:5432 \\")
        print(f"    postgres:14")
        print("\n  # ou use o podman-compose.yml do projeto")
        return False
    
    # 2. Criar banco se necessário
    print("\n📦 Verificando/criando banco...")
    if not create_database_if_not_exists():
        return False
    
    # 3. Criar schema e tabelas
    print("\n📋 Configurando schema e tabelas...")
    if not create_schema_and_tables():
        return False
    
    # 4. Inserir dados padrão
    print("\n🔧 Inserindo dados padrão...")
    if not insert_default_providers():
        return False
    
    # 5. Verificar estrutura
    print("\n🔍 Verificando estrutura final...")
    if not verify_database_structure():
        return False
    
    print("\n" + "="*60)
    print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("✅ PostgreSQL configurado e pronto para uso")
    print("✅ Schema 'finops' criado")
    print("✅ Tabelas criadas")
    print("✅ Provedores padrão inseridos")
    print("\n📝 Próximo passo:")
    print("  python scripts/populate_database.py")
    print("="*60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
