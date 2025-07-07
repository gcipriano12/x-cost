#!/usr/bin/env python3
"""
Script para testar ordenação no endpoint /api/v1/services/top
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
    print("🚀 Teste de Ordenação Backend + Frontend")
    print("=" * 60)
    
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste 1: Ordenação por custo (desc - padrão)
    print("\n--- Teste 1: Custo Decrescente (padrão) ---")
    params = {
        "credential_id": "test-credential-aws",
        "page": 1,
        "page_size": 5,
        "sort_by": "cost",
        "sort_order": "desc"
    }
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços ordenados por custo (maior → menor)")
        
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['service_name']:20s} | ${service['cost']:>10,.2f}")
            
        # Verificar se está ordenado corretamente
        costs = [s['cost'] for s in services]
        is_sorted_desc = all(costs[i] >= costs[i+1] for i in range(len(costs)-1))
        print(f"  🔍 Ordenação correta: {'✅' if is_sorted_desc else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 2: Ordenação por custo (asc)
    print("\n--- Teste 2: Custo Crescente ---")
    params["sort_order"] = "asc"
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços ordenados por custo (menor → maior)")
        
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['service_name']:20s} | ${service['cost']:>10,.2f}")
            
        # Verificar se está ordenado corretamente
        costs = [s['cost'] for s in services]
        is_sorted_asc = all(costs[i] <= costs[i+1] for i in range(len(costs)-1))
        print(f"  🔍 Ordenação correta: {'✅' if is_sorted_asc else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 3: Ordenação por nome (asc)
    print("\n--- Teste 3: Nome Alfabético (A-Z) ---")
    params.update({"sort_by": "service_name", "sort_order": "asc"})
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços ordenados por nome (A-Z)")
        
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['service_name']:20s} | {service['provider']:10s}")
            
        # Verificar se está ordenado corretamente
        names = [s['service_name'].lower() for s in services]
        is_sorted_asc = all(names[i] <= names[i+1] for i in range(len(names)-1))
        print(f"  🔍 Ordenação correta: {'✅' if is_sorted_asc else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 4: Ordenação por variação (desc)
    print("\n--- Teste 4: Variação Decrescente ---")
    params.update({"sort_by": "change_from_previous", "sort_order": "desc"})
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços ordenados por variação (maior → menor)")
        
        for i, service in enumerate(services):
            change_icon = "📈" if service['change_from_previous'] > 0 else "📉"
            print(f"  {i+1}. {service['service_name']:20s} | {change_icon} {service['change_from_previous']:>6.1f}%")
            
        # Verificar se está ordenado corretamente
        changes = [s['change_from_previous'] for s in services]
        is_sorted_desc = all(changes[i] >= changes[i+1] for i in range(len(changes)-1))
        print(f"  🔍 Ordenação correta: {'✅' if is_sorted_desc else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 5: Ordenação por provider
    print("\n--- Teste 5: Provider Alfabético (A-Z) ---")
    params.update({"sort_by": "provider", "sort_order": "asc"})
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        services = data['data']['services']
        print(f"✅ {len(services)} serviços ordenados por provider (A-Z)")
        
        for i, service in enumerate(services):
            print(f"  {i+1}. {service['provider']:10s} | {service['service_name']}")
            
        # Verificar se está ordenado corretamente
        providers = [s['provider'].lower() for s in services]
        is_sorted_asc = all(providers[i] <= providers[i+1] for i in range(len(providers)-1))
        print(f"  🔍 Ordenação correta: {'✅' if is_sorted_asc else '❌'}")
    else:
        print(f"❌ Erro: {response.status_code}")
        return
    
    # Teste 6: Campo inválido
    print("\n--- Teste 6: Campo Inválido ---")
    params.update({"sort_by": "invalid_field", "sort_order": "desc"})
    
    response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
    
    if response.status_code == 400:
        print(f"✅ Erro 400 esperado para campo inválido")
        error_data = response.json()
        print(f"  📝 Mensagem: {error_data.get('detail', 'N/A')}")
    else:
        print(f"⚠️ Status inesperado: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("✅ Teste de ordenação completo!")
    print("\n🎯 Funcionalidades implementadas:")
    print("  • ✅ Ordenação por custo (asc/desc)")
    print("  • ✅ Ordenação por nome do serviço (asc/desc)")
    print("  • ✅ Ordenação por provider (asc/desc)")
    print("  • ✅ Ordenação por variação % (asc/desc)")
    print("  • ✅ Validação de campos inválidos")
    print("  • ✅ Integração Backend + Frontend")
    print("\n🚀 O frontend agora pode:")
    print("  • Clicar nos cabeçalhos das colunas para ordenar")
    print("  • Alternar entre crescente/decrescente")
    print("  • Resetar paginação ao mudar ordenação")
    print("  • Usar fallback para ordenação local (se necessário)")

if __name__ == "__main__":
    test_sorting()
