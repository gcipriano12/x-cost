#!/usr/bin/env python3
"""
Script para testar a API de Virtual Tags
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Testa login"""
    url = f"{BASE_URL}/api/v1/auth/login"
    data = {
        "username": "test",
        "password": "test123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Error during login: {e}")
        return None

def test_virtual_tags_api(token):
    """Testa API de Virtual Tags"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Testar listagem de campos disponíveis
    print("\n=== Testando campos disponíveis ===")
    url = f"{BASE_URL}/api/v1/virtual-tags/fields/available"
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
    
    # Testar listagem de Virtual Tags
    print("\n=== Testando listagem de Virtual Tags ===")
    url = f"{BASE_URL}/api/v1/virtual-tags/"
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Testar métricas do dashboard
    print("\n=== Testando métricas do dashboard ===")
    url = f"{BASE_URL}/api/v1/virtual-tags/metrics/dashboard"
    response = requests.get(url, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}...")

if __name__ == "__main__":
    print("=== Testando API de Virtual Tags ===")
    
    # Fazer login
    print("1. Fazendo login...")
    token = test_login()
    
    if token:
        print(f"Login successful! Token: {token[:50]}...")
        
        # Testar API
        test_virtual_tags_api(token)
    else:
        print("Login failed!")
