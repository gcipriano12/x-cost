#!/usr/bin/env python3
"""
Teste da API de forecast com diferentes parâmetros para debugar o erro 400
"""

import os
import requests
import json
from datetime import datetime, timedelta

# Token atual
TOKEN = os.environ.get("X_COST_API_TOKEN", "")

if not TOKEN:
    print("⚠️ Configure a variável de ambiente X_COST_API_TOKEN antes de executar este script.")
    print("Exemplo: export X_COST_API_TOKEN='seu-token-aqui'")
    exit(1)

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}

def test_forecast_api():
    """Testa diferentes combinações de parâmetros"""
    
    print("🧪 TESTANDO API DE FORECAST - Debug 400 Error")
    print("=" * 60)
    
    # Cenários de teste
    test_scenarios = [
        {
            "name": "1. Sem parâmetros (deve funcionar)",
            "params": {}
        },
        {
            "name": "2. Apenas months",
            "params": {"months": 7}
        },
        {
            "name": "3. Com provider_name",
            "params": {"months": 7, "provider_name": "AWS"}
        },
        {
            "name": "4. Com datas (como o frontend pode estar passando)",
            "params": {
                "months": 7,
                "start_date": "2025-04-09",  # 90 dias atrás
                "end_date": "2025-07-07"     # hoje
            }
        },
        {
            "name": "5. Com datas + provider",
            "params": {
                "months": 7,
                "provider_name": "AWS",
                "start_date": "2025-04-09",
                "end_date": "2025-07-07"
            }
        },
        {
            "name": "6. Com credential_id (possivelmente None)",
            "params": {
                "months": 7,
                "credential_id": None
            }
        },
        {
            "name": "7. Datas inválidas (possível causa do 400)",
            "params": {
                "months": 7,
                "start_date": "invalid-date",
                "end_date": "2025-07-07"
            }
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n{scenario['name']}")
        print("-" * 40)
        
        # Filtrar parâmetros None
        clean_params = {k: v for k, v in scenario['params'].items() if v is not None}
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/analytics/forecast",
                headers=HEADERS,
                params=clean_params,
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            print(f"Parâmetros enviados: {clean_params}")
            
            if response.status_code == 200:
                data = response.json()
                forecast_data = data.get('data', {}).get('forecast_data', [])
                print(f"✅ Sucesso! {len(forecast_data)} pontos de forecast")
            else:
                print(f"❌ Erro {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Erro: {error_data}")
                except:
                    print(f"Resposta: {response.text[:200]}")
        
        except Exception as e:
            print(f"💥 Exceção: {e}")
    
    # Teste específico com o que o frontend pode estar enviando
    print(f"\n🎯 TESTE ESPECÍFICO - Simulando frontend")
    print("-" * 40)
    
    # Parâmetros que o frontend provavelmente envia
    frontend_params = {
        "months": 7,
        "credential_id": "",  # String vazia
        "provider_name": "",  # String vazia 
        "start_date": "",     # String vazia
        "end_date": ""        # String vazia
    }
    
    print(f"Parâmetros simulando frontend: {frontend_params}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/analytics/forecast",
            headers=HEADERS,
            params=frontend_params,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code != 200:
            try:
                error_data = response.json()
                print(f"Erro detalhado: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Resposta texto: {response.text}")
    
    except Exception as e:
        print(f"💥 Exceção: {e}")

if __name__ == "__main__":
    test_forecast_api()
