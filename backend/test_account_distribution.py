#!/usr/bin/env python3
"""
Script para testar o endpoint account-distribution existente
"""

import requests
import json

# Token válido
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUxOTQyMTQ4LCJpYXQiOjE3NTE4NTU3NDgsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.xM9WaQz1EbKedpVUzgicCqaiodPuBvxkiLYMOJjN9uc"

BASE_URL = "http://localhost:8000"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_account_distribution():
    """Testar endpoint account-distribution"""
    
    print("🧪 TESTANDO ENDPOINT ACCOUNT-DISTRIBUTION")
    print("=" * 60)
    
    tests = [
        {
            "name": "Oracle Cloud (nome exato)",
            "params": {
                "provider": "Oracle Cloud",
                "time_filter": "30d"
            }
        },
        {
            "name": "Oracle (nome normalizado)",
            "params": {
                "provider": "Oracle",
                "time_filter": "30d"
            }
        },
        {
            "name": "AWS (comparação)",
            "params": {
                "provider": "AWS",
                "time_filter": "30d"
            }
        }
    ]
    
    for test in tests:
        print(f"\n🔍 Teste: {test['name']}")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/dashboard/account-distribution",
                headers=HEADERS,
                params=test["params"]
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   URL: {response.url}")
            
            if response.status_code == 200:
                data = response.json()
                
                if 'data' in data:
                    accounts = data['data']
                    print(f"   ✅ Contas encontradas: {len(accounts)}")
                    
                    total_percentage = 0
                    for account in accounts:
                        print(f"      - {account['billing_account_name']}")
                        print(f"        ID: {account['account_id']}")
                        print(f"        Custo: ${account['total_cost']:,.2f}")
                        print(f"        Percentual: {account['percentage']:.1f}%")
                        total_percentage += account['percentage']
                    
                    print(f"   📊 Total percentual: {total_percentage:.1f}%")
                else:
                    print(f"   📄 Resposta: {data}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")

if __name__ == "__main__":
    test_account_distribution()
