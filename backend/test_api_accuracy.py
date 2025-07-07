#!/usr/bin/env python3

import requests
import json

def test_api_accuracy():
    print("🌐 TESTANDO API DE FORECAST")
    print("=" * 40)
    
    url = "http://localhost:8000/api/forecast"
    params = {
        "credential_id": "1",
        "provider_name": "oracle", 
        "start_date": "2024-07-07",
        "end_date": "2025-07-07",
        "months": 7
    }
    
    try:
        print("📡 Fazendo requisição para API...")
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            metadata = data.get('metadata', {})
            
            print("✅ API respondeu com sucesso!")
            print(f"   Acurácia: {metadata.get('model_accuracy', 'N/A')}%")
            print(f"   Método: {metadata.get('forecast_method', 'N/A')}")
            print(f"   Completude: {metadata.get('data_completeness', 'N/A')}%")
            
            # Verificar se a acurácia melhorou
            accuracy = metadata.get('model_accuracy', 0)
            if accuracy > 70:
                print("🎉 MELHORIAS APLICADAS! Acurácia alta!")
            elif accuracy > 50:
                print("🟡 Melhoria parcial detectada")
            else:
                print("❌ Acurácia ainda baixa - melhorias não aplicadas")
                
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar - backend pode estar offline")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_api_accuracy()
