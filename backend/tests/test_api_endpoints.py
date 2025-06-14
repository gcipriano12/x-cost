#!/usr/bin/env python3
"""
🧪 Teste Completo dos Endpoints da API
=====================================

Este script testa todos os principais endpoints da API FinOps
após a população de dados.

Uso:
    python test_api_endpoints.py
    python test_api_endpoints.py --base-url http://localhost:8000
"""

import requests
import json
import argparse
import sys
from datetime import datetime, timedelta

class FinOpsAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.session = requests.Session()
        
    def print_result(self, test_name, success, details=""):
        """Imprimir resultado do teste"""
        status = "✅" if success else "❌"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
    
    def test_health_check(self):
        """Testar health check"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/health")
            
            if response.status_code == 200:
                data = response.json()
                overall_health = data.get("overall", False)
                
                if overall_health:
                    self.print_result("Health Check", True, f"Status: {response.status_code}")
                    return True
                else:
                    self.print_result("Health Check", False, f"Sistema não está saudável: {data}")
                    return False
            else:
                self.print_result("Health Check", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Health Check", False, f"Erro: {e}")
            return False
    
    def test_authentication(self):
        """Testar autenticação"""
        try:
            login_data = {
                "username": "admin",
                "password": "ChangeMe123!"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                
                if self.access_token:
                    # Configurar headers para próximas requisições
                    self.session.headers.update({
                        "Authorization": f"Bearer {self.access_token}"
                    })
                    
                    user_info = data.get("user", {})
                    self.print_result(
                        "Autenticação", 
                        True, 
                        f"Usuário: {user_info.get('username')} ({user_info.get('role')})"
                    )
                    return True
                else:
                    self.print_result("Autenticação", False, "Token não recebido")
                    return False
            else:
                self.print_result("Autenticação", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Autenticação", False, f"Erro: {e}")
            return False
    
    def test_credentials_list(self):
        """Testar listagem de credenciais"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/credentials")
            
            if response.status_code == 200:
                data = response.json()
                credential_count = len(data)
                
                self.print_result(
                    "Listar Credenciais", 
                    True, 
                    f"{credential_count} credenciais encontradas"
                )
                
                # Mostrar detalhes das credenciais
                for cred in data[:3]:  # Primeiras 3
                    print(f"   • {cred.get('name')} ({cred.get('provider_type')}) - {cred.get('status')}")
                
                return True
            else:
                self.print_result("Listar Credenciais", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Listar Credenciais", False, f"Erro: {e}")
            return False
    
    def test_costs_data(self):
        """Testar dados de custo"""
        try:
            # Testar sem filtros
            response = self.session.get(f"{self.base_url}/api/v1/costs?limit=10")
            
            if response.status_code == 200:
                data = response.json()
                cost_count = len(data)
                
                if cost_count > 0:
                    total_cost = sum(float(record.get('effective_cost', 0)) for record in data)
                    
                    self.print_result(
                        "Dados de Custo", 
                        True, 
                        f"{cost_count} registros (Total: ${total_cost:.2f})"
                    )
                    
                    # Mostrar detalhes dos primeiros registros
                    for record in data[:2]:
                        provider = record.get('provider_name')
                        service = record.get('service_name')
                        cost = record.get('effective_cost', 0)
                        date = record.get('billing_period_start', 'N/A')
                        print(f"   • {provider} - {service}: ${cost} ({date})")
                    
                    return True
                else:
                    self.print_result("Dados de Custo", False, "Nenhum dado de custo encontrado")
                    return False
            else:
                self.print_result("Dados de Custo", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Dados de Custo", False, f"Erro: {e}")
            return False
    
    def test_analytics_trend(self):
        """Testar análise de tendência"""
        try:
            # Definir período dos últimos 30 dias
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            params = {
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "period": "daily"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/analytics/trend",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                trend_data = data.get("trend_data", [])
                
                if trend_data:
                    total_days = len(trend_data)
                    total_cost = sum(float(day.get('total_cost', 0)) for day in trend_data)
                    avg_daily = total_cost / total_days if total_days > 0 else 0
                    
                    self.print_result(
                        "Análise de Tendência", 
                        True, 
                        f"{total_days} dias analisados (Média diária: ${avg_daily:.2f})"
                    )
                    
                    # Mostrar últimos 3 dias
                    for day in trend_data[-3:]:
                        period = day.get('period')
                        cost = day.get('total_cost', 0)
                        trend = day.get('trend_percentage')
                        trend_str = f" ({trend:+.1f}%)" if trend else ""
                        print(f"   • {period}: ${cost:.2f}{trend_str}")
                    
                    return True
                else:
                    self.print_result("Análise de Tendência", False, "Nenhum dado de tendência")
                    return False
            else:
                self.print_result("Análise de Tendência", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Análise de Tendência", False, f"Erro: {e}")
            return False
    
    def test_cost_forecast(self):
        """Testar previsão de custos"""
        try:
            params = {
                "forecast_days": 30,
                "historical_days": 60
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/analytics/forecast",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "error" not in data:
                    total_forecast = data.get("total_forecasted_cost", 0)
                    avg_daily = data.get("average_daily_forecast", 0)
                    accuracy = data.get("model_accuracy", {})
                    r2 = accuracy.get("r_squared", 0)
                    
                    self.print_result(
                        "Previsão de Custos", 
                        True, 
                        f"Previsão 30 dias: ${total_forecast:.2f} (R²: {r2:.3f})"
                    )
                    
                    print(f"   • Média diária prevista: ${avg_daily:.2f}")
                    print(f"   • Precisão do modelo: {r2:.1%}")
                    
                    return True
                else:
                    error_msg = data.get("error", "Erro desconhecido")
                    self.print_result("Previsão de Custos", False, f"Erro: {error_msg}")
                    return False
            else:
                self.print_result("Previsão de Custos", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Previsão de Custos", False, f"Erro: {e}")
            return False
    
    def test_cost_by_service(self):
        """Testar análise por serviço"""
        try:
            params = {
                "top_n": 5
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/analytics/by-service",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    total_analyzed = sum(float(service.get('total_cost', 0)) for service in data)
                    
                    self.print_result(
                        "Análise por Serviço", 
                        True, 
                        f"Top 5 serviços (Total: ${total_analyzed:.2f})"
                    )
                    
                    # Mostrar top serviços
                    for i, service in enumerate(data, 1):
                        provider = service.get('provider_name')
                        service_name = service.get('service_name')
                        cost = service.get('total_cost', 0)
                        percentage = service.get('percentage_of_total', 0)
                        print(f"   {i}. {provider} - {service_name}: ${cost:.2f} ({percentage:.1f}%)")
                    
                    return True
                else:
                    self.print_result("Análise por Serviço", False, "Nenhum dado de serviço")
                    return False
            else:
                self.print_result("Análise por Serviço", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Análise por Serviço", False, f"Erro: {e}")
            return False
    
    def test_system_status(self):
        """Testar status do sistema"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/system/status")
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar componentes do sistema
                system_health = data.get("system_health", {})
                credential_stats = data.get("credential_stats", {})
                user_stats = data.get("user_stats", {})
                
                health_ok = system_health.get("overall", False)
                total_credentials = credential_stats.get("total", 0)
                total_users = user_stats.get("total_users", 0)
                
                self.print_result(
                    "Status do Sistema", 
                    health_ok, 
                    f"Credenciais: {total_credentials}, Usuários: {total_users}"
                )
                
                # Mostrar detalhes da saúde
                if "database" in system_health:
                    db_status = "✅" if system_health["database"] else "❌"
                    print(f"   • Database: {db_status}")
                
                if "cache" in system_health:
                    cache_status = "✅" if system_health["cache"] else "❌"
                    print(f"   • Cache: {cache_status}")
                
                return health_ok
            else:
                self.print_result("Status do Sistema", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Status do Sistema", False, f"Erro: {e}")
            return False
    
    def test_providers_status(self):
        """Testar status dos provedores"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/providers/status")
            
            if response.status_code == 200:
                data = response.json()
                providers = data.get("providers", {})
                total_configured = data.get("total_configured", 0)
                
                self.print_result(
                    "Status dos Provedores", 
                    True, 
                    f"{total_configured} provedores configurados"
                )
                
                # Mostrar status de cada provedor
                for provider, status in providers.items():
                    active_creds = status.get("active_credentials", 0)
                    total_creds = status.get("total_credentials", 0)
                    provider_status = status.get("status", "unknown")
                    
                    status_icon = "✅" if provider_status == "configured" else "⚠️"
                    print(f"   {status_icon} {provider}: {active_creds}/{total_creds} credenciais ativas")
                
                return True
            else:
                self.print_result("Status dos Provedores", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Status dos Provedores", False, f"Erro: {e}")
            return False
    
    def test_create_credential(self):
        """Testar criação de credencial (teste básico)"""
        try:
            test_credential = {
                "name": f"test-credential-{int(datetime.now().timestamp())}",
                "description": "Credencial de teste criada automaticamente",
                "provider_type": "AWS",
                "credentials": {
                    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
                    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                    "region": "us-east-1",
                    "account_id": "123456789012"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/credentials",
                json=test_credential
            )
            
            if response.status_code == 201:
                data = response.json()
                credential_id = data.get("id")
                
                self.print_result(
                    "Criar Credencial", 
                    True, 
                    f"Credencial criada: {data.get('name')} (ID: {credential_id})"
                )
                
                # Tentar deletar a credencial de teste
                if credential_id:
                    delete_response = self.session.delete(
                        f"{self.base_url}/api/v1/credentials/{credential_id}"
                    )
                    if delete_response.status_code == 200:
                        print("   • Credencial de teste removida")
                
                return True
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    error_detail = error_data.get("detail", "")
                except:
                    error_detail = response.text
                
                self.print_result(
                    "Criar Credencial", 
                    False, 
                    f"Status: {response.status_code} - {error_detail}"
                )
                return False
                
        except Exception as e:
            self.print_result("Criar Credencial", False, f"Erro: {e}")
            return False
    
    def test_cost_filters(self):
        """Testar filtros de custo"""
        try:
            # Testar filtro por provedor
            params = {
                "provider_name": "AWS",
                "limit": 5
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/costs",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se todos os resultados são do AWS
                aws_only = all(record.get('provider_name') == 'AWS' for record in data)
                
                self.print_result(
                    "Filtros de Custo", 
                    aws_only, 
                    f"{len(data)} registros AWS filtrados"
                )
                
                return aws_only
            else:
                self.print_result("Filtros de Custo", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Filtros de Custo", False, f"Erro: {e}")
            return False
    
    def run_all_tests(self):
        """Executar todos os testes"""
        print("🧪 TESTANDO ENDPOINTS DA API FINOPS")
        print("=" * 50)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Autenticação", self.test_authentication),
            ("Credenciais", self.test_credentials_list),
            ("Dados de Custo", self.test_costs_data),
            ("Filtros de Custo", self.test_cost_filters),
            ("Análise de Tendência", self.test_analytics_trend),
            ("Previsão de Custos", self.test_cost_forecast),
            ("Análise por Serviço", self.test_cost_by_service),
            ("Status do Sistema", self.test_system_status),
            ("Status dos Provedores", self.test_providers_status),
            ("Criar Credencial", self.test_create_credential),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testando: {test_name}")
            try:
                success = test_func()
                results.append((test_name, success))
            except Exception as e:
                print(f"❌ {test_name}: Erro inesperado - {e}")
                results.append((test_name, False))
        
        # Resumo final
        print("\n" + "=" * 50)
        print("📊 RESUMO DOS TESTES")
        print("=" * 50)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"{test_name:25} {status}")
        
        print("=" * 50)
        print(f"📈 RESULTADO FINAL: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM! API está funcionando perfeitamente.")
        elif passed >= total * 0.8:
            print("⚠️ A maioria dos testes passou. Verifique os que falharam.")
        else:
            print("❌ Muitos testes falharam. Verifique a configuração da API.")
        
        return passed == total

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Testar endpoints da API FinOps")
    parser.add_argument(
        "--base-url", 
        default="http://localhost:8000",
        help="URL base da API (padrão: http://localhost:8000)"
    )
    parser.add_argument(
        "--single-test",
        choices=[
            "health", "auth", "credentials", "costs", "filters", 
            "trend", "forecast", "service", "system", "providers", "create"
        ],
        help="Executar apenas um teste específico"
    )
    
    args = parser.parse_args()
    
    tester = FinOpsAPITester(args.base_url)
    
    # Verificar se API está respondendo
    print(f"🔗 Testando API em: {args.base_url}")
    
    if args.single_test:
        # Executar teste específico
        test_map = {
            "health": tester.test_health_check,
            "auth": tester.test_authentication,
            "credentials": tester.test_credentials_list,
            "costs": tester.test_costs_data,
            "filters": tester.test_cost_filters,
            "trend": tester.test_analytics_trend,
            "forecast": tester.test_cost_forecast,
            "service": tester.test_cost_by_service,
            "system": tester.test_system_status,
            "providers": tester.test_providers_status,
            "create": tester.test_create_credential,
        }
        
        if args.single_test in test_map:
            # Para testes que precisam de auth, fazer login primeiro
            if args.single_test != "health":
                print("🔐 Fazendo login...")
                if not tester.test_authentication():
                    print("❌ Falha na autenticação. Não é possível continuar.")
                    return 1
            
            print(f"🧪 Executando teste: {args.single_test}")
            success = test_map[args.single_test]()
            
            if success:
                print("✅ Teste passou!")
                return 0
            else:
                print("❌ Teste falhou!")
                return 1
        else:
            print(f"❌ Teste '{args.single_test}' não encontrado")
            return 1
    else:
        # Executar todos os testes
        success = tester.run_all_tests()
        return 0 if success else 1

if __name__ == "__main__":
    exit(main())