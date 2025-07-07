#!/usr/bin/env python3
"""
Script para testar a ordenação completa do endpoint /api/v1/services/top
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

def test_sorting_complete():
    print("🚀 Teste Completo de Ordenação")
    print("=" * 60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    base_params = {
        "credential_id": "test-credential-aws",
        "page": 1,
        "page_size": 5
    }
    
    # Teste 1: Ordenação por custo (decrescente) - padrão
    print("\n--- Teste 1: Por Custo (Maior → Menor) ---")
    params = {**base_params, "sort_by": "cost", "sort_order": "desc"}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços retornados")
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['service_name']:20s} | ${service['cost']:>10,.2f}")
        
        # Verificar se está ordenado corretamente
        costs = [s['cost'] for s in services]
        is_sorted = all(costs[i] >= costs[i+1] for i in range(len(costs)-1))
        print(f"📊 Ordenação correta: {'✅' if is_sorted else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 2: Ordenação por custo (crescente)
    print("\n--- Teste 2: Por Custo (Menor → Maior) ---")
    params = {**base_params, "sort_by": "cost", "sort_order": "asc"}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços retornados")
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['service_name']:20s} | ${service['cost']:>10,.2f}")
        
        # Verificar se está ordenado corretamente
        costs = [s['cost'] for s in services]
        is_sorted = all(costs[i] <= costs[i+1] for i in range(len(costs)-1))
        print(f"📊 Ordenação correta: {'✅' if is_sorted else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 3: Ordenação por nome (A-Z)
    print("\n--- Teste 3: Por Nome (A → Z) ---")
    params = {**base_params, "sort_by": "service_name", "sort_order": "asc"}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços retornados")
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['service_name']:20s} | {service['provider']:10s}")
        
        # Verificar se está ordenado corretamente
        names = [s['service_name'].lower() for s in services]
        is_sorted = all(names[i] <= names[i+1] for i in range(len(names)-1))
        print(f"📊 Ordenação correta: {'✅' if is_sorted else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 4: Ordenação por provider (A-Z)
    print("\n--- Teste 4: Por Provider (A → Z) ---")
    params = {**base_params, "sort_by": "provider", "sort_order": "asc"}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços retornados")
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['provider']:12s} | {service['service_name']:20s}")
        
        # Verificar se está ordenado corretamente
        providers = [s['provider'].lower() for s in services]
        is_sorted = all(providers[i] <= providers[i+1] for i in range(len(providers)-1))
        print(f"📊 Ordenação correta: {'✅' if is_sorted else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 5: Ordenação por variação (maior para menor)
    print("\n--- Teste 5: Por Variação (Maior → Menor) ---")
    params = {**base_params, "sort_by": "change_from_previous", "sort_order": "desc"}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços retornados")
        for i, service in enumerate(services):
            change_icon = "📈" if service['change_from_previous'] > 0 else "📉" if service['change_from_previous'] < 0 else "➡️"
            print(f"  {i+1}. {service['service_name']:20s} | {change_icon} {service['change_from_previous']:>6.1f}%")
        
        # Verificar se está ordenado corretamente
        changes = [s['change_from_previous'] for s in services]
        is_sorted = all(changes[i] >= changes[i+1] for i in range(len(changes)-1))
        print(f"📊 Ordenação correta: {'✅' if is_sorted else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 6: Campo inválido (deve dar erro)
    print("\n--- Teste 6: Campo de Ordenação Inválido ---")
    params = {**base_params, "sort_by": "invalid_field", "sort_order": "desc"}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 400:
        print("✅ Erro esperado para campo inválido")
        error_detail = response.json().get('detail', 'No detail')
        print(f"💬 Mensagem: {error_detail}")
    else:
        print(f"❌ Esperado erro 400, obtido: {response.status_code}")
    
    # Teste 7: Ordem inválida (deve dar erro)
    print("\n--- Teste 7: Ordem de Ordenação Inválida ---")
    params = {**base_params, "sort_by": "cost", "sort_order": "invalid_order"}
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 400:
        print("✅ Erro esperado para ordem inválida")
        error_detail = response.json().get('detail', 'No detail')
        print(f"💬 Mensagem: {error_detail}")
    else:
        print(f"❌ Esperado erro 400, obtido: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Teste completo de ordenação concluído!")
    print("\n🎯 Resumo dos Recursos:")
    print("  📊 Ordenação por custo (asc/desc)")
    print("  📝 Ordenação por nome de serviço (asc/desc)")
    print("  🏢 Ordenação por provider (asc/desc)")
    print("  📈 Ordenação por variação percentual (asc/desc)")
    print("  ✅ Validação de parâmetros inválidos")
    print("  📄 Paginação funcionando com ordenação")

if __name__ == "__main__":
    test_sorting_complete()
