#!/usr/bin/env python3
"""
Teste completo da paginação - cenários avançados
"""

import requests
import json

# Configuração
BASE_URL = "http://localhost:8000"
USERNAME = "finops_admin"  
PASSWORD = "Password123!"

def get_token():
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        json={"username": USERNAME, "password": PASSWORD}
    )
    return response.json()["access_token"]

def test_advanced_pagination():
    print("🚀 Teste Avançado de Paginação")
    print("=" * 50)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste 1: Page size máximo (100)
    print("\n--- Teste 1: Page size máximo (100) ---")
    params = {"credential_id": "test-credential-aws", "page": 1, "page_size": 100}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Consegue listar todos os {len(data['data']['services'])} serviços em uma página")
        print(f"📊 Total: {data['data']['total_services']} serviços")
        print(f"📚 Páginas: {data['data']['pagination']['total_pages']}")
    else:
        print(f"❌ Erro: {response.status_code}")
    
    # Teste 2: Page size mínimo (1)
    print("\n--- Teste 2: Page size mínimo (1) ---")
    params = {"credential_id": "test-credential-aws", "page": 1, "page_size": 1}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        total_pages = data['data']['pagination']['total_pages']
        print(f"✅ Com page_size=1, temos {total_pages} páginas")
        print(f"🏆 Serviço #1: {data['data']['services'][0]['service_name']} - ${data['data']['services'][0]['cost']:,.2f}")
    else:
        print(f"❌ Erro: {response.status_code}")
    
    # Teste 3: Navegação sequencial
    print("\n--- Teste 3: Navegação sequencial (páginas 1-5) ---")
    for page in range(1, 6):
        params = {"credential_id": "test-credential-aws", "page": page, "page_size": 5}
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            pagination = data['data']['pagination']
            print(f"📄 Página {page}: {len(data['data']['services'])} serviços")
            print(f"   ◀️ Tem anterior: {pagination['has_previous']}")
            print(f"   ▶️ Tem próxima: {pagination['has_next']}")
        else:
            print(f"❌ Erro na página {page}: {response.status_code}")
    
    # Teste 4: Filtro por provider com paginação
    print("\n--- Teste 4: Filtro por provider (AWS) com paginação ---")
    params = {"credential_id": "test-credential-aws", "provider_name": "AWS", "page": 1, "page_size": 10}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Serviços AWS: {data['data']['total_services']} encontrados")
        print(f"📚 Páginas: {data['data']['pagination']['total_pages']}")
        
        aws_services = [s for s in data['data']['services'] if s['provider'] == 'AWS']
        print(f"🔍 Serviços AWS nesta página: {len(aws_services)}")
        
        for service in aws_services[:3]:
            print(f"   • {service['service_name']} - ${service['cost']:,.2f}")
    else:
        print(f"❌ Erro: {response.status_code}")
    
    # Teste 5: Página inexistente
    print("\n--- Teste 5: Página inexistente (999) ---")
    params = {"credential_id": "test-credential-aws", "page": 999, "page_size": 10}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Página 999: {len(data['data']['services'])} serviços (provavelmente 0)")
        print(f"📄 Página retornada: {data['data']['pagination']['page']}")
    else:
        print(f"⚠️ Status: {response.status_code} (esperado para página inexistente)")
    
    print("\n" + "=" * 50)
    print("✅ Teste avançado de paginação concluído!")

if __name__ == "__main__":
    test_advanced_pagination()
