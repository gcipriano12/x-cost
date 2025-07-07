#!/usr/bin/env python3
"""
Debug completo - testando token, conectividade e resposta
"""

import requests
import json

def debug_forecast_frontend():
    """Debug completo da API de forecast"""
    
    print("🔍 DEBUG COMPLETO - FORECAST API")
    print("=" * 60)
    
    # 1. Ler token do arquivo
    try:
        with open('/Users/gcipriano/Repositories/x-cost/frontend/current-token.txt', 'r') as f:
            token = f.read().strip()
        print(f"✅ Token lido do arquivo: {token[:50]}...")
    except Exception as e:
        print(f"❌ Erro lendo token: {e}")
        return
    
    # 2. Testar conectividade básica
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Backend conectividade: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend não responde: {e}")
        return
    
    # 3. Testar forecast simples
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/analytics/forecast",
            headers=headers,
            params={"months": 7},
            timeout=30
        )
        
        print(f"📊 Forecast API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("✅ SUCESSO! Estrutura da resposta:")
            print(f"  - success: {data.get('success')}")
            print(f"  - data exists: {'data' in data}")
            
            if 'data' in data:
                forecast_data = data['data']
                print(f"  - forecast_data length: {len(forecast_data.get('forecast_data', []))}")
                print(f"  - metadata exists: {'metadata' in forecast_data}")
                print(f"  - budget_info exists: {'budget_info' in forecast_data}")
                
                # Mostrar alguns pontos de dados
                points = forecast_data.get('forecast_data', [])[:5]
                print(f"  - Primeiros 5 pontos:")
                for point in points:
                    print(f"    {point.get('month')}: actual={point.get('actual')}, forecast={point.get('forecast')}")
        else:
            print(f"❌ Erro {response.status_code}:")
            try:
                error_data = response.json()
                print(f"  {json.dumps(error_data, indent=2)}")
            except:
                print(f"  {response.text}")
    
    except Exception as e:
        print(f"💥 Exceção na requisição: {e}")
    
    # 4. Testar com diferentes parâmetros (como frontend pode estar enviando)
    print(f"\n🧪 TESTE COM PARÂMETROS DO FRONTEND:")
    
    frontend_params = {
        "months": 7,
        "credential_id": "",
        "provider_name": "", 
        "start_date": "",
        "end_date": ""
    }
    
    try:
        response = requests.get(
            "http://localhost:8000/api/v1/analytics/forecast",
            headers=headers,
            params=frontend_params,
            timeout=30
        )
        
        print(f"Status com params frontend: {response.status_code}")
        if response.status_code != 200:
            print(f"Erro: {response.text}")
    
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    debug_forecast_frontend()
