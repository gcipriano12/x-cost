#!/usr/bin/env python3
"""
Script para simular requisição do frontend e verificar response
"""

import requests
import json

# Simular headers que o frontend usa
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9,pt;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "User-Agent": "Mozilla/5.0 (compatible; Frontend-Test)",
    "Origin": "http://localhost:3000",
    "Referer": "http://localhost:3000/",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaW5vcHNfYWRtaW4iLCJyb2xlIjoiZmlub3BzX2FkbWluIiwiZXhwIjoxNzUyMjUxMDIyLCJpYXQiOjE3NTIyNDc0MjIsInR5cGUiOiJhY2Nlc3NfdG9rZW4ifQ.3ZlioZe-QkHfb5FI7G9pXapsX3YVZB6RcRkCAhWaIrQ"
}

print("🌐 SIMULANDO REQUISIÇÃO DO FRONTEND")
print("=" * 60)

try:
    response = requests.get("http://localhost:8000/api/v1/credentials/", headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"📊 Total de credenciais: {len(data)}")
        print("\n📋 Status das credenciais:")
        
        for i, cred in enumerate(data, 1):
            name = cred.get('name', 'N/A')
            status = cred.get('status', 'N/A')
            provider = cred.get('provider_type', 'N/A')
            validated = cred.get('last_validated', 'Nunca')
            
            icon = "✅" if status == "active" else "❌"
            print(f"   {icon} {i}. {name} ({provider})")
            print(f"      Status: {status}")
            print(f"      Última validação: {validated}")
            print()
        
        print("🎯 RESULTADO: Todas as credenciais deveriam aparecer como ACTIVE no frontend!")
        
    else:
        print(f"❌ Erro: {response.text}")
        
except Exception as e:
    print(f"💥 Erro: {e}")

print("\n💡 SE O FRONTEND AINDA MOSTRA 'INACTIVE':")
print("1. Faça hard refresh: Ctrl+Shift+R (ou Cmd+Shift+R)")
print("2. Limpe o cache do navegador")
print("3. Verifique se o token do frontend está correto")
print("4. Verifique o console do navegador para erros")
print("5. Use as ferramentas de desenvolvedor para ver as requisições")
