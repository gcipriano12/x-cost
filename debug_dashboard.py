#!/usr/bin/env python3
"""
Script para debug detalhado do endpoint do dashboard
"""
import requests
import json
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "ChangeMe123!"

def get_token():
    """Obtém token de autenticação"""
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
        return response.json().get('access_token')
    return None

def debug_dashboard():
    """Debug completo do dashboard"""
    print("🔍 Debug detalhado do endpoint dashboard...")
    
    token = get_token()
    if not token:
        print("❌ Não foi possível obter token")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{BASE_URL}/api/v1/dashboard/summary?period_days=30",
        headers=headers
    )
    
    print(f"📊 Status Code: {response.status_code}")
    print(f"📄 Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\n📋 JSON Completo:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print(f"❌ Erro: {response.text}")

if __name__ == "__main__":
    debug_dashboard()
