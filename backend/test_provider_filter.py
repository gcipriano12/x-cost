#!/usr/bin/env python3
"""
Script para testar o filtro de provedor no endpoint do dashboard
"""
import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "ChangeMe123!"

def get_token():
    """Obtém token de autenticação"""
    print("🔐 Fazendo login...")
    
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json=login_data,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"✅ Login realizado com sucesso!")
        return token_data.get('access_token')
    else:
        print(f"❌ Erro no login: {response.status_code}")
        return None

def test_provider_filter(token):
    """Testa o filtro de provedor"""
    print("\n🔍 Testando filtro de provedor...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Lista de provedores para testar
    providers = [None, "AWS", "Azure", "GCP", "Oracle"]
    
    for provider in providers:
        print(f"\n📊 Testando provider: {provider or 'TODOS'}")
        
        # Construir parâmetros
        params = {"period_days": 30}
        if provider:
            params["provider_name"] = provider
        
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboard/summary",
            params=params,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Extrair métricas principais
            metrics = data.get('metrics', {})
            provider_dist = data.get('provider_distribution', [])
            
            print(f"✅ Dados obtidos com sucesso!")
            print(f"   • Gasto total: R$ {float(metrics.get('total_cost', 0)):,.2f}")
            print(f"   • Top serviço: {metrics.get('top_service', {}).get('service_name', 'N/A')} ({metrics.get('top_service', {}).get('provider_name', 'N/A')})")
            
            # Mostrar distribuição por provedor
            print(f"   • Distribuição por provedor:")
            for p in provider_dist:
                print(f"     - {p.get('provider_name', 'Unknown')}: {float(p.get('percentage', 0)):.1f}% (R$ {float(p.get('total_cost', 0)):,.2f})")
            
            # Validar se o filtro está funcionando
            if provider:
                # Se filtramos por um provedor específico, a distribuição deve ter apenas esse provedor
                if len(provider_dist) == 1 and provider_dist[0].get('provider_name') == provider:
                    print(f"   ✅ Filtro funcionando corretamente - apenas {provider} retornado")
                else:
                    print(f"   ⚠️ Possível problema no filtro - esperado apenas {provider}")
                    
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(f"Response: {response.text}")

def main():
    print("🚀 Testando filtro de provedor no dashboard...")
    print(f"📍 URL base: {BASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Obter token
    token = get_token()
    if not token:
        print("❌ Não foi possível obter token de autenticação")
        return
    
    # Testar filtro de provedor
    test_provider_filter(token)
    
    print("\n✅ Teste de filtro de provedor concluído!")

if __name__ == "__main__":
    main()
