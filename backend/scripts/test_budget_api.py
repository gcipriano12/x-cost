#!/usr/bin/env python3
"""
Script para testar as rotas de Budget implementadas.
Este script faz requisições HTTP para as rotas criadas e verifica se estão funcionando.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any

# Configurações
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class BudgetAPITester:
    def __init__(self):
        self.token = None
        self.headers = {}
    
    def login(self, username: str = "admin", password: str = "AdminPass123!") -> bool:
        """Faz login e obtém token de autenticação"""
        try:
            login_data = {
                "username": username,
                "password": password
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=login_data)
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.headers = {"Authorization": f"Bearer {self.token}"}
                print(f"✅ Login realizado com sucesso para {username}")
                return True
            else:
                print(f"❌ Falha no login: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            return False
    
    def test_list_budgets(self) -> bool:
        """Testa listagem de budgets"""
        try:
            response = requests.get(f"{API_BASE}/budgets", headers=self.headers)
            
            if response.status_code == 200:
                budgets = response.json()
                print(f"✅ Lista de budgets obtida: {len(budgets)} budgets encontrados")
                return True
            else:
                print(f"❌ Falha ao listar budgets: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao listar budgets: {e}")
            return False
    
    def test_create_budget(self) -> Dict[str, Any]:
        """Testa criação de budget"""
        try:
            budget_data = {
                "budget_name": f"Test Budget {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "provider_name": "AWS",
                "service_name": "EC2",
                "budget_amount": 5000.00,
                "budget_period": "monthly",
                "alert_threshold": 80.0,
                "is_active": True,
                "tags": {
                    "environment": "test",
                    "created_by": "api_test"
                }
            }
            
            response = requests.post(f"{API_BASE}/budgets", json=budget_data, headers=self.headers)
            
            if response.status_code == 200:
                budget = response.json()
                print(f"✅ Budget criado com sucesso: {budget['budget_name']} (ID: {budget['id']})")
                return budget
            else:
                print(f"❌ Falha ao criar budget: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ Erro ao criar budget: {e}")
            return {}
    
    def test_get_budget(self, budget_id: int) -> bool:
        """Testa obtenção de budget específico"""
        try:
            response = requests.get(f"{API_BASE}/budgets/{budget_id}", headers=self.headers)
            
            if response.status_code == 200:
                budget = response.json()
                print(f"✅ Budget obtido: {budget['budget_name']} - ${budget['budget_amount']}")
                return True
            else:
                print(f"❌ Falha ao obter budget: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao obter budget: {e}")
            return False
    
    def test_update_budget(self, budget_id: int) -> bool:
        """Testa atualização de budget"""
        try:
            updated_data = {
                "budget_name": f"Updated Test Budget {datetime.now().strftime('%H%M%S')}",
                "provider_name": "AWS",
                "service_name": "EC2",
                "budget_amount": 6000.00,
                "budget_period": "monthly",
                "alert_threshold": 85.0,
                "is_active": True,
                "tags": {
                    "environment": "test",
                    "updated_by": "api_test"
                }
            }
            
            response = requests.put(f"{API_BASE}/budgets/{budget_id}", json=updated_data, headers=self.headers)
            
            if response.status_code == 200:
                budget = response.json()
                print(f"✅ Budget atualizado: {budget['budget_name']} - ${budget['budget_amount']}")
                return True
            else:
                print(f"❌ Falha ao atualizar budget: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao atualizar budget: {e}")
            return False
    
    def test_budget_usage(self, budget_id: int) -> bool:
        """Testa endpoint de uso do budget"""
        try:
            response = requests.get(f"{API_BASE}/budgets/{budget_id}/usage", headers=self.headers)
            
            if response.status_code == 200:
                usage = response.json()
                print(f"✅ Uso do budget obtido: {usage['usage_percentage']:.2f}% usado")
                print(f"   Gasto atual: ${usage['current_spend']:.2f} de ${usage['budget_amount']:.2f}")
                return True
            else:
                print(f"❌ Falha ao obter uso do budget: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao obter uso do budget: {e}")
            return False
    
    def test_budget_alerts(self, budget_id: int) -> bool:
        """Testa endpoint de alertas do budget"""
        try:
            response = requests.get(f"{API_BASE}/budgets/{budget_id}/alerts", headers=self.headers)
            
            if response.status_code == 200:
                alerts = response.json()
                if alerts['has_alerts']:
                    print(f"⚠️  Budget tem {alerts['alert_count']} alertas")
                else:
                    print("✅ Budget dentro dos limites - sem alertas")
                return True
            else:
                print(f"❌ Falha ao verificar alertas: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao verificar alertas: {e}")
            return False
    
    def test_all_alerts(self) -> bool:
        """Testa endpoint de todos os alertas"""
        try:
            response = requests.get(f"{API_BASE}/budgets/alerts/all", headers=self.headers)
            
            if response.status_code == 200:
                alerts = response.json()
                print(f"✅ Alertas gerais obtidos: {alerts['total_alerts']} alertas encontrados")
                if alerts['summary']:
                    summary = alerts['summary']
                    print(f"   Críticos: {summary['critical_alerts']}, Avisos: {summary['warning_alerts']}")
                return True
            else:
                print(f"❌ Falha ao obter alertas gerais: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao obter alertas gerais: {e}")
            return False
    
    def test_delete_budget(self, budget_id: int) -> bool:
        """Testa exclusão de budget"""
        try:
            response = requests.delete(f"{API_BASE}/budgets/{budget_id}", headers=self.headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Budget deletado: {result['message']}")
                return True
            else:
                print(f"❌ Falha ao deletar budget: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao deletar budget: {e}")
            return False

def main():
    """Executa todos os testes"""
    print("🚀 Testando API de Budgets")
    print("=" * 50)
    
    tester = BudgetAPITester()
    
    # 1. Login
    print("\n1. Teste de Login")
    if not tester.login():
        print("❌ Não foi possível fazer login. Verifique se o servidor está rodando.")
        return
    
    # 2. Listar budgets existentes
    print("\n2. Teste de Listagem")
    tester.test_list_budgets()
    
    # 3. Criar novo budget
    print("\n3. Teste de Criação")
    new_budget = tester.test_create_budget()
    if not new_budget:
        print("❌ Não foi possível criar budget para testes subsequentes")
        return
    
    budget_id = new_budget.get('id')
    
    # 4. Obter budget específico
    print("\n4. Teste de Obtenção Específica")
    tester.test_get_budget(budget_id)
    
    # 5. Atualizar budget
    print("\n5. Teste de Atualização")
    tester.test_update_budget(budget_id)
    
    # 6. Verificar uso do budget
    print("\n6. Teste de Uso do Budget")
    tester.test_budget_usage(budget_id)
    
    # 7. Verificar alertas do budget
    print("\n7. Teste de Alertas Específicos")
    tester.test_budget_alerts(budget_id)
    
    # 8. Verificar todos os alertas
    print("\n8. Teste de Alertas Gerais")
    tester.test_all_alerts()
    
    # 9. Deletar budget de teste
    print("\n9. Teste de Exclusão")
    tester.test_delete_budget(budget_id)
    
    print("\n" + "=" * 50)
    print("🎉 Testes concluídos!")
    print("\n💡 Dicas:")
    print("  • Para ver todos os endpoints: http://localhost:8000/docs")
    print("  • Para acessar frontend: http://localhost:3000")

if __name__ == "__main__":
    main()
