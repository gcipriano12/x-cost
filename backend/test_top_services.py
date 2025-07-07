#!/usr/bin/env python3
"""
Script para testar o endpoint Top Services
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

import requests
import json
from datetime import date, timedelta
from app.top_services_analytics import TopServicesAnalyzer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Configurações
BASE_URL = "http://localhost:8000"
USERNAME = "finops_admin"
PASSWORD = "Password123!"

def get_auth_token():
    """Obter token de autenticação"""
    
    auth_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/auth/login", data=auth_data)
    
    if response.status_code == 200:
        token_data = response.json()
        return token_data.get("access_token")
    else:
        print(f"Erro na autenticação: {response.status_code}")
        print(response.text)
        return None

def test_top_services_direct():
    """Testar analyzer diretamente"""
    
    print("🧪 Testando TopServicesAnalyzer diretamente...")
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        analyzer = TopServicesAnalyzer(db)
        
        # Período de teste: últimos 30 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"📅 Período: {start_date} a {end_date}")
        
        # Teste 1: Todos os providers
        print("\n1️⃣ Teste: Todos os providers")
        result = analyzer.get_top_services(
            credential_id="test-credential",
            start_date=start_date,
            end_date=end_date,
            provider_name=None,
            limit=5
        )
        
        print(f"   ✅ Total de serviços únicos: {result.total_services}")
        print(f"   📊 Top {len(result.services)} serviços:")
        
        for i, service in enumerate(result.services, 1):
            print(f"      {i}. {service.service_name} ({service.provider})")
            print(f"         💰 Custo: ${service.cost:,.2f}")
            print(f"         📈 Variação: {service.change_from_previous:+.1f}%")
            print(f"         🌍 Região: {service.region or 'N/A'}")
        
        # Teste 2: Filtro por provider específico
        print("\n2️⃣ Teste: Provider específico (Oracle Cloud)")
        try:
            result_oracle = analyzer.get_top_services(
                credential_id="test-credential",
                start_date=start_date,
                end_date=end_date,
                provider_name="Oracle Cloud",
                limit=3
            )
            
            print(f"   ✅ Oracle Cloud - {len(result_oracle.services)} serviços:")
            for service in result_oracle.services:
                print(f"      - {service.service_name}: ${service.cost:,.2f} ({service.change_from_previous:+.1f}%)")
        
        except Exception as e:
            print(f"   ⚠️ Oracle Cloud: {e}")
        
        # Teste 3: Diferentes limites
        print("\n3️⃣ Teste: Diferentes limites")
        for limit in [1, 3, 10]:
            result_limit = analyzer.get_top_services(
                credential_id="test-credential",
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
            print(f"   Limit {limit}: {len(result_limit.services)} serviços retornados")
        
    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_top_services_api():
    """Testar endpoint via API"""
    
    print("\n🌐 Testando endpoint via API...")
    
    # Obter token
    token = get_auth_token()
    if not token:
        print("❌ Não foi possível obter token de autenticação")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Teste 1: Request básico
    print("\n1️⃣ Request básico")
    params = {
        "credential_id": "test-credential",
        "limit": 5
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Sucesso! {len(data['data']['services'])} serviços retornados")
            
            for service in data['data']['services'][:3]:  # Mostrar apenas 3
                print(f"      - {service['service_name']} ({service['provider']}): ${service['cost']:,.2f}")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 2: Com filtros específicos
    print("\n2️⃣ Request com filtros")
    end_date = date.today()
    start_date = end_date - timedelta(days=7)  # 7 dias
    
    params = {
        "credential_id": "test-credential",
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "provider_name": "AWS",
        "limit": 3
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ AWS - {len(data['data']['services'])} serviços")
            print(f"   📅 Período: {data['data']['period']['start_date']} a {data['data']['period']['end_date']}")
        else:
            print(f"   ❌ Erro: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")
    
    # Teste 3: Validação de erro
    print("\n3️⃣ Teste de validação (provider inválido)")
    params = {
        "credential_id": "test-credential",
        "provider_name": "InvalidProvider",
        "limit": 5
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/services/top", headers=headers, params=params)
        
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:200]}...")
    
    except Exception as e:
        print(f"   ❌ Erro na requisição: {e}")

def main():
    """Função principal"""
    
    print("🔧 TESTE DO ENDPOINT TOP SERVICES")
    print("=" * 50)
    
    # Teste direto do analyzer
    test_top_services_direct()
    
    # Teste via API
    test_top_services_api()
    
    print("\n🎉 Testes concluídos!")

if __name__ == "__main__":
    main()
