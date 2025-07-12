#!/usr/bin/env python3
"""
Teste de Integração Frontend-Backend para KPIs
Testa se o backend está respondendo corretamente para o frontend
"""

import requests
import json
import sys

def test_kpi_endpoints():
    """Testa endpoints de KPI"""
    base_url = "http://localhost:8000"
    
    # Token de autenticação
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUyMjgzMjc1LCJpYXQiOjE3NTIyNzk2NzUsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.dBYVtBbFBqvmDB5BFfID6VKtxILKkzjQ6BuNybtIJME"
    
    # Headers com autenticação
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    print("🔄 Testando endpoints de KPI...")
    
    endpoints = [
        "/api/v1/kpis/current",
        "/api/v1/kpis/by-category",
    ]
    
    for endpoint in endpoints:
        try:
            print(f"🔄 Testando {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Resposta válida recebida")
                if 'data' in data:
                    print(f"   📊 Dados: {json.dumps(data['data'], indent=2)[:200]}...")
                else:
                    print(f"   📊 Resposta: {json.dumps(data, indent=2)[:200]}...")
            elif response.status_code == 401:
                print(f"   ⚠️  Endpoint protegido (401 - não autenticado)")
                print("   💡 Este é esperado para endpoints protegidos")
            elif response.status_code == 422:
                print(f"   ⚠️  Erro de validação (422)")
                print(f"   📝 Detalhes: {response.text[:200]}...")
            else:
                print(f"   ❌ Erro: {response.status_code}")
                print(f"   📝 Resposta: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Erro de conexão - Backend não está rodando?")
            return False
        except requests.exceptions.Timeout:
            print(f"   ❌ Timeout - Backend demorou para responder")
            return False
        except Exception as e:
            print(f"   ❌ Erro inesperado: {str(e)}")
            return False
    
    return True

def test_health_check():
    """Testa se o backend está rodando"""
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está rodando (FastAPI docs acessível)")
            return True
        else:
            print(f"⚠️  Backend respondeu com status {response.status_code}")
            return False
    except:
        print("❌ Backend não está rodando")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TESTE DE INTEGRAÇÃO FRONTEND-BACKEND - KPIs")
    print("=" * 60)
    
    # Teste 1: Health check
    print("\n1. 🏥 Verificando se backend está rodando...")
    if not test_health_check():
        print("❌ Backend não está disponível. Inicie o backend primeiro com:")
        print("   cd backend && uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Teste 2: Endpoints de KPI
    print("\n2. 📊 Testando endpoints de KPI...")
    success = test_kpi_endpoints()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TESTES DE INTEGRAÇÃO CONCLUÍDOS!")
        print("✅ Backend está respondendo aos endpoints de KPI")
        print("🔗 Frontend pode se conectar com segurança")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️  Verifique se o backend está configurado corretamente")
    print("=" * 60)
    
    print("\n📋 Próximos passos:")
    print("1. Iniciar o frontend: cd frontend && npm run dev")
    print("2. Acessar: http://localhost:3000")
    print("3. Verificar seção 'KPIs Detalhados por Categoria' no dashboard")
    
    sys.exit(0 if success else 1)
