#!/usr/bin/env python3
"""
Script para testar os endpoints corrigidos do Oracle Cloud com token de autenticação
"""

import requests
import json
from datetime import date, timedelta

# Token fornecido pelo usuário (atualizado)
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUxOTQyMTQ4LCJpYXQiOjE3NTE4NTU3NDgsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.xM9WaQz1EbKedpVUzgicCqaiodPuBvxkiLYMOJjN9uc"

# Base URL da API
BASE_URL = "http://localhost:8000"

# Headers com autenticação
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_dashboard_summary():
    """Testar o endpoint dashboard summary"""
    print("🏠 TESTANDO DASHBOARD SUMMARY")
    print("=" * 50)
    
    # Período de teste (baseado nos dados do debug - com dados Oracle)
    end_date = date(2025, 7, 6)
    start_date = date(2025, 6, 6)
    
    tests = [
        {
            "name": "Summary ALL (sem filtro)",
            "url": f"{BASE_URL}/api/v1/dashboard/summary",
            "params": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        },
        {
            "name": "Summary Oracle Cloud (com filtro)",
            "url": f"{BASE_URL}/api/v1/dashboard/summary",
            "params": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "provider_name": "Oracle Cloud"
            }
        }
    ]
    
    for test in tests:
        print(f"\n🧪 {test['name']}:")
        try:
            response = requests.get(test["url"], headers=HEADERS, params=test["params"])
            
            print(f"   Status: {response.status_code}")
            print(f"   URL: {response.url}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Raw response keys: {list(data.keys())}")
                print(f"   Total Cost: ${data.get('cost_summary', {}).get('totals', {}).get('total_cost', 0):,.2f}")
                
                # Analisar distribuição de provedores
                provider_distribution = data.get('provider_distribution', [])
                print(f"   Providers na distribuição: {len(provider_distribution)}")
                
                oracle_in_distribution = [p for p in provider_distribution if 'Oracle' in p.get('provider', '')]
                if oracle_in_distribution:
                    print("   🎯 Oracle Cloud encontrado na distribuição:")
                    for p in oracle_in_distribution:
                        print(f"      - {p.get('provider')}: ${p.get('cost', 0):,.2f} ({p.get('percentage', 0):.1f}%)")
                else:
                    print("   ❌ Oracle Cloud NÃO encontrado na distribuição")
                
                # Mostrar top 3 providers
                if provider_distribution:
                    print("   📊 Top 3 providers:")
                    for i, p in enumerate(provider_distribution[:3], 1):
                        print(f"      {i}. {p.get('provider')}: ${p.get('cost', 0):,.2f}")
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            import traceback
            traceback.print_exc()

def test_analytics_by_provider():
    """Testar o endpoint analytics by provider (corrigido)"""
    print("\n📊 TESTANDO ANALYTICS BY PROVIDER")
    print("=" * 50)
    
    # Período de teste (baseado nos dados do debug - com dados Oracle)
    end_date = date(2025, 7, 6)
    start_date = date(2025, 6, 6)
    
    tests = [
        {
            "name": "Analytics ALL (sem filtro)",
            "url": f"{BASE_URL}/api/v1/analytics/by-provider",
            "params": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            }
        },
        {
            "name": "Analytics Oracle Cloud (com filtro)",
            "url": f"{BASE_URL}/api/v1/analytics/by-provider",
            "params": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "provider_name": "Oracle Cloud"
            }
        }
    ]
    
    for test in tests:
        print(f"\n🧪 {test['name']}:")
        try:
            response = requests.get(test["url"], headers=HEADERS, params=test["params"])
            
            print(f"   Status: {response.status_code}")
            print(f"   URL: {response.url}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Raw response keys: {list(data.keys())}")
                
                providers = data.get('data', {}).get('provider_breakdown', [])
                
                print(f"   Total de providers retornados: {len(providers)}")
                
                # Mostrar todos os providers
                for provider in providers:
                    print(f"      - {provider.get('provider_name')}: ${provider.get('total_cost', 0):,.2f}")
                
                # Verificar se Oracle está presente
                oracle_providers = [p for p in providers if 'Oracle' in p.get('provider_name', '')]
                if oracle_providers:
                    print("   ✅ Oracle Cloud encontrado no resultado!")
                else:
                    print("   ❌ Oracle Cloud NÃO encontrado no resultado")
                    
            else:
                print(f"   ❌ Erro: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Exceção: {e}")
            import traceback
            traceback.print_exc()

def test_cost_trends():
    """Testar outros endpoints relacionados para comparação"""
    print("\n📈 TESTANDO OUTROS ENDPOINTS PARA COMPARAÇÃO")
    print("=" * 50)
    
    # Período de teste (baseado nos dados do debug - com dados Oracle)
    end_date = date(2025, 7, 6)
    start_date = date(2025, 6, 6)
    
    # Testar top services
    print("\n🧪 Top Services Oracle Cloud:")
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/top-services",
            headers=HEADERS,
            params={
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "provider_name": "Oracle Cloud",
                "limit": 5
            }
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            services = data.get('services', [])
            print(f"   Total de serviços Oracle: {len(services)}")
            
            for service in services:
                print(f"      - {service.get('service_name')}: ${service.get('cost', 0):,.2f}")
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Exceção: {e}")

def main():
    """Função principal"""
    print("🔍 TESTE DOS ENDPOINTS ORACLE CLOUD COM TOKEN")
    print("=" * 60)
    print(f"Token: {TOKEN[:20]}...")
    print(f"Base URL: {BASE_URL}")
    
    # Executar testes
    test_dashboard_summary()
    test_analytics_by_provider()
    test_cost_trends()
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO DOS TESTES:")
    print("1. Verifique se o Oracle Cloud aparece na distribuição do dashboard")
    print("2. Confirme se o filtro by-provider funciona corretamente")
    print("3. Valide se os custos estão consistentes entre endpoints")
    print("4. Teste se o frontend consegue consumir essas respostas")

if __name__ == "__main__":
    main()
