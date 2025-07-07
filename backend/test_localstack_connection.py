#!/usr/bin/env python3

"""
Script para testar a conexão com Localstack
"""

import os
import sys
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from dotenv import load_dotenv
load_dotenv()

import boto3
from botocore.exceptions import ClientError

def test_localstack_connection():
    print("🔍 TESTANDO CONEXÃO COM LOCALSTACK")
    print("=" * 50)
    
    # Verificar variáveis de ambiente
    print("📋 VARIÁVEIS DE AMBIENTE:")
    print(f"   AWS_ENDPOINT_URL: {os.getenv('AWS_ENDPOINT_URL')}")
    print(f"   AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')}")
    print(f"   AWS_SECRET_ACCESS_KEY: {os.getenv('AWS_SECRET_ACCESS_KEY')}")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION')}")
    print()
    
    try:
        # Configurar cliente S3 para Localstack
        s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        print("🚀 TESTANDO CLIENTE S3:")
        # Tentar listar buckets
        response = s3_client.list_buckets()
        print(f"   ✅ Conexão S3 bem-sucedida!")
        print(f"   📦 Buckets encontrados: {len(response.get('Buckets', []))}")
        
        # Configurar cliente Cost Explorer (se disponível no Localstack)
        ce_client = boto3.client(
            'ce',
            endpoint_url=os.getenv('AWS_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        print("💰 TESTANDO CLIENTE COST EXPLORER:")
        try:
            # Testar uma operação simples
            response = ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': '2024-01-01',
                    'End': '2024-01-02'
                },
                Granularity='DAILY',
                Metrics=['BlendedCost']
            )
            print("   ✅ Cost Explorer conectado!")
        except Exception as e:
            print(f"   ⚠️  Cost Explorer não disponível: {e}")
        
        print()
        print("✅ RESULTADO: Localstack está funcionando corretamente!")
        print("   O backend deveria conseguir se conectar sem problemas.")
        
    except ClientError as e:
        print(f"❌ ERRO DE CLIENTE AWS: {e}")
        print("   Verifique se o Localstack está rodando na porta 4566")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        print("   Verifique a configuração do Localstack")

if __name__ == "__main__":
    test_localstack_connection()
