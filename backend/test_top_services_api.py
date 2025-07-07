#!/usr/bin/env python3
"""
Teste do endpoint Top Services com token fornecido
"""

import requests
import json
from datetime import date, timedelta

# Configurações
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUxODU2ODg3LCJpYXQiOjE3NTE4NTMyODcsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.bok6-YKFZqVmN-SzfxNn0p6W0d7gSUEWEyhVkk6itoA"

def test_top_services_endpoint():
    """Testar endpoint Top Services"""
    
    print("🌐 TESTANDO ENDPOINT TOP SERVICES")
    print("=" * 50)
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Teste 1: Request básico
    print("\n1️⃣ Teste básico - Top 5 serviços")
    params = {
        "credential_id": "test-credential",
        "limit": 5
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data['data']['services'])} serviços retornados")
            print(f"   📈 Total de serviços únicos: {data['data']['total_services']}")
            print(f"   📅 Período: {data['data']['period']['start_date']} a {data['data']['period']['end_date']}")
            
            print("\n   🏆 Top Services:")
            for i, service in enumerate(data['data']['services'], 1):
                print(f"      {i}. {service['service_name']} ({service['provider']})")
                print(f"         💰 Custo: ${service['cost']:,.2f}")
                print(f"         📈 Variação: {service['change_from_previous']:+.1f}%")
                print(f"         🌍 Região: {service['region'] or 'N/A'}")
                print(f"         🆔 ID: {service['id']}")
                print()
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 2: Com período específico
    print("\n2️⃣ Teste com período específico (últimos 7 dias)")
    end_date = date.today()
    start_date = end_date - timedelta(days=7)
    
    params = {
        "credential_id": "test-credential",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "limit": 3
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! Período de 7 dias")
            print(f"   📈 {len(data['data']['services'])} serviços retornados")
            
            for service in data['data']['services']:
                print(f"      - {service['service_name']} ({service['provider']}): ${service['cost']:,.2f} ({service['change_from_previous']:+.1f}%)")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 3: Filtro por provider
    print("\n3️⃣ Teste com filtro de provider (Oracle Cloud)")
    params = {
        "credential_id": "test-credential",
        "provider_name": "Oracle Cloud",
        "limit": 3
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Oracle Cloud - {len(data['data']['services'])} serviços")
            
            for service in data['data']['services']:
                print(f"      - {service['service_name']}: ${service['cost']:,.2f} ({service['change_from_previous']:+.1f}%)")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 4: AWS específico
    print("\n4️⃣ Teste com filtro de provider (AWS)")
    params = {
        "credential_id": "test-credential",
        "provider_name": "AWS",
        "limit": 5
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ AWS - {len(data['data']['services'])} serviços")
            
            for service in data['data']['services']:
                print(f"      - {service['service_name']}: ${service['cost']:,.2f} ({service['change_from_previous']:+.1f}%)")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 5: Validação de erro (provider inválido)
    print("\n5️⃣ Teste de validação (provider inválido)")
    params = {
        "credential_id": "test-credential",
        "provider_name": "InvalidProvider",
        "limit": 5
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   📊 Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   ✅ Validação funcionando: {response.text}")
        else:
            print(f"   ⚠️ Deveria ter dado erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 6: Formato da resposta completa
    print("\n6️⃣ Teste do formato da resposta (JSON completo)")
    params = {
        "credential_id": "test-credential",
        "limit": 2
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Estrutura da resposta:")
            print(f"      - status: {data.get('status')}")
            print(f"      - data.services: {len(data['data']['services'])} items")
            print(f"      - data.total_services: {data['data']['total_services']}")
            print(f"      - data.period: {data['data']['period']}")
            
            # Validar formato de cada serviço
            if data['data']['services']:
                service = data['data']['services'][0]
                required_fields = ['id', 'service_name', 'provider', 'cost', 'change_from_previous', 'currency']
                print(f"      - Campos do serviço:")
                for field in required_fields:
                    value = service.get(field)
                    print(f"        * {field}: {value} ({type(value).__name__})")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")

def main():
    """Função principal"""
    test_top_services_endpoint()
    print("\n🎉 Testes do endpoint concluídos!")

if __name__ == "__main__":
    main()
