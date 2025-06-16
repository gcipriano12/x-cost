#!/usr/bin/env python3
"""
Teste do backend local (localhost:8000) com dados do LocalStack
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any

# Configurações
BACKEND_URL = "http://localhost:8000"
LOCALSTACK_URL = "http://localhost:4566"

def check_backend_health() -> bool:
    """Verifica se o backend está rodando"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está rodando")
            return True
    except:
        pass
    
    print("❌ Backend não está rodando")
    print(f"   Certifique-se de que a API está rodando em {BACKEND_URL}")
    print("   Execute: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
    return False

def check_localstack_health() -> bool:
    """Verifica se o LocalStack está rodando"""
    try:
        response = requests.get(f"{LOCALSTACK_URL}/_localstack/health", timeout=5)
        if response.status_code == 200:
            print("✅ LocalStack está rodando")
            return True
    except:
        pass
    
    print("❌ LocalStack não está rodando")
    print("   Execute: podman-compose up localstack")
    return False

def get_jwt_token() -> str:
    """
    Obtém token JWT para autenticação
    Substitua por sua lógica de autenticação real
    """
    try:
        # Tentar endpoint de login se existir
        login_data = {
            "username": "admin",
            "password": "admin"
        }
        response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            if token:
                print("✅ Token JWT obtido")
                return token
    except:
        pass
    
    # Se não conseguir obter token, criar um mock (apenas para teste)
    print("⚠️ Usando token mock para teste")
    return "mock-jwt-token-for-testing"

def test_endpoint(endpoint: str, headers: Dict[str, str] = None, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Testa um endpoint específico"""
    url = f"{BACKEND_URL}{endpoint}"
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        result = {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "data": None,
            "error": None
        }
        
        if response.status_code == 200:
            try:
                result["data"] = response.json()
            except:
                result["data"] = response.text
        else:
            result["error"] = response.text
        
        return result
        
    except Exception as e:
        return {
            "endpoint": endpoint,
            "status_code": None,
            "success": False,
            "data": None,
            "error": str(e)
        }

def print_test_result(result: Dict[str, Any]):
    """Imprime resultado do teste de forma formatada"""
    endpoint = result["endpoint"]
    status = result["status_code"]
    success = result["success"]
    
    status_icon = "✅" if success else "❌"
    
    print(f"\n{status_icon} {endpoint}")
    print(f"   Status: {status}")
    
    if success:
        data = result["data"]
        if isinstance(data, dict):
            # Extrair informações principais
            if "opportunities" in data:
                opportunities = data["opportunities"]
                total_savings = data.get("metadata", {}).get("total_estimated_savings", 0)
                print(f"   Oportunidades: {len(opportunities)}")
                print(f"   Economia total: ${total_savings}")
                
                # Mostrar algumas oportunidades
                for i, opp in enumerate(opportunities[:3]):
                    print(f"     {i+1}. {opp.get('id', 'unknown')}: ${opp.get('estimated_savings', 0)} ({opp.get('opportunity_type', 'unknown')})")
                
                if len(opportunities) > 3:
                    print(f"     ... e mais {len(opportunities) - 3} oportunidades")
                    
            elif "anomalies" in data:
                anomalies = data["anomalies"]
                print(f"   Anomalias: {len(anomalies)}")
                
                for i, anom in enumerate(anomalies[:3]):
                    print(f"     {i+1}. {anom.get('id', 'unknown')}: ${anom.get('cost_impact', 0)} ({anom.get('severity', 'unknown')})")
                    
            elif "total_opportunities" in data:
                print(f"   Total oportunidades: {data.get('total_opportunities', 0)}")
                print(f"   Total anomalias: {data.get('total_anomalies', 0)}")
                print(f"   Economia estimada: ${data.get('total_estimated_savings', 0)}")
            else:
                print(f"   Dados: {str(data)[:200]}...")
        else:
            print(f"   Resposta: {str(data)[:200]}...")
    else:
        error = result["error"]
        print(f"   Erro: {error[:200]}...")

def main():
    """Função principal"""
    print("🧪 Testando backend local com dados do LocalStack")
    print("=" * 60)
    
    # Verificar serviços
    if not check_backend_health():
        return
    
    if not check_localstack_health():
        print("⚠️ Continuando sem LocalStack (alguns dados podem não estar disponíveis)")
    
    # Obter token JWT
    jwt_token = get_jwt_token()
    headers = {"Authorization": f"Bearer {jwt_token}"}
    
    # Lista de endpoints para testar
    endpoints_to_test = [
        {
            "endpoint": "/",
            "description": "Página inicial",
            "headers": None
        },
        {
            "endpoint": "/health",
            "description": "Health check",
            "headers": None
        },
        {
            "endpoint": "/api/v1/savings-opportunities",
            "description": "Todas as oportunidades de economia",
            "headers": headers
        },
        {
            "endpoint": "/api/v1/savings-opportunities",
            "description": "Oportunidades AWS",
            "headers": headers,
            "params": {"provider": "aws"}
        },
        {
            "endpoint": "/api/v1/savings-opportunities",
            "description": "Oportunidades com economia mínima $100",
            "headers": headers,
            "params": {"min_savings": 100}
        },
        {
            "endpoint": "/api/v1/anomalies",
            "description": "Anomalias de custo",
            "headers": headers
        },
        {
            "endpoint": "/api/v1/anomalies",
            "description": "Anomalias AWS",
            "headers": headers,
            "params": {"provider": "aws"}
        },
        {
            "endpoint": "/api/v1/optimization/summary",
            "description": "Resumo de otimização",
            "headers": headers
        },
        {
            "endpoint": "/api/v1/optimization/summary",
            "description": "Resumo AWS",
            "headers": headers,
            "params": {"provider": "aws"}
        }
    ]
    
    # Executar testes
    print("\n🔍 Executando testes dos endpoints...")
    
    for test_config in endpoints_to_test:
        endpoint = test_config["endpoint"]
        description = test_config["description"]
        headers = test_config.get("headers")
        params = test_config.get("params")
        
        print(f"\n📡 Testando: {description}")
        result = test_endpoint(endpoint, headers, params)
        print_test_result(result)
        
        # Pequena pausa entre requests
        time.sleep(0.5)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("📋 Resumo dos testes:")
    print("   - Testou endpoints principais da API")
    print("   - Verificou autenticação JWT")
    print("   - Testou filtros por provider")
    print("   - Testou parâmetros de economia mínima")
    print("")
    print("🎯 Para testar com dados reais do LocalStack:")
    print("   1. Execute: python populate_localstack.py")
    print("   2. Configure credenciais AWS no .env:")
    print("      AWS_ENDPOINT_URL=http://localhost:4566")
    print("      AWS_ACCESS_KEY_ID=test")
    print("      AWS_SECRET_ACCESS_KEY=test")
    print("   3. Reinicie o backend")
    print("   4. Execute este teste novamente")

if __name__ == "__main__":
    main()
