#!/usr/bin/env python3
"""
Script para verificar as colunas da tabela cloud_credential_configs
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_database
from sqlalchemy import text

def check_table_structure():
    """Verifica a estrutura da tabela cloud_credential_configs"""
    print("🔍 Verificando estrutura da tabela cloud_credential_configs...")
    
    # Obter conexão com o banco
    db = next(get_database())
    
    try:
        # Verificar colunas da tabela
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'finops' 
            AND table_name = 'cloud_credential_configs'
            ORDER BY ordinal_position;
        """))
        
        columns = result.fetchall()
        
        print(f"\n📋 Colunas encontradas na tabela finops.cloud_credential_configs:")
        print("-" * 80)
        print(f"{'Nome da Coluna':<25} {'Tipo':<20} {'Nulo?':<8} {'Padrão':<20}")
        print("-" * 80)
        
        # Colunas que esperamos do sistema dual
        expected_dual_columns = [
            'access_pattern',
            'credential_type', 
            'api_role_arn',
            'data_role_arn',
            'external_id',
            'session_duration'
        ]
        
        found_dual_columns = []
        
        for column in columns:
            column_name, data_type, is_nullable, column_default = column
            nullable = "SIM" if is_nullable == "YES" else "NÃO"
            default = str(column_default) if column_default else ""
            
            print(f"{column_name:<25} {data_type:<20} {nullable:<8} {default:<20}")
            
            if column_name in expected_dual_columns:
                found_dual_columns.append(column_name)
        
        print("-" * 80)
        
        # Verificar se todas as colunas do sistema dual foram criadas
        missing_columns = [col for col in expected_dual_columns if col not in found_dual_columns]
        
        if missing_columns:
            print(f"\n❌ Colunas FALTANTES do sistema dual:")
            for col in missing_columns:
                print(f"   - {col}")
        else:
            print(f"\n✅ Todas as colunas do sistema dual foram criadas com sucesso!")
            print(f"   Colunas encontradas: {', '.join(found_dual_columns)}")
        
        # Verificar índices
        print(f"\n🔍 Verificando índices...")
        result = db.execute(text("""
            SELECT indexname, indexdef
            FROM pg_indexes 
            WHERE schemaname = 'finops' 
            AND tablename = 'cloud_credential_configs'
            AND indexname LIKE '%access_pattern%' OR indexname LIKE '%credential_type%';
        """))
        
        indexes = result.fetchall()
        if indexes:
            print("✅ Índices do sistema dual encontrados:")
            for index_name, index_def in indexes:
                print(f"   - {index_name}")
        else:
            print("⚠️  Nenhum índice específico do sistema dual encontrado")
        
        return len(missing_columns) == 0
        
    except Exception as e:
        print(f"❌ Erro ao verificar estrutura da tabela: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = check_table_structure()
    
    if success:
        print(f"\n🎉 Banco de dados pronto para o sistema de duplas credenciais!")
        exit(0)
    else:
        print(f"\n💥 Problemas encontrados na estrutura do banco")
        exit(1)
