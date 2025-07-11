#!/usr/bin/env python3
"""
Teste final para validar criação de credencial com campos estendidos
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUyMjA0MDY2LCJpYXQiOjE3NTIyMDA0NjYsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.6VK3OmHwzf-OIWHoekzBVjYP44nBsqYGa2cTYmy6i0Q"

def test_create_enhanced_credential():
    """Testa criação de credencial com campos estendidos"""
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Dados da credencial com campos estendidos
    credential_data = {
        "name": "test-dual-credential-final",
        "description": "Teste final do sistema de duplas credenciais",
        "provider_type": "AWS",
        "credentials": {
            "access_key_id": "AKIATEST123456789012", 
            "secret_access_key": "test-secret-key-1234567890abcdef",
            "region": "us-east-1",
            "account_id": "123456789012"
        },
        # Campos estendidos do sistema dual
        "access_pattern": "HYBRID",
        "credential_type": "ROLE_BASED", 
        "api_role_arn": "arn:aws:iam::123456789012:role/XCostAPIRole",
        "data_role_arn": "arn:aws:iam::123456789012:role/XCostDataRole",
        "external_id": "xcost-external-id-final-test",
        "session_duration": 7200
    }
    
    print("🧪 Testando criação de credencial com campos estendidos...")
    print(f"📋 Dados enviados:")
    print(json.dumps(credential_data, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/credentials",
            headers=headers,
            json=credential_data
        )
        
        print(f"\n📊 Resultado:")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 201:
            result = response.json()
            print("✅ SUCESSO! Credencial criada com campos estendidos:")
            print(f"   ID: {result['id']}")
            print(f"   Nome: {result['name']}")
            print(f"   Access Pattern: {result['access_pattern']}")
            print(f"   Credential Type: {result['credential_type']}")
            print(f"   API Role ARN: {result['api_role_arn']}")
            print(f"   Data Role ARN: {result['data_role_arn']}")
            print(f"   External ID: {result['external_id']}")
            print(f"   Session Duration: {result['session_duration']}")
            
            return True, result['id']
        else:
            print(f"❌ ERRO na criação:")
            print(f"   Response: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ ERRO na requisição: {e}")
        return False, None

def test_get_enhanced_credential(credential_id):
    """Testa busca da credencial criada"""
    
    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }
    
    print(f"\n🔍 Testando busca da credencial criada...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/credentials/{credential_id}",
            headers=headers
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCESSO! Credencial recuperada com todos os campos:")
            print(f"   Access Pattern: {result['access_pattern']}")
            print(f"   Credential Type: {result['credential_type']}")
            print(f"   API Role ARN: {result['api_role_arn']}")
            print(f"   Data Role ARN: {result['data_role_arn']}")
            print(f"   External ID: {result['external_id']}")
            print(f"   Session Duration: {result['session_duration']}")
            
            return True
        else:
            print(f"❌ ERRO na busca:")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERRO na requisição: {e}")
        return False

if __name__ == "__main__":
    print("="*80)
    print("🚀 TESTE FINAL DO SISTEMA DE DUPLAS CREDENCIAIS")
    print("="*80)
    
    # Teste 1: Criar credencial
    success_create, credential_id = test_create_enhanced_credential()
    
    if success_create and credential_id:
        # Teste 2: Buscar credencial
        success_get = test_get_enhanced_credential(credential_id)
        
        if success_get:
            print("\n" + "="*80)
            print("🎉 TODOS OS TESTES PASSARAM!")
            print("✅ Sistema de duplas credenciais TOTALMENTE FUNCIONAL")
            print("✅ Frontend pode ser integrado com confiança")
            print("="*80)
        else:
            print("\n❌ Falha no teste de busca")
    else:
        print("\n❌ Falha no teste de criação")
