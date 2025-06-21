#!/usr/bin/env python3
"""
Script de teste para Virtual Tags API
"""

import sys
import requests
import json
from datetime import datetime, date

# Configuração da API
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def get_auth_token():
    """Obter token de autenticação"""
    login_data = {
        "username": "admin",
        "password": "ChangeMe123!"
    }
    
    try:
        response = requests.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Erro ao fazer login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return None

def test_virtual_tags_api(token):
    """Testar endpoints de Virtual Tags"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧪 Testando API de Virtual Tags...")
    
    # 1. Listar Virtual Tags (deve estar vazio inicialmente)
    print("\n1. Listando Virtual Tags...")
    try:
        response = requests.get(f"{API_URL}/virtual-tags/", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            tags = response.json()
            print(f"Tags encontradas: {len(tags)}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 2. Obter campos disponíveis
    print("\n2. Obtendo campos disponíveis...")
    try:
        response = requests.get(f"{API_URL}/virtual-tags/fields/available", headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            fields = response.json()
            print(f"Campos disponíveis: {len(fields)}")
            for field in fields[:3]:  # Mostrar apenas os primeiros 3
                print(f"  - {field['field_name']}: {field['field_type']}")
        else:
            print(f"Erro: {response.text}")
    except Exception as e:
        print(f"Erro: {e}")
    
    # 3. Criar uma Virtual Tag de teste
    print("\n3. Criando Virtual Tag de teste...")
    virtual_tag_data = {
        "name": "Ambiente de Teste",
        "description": "Tag para identificar ambiente de desenvolvimento",
        "category": "environment",
        "priority": 100,
        "default_value": "unknown",
        "rules": [
            {
                "name": "Regra Desenvolvimento",
                "description": "Identifica recursos de desenvolvimento",
                "conditions": [
                    {
                        "field": "resource_name",
                        "operator": "contains",
                        "value": "dev",
                        "case_sensitive": False
                    }
                ],
                "action": {
                    "type": "set_value",
                    "value": "development"
                },
                "priority": 100,
                "logical_operator": "AND"
            }
        ]
    }
    
    try:
        response = requests.post(f"{API_URL}/virtual-tags/", json=virtual_tag_data, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            created_tag = response.json()
            print(f"Tag criada com ID: {created_tag['id']}")
            tag_id = created_tag['id']
            
            # 4. Obter a Virtual Tag criada
            print(f"\n4. Obtendo Virtual Tag {tag_id}...")
            response = requests.get(f"{API_URL}/virtual-tags/{tag_id}", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                tag = response.json()
                print(f"Tag: {tag['name']} - {tag['category']}")
                print(f"Regras: {len(tag['rules'])}")
            
            # 5. Testar preview de alocação
            print(f"\n5. Testando preview de alocação...")
            preview_data = {
                "start_date": "2024-01-01",
                "end_date": "2024-01-31"
            }
            response = requests.post(f"{API_URL}/virtual-tags/{tag_id}/preview", json=preview_data, headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                preview = response.json()
                print(f"Preview gerado com {len(preview)} registros")
            else:
                print(f"Preview: {response.text}")
            
            # 6. Obter métricas do dashboard
            print("\n6. Obtendo métricas do dashboard...")
            response = requests.get(f"{API_URL}/virtual-tags/metrics/dashboard", headers=headers)
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                metrics = response.json()
                print(f"Métricas obtidas: {list(metrics.keys())}")
            else:
                print(f"Métricas: {response.text}")
            
            return tag_id
        else:
            print(f"Erro ao criar tag: {response.text}")
            return None
    except Exception as e:
        print(f"Erro: {e}")
        return None

def test_cleanup(token, tag_id):
    """Limpar dados de teste"""
    if not tag_id:
        return
        
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n🧹 Limpando dados de teste...")
    
    try:
        response = requests.delete(f"{API_URL}/virtual-tags/{tag_id}", headers=headers)
        print(f"Delete status: {response.status_code}")
        if response.status_code == 204:
            print("Virtual Tag de teste removida com sucesso")
        else:
            print(f"Erro ao remover: {response.text}")
    except Exception as e:
        print(f"Erro na limpeza: {e}")

def main():
    """Função principal"""
    print("🚀 Iniciando teste da API Virtual Tags...")
    
    # Obter token de autenticação
    token = get_auth_token()
    if not token:
        print("❌ Falha na autenticação")
        sys.exit(1)
    
    print("✅ Autenticação bem-sucedida")
    
    # Testar API
    tag_id = test_virtual_tags_api(token)
    
    # Limpar dados de teste
    if tag_id:
        test_cleanup(token, tag_id)
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
