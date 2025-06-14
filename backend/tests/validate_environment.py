#!/usr/bin/env python3
"""
🔧 Validador de Ambiente e Configuração - FinOps API
==================================================

Este script valida se o ambiente está configurado corretamente para executar
os testes da FinOps API:
- Verifica se todos os serviços estão rodando
- Valida conectividade com a API
- Testa autenticação
- Verifica dependências Python
- Gera relatório de saúde do ambiente

Uso:
    python validate_environment.py
    python validate_environment.py --detailed
    python validate_environment.py --fix-issues
"""

import requests
import subprocess
import sys
import time
import argparse
import logging
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import socket
import psutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnvironmentValidator:
    """Validador de ambiente para testes da FinOps API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.checks = []
        self.issues = []
        self.warnings = []
    
    def add_check(self, name: str, success: bool, message: str, fix_command: Optional[str] = None):
        """Adiciona resultado de uma verificação"""
        self.checks.append({
            "name": name,
            "success": success,
            "message": message,
            "fix_command": fix_command,
            "timestamp": datetime.now()
        })
        
        status = "✅" if success else "❌"
        logger.info(f"{status} {name}: {message}")
        
        if not success:
            self.issues.append({"name": name, "message": message, "fix_command": fix_command})
    
    def add_warning(self, name: str, message: str):
        """Adiciona um warning"""
        self.warnings.append({"name": name, "message": message})
        logger.warning(f"⚠️ {name}: {message}")
    
    def check_port_availability(self, port: int, service_name: str) -> bool:
        """Verifica se uma porta está acessível"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                result = sock.connect_ex(('localhost', port))
                return result == 0
        except Exception:
            return False
    
    def check_python_dependencies(self):
        """Verifica dependências Python necessárias"""
        required_packages = [
            "requests",
            "aiohttp",
            "psutil",
            "asyncio"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                self.add_check(
                    f"Python package: {package}",
                    True,
                    "Instalado"
                )
            except ImportError:
                missing_packages.append(package)
                self.add_check(
                    f"Python package: {package}",
                    False,
                    "Não instalado",
                    f"pip install {package}"
                )
        
        return len(missing_packages) == 0
    
    def check_container_services(self):
        """Verifica se os serviços de containers estão rodando"""
        services_to_check = [
            {"name": "PostgreSQL", "port": 5432},
            {"name": "Redis", "port": 6379},
            {"name": "LocalStack", "port": 4566},
            {"name": "FinOps API", "port": 8000}
        ]
        
        all_services_running = True
        
        for service in services_to_check:
            if self.check_port_availability(service["port"], service["name"]):
                self.add_check(
                    f"Serviço {service['name']}",
                    True,
                    f"Rodando na porta {service['port']}"
                )
            else:
                all_services_running = False
                # Verificar qual comando compose usar
                if hasattr(self, '_compose_cmd'):
                    fix_cmd = f"{self._compose_cmd} up -d"
                else:
                    fix_cmd = "podman-compose up -d (ou docker-compose up -d)"
                
                self.add_check(
                    f"Serviço {service['name']}",
                    False,
                    f"Não acessível na porta {service['port']}",
                    fix_cmd
                )
        
        return all_services_running
    
    def check_api_health(self):
        """Verifica se a API está saudável"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                overall_health = health_data.get("overall", False)
                
                if overall_health:
                    self.add_check(
                        "API Health Check",
                        True,
                        "API está saudável"
                    )
                    return True
                else:
                    # Verificar componentes específicos
                    failed_components = []
                    for key, value in health_data.items():
                        if key != "overall" and not value:
                            failed_components.append(key)
                    
                    self.add_check(
                        "API Health Check",
                        False,
                        f"Componentes falhando: {', '.join(failed_components)}",
                        "Verificar logs da aplicação"
                    )
                    return False
            else:
                self.add_check(
                    "API Health Check",
                    False,
                    f"API retornou status {response.status_code}",
                    "Verificar logs da aplicação"
                )
                return False
                
        except requests.RequestException as e:
            self.add_check(
                "API Health Check",
                False,
                f"Erro de conectividade: {str(e)}",
                "Verificar se a API está rodando"
            )
            return False
    
    def check_api_authentication(self):
        """Verifica se a autenticação está funcionando"""
        try:
            login_data = {
                "username": "admin",
                "password": "ChangeMe123!"
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/auth/login",
                json=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                
                if token:
                    self.add_check(
                        "API Authentication",
                        True,
                        "Login bem-sucedido"
                    )
                    
                    # Testar endpoint protegido
                    headers = {"Authorization": f"Bearer {token}"}
                    protected_response = requests.get(
                        f"{self.base_url}/api/v1/credentials",
                        headers=headers,
                        timeout=10
                    )
                    
                    if protected_response.status_code in [200, 401]:  # 401 é OK se não há credenciais
                        self.add_check(
                            "Protected Endpoint Access",
                            True,
                            "Acesso a endpoint protegido funcionando"
                        )
                        return True
                    else:
                        self.add_check(
                            "Protected Endpoint Access",
                            False,
                            f"Endpoint protegido retornou {protected_response.status_code}",
                            "Verificar configuração de autenticação"
                        )
                        return False
                else:
                    self.add_check(
                        "API Authentication",
                        False,
                        "Token não recebido na resposta",
                        "Verificar configuração JWT"
                    )
                    return False
            else:
                self.add_check(
                    "API Authentication",
                    False,
                    f"Login falhou com status {response.status_code}",
                    "Verificar credenciais padrão"
                )
                return False
                
        except requests.RequestException as e:
            self.add_check(
                "API Authentication",
                False,
                f"Erro de conectividade: {str(e)}",
                "Verificar se a API está rodando"
            )
            return False
    
    def check_system_resources(self):
        """Verifica recursos do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 80:
                self.add_check(
                    "CPU Usage",
                    True,
                    f"CPU em {cpu_percent:.1f}% (OK)"
                )
            else:
                self.add_warning(
                    "CPU Usage",
                    f"CPU em {cpu_percent:.1f}% (Alto)"
                )
            
            # Memória
            memory = psutil.virtual_memory()
            if memory.percent < 85:
                self.add_check(
                    "Memory Usage",
                    True,
                    f"Memória em {memory.percent:.1f}% (OK)"
                )
            else:
                self.add_warning(
                    "Memory Usage",
                    f"Memória em {memory.percent:.1f}% (Alto)"
                )
            
            # Disco
            disk = psutil.disk_usage('/')
            if disk.percent < 90:
                self.add_check(
                    "Disk Usage",
                    True,
                    f"Disco em {disk.percent:.1f}% (OK)"
                )
            else:
                self.add_warning(
                    "Disk Usage",
                    f"Disco em {disk.percent:.1f}% (Alto)"
                )
            
            return True
            
        except Exception as e:
            self.add_check(
                "System Resources",
                False,
                f"Erro ao verificar recursos: {str(e)}",
                "Instalar psutil: pip install psutil"
            )
            return False
    
    def check_network_connectivity(self):
        """Verifica conectividade de rede"""
        try:
            # Testar conectividade básica
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            response_time = response.elapsed.total_seconds()
            
            if response_time < 1.0:
                self.add_check(
                    "Network Latency",
                    True,
                    f"Latência: {response_time:.2f}s (Boa)"
                )
            elif response_time < 2.0:
                self.add_warning(
                    "Network Latency",
                    f"Latência: {response_time:.2f}s (Moderada)"
                )
            else:
                self.add_warning(
                    "Network Latency",
                    f"Latência: {response_time:.2f}s (Alta)"
                )
            
            return True
            
        except Exception as e:
            self.add_check(
                "Network Connectivity",
                False,
                f"Erro de rede: {str(e)}",
                "Verificar conectividade de rede"
            )
            return False
    
    def check_api_endpoints(self):
        """Verifica se os principais endpoints estão respondendo"""
        # Primeiro, fazer login
        try:
            login_data = {"username": "admin", "password": "ChangeMe123!"}
            login_response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
            
            if login_response.status_code != 200:
                self.add_check(
                    "API Endpoints Test",
                    False,
                    "Não foi possível fazer login para testar endpoints",
                    "Verificar autenticação"
                )
                return False
            
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            endpoints_to_test = [
                {"path": "/api/v1/credentials", "method": "GET"},
                {"path": "/api/v1/costs", "method": "GET"},
                {"path": "/api/v1/system/status", "method": "GET"},
                {"path": "/api/v1/audit/logs", "method": "GET"}
            ]
            
            successful_endpoints = 0
            
            for endpoint in endpoints_to_test:
                try:
                    if endpoint["method"] == "GET":
                        response = requests.get(
                            f"{self.base_url}{endpoint['path']}",
                            headers=headers,
                            timeout=10
                        )
                    
                    if response.status_code < 500:  # Não é erro do servidor
                        successful_endpoints += 1
                        
                except Exception:
                    pass  # Endpoint falhou
            
            if successful_endpoints == len(endpoints_to_test):
                self.add_check(
                    "API Endpoints",
                    True,
                    f"Todos os {len(endpoints_to_test)} endpoints principais funcionando"
                )
                return True
            else:
                self.add_check(
                    "API Endpoints",
                    False,
                    f"Apenas {successful_endpoints}/{len(endpoints_to_test)} endpoints funcionando",
                    "Verificar logs da aplicação"
                )
                return False
                
        except Exception as e:
            self.add_check(
                "API Endpoints Test",
                False,
                f"Erro ao testar endpoints: {str(e)}",
                "Verificar se a API está rodando"
            )
            return False
    
    def check_podman_compose(self):
        """Verifica se podman-compose está funcionando"""
        # Primeiro tenta podman-compose, depois docker-compose (para compatibilidade)
        compose_commands = ["podman-compose", "docker-compose"]
        
        for compose_cmd in compose_commands:
            try:
                result = subprocess.run(
                    [compose_cmd, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    self.add_check(
                        f"Container Compose ({compose_cmd})",
                        True,
                        f"Versão: {version}"
                    )
                    
                    # Verificar se os containers estão rodando
                    try:
                        result = subprocess.run(
                            [compose_cmd, "ps"],
                            capture_output=True,
                            text=True,
                            timeout=10,
                            cwd="."
                        )
                        
                        if "Up" in result.stdout or "running" in result.stdout.lower():
                            self.add_check(
                                "Container Services",
                                True,
                                "Containers em execução"
                            )
                        else:
                            self.add_check(
                                "Container Services",
                                False,
                                "Alguns containers não estão rodando",
                                f"{compose_cmd} up -d"
                            )
                            
                    except subprocess.TimeoutExpired:
                        self.add_warning(
                            "Container Services",
                            "Timeout ao verificar status dos containers"
                        )
                    
                    return True, compose_cmd
                    
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                continue
        
        # Se nenhum compose foi encontrado
        self.add_check(
            "Container Compose",
            False,
            "Nem podman-compose nem docker-compose encontrados",
            "Instalar podman-compose ou docker-compose"
        )
        return False, None
    
    def run_all_checks(self, detailed: bool = False):
        """Executa todas as verificações"""
        logger.info("🔧 Iniciando validação do ambiente...")
        
        # Verificações básicas
        self.check_python_dependencies()
        
        # Verificar compose e armazenar comando encontrado
        compose_ok, compose_cmd = self.check_podman_compose()
        if compose_ok:
            self._compose_cmd = compose_cmd
        
        self.check_system_resources()
        
        # Verificações de serviços
        self.check_container_services()
        self.check_network_connectivity()
        
        # Verificações da API
        api_healthy = self.check_api_health()
        if api_healthy:
            self.check_api_authentication()
            if detailed:
                self.check_api_endpoints()
        
        return len(self.issues) == 0
    
    def print_summary(self):
        """Imprime resumo das verificações"""
        successful_checks = sum(1 for check in self.checks if check["success"])
        total_checks = len(self.checks)
        
        print("\n" + "=" * 80)
        print("🔧 RELATÓRIO DE VALIDAÇÃO DO AMBIENTE")
        print("=" * 80)
        print(f"✅ Verificações bem-sucedidas: {successful_checks}/{total_checks}")
        print(f"❌ Problemas encontrados: {len(self.issues)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        
        if self.issues:
            print(f"\n❌ PROBLEMAS ENCONTRADOS:")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. {issue['name']}: {issue['message']}")
                if issue['fix_command']:
                    print(f"   Fix: {issue['fix_command']}")
        
        if self.warnings:
            print(f"\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"• {warning['name']}: {warning['message']}")
        
        # Status geral
        if len(self.issues) == 0:
            print(f"\n🎉 AMBIENTE VALIDADO COM SUCESSO!")
            print("Você pode executar os testes da FinOps API.")
        elif len(self.issues) <= 2:
            print(f"\n⚠️ AMBIENTE PARCIALMENTE VALIDADO")
            print("Alguns problemas menores foram encontrados, mas os testes podem funcionar.")
        else:
            print(f"\n❌ AMBIENTE COM PROBLEMAS")
            print("Corrija os problemas antes de executar os testes.")
        
        print("=" * 80)
    
    def fix_issues(self):
        """Tenta corrigir automaticamente alguns problemas"""
        logger.info("🔨 Tentando corrigir problemas automaticamente...")
        
        fixed_issues = 0
        
        for issue in self.issues:
            if issue['fix_command']:
                logger.info(f"Executando: {issue['fix_command']}")
                
                try:
                    if issue['fix_command'].startswith('pip install'):
                        # Instalar pacote Python
                        package = issue['fix_command'].split()[-1]
                        result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                              capture_output=True, text=True)
                        if result.returncode == 0:
                            logger.info(f"✅ {package} instalado com sucesso")
                            fixed_issues += 1
                        else:
                            logger.error(f"❌ Falha ao instalar {package}: {result.stderr}")
                    
                    elif 'compose up -d' in issue['fix_command']:
                        # Iniciar serviços de containers
                        # Detectar comando correto (podman-compose ou docker-compose)
                        if 'podman-compose' in issue['fix_command']:
                            cmd = ['podman-compose', 'up', '-d']
                        elif 'docker-compose' in issue['fix_command']:
                            cmd = ['docker-compose', 'up', '-d']
                        else:
                            # Tentar descobrir qual está disponível
                            try:
                                subprocess.run(['podman-compose', '--version'], capture_output=True)
                                cmd = ['podman-compose', 'up', '-d']
                            except FileNotFoundError:
                                cmd = ['docker-compose', 'up', '-d']
                        
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            logger.info("✅ Serviços de container iniciados")
                            fixed_issues += 1
                            time.sleep(15)  # Aguardar serviços iniciarem
                        else:
                            logger.error(f"❌ Falha ao iniciar serviços: {result.stderr}")
                    
                except Exception as e:
                    logger.error(f"❌ Erro ao executar comando: {e}")
        
        if fixed_issues > 0:
            logger.info(f"🔨 {fixed_issues} problemas corrigidos. Re-executando validação...")
            # Limpar verificações anteriores e re-executar
            self.checks = []
            self.issues = []
            self.warnings = []
            self.run_all_checks()

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Validar ambiente para testes da FinOps API")
    parser.add_argument("--base-url", default="http://localhost:8000", help="URL base da API")
    parser.add_argument("--detailed", action="store_true", help="Executar verificações detalhadas")
    parser.add_argument("--fix-issues", action="store_true", help="Tentar corrigir problemas automaticamente")
    
    args = parser.parse_args()
    
    print("🔧 VALIDADOR DE AMBIENTE - FINOPS API")
    print("=" * 80)
    
    validator = EnvironmentValidator(args.base_url)
    
    # Executar verificações
    environment_ok = validator.run_all_checks(detailed=args.detailed)
    
    # Tentar corrigir problemas se solicitado
    if args.fix_issues and not environment_ok:
        validator.fix_issues()
    
    # Mostrar resumo
    validator.print_summary()
    
    # Código de saída
    sys.exit(0 if len(validator.issues) == 0 else 1)

if __name__ == "__main__":
    main()
