#!/usr/bin/env python3
"""
Teste simples da paginação do endpoint Top Services
"""

import requests
import json
from datetime import date, timedelta

# Configurações
BASE_URL = "http://localhost:8000"

def get_fresh_token():
    """Obter token fresh via login"""
    print("🔐 Obtendo token de autenticação...")
    
    login_data = {
        "username": "admin",
        "password": "ChangeMe123!"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json().get("data", {}).get("access_token")
        print("✅ Token obtido com sucesso!")
        return token
    else:
        print(f"❌ Erro ao obter token: {response.status_code}")
        print(f"   Resposta: {response.text}")
        return None

def test_pagination():
    """Testar paginação do endpoint"""
    
    print("\n🔄 TESTANDO PAGINAÇÃO DO ENDPOINT TOP SERVICES")
    print("=" * 60)
    
    # Obter token
    token = get_fresh_token()
    if not token:
        print("❌ Não foi possível obter token, abortando teste")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Teste 1: Primeira página com 3 itens
    print("\n1️⃣ Teste: Primeira página (3 itens)")
    params = {
        "credential_id": "oracle-primary",
        "page": 1,
        "page_size": 3
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pagination = data['data']['pagination']
            services = data['data']['services']
            
            print(f"   ✅ Sucesso! {len(services)} serviços retornados")
            print(f"   📄 Página: {pagination['page']}/{pagination['total_pages']}")
            print(f"   📊 Total de itens: {pagination['total_items']}")
            print(f"   ➡️  Próxima página: {'Sim' if pagination['has_next'] else 'Não'}")
            print(f"   ⬅️  Página anterior: {'Sim' if pagination['has_previous'] else 'Não'}")
            
            print("\n   🏆 Serviços da página 1:")
            for i, service in enumerate(services, 1):
                print(f"      {i}. {service['service_name']} ({service['provider']}) - ${service['cost']:,.2f}")
        else:
            print(f"   ❌ Erro: {response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Exceção: {str(e)}")
        return
    
    # Teste 2: Segunda página
    if data['data']['pagination']['has_next']:
        print("\n2️⃣ Teste: Segunda página (3 itens)")
        params['page'] = 2
        
        try:
            response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                pagination = data['data']['pagination']
                services = data['data']['services']
                
                print(f"   ✅ Sucesso! {len(services)} serviços retornados")
                print(f"   📄 Página: {pagination['page']}/{pagination['total_pages']}")
                print(f"   ➡️  Próxima página: {'Sim' if pagination['has_next'] else 'Não'}")
                print(f"   ⬅️  Página anterior: {'Sim' if pagination['has_previous'] else 'Não'}")
                
                print("\n   🏆 Serviços da página 2:")
                for i, service in enumerate(services, 1):
                    print(f"      {i}. {service['service_name']} ({service['provider']}) - ${service['cost']:,.2f}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {str(e)}")
    
    # Teste 3: Página com mais itens (10)
    print("\n3️⃣ Teste: Primeira página com 10 itens")
    params = {
        "credential_id": "oracle-primary",
        "page": 1,
        "page_size": 10
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pagination = data['data']['pagination']
            services = data['data']['services']
            
            print(f"   ✅ Sucesso! {len(services)} serviços retornados")
            print(f"   📄 Página: {pagination['page']}/{pagination['total_pages']}")
            print(f"   📊 Total de itens: {pagination['total_items']}")
            print(f"   📏 Itens por página: {pagination['page_size']}")
            
            print("\n   🏆 Top 10 serviços:")
            for i, service in enumerate(services, 1):
                print(f"      {i:2d}. {service['service_name']:20} ({service['provider']:15}) - ${service['cost']:>10,.2f}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {str(e)}")
    
    print("\n🎉 Testes de paginação concluídos!")

if __name__ == "__main__":
    test_pagination()
