#!/usr/bin/env python3
"""
Teste dos endpoints REST para validar a integração com o novo get_aws_savings
"""

import asyncio
import json
import logging
from fastapi.testclient import TestClient
from app.main import app

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_savings_endpoints():
    """Testa os endpoints de savings opportunities"""
    
    print("🧪 Testando endpoints REST de savings opportunities...")
    
    client = TestClient(app)
    
    # Teste 1: Endpoint de savings opportunities
    print("🔍 Testando GET /api/v1/savings-opportunities...")
    
    try:
        response = client.get("/api/v1/savings-opportunities")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Resposta recebida: {len(data.get('opportunities', []))} oportunidades")
            print(f"   Total estimado: ${data.get('metadata', {}).get('total_estimated_savings', 0)}")
        elif response.status_code == 401:
            print("   ⚠️ Erro de autenticação (esperado sem token JWT)")
        else:
            print(f"   ❌ Erro inesperado: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")
    
    # Teste 2: Endpoint com filtro de provider
    print("🔍 Testando GET /api/v1/savings-opportunities?provider=aws...")
    
    try:
        response = client.get("/api/v1/savings-opportunities?provider=aws")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Resposta para AWS: {len(data.get('opportunities', []))} oportunidades")
        elif response.status_code == 401:
            print("   ⚠️ Erro de autenticação (esperado sem token JWT)")
        else:
            print(f"   ❌ Erro inesperado: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint com filtro: {e}")
    
    # Teste 3: Endpoint de summary
    print("🔍 Testando GET /api/v1/optimization/summary...")
    
    try:
        response = client.get("/api/v1/optimization/summary")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Summary recebido: {data.get('total_opportunities', 0)} oportunidades totais")
            print(f"   Total de economia: ${data.get('total_estimated_savings', 0)}")
        elif response.status_code == 401:
            print("   ⚠️ Erro de autenticação (esperado sem token JWT)")
        else:
            print(f"   ❌ Erro inesperado: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint summary: {e}")
    
    print("✅ Testes dos endpoints concluídos!")

if __name__ == "__main__":
    test_savings_endpoints()
