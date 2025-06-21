#!/usr/bin/env python3
"""
Teste simples para debug da API Virtual Tags
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"

def get_token():
    login_data = {"username": "admin", "password": "ChangeMe123!"}
    response = requests.post(f"{API_URL}/auth/login", json=login_data)
    return response.json()["access_token"]

def test_minimal_creation():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Virtual Tag mínima sem regras
    minimal_tag = {
        "name": "Test Tag",
        "category": "environment",
        "priority": 100,
        "rules": []
    }
    
    print("Testando criação de Virtual Tag mínima...")
    response = requests.post(f"{API_URL}/virtual-tags/", json=minimal_tag, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 201:
        tag_id = response.json()["id"]
        print(f"✅ Tag criada com ID: {tag_id}")
        
        # Limpar
        delete_response = requests.delete(f"{API_URL}/virtual-tags/{tag_id}", headers=headers)
        print(f"Delete status: {delete_response.status_code}")
    else:
        print("❌ Erro na criação")

if __name__ == "__main__":
    test_minimal_creation()
