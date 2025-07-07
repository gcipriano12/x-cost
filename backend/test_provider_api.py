#!/usr/bin/env python3
"""
Script para testar a API de provider distribution
"""

import os
import requests
import json

def test_provider_api():
    """Testar API de provider distribution"""
    
    # Token válido
    token = os.environ.get("X_COST_API_TOKEN", "")
        if not token:
            print("⚠️ Configure a variável de ambiente X_COST_API_TOKEN")
            return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧪 TESTE API - Provider Distribution")
    print("=" * 50)
    
    # 1. Teste endpoint /analytics/by-provider
    print("\n1️⃣ Teste /analytics/by-provider:")
    response = requests.get(
        "http://localhost:8000/api/v1/analytics/by-provider",
        headers=headers,
        params={"days": 30}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'provider_breakdown' in data['data']:
            providers = data['data']['provider_breakdown']
            print(f"Providers retornados: {len(providers)}")
            for p in providers:
                print(f"  {p['provider_name']:<15}: ${p['total_cost']:>12,.2f} ({p['percentage_of_total']:>5.1f}%)")
        else:
            print(f"Estrutura inesperada: {json.dumps(data, indent=2)}")
    else:
        print(f"Erro: {response.text}")
    
    # 2. Teste endpoint /dashboard/summary
    print("\n2️⃣ Teste /dashboard/summary:")
    response = requests.get(
        "http://localhost:8000/api/v1/dashboard/summary",
        headers=headers,
        params={"time_filter": "30-days"}
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        provider_dist = data.get('provider_distribution', [])
        print(f"Provider Distribution: {len(provider_dist)} providers")
        for p in provider_dist:
            print(f"  {p['provider_name']:<15}: ${p['total_cost']:>12,.2f} ({p.get('percentage', 0):>5.1f}%)")
            
        # Verificar highlights
        highlights = data.get('highlights')
        print(f"Highlights: {'✓' if highlights else '✗'}")
        if highlights:
            print(f"  - estimated_waste: {highlights.get('estimated_waste', {}).get('amount', 'N/A')}")
            print(f"  - savings_achieved: {highlights.get('savings_achieved', {}).get('amount', 'N/A')}")
            print(f"  - next_month_forecast: {highlights.get('next_month_forecast', {}).get('amount', 'N/A')}")
    else:
        print(f"Erro: {response.text}")

if __name__ == "__main__":
    test_provider_api()