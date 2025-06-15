#!/usr/bin/env python3
"""
Teste do endpoint de distribuição por categorias
"""

import requests
import json

def test_category_endpoint():
    """Testa o endpoint de distribuição por categorias"""
    
    # Login para obter token
    login_response = requests.post(
        "http://localhost:8000/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        json={"username": "admin", "password": "ChangeMe123!"}
    )
    
    if login_response.status_code != 200:
        print("❌ Falha no login")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Teste 1: Dados de 2024 (ano anterior)
    print("🧪 Testando endpoint com dados de 2024...")
    response = requests.get(
        "http://localhost:8000/api/v1/analytics/by-category",
        headers=headers,
        params={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "top_n": 8
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Endpoint funcionando!")
        print(f"📊 Categorias encontradas: {len(data['category_breakdown'])}")
        print(f"💰 Custo total: ${data['total_cost']:,.2f}")
        
        print("\n📈 Distribuição por categorias:")
        for category in data['category_breakdown']:
            print(f"  • {category['name']}: ${category['total_cost']:,.2f} ({category['percentage']:.1f}%)")
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")
    
    # Teste 2: Dados dos últimos 30 dias
    print("\n🧪 Testando endpoint com últimos 30 dias...")
    response = requests.get(
        "http://localhost:8000/api/v1/analytics/by-category",
        headers=headers,
        params={"days": 30, "top_n": 5}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Últimos 30 dias: {len(data['category_breakdown'])} categorias")
        print(f"💰 Custo total: ${data['total_cost']:,.2f}")
    else:
        print(f"❌ Erro {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_category_endpoint()
