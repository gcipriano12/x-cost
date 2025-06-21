#!/usr/bin/env python3
"""
Teste completo da API Virtual Tags
"""

import requests
import json
from datetime import datetime

# Configuração
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0Iiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzUwNDg3MzQ3LCJpYXQiOjE3NTA0ODM3NDcsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.-fZDhyNxXZqOBC1LmYuOOrJKECAF2naaXr8HSGS9qlg"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_endpoint(method, endpoint, data=None):
    """Testa um endpoint"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        print(f"\n{method} {endpoint}")
        print(f"Status: {response.status_code}")
        
        if response.status_code < 400:
            try:
                result = response.json()
                if isinstance(result, list):
                    print(f"Retornou lista com {len(result)} itens")
                    if result:
                        print(f"Primeiro item: {json.dumps(result[0], indent=2, default=str)[:200]}...")
                elif isinstance(result, dict):
                    print(f"Retornou objeto: {json.dumps(result, indent=2, default=str)[:200]}...")
                else:
                    print(f"Resultado: {result}")
            except:
                print(f"Resposta não-JSON: {response.text[:200]}...")
        else:
            print(f"Erro: {response.text}")
        
        return response
    except Exception as e:
        print(f"Erro na requisição: {e}")
        return None

def main():
    print("🚀 TESTANDO API VIRTUAL TAGS")
    print("=" * 50)
    
    # 1. Listar Virtual Tags
    test_endpoint("GET", "/api/v1/virtual-tags/")
    
    # 2. Campos disponíveis
    test_endpoint("GET", "/api/v1/virtual-tags/fields/available")
    
    # 3. Métricas do dashboard
    test_endpoint("GET", "/api/v1/virtual-tags/metrics/dashboard")
    
    # 4. Criar nova Virtual Tag
    new_tag = {
        "name": "Test API Virtual Tag",
        "description": "Tag criada via teste da API",
        "category": "project",
        "priority": 150,
        "rules": [
            {
                "name": "AWS S3 Rule",
                "description": "Identifica recursos S3",
                "conditions": [
                    {
                        "field": "service_name",
                        "operator": "equals",
                        "value": "S3",
                        "case_sensitive": False
                    }
                ],
                "action": {
                    "type": "set_value",
                    "value": "Storage Project"
                },
                "priority": 1
            }
        ]
    }
    
    create_response = test_endpoint("POST", "/api/v1/virtual-tags/", new_tag)
    
    if create_response and create_response.status_code < 400:
        new_tag_data = create_response.json()
        tag_id = new_tag_data["id"]
        
        # 5. Obter Virtual Tag específica
        test_endpoint("GET", f"/api/v1/virtual-tags/{tag_id}")
        
        # 6. Preview de alocação
        preview_data = {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31"
        }
        test_endpoint("POST", f"/api/v1/virtual-tags/{tag_id}/preview", preview_data)
        
        # 7. Atualizar Virtual Tag
        update_data = {
            "name": "Updated Test API Virtual Tag",
            "description": "Tag atualizada via API",
            "category": "project",
            "priority": 200
        }
        test_endpoint("PUT", f"/api/v1/virtual-tags/{tag_id}", update_data)
        
        # 8. Deletar Virtual Tag
        test_endpoint("DELETE", f"/api/v1/virtual-tags/{tag_id}")
    
    print("\n" + "=" * 50)
    print("✅ TESTE COMPLETO DA API VIRTUAL TAGS FINALIZADO")

if __name__ == "__main__":
    main()
