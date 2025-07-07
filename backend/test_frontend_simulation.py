#!/usr/bin/env python3
"""
Script para testar exatamente como o frontend chama a API
"""

import requests
import json
from datetime import date, timedelta

# Token fornecido
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUxODU2ODg3LCJpYXQiOjE3NTE4NTMyODcsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.bok6-YKFZqVmN-SzfxNn0p6W0d7gSUEWEyhVkk6itoA"

def test_frontend_calls():
    """Simular exatamente as chamadas do frontend"""
    
    print("🌐 SIMULANDO CHAMADAS DO FRONTEND")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Calcular período de 90 dias como o frontend faria
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    print(f"📅 Período: {start_date} a {end_date} (90 dias)")
    
    # Teste 1: All providers (como primeira imagem)
    print("\n1️⃣ Teste: All providers (equivalente ao filtro 'All')")
    params_all = {
        "credential_id": "test-credential",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "limit": 10
        # Sem provider_name = All
    }
    
    try:
        response = requests.get(f"{base_url}/api/v1/services/top", headers=headers, params=params_all)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            services = data['data']['services']
            oracle_services = [s for s in services if 'Oracle' in s['provider']]
            
            print(f"   ✅ Total de serviços: {len(services)}")
            print(f"   🎯 Serviços Oracle encontrados: {len(oracle_services)}")
            
            print(f"   📊 Top serviços:")
            for i, service in enumerate(services[:5], 1):
                oracle_indicator = "🔥" if 'Oracle' in service['provider'] else "  "
                print(f"      {oracle_indicator} {i}. {service['service_name']} ({service['provider']}): ${service['cost']:,.2f}")
            
            if oracle_services:
                print(f"\n   🎯 Detalhes dos serviços Oracle:")
                for service in oracle_services:
                    print(f"      - {service['service_name']}: ${service['cost']:,.2f} ({service['change_from_previous']:+.1f}%)")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 2: Oracle Cloud específico (como segunda imagem)
    print("\n2️⃣ Teste: Oracle Cloud específico")
    params_oracle = {
        "credential_id": "test-credential",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "provider_name": "Oracle Cloud",
        "limit": 10
    }
    
    try:
        response = requests.get(f"{base_url}/api/v1/services/top", headers=headers, params=params_oracle)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            services = data['data']['services']
            
            print(f"   ✅ Serviços Oracle Cloud: {len(services)}")
            
            if services:
                print(f"   📊 Serviços Oracle Cloud encontrados:")
                for i, service in enumerate(services, 1):
                    print(f"      {i}. {service['service_name']}: ${service['cost']:,.2f} ({service['change_from_previous']:+.1f}%)")
            else:
                print(f"   ❌ PROBLEMA: Nenhum serviço Oracle Cloud encontrado!")
                print(f"   📋 Dados da resposta: {data}")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 3: Verificar diferentes períodos
    print("\n3️⃣ Teste: Diferentes períodos para Oracle Cloud")
    
    test_periods = [
        ("30 dias", 30),
        ("60 dias", 60),
        ("90 dias", 90),
        ("120 dias", 120)
    ]
    
    for period_name, days in test_periods:
        test_end = date.today()
        test_start = test_end - timedelta(days=days)
        
        params = {
            "credential_id": "test-credential",
            "start_date": test_start.isoformat(),
            "end_date": test_end.isoformat(),
            "provider_name": "Oracle Cloud",
            "limit": 5
        }
        
        try:
            response = requests.get(f"{base_url}/api/v1/services/top", headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                services_count = len(data['data']['services'])
                total_services = data['data']['total_services']
                
                print(f"   📅 {period_name}: {services_count} serviços retornados (total: {total_services})")
                
                if services_count > 0:
                    top_service = data['data']['services'][0]
                    print(f"      🏆 Top: {top_service['service_name']} - ${top_service['cost']:,.2f}")
            else:
                print(f"   📅 {period_name}: Erro {response.status_code}")
        
        except Exception as e:
            print(f"   📅 {period_name}: Erro - {e}")
    
    # Teste 4: Verificar se o problema está no período específico
    print("\n4️⃣ Teste: Verificar range de datas dos dados Oracle")
    
    # Testar com período mais amplo
    extended_start = date(2025, 3, 1)  # Março
    extended_end = date.today()
    
    params_extended = {
        "credential_id": "test-credential",
        "start_date": extended_start.isoformat(),
        "end_date": extended_end.isoformat(),
        "provider_name": "Oracle Cloud",
        "limit": 5
    }
    
    try:
        response = requests.get(f"{base_url}/api/v1/services/top", headers=headers, params=params_extended)
        
        print(f"   📅 Período estendido ({extended_start} a {extended_end}):")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            services = data['data']['services']
            print(f"   ✅ Serviços encontrados: {len(services)}")
            
            for service in services[:3]:
                print(f"      - {service['service_name']}: ${service['cost']:,.2f}")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def main():
    """Função principal"""
    test_frontend_calls()
    
    print("\n" + "=" * 50)
    print("🔍 ANÁLISE:")
    print("1. Compare os resultados 'All' vs 'Oracle Cloud'")
    print("2. Verifique se o problema é relacionado ao período")
    print("3. Analise se há dados Oracle no período de 90 dias")
    print("4. Confirme se o filtro está funcionando corretamente")

if __name__ == "__main__":
    main()
