#!/usr/bin/env python3
"""
Teste para verificar o comportamento do frontend com dados de equipe vazios.
"""

import requests
import json
from datetime import datetime, timedelta

def test_empty_team_data():
    """Testa se o backend retorna dados vazios para período curto (7d)"""
    base_url = "http://localhost:8000"
    endpoint = "/api/team-costs"
    
    # Teste com período de 7 dias que provavelmente não tem dados
    params = {
        "time_period": "7d",
        "limit": 10
    }
    
    try:
        response = requests.get(f"{base_url}{endpoint}", params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response data: {json.dumps(data, indent=2)}")
            print(f"Teams count: {len(data.get('data', []))}")
            print(f"Total cost: {data.get('total_cost', 0)}")
            
            if len(data.get('data', [])) == 0:
                print("✅ Backend retorna corretamente lista vazia para período sem dados")
            else:
                print(f"❌ Backend retorna {len(data['data'])} equipes para período 7d")
        else:
            print(f"❌ Erro na requisição: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")

if __name__ == "__main__":
    test_empty_team_data()
