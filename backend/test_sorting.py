#!/usr/bin/env python3
"""
Script para testar a ordenação no endpoint /api/v1/services/top
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

def test_sorting():
    print("🚀 Teste de Ordenação no Frontend")
    print("=" * 50)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Buscar dados para verificar se a ordenação frontend funcionará
    print("\n--- Dados para Ordenação ---")
    params = {"credential_id": "test-credential-aws", "page": 1, "page_size": 10}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        
        print(f"✅ {len(services)} serviços obtidos do backend")
        print("\n📊 Dados dos serviços (para verificar ordenação frontend):")
        
        for i, service in enumerate(services):
            print(f"  {i+1:2d}. {service['service_name']:20s} | {service['provider']:10s} | ${service['cost']:>10,.2f} | {service['change_from_previous']:>6.1f}%")
        
        # Simular ordenações que o frontend fará
        print("\n🔄 Simulação de Ordenações Frontend:")
        
        # 1. Por nome (A-Z)
        sorted_by_name = sorted(services, key=lambda x: x['service_name'].lower())
        print(f"\n📝 Por Nome (A-Z) - Primeiros 5:")
        for i, service in enumerate(sorted_by_name[:5]):
            print(f"  {i+1}. {service['service_name']} (${service['cost']:,.2f})")
        
        # 2. Por custo (maior para menor)
        sorted_by_cost_desc = sorted(services, key=lambda x: x['cost'], reverse=True)
        print(f"\n💰 Por Custo (Maior → Menor) - Top 5:")
        for i, service in enumerate(sorted_by_cost_desc[:5]):
            print(f"  {i+1}. {service['service_name']} - ${service['cost']:,.2f}")
        
        # 3. Por custo (menor para maior)
        sorted_by_cost_asc = sorted(services, key=lambda x: x['cost'])
        print(f"\n💸 Por Custo (Menor → Maior) - Bottom 5:")
        for i, service in enumerate(sorted_by_cost_asc[:5]):
            print(f"  {i+1}. {service['service_name']} - ${service['cost']:,.2f}")
        
        # 4. Por variação (maior para menor)
        sorted_by_trend_desc = sorted(services, key=lambda x: x['change_from_previous'], reverse=True)
        print(f"\n📈 Por Variação (Maior → Menor) - Top 5:")
        for i, service in enumerate(sorted_by_trend_desc[:5]):
            print(f"  {i+1}. {service['service_name']} - {service['change_from_previous']:+.1f}%")
        
        # 5. Por provider
        sorted_by_provider = sorted(services, key=lambda x: x['provider'].lower())
        print(f"\n🏢 Por Provider (A-Z) - Primeiros 5:")
        for i, service in enumerate(sorted_by_provider[:5]):
            print(f"  {i+1}. {service['provider']} - {service['service_name']}")
        
        print(f"\n✅ Frontend terá {len(services)} itens para ordenar em tempo real!")
        print("🎯 Ordenação será instantânea no lado do cliente")
        
    else:
        print(f"❌ Erro: {response.status_code}")
        print(f"Resposta: {response.text}")

if __name__ == "__main__":
    test_sorting()
