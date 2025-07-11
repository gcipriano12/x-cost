#!/usr/bin/env python3
"""
Script para comparar resposta da API com o que o frontend deveria ver
"""

import requests
import json
import sys

# Configuração
BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUyMjUxMDIyLCJpYXQiOjE3NTIyNDc0MjIsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.3ZlioZe-QkHfb5FI7G9pXapsX3YVZB6RcRkCAhWaIrQ"

def test_api_endpoints():
    """Testa diferentes endpoints que o frontend pode estar chamando"""
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    endpoints_to_test = [
        "/api/v1/credentials/",
        "/api/v1/credentials",
        "/credentials/",
        "/credentials"
    ]
    
    print("🔍 TESTANDO ENDPOINTS DA API")
    print("="*60)
    
    for endpoint in endpoints_to_test:
        print(f"\n📡 Testando: {BASE_URL}{endpoint}")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"   📊 Encontradas {len(data)} credenciais")
                    for i, cred in enumerate(data[:3], 1):  # Mostrar apenas as 3 primeiras
                        name = cred.get('name', 'N/A')
                        status = cred.get('status', 'N/A')
                        print(f"     {i}. {name}: {status}")
                    if len(data) > 3:
                        print(f"     ... e mais {len(data) - 3} credenciais")
                else:
                    print(f"   📋 Resposta: {data}")
            else:
                print(f"   ❌ Erro: {response.text[:100]}")
                
        except Exception as e:
            print(f"   💥 Exceção: {e}")
    
    print("\n" + "="*60)
    print("✅ TESTE DE ENDPOINTS COMPLETO")

def test_cors_headers():
    """Testa headers CORS que podem afetar o frontend"""
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Origin": "http://localhost:3000",  # Frontend típico
        "Access-Control-Request-Method": "GET"
    }
    
    print("\n🌐 TESTANDO CORS E HEADERS")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v1/credentials/", headers=headers)
        print(f"Status: {response.status_code}")
        print("\n📋 Headers de resposta:")
        for header, value in response.headers.items():
            if 'cors' in header.lower() or 'access-control' in header.lower():
                print(f"   {header}: {value}")
        
        # Verificar se há cache headers
        cache_headers = ['cache-control', 'etag', 'last-modified', 'expires']
        print("\n🗄️  Headers de cache:")
        for header in cache_headers:
            if header in response.headers:
                print(f"   {header}: {response.headers[header]}")
        
    except Exception as e:
        print(f"💥 Erro no teste CORS: {e}")

def main():
    print("🚀 DIAGNÓSTICO FRONTEND vs BACKEND")
    print("="*80)
    
    test_api_endpoints()
    test_cors_headers()
    
    print("\n💡 POSSÍVEIS SOLUÇÕES:")
    print("1. Limpar cache do navegador (Ctrl+Shift+R)")
    print("2. Verificar se o frontend está usando o endpoint correto")
    print("3. Verificar se há cache no React Query/TanStack Query")
    print("4. Verificar se o token do frontend está válido")
    print("5. Forçar refresh dos dados no frontend")

if __name__ == "__main__":
    main()
