#!/usr/bin/env python3
"""
Script para testar a integração LocalStack + Backend + Frontend
"""

import os
import sys
import json
import requests
from pathlib import Path

# Definir variáveis de ambiente do LocalStack
os.environ['AWS_ENDPOINT_URL'] = 'http://localhost:4566'
os.environ['AWS_ACCESS_KEY_ID'] = 'test'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['USE_LOCALSTACK'] = 'true'

def test_backend_optimization_apis():
    """Testa as APIs de otimização do backend"""
    
    base_url = "http://localhost:8000"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDEwMjA3NCwiaWF0IjoxNzUwMDk4NDc0LCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.8fsMHVJnIdFUew4cVpWQUuNnP5z4dmQzxHoZzzkrAqk"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    endpoints = [
        "/api/v1/optimization/summary",
        "/api/v1/anomalies",
        "/api/v1/savings-opportunities",
        "/api/v1/optimization/recommendations"
    ]
    
    print("🧪 Testando APIs de Otimização...")
    
    for endpoint in endpoints:
        try:
            print(f"\n🔍 Testando {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Sucesso: {json.dumps(data, indent=2)[:200]}...")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro de conexão: {e}")

def check_localstack():
    """Verifica se o LocalStack está rodando"""
    try:
        print("🔍 Verificando LocalStack...")
        response = requests.get("http://localhost:4566/_localstack/health", timeout=5)
        
        if response.status_code == 200:
            health = response.json()
            print("✅ LocalStack está rodando")
            print(f"   Serviços disponíveis: {list(health.get('services', {}).keys())}")
            return True
        else:
            print("❌ LocalStack não está respondendo corretamente")
            return False
            
    except requests.exceptions.RequestException:
        print("❌ LocalStack não está rodando na porta 4566")
        return False

def populate_localstack_data():
    """Popula o LocalStack com dados de teste"""
    try:
        print("\n🔄 Populando LocalStack com dados de teste...")
        
        # Importar e executar o serviço AWS mockado
        sys.path.append(str(Path(__file__).parent))
        from app.cloud_native_optimization import AWSOptimizationService
        
        # Criar instância do serviço AWS
        aws_service = AWSOptimizationService()
        
        print("✅ Serviço AWS criado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular LocalStack: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Iniciando teste completo de integração...")
    
    # 1. Verificar LocalStack
    if not check_localstack():
        print("\n❌ LocalStack não está disponível. Execute: docker run -p 4566:4566 localstack/localstack")
        return
    
    # 2. Popular dados de teste
    if not populate_localstack_data():
        print("\n❌ Falha ao popular dados de teste")
        return
    
    # 3. Testar APIs do backend
    test_backend_optimization_apis()
    
    print("\n✅ Teste de integração concluído!")

if __name__ == "__main__":
    main()
