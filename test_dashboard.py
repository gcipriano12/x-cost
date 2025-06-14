#!/usr/bin/env python3
"""
Script para testar o endpoint do dashboard
"""
import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "ChangeMe123!"

def test_login():
    """Testa o login e retorna o token"""
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
        print(f"Token type: {token_data.get('token_type')}")
        return token_data.get('access_token')
    else:
        print(f"❌ Erro no login: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_dashboard(token):
    """Testa o endpoint do dashboard"""
    print("\n📊 Testando endpoint do dashboard...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Testar com diferentes períodos
    for period_days in [7, 30, 90]:
        print(f"\n📈 Testando período de {period_days} dias...")
        
        response = requests.get(
            f"{BASE_URL}/api/v1/dashboard/summary?period_days={period_days}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard data retrieved successfully!")
            
            # Exibir estrutura dos dados
            print("\n📋 Estrutura dos dados:")
            print(f"  - Métricas principais:")
            if 'metrics' in data:
                metrics = data['metrics']
                total_cost = float(metrics.get('total_cost', 0))
                cost_change = float(metrics.get('cost_change_percentage', 0))
                monthly_avg = float(metrics.get('monthly_average', 0))
                annual_proj = float(metrics.get('annual_projection', 0))
                
                print(f"    • Gasto total: R$ {total_cost:,.2f}")
                print(f"    • Variação: {cost_change:.1f}%")
                print(f"    • Média mensal: R$ {monthly_avg:,.2f}")
                print(f"    • Projeção anual: R$ {annual_proj:,.2f}")
                
                if 'top_service' in metrics:
                    top_service = metrics['top_service']
                    service_name = top_service.get('service_name', 'N/A')
                    provider_name = top_service.get('provider_name', 'N/A')
                    service_cost = float(top_service.get('total_cost', 0))
                    print(f"    • Top serviço: {service_name} ({provider_name}) - R$ {service_cost:,.2f}")
                
                if 'budget_consumption' in metrics:
                    budget = metrics['budget_consumption']
                    total_budget = float(budget.get('total_budget', 0))
                    current_spend = float(budget.get('current_spend', 0))
                    consumption_pct = float(budget.get('consumption_percentage', 0))
                    print(f"    • Orçamento: R$ {current_spend:,.2f} / R$ {total_budget:,.2f} ({consumption_pct:.1f}%)")
            
            print(f"\n  - Distribuição por provedor:")
            if 'provider_distribution' in data:
                for provider in data['provider_distribution']:
                    provider_name = provider.get('provider_name', 'N/A')
                    percentage = provider.get('percentage', 0)
                    cost = provider.get('total_cost', 0)
                    # Garantir que percentage e cost sejam números
                    try:
                        percentage = float(percentage) if percentage is not None else 0.0
                        cost = float(cost) if cost is not None else 0.0
                        print(f"    • {provider_name}: {percentage:.1f}% (R$ {cost:,.2f})")
                    except (ValueError, TypeError):
                        print(f"    • {provider_name}: N/A% (R$ N/A)")
            
            print(f"\n  - Highlights:")
            if 'highlights' in data:
                highlights = data['highlights']
                
                # Previsão próximo mês
                if 'next_month_forecast' in highlights:
                    forecast_data = highlights['next_month_forecast']
                    forecast = float(forecast_data.get('amount', 0))
                    change = float(forecast_data.get('change_percentage', 0))
                    print(f"    • Previsão próximo mês: R$ {forecast:,.2f} ({change:+.1f}%)")
                
                # Desperdício estimado
                if 'estimated_waste' in highlights:
                    waste_data = highlights['estimated_waste']
                    waste = float(waste_data.get('amount', 0))
                    waste_pct = float(waste_data.get('percentage', 0))
                    print(f"    • Desperdício estimado: R$ {waste:,.2f} ({waste_pct:.1f}%)")
                
                # Economias realizadas
                if 'savings_achieved' in highlights:
                    savings_data = highlights['savings_achieved']
                    savings = float(savings_data.get('amount', 0))
                    savings_pct = float(savings_data.get('percentage', 0))
                    print(f"    • Economias realizadas: R$ {savings:,.2f} ({savings_pct:.1f}%)")
                
        else:
            print(f"❌ Erro no dashboard: {response.status_code}")
            print(f"Response: {response.text}")

def main():
    print("🚀 Iniciando teste do dashboard endpoint...")
    print(f"📍 URL base: {BASE_URL}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Fazer login
    token = test_login()
    if not token:
        print("❌ Não foi possível obter token. Encerrando teste.")
        return
    
    # Testar dashboard
    test_dashboard(token)
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    main()
