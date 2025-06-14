#!/usr/bin/env python3
"""
Script para testar as rotas de budgets da API X-Cost FinOps.
Este script testa todas as funcionalidades CRUD dos budgets.

Uso:
    python scripts/test_budget_routes.py
"""

import requests
import json
import sys
from datetime import datetime

# Configuração
API_BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"

def print_section(title):
    """Imprime uma seção formatada"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

def print_result(method, endpoint, status_code, response_data=None):
    """Imprime o resultado de uma requisição"""
    status_icon = "✅" if 200 <= status_code < 300 else "❌"
    print(f"{status_icon} {method} {endpoint} - Status: {status_code}")
    
    if response_data:
        if isinstance(response_data, dict):
            print(f"   Response: {json.dumps(response_data, indent=2, default=str)}")
        else:
            print(f"   Response: {response_data}")

def login_user(username, password):
    """Faz login e retorna o token de acesso"""
    print_section("AUTENTICAÇÃO")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print_result("POST", "/auth/login", response.status_code)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ Login realizado com sucesso para {username}")
            return access_token
        else:
            print(f"❌ Falha no login: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição de login: {e}")
        return None

def test_budget_routes(token):
    """Testa todas as rotas de budgets"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Testar listagem de budgets (inicialmente vazia)
    print_section("TESTE 1: LISTAR BUDGETS")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/budgets", headers=headers)
        print_result("GET", "/budgets", response.status_code, response.json())
    except Exception as e:
        print(f"❌ Erro ao listar budgets: {e}")
    
    # 2. Criar um novo budget
    print_section("TESTE 2: CRIAR BUDGET")
    budget_data = {
        "budget_name": "AWS Production Monthly Test",
        "provider_name": "AWS",
        "service_name": "EC2",
        "budget_amount": 5000.00,
        "budget_period": "monthly",
        "alert_threshold": 80.0,
        "is_active": True,
        "tags": {
            "environment": "production",
            "team": "devops",
            "created_by": "test_script"
        }
    }
    
    created_budget_id = None
    try:
        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/budgets",
            json=budget_data,
            headers=headers
        )
        print_result("POST", "/budgets", response.status_code, response.json())
        
        if response.status_code == 201:
            created_budget = response.json()
            created_budget_id = created_budget.get("id")
            print(f"✅ Budget criado com ID: {created_budget_id}")
        
    except Exception as e:
        print(f"❌ Erro ao criar budget: {e}")
    
    # 3. Buscar budget específico
    if created_budget_id:
        print_section("TESTE 3: BUSCAR BUDGET ESPECÍFICO")
        try:
            response = requests.get(
                f"{API_BASE_URL}{API_PREFIX}/budgets/{created_budget_id}",
                headers=headers
            )
            print_result("GET", f"/budgets/{created_budget_id}", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Erro ao buscar budget: {e}")
    
    # 4. Atualizar budget
    if created_budget_id:
        print_section("TESTE 4: ATUALIZAR BUDGET")
        update_data = {
            "budget_name": "AWS Production Monthly Test (Updated)",
            "provider_name": "AWS",
            "service_name": "EC2",
            "budget_amount": 6000.00,  # Aumentar budget
            "budget_period": "monthly",
            "alert_threshold": 75.0,   # Diminuir threshold
            "is_active": True,
            "tags": {
                "environment": "production",
                "team": "devops",
                "created_by": "test_script",
                "updated_at": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.put(
                f"{API_BASE_URL}{API_PREFIX}/budgets/{created_budget_id}",
                json=update_data,
                headers=headers
            )
            print_result("PUT", f"/budgets/{created_budget_id}", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Erro ao atualizar budget: {e}")
    
    # 5. Verificar alertas do budget
    if created_budget_id:
        print_section("TESTE 5: VERIFICAR ALERTAS DO BUDGET")
        try:
            response = requests.get(
                f"{API_BASE_URL}{API_PREFIX}/budgets/{created_budget_id}/alerts",
                headers=headers
            )
            print_result("GET", f"/budgets/{created_budget_id}/alerts", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Erro ao verificar alertas: {e}")
    
    # 6. Listar todos os alertas de budgets
    print_section("TESTE 6: LISTAR TODOS OS ALERTAS")
    try:
        response = requests.get(
            f"{API_BASE_URL}{API_PREFIX}/budgets/alerts",
            headers=headers
        )
        print_result("GET", "/budgets/alerts", response.status_code, response.json())
    except Exception as e:
        print(f"❌ Erro ao listar alertas: {e}")
    
    # 7. Listar budgets novamente (agora com dados)
    print_section("TESTE 7: LISTAR BUDGETS (COM DADOS)")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/budgets", headers=headers)
        print_result("GET", "/budgets", response.status_code, response.json())
    except Exception as e:
        print(f"❌ Erro ao listar budgets: {e}")
    
    # 8. Deletar budget (opcional - comentado para preservar dados de teste)
    # if created_budget_id:
    #     print_section("TESTE 8: DELETAR BUDGET")
    #     try:
    #         response = requests.delete(
    #             f"{API_BASE_URL}{API_PREFIX}/budgets/{created_budget_id}",
    #             headers=headers
    #         )
    #         print_result("DELETE", f"/budgets/{created_budget_id}", response.status_code)
    #     except Exception as e:
    #         print(f"❌ Erro ao deletar budget: {e}")
    
    return created_budget_id

def test_error_scenarios(token):
    """Testa cenários de erro"""
    print_section("TESTES DE CENÁRIOS DE ERRO")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 1. Buscar budget inexistente
    print("\n🧪 Teste: Budget inexistente")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/budgets/99999", headers=headers)
        print_result("GET", "/budgets/99999", response.status_code, response.json())
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 2. Criar budget com dados inválidos
    print("\n🧪 Teste: Dados inválidos")
    invalid_data = {
        "budget_name": "",  # Nome vazio
        "budget_amount": -100,  # Valor negativo
        "budget_period": "invalid_period"  # Período inválido
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}{API_PREFIX}/budgets",
            json=invalid_data,
            headers=headers
        )
        print_result("POST", "/budgets", response.status_code, response.json())
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    # 3. Acesso sem autenticação
    print("\n🧪 Teste: Sem autenticação")
    try:
        response = requests.get(f"{API_BASE_URL}{API_PREFIX}/budgets")
        print_result("GET", "/budgets", response.status_code, response.json())
    except Exception as e:
        print(f"❌ Erro: {e}")

def main():
    """Função principal"""
    print("🚀 Testando Rotas de Budgets da API X-Cost FinOps")
    print(f"📡 URL Base: {API_BASE_URL}")
    
    # Testar com usuário admin
    print_section("TESTE COM USUÁRIO ADMIN")
    token = login_user("admin", "AdminPass123!")
    
    if not token:
        print("❌ Não foi possível fazer login. Verifique se:")
        print("  1. A aplicação está rodando em http://localhost:8000")
        print("  2. Os dados de teste foram populados (scripts/populate_database.py)")
        print("  3. As credenciais estão corretas")
        return
    
    # Executar testes principais
    budget_id = test_budget_routes(token)
    
    # Executar testes de erro
    test_error_scenarios(token)
    
    # Testar com usuário viewer (permissões limitadas)
    print_section("TESTE COM USUÁRIO VIEWER")
    viewer_token = login_user("cost_viewer", "ViewerPass123!")
    
    if viewer_token:
        print("\n🧪 Teste: Viewer tentando criar budget (deve falhar)")
        budget_data = {
            "budget_name": "Test Budget by Viewer",
            "provider_name": "AWS",
            "budget_amount": 1000.00,
            "budget_period": "monthly",
            "alert_threshold": 80.0
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}{API_PREFIX}/budgets",
                json=budget_data,
                headers={
                    "Authorization": f"Bearer {viewer_token}",
                    "Content-Type": "application/json"
                }
            )
            print_result("POST", "/budgets", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Erro: {e}")
        
        # Viewer deve conseguir listar budgets
        print("\n🧪 Teste: Viewer listando budgets (deve funcionar)")
        try:
            response = requests.get(
                f"{API_BASE_URL}{API_PREFIX}/budgets",
                headers={"Authorization": f"Bearer {viewer_token}"}
            )
            print_result("GET", "/budgets", response.status_code, response.json())
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print_section("RESUMO DOS TESTES")
    print("✅ Testes de rotas de budgets concluídos!")
    print("📊 Verifique os resultados acima para validar o funcionamento")
    print("🌐 Acesse http://localhost:8000/docs para ver a documentação da API")
    
    if budget_id:
        print(f"💡 Budget de teste criado com ID: {budget_id}")
        print("   Use este ID para testes adicionais se necessário")

if __name__ == "__main__":
    main()
