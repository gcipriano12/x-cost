#!/usr/bin/env python3
"""
Script para testar a paginação do endpoint /api/v1/services/top
"""

import requests
import json
from datetime import datetime, date, timedelta

# Configuração
BASE_URL = "http://localhost:8000"
USERNAME = "finops_admin"
PASSWORD = "Password123!"

def get_auth_token():
    """Obter token de autenticação"""
    print("🔐 Fazendo login...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        json={"username": USERNAME, "password": PASSWORD}
    )
    
    if response.status_code != 200:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"Resposta: {response.text}")
        return None
    
    token_data = response.json()
    print(f"✅ Login realizado com sucesso!")
    return token_data["access_token"]

def test_pagination(token):
    """Testar paginação do endpoint top services"""
    print("\n📊 Testando paginação do endpoint /api/v1/services/top")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Parâmetros base
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Teste 1: Primeira página com page_size=3
    print("\n--- Teste 1: Página 1 com 3 itens ---")
    params = {
        "credential_id": "test-credential-aws",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "page": 1,
        "page_size": 3
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Página: {data['data']['pagination']['page']}")
        print(f"📊 Total de serviços: {data['data']['total_services']}")
        print(f"📦 Itens por página: {data['data']['pagination']['page_size']}")
        print(f"📚 Total de páginas: {data['data']['pagination']['total_pages']}")
        print(f"🔍 Serviços nesta página: {len(data['data']['services'])}")
        
        # Mostrar alguns serviços
        for i, service in enumerate(data['data']['services'][:3]):
            print(f"  {i+1}. {service['service_name']} ({service['provider']}) - ${service['cost']:,.2f}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")
        return
    
    # Teste 2: Segunda página
    print("\n--- Teste 2: Página 2 com 3 itens ---")
    params["page"] = 2
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📄 Página: {data['data']['pagination']['page']}")
        print(f"🔍 Serviços nesta página: {len(data['data']['services'])}")
        
        # Mostrar alguns serviços
        for i, service in enumerate(data['data']['services'][:3]):
            print(f"  {i+1}. {service['service_name']} ({service['provider']}) - ${service['cost']:,.2f}")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")
        return
    
    # Teste 3: Page size maior para ver mais dados
    print("\n--- Teste 3: Página 1 com 10 itens ---")
    params = {
        "credential_id": "test-credential-aws",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "page": 1,
        "page_size": 10
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Status: {response.status_code}")
        print(f"📊 Total de serviços únicos: {data['data']['total_services']}")
        print(f"📚 Total de páginas: {data['data']['pagination']['total_pages']}")
        print(f"🔍 Serviços nesta página: {len(data['data']['services'])}")
        
        print(f"\n🏆 Top 5 serviços com maior custo:")
        for i, service in enumerate(data['data']['services'][:5]):
            change_icon = "📈" if service['change_from_previous'] > 0 else "📉" if service['change_from_previous'] < 0 else "➡️"
            print(f"  {i+1}. {service['service_name']} ({service['provider']})")
            print(f"     💰 ${service['cost']:,.2f} | {change_icon} {service['change_from_previous']:+.1f}%")
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")
    
    # Teste 4: Verificar se conseguimos navegar por todas as páginas
    if response.status_code == 200:
        total_pages = data['data']['pagination']['total_pages']
        total_services = data['data']['total_services']
        
        print(f"\n--- Teste 4: Navegação completa ---")
        print(f"📚 Total de páginas: {total_pages}")
        print(f"📊 Total de serviços: {total_services}")
        
        # Teste da última página
        if total_pages > 1:
            print(f"\n🔍 Testando última página ({total_pages})...")
            params["page"] = total_pages
            
            response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Última página acessível!")
                print(f"🔍 Serviços na última página: {len(data['data']['services'])}")
            else:
                print(f"❌ Erro ao acessar última página: {response.status_code}")

def main():
    print("🚀 Testando paginação do endpoint Top Services")
    print("=" * 60)
    
    # Obter token
    token = get_auth_token()
    if not token:
        print("❌ Não foi possível obter token de autenticação")
        return
    
    # Testar paginação
    test_pagination(token)
    
    print("\n" + "=" * 60)
    print("✅ Teste de paginação concluído!")

if __name__ == "__main__":
    main()
