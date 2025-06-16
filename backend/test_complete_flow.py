#!/usr/bin/env python3
"""
Script para testar se o processo completo de login -> API está funcionando
"""

import requests
import json

def test_complete_flow():
    """Testa o fluxo completo de autenticação e acesso à API"""
    
    base_url = "http://localhost:8000"
    
    print("🔐 Testando fluxo de autenticação...")
    
    # 1. Fazer login
    login_data = {
        "username": "admin",
        "password": "ChangeMe123!"
    }
    
    print("🚀 Fazendo login...")
    login_response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if login_response.status_code != 200:
        print(f"❌ Erro no login: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    login_result = login_response.json()
    access_token = login_result.get("access_token")
    
    if not access_token:
        print(f"❌ Token não encontrado na resposta: {login_result}")
        return False
    
    print(f"✅ Login realizado com sucesso!")
    print(f"Token: {access_token[:20]}...")
    
    # 2. Testar endpoints de otimização
    headers = {"Authorization": f"Bearer {access_token}"}
    
    print("\n📊 Testando endpoint de anomalias...")
    anomalies_response = requests.get(
        f"{base_url}/api/v1/anomalies?page=1&per_page=5",
        headers=headers
    )
    
    if anomalies_response.status_code != 200:
        print(f"❌ Erro ao buscar anomalias: {anomalies_response.status_code}")
        print(f"Response: {anomalies_response.text}")
        return False
    
    anomalies_data = anomalies_response.json()
    print(f"✅ Anomalias: {len(anomalies_data.get('anomalies', []))} encontradas")
    print(f"Total count: {anomalies_data.get('total_count', 0)}")
    
    # 3. Testar endpoint de savings
    print("\n💰 Testando endpoint de savings...")
    savings_response = requests.get(
        f"{base_url}/api/v1/savings-opportunities?page=1&per_page=5",
        headers=headers
    )
    
    if savings_response.status_code != 200:
        print(f"❌ Erro ao buscar savings: {savings_response.status_code}")
        print(f"Response: {savings_response.text}")
        return False
    
    savings_data = savings_response.json()
    print(f"✅ Savings: {len(savings_data.get('opportunities', []))} encontradas")
    print(f"Total count: {savings_data.get('total_count', 0)}")
    
    # 4. Testar endpoint de summary
    print("\n📈 Testando endpoint de summary...")
    summary_response = requests.get(
        f"{base_url}/api/v1/optimization/summary",
        headers=headers
    )
    
    if summary_response.status_code != 200:
        print(f"❌ Erro ao buscar summary: {summary_response.status_code}")
        print(f"Response: {summary_response.text}")
        return False
    
    summary_data = summary_response.json()
    print(f"✅ Summary obtido: {type(summary_data)}")
    print(f"Keys: {list(summary_data.keys()) if isinstance(summary_data, dict) else 'Not a dict'}")
    
    return True

if __name__ == "__main__":
    success = test_complete_flow()
    if success:
        print("\n🎉 Todos os testes passaram! O backend está funcionando corretamente.")
        print("🔍 Se o frontend não está funcionando, pode ser:")
        print("   - Problema no token localStorage")
        print("   - Erro no código do frontend")
        print("   - Cache do navegador")
    else:
        print("\n💥 Algum teste falhou!")
