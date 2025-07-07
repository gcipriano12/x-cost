#!/usr/bin/env python3
"""
Script simples para testar a resposta do endpoint top services
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:8000"
USERNAME = "finops_admin"
PASSWORD = "Password123!"

def main():
    print("🔐 Fazendo login...")
    
    # Login
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return
    
    token = response.json()["access_token"]
    print("✅ Login realizado com sucesso!")
    
    # Testar endpoint
    print("📊 Testando endpoint /api/v1/services/top...")
    
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "credential_id": "test-credential-aws",
        "page": 1,
        "page_size": 3
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Sucesso!")
        print("\n📋 Estrutura da resposta:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")

if __name__ == "__main__":
    main()
