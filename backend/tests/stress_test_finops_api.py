#!/usr/bin/env python3
"""
🔥 Teste de Performance e Stress da X Cost API
==============================================

Este script executa testes específicos de performance e stress testing:
- Testes de carga progressiva
- Testes de stress de endpoints críticos
- Monitoramento de métricas de performance
- Análise de vazamentos de memória
- Testes de concorrência extrema

Uso:
    python stress_test_finops_api.py
    python stress_test_finops_api.py --duration 300 --max-concurrent 50
    python stress_test_finops_api.py --endpoint /api/v1/credentials
"""

import asyncio
import aiohttp
import argparse
import time
import statistics
import psutil
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
from urllib.parse import urljoin
import sys
import signal

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Métricas de performance"""
    endpoint: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    response_times: List[float] = field(default_factory=list)
    status_codes: Dict[int, int] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def avg_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return statistics.mean(self.response_times)
    
    @property
    def percentile_95(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(0.95 * len(sorted_times))
        return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]
    
    @property
    def percentile_99(self) -> float:
        if not self.response_times:
            return 0.0
        sorted_times = sorted(self.response_times)
        index = int(0.99 * len(sorted_times))
        return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]

@dataclass
class SystemMetrics:
    """Métricas do sistema"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_io_read: int
    disk_io_write: int
    network_sent: int
    network_recv: int

class FinOpsStressTester:
    """Testador de stress e performance da X Cost API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.system_metrics: List[SystemMetrics] = []
        self.running = True
        self.start_time = None
        
        # Configurar handler para interrupção
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para interrupção do usuário"""
        logger.info("🛑 Recebido sinal de interrupção, finalizando testes...")
        self.running = False
    
    async def authenticate(self) -> bool:
        """Autentica e obtém token de acesso"""
        try:
            async with aiohttp.ClientSession() as session:
                login_data = {
                    "username": "admin",
                    "password": "ChangeMe123!"
                }
                
                url = urljoin(self.base_url, "/api/v1/auth/login")
                async with session.post(url, json=login_data) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.access_token = data.get("access_token")
                        logger.info("✅ Autenticação bem-sucedida")
                        return True
                    else:
                        logger.error(f"❌ Falha na autenticação: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {e}")
            return False
    
    def get_headers(self) -> Dict[str, str]:
        """Retorna headers com autenticação"""
        headers = {"Content-Type": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    async def collect_system_metrics(self):
        """Coleta métricas do sistema em background"""
        logger.info("📊 Iniciando coleta de métricas do sistema...")
        
        while self.running:
            try:
                # CPU
                cpu_percent = psutil.cpu_percent(interval=1)
                
                # Memória
                memory = psutil.virtual_memory()
                
                # Disco I/O
                disk_io = psutil.disk_io_counters()
                
                # Rede
                network_io = psutil.net_io_counters()
                
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    memory_used_mb=memory.used / (1024 * 1024),
                    disk_io_read=disk_io.read_bytes if disk_io else 0,
                    disk_io_write=disk_io.write_bytes if disk_io else 0,
                    network_sent=network_io.bytes_sent if network_io else 0,
                    network_recv=network_io.bytes_recv if network_io else 0
                )
                
                self.system_metrics.append(metrics)
                
            except Exception as e:
                logger.warning(f"⚠️ Erro ao coletar métricas do sistema: {e}")
            
            await asyncio.sleep(5)  # Coleta a cada 5 segundos
    
    async def make_request(self, session: aiohttp.ClientSession, endpoint: str, method: str = "GET", **kwargs) -> Dict[str, Any]:
        """Faz uma requisição e registra métricas"""
        start_time = time.time()
        
        try:
            url = urljoin(self.base_url, endpoint)
            headers = self.get_headers()
            
            async with session.request(method, url, headers=headers, **kwargs) as response:
                response_time = time.time() - start_time
                
                # Atualizar métricas
                if endpoint not in self.metrics:
                    self.metrics[endpoint] = PerformanceMetrics(endpoint=endpoint)
                
                metrics = self.metrics[endpoint]
                metrics.total_requests += 1
                metrics.response_times.append(response_time)
                
                # Contar status codes
                if response.status not in metrics.status_codes:
                    metrics.status_codes[response.status] = 0
                metrics.status_codes[response.status] += 1
                
                if response.status < 400:
                    metrics.successful_requests += 1
                else:
                    metrics.failed_requests += 1
                    if response.status >= 500:
                        metrics.errors.append(f"HTTP {response.status} at {datetime.now()}")
                
                return {
                    "status": response.status,
                    "response_time": response_time,
                    "success": response.status < 400
                }
                
        except Exception as e:
            response_time = time.time() - start_time
            
            if endpoint not in self.metrics:
                self.metrics[endpoint] = PerformanceMetrics(endpoint=endpoint)
            
            metrics = self.metrics[endpoint]
            metrics.total_requests += 1
            metrics.failed_requests += 1
            metrics.response_times.append(response_time)
            metrics.errors.append(f"Exception: {str(e)} at {datetime.now()}")
            
            return {
                "status": 0,
                "response_time": response_time,
                "success": False,
                "error": str(e)
            }
    
    async def progressive_load_test(self, endpoint: str, max_concurrent: int = 50, step: int = 5, duration_per_step: int = 30):
        """Teste de carga progressiva"""
        logger.info(f"🔥 Iniciando teste de carga progressiva para {endpoint}")
        logger.info(f"   Máximo concurrent: {max_concurrent}")
        logger.info(f"   Incremento: {step}")
        logger.info(f"   Duração por step: {duration_per_step}s")
        
        for concurrent_users in range(step, max_concurrent + 1, step):
            if not self.running:
                break
                
            logger.info(f"📈 Testando com {concurrent_users} usuários concorrentes...")
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                connector=aiohttp.TCPConnector(limit=concurrent_users * 2)
            ) as session:
                
                # Executar testes por duração especificada
                end_time = time.time() + duration_per_step
                tasks = []
                
                while time.time() < end_time and self.running:
                    # Manter número de tasks ativas
                    while len(tasks) < concurrent_users and self.running:
                        task = asyncio.create_task(
                            self.make_request(session, endpoint)
                        )
                        tasks.append(task)
                    
                    # Aguardar algumas tasks completarem
                    if tasks:
                        done, pending = await asyncio.wait(
                            tasks, 
                            timeout=1.0, 
                            return_when=asyncio.FIRST_COMPLETED
                        )
                        
                        # Remover tasks concluídas
                        for task in done:
                            tasks.remove(task)
                
                # Aguardar tasks restantes
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)
            
            # Mostrar métricas do step atual
            if endpoint in self.metrics:
                metrics = self.metrics[endpoint]
                logger.info(f"   ✅ {concurrent_users} usuários: "
                          f"{metrics.success_rate:.1f}% sucesso, "
                          f"{metrics.avg_response_time:.2f}s tempo médio")
            
            # Pausa entre steps
            if concurrent_users < max_concurrent:
                await asyncio.sleep(5)
    
    async def stress_test_endpoint(self, endpoint: str, concurrent: int = 20, duration: int = 300):
        """Teste de stress para um endpoint específico"""
        logger.info(f"💥 Iniciando teste de stress para {endpoint}")
        logger.info(f"   Usuários concorrentes: {concurrent}")
        logger.info(f"   Duração: {duration}s")
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            connector=aiohttp.TCPConnector(limit=concurrent * 2)
        ) as session:
            
            end_time = time.time() + duration
            tasks = []
            
            while time.time() < end_time and self.running:
                # Manter tasks ativas
                while len(tasks) < concurrent and self.running:
                    task = asyncio.create_task(
                        self.make_request(session, endpoint)
                    )
                    tasks.append(task)
                
                # Aguardar algumas tasks
                if tasks:
                    done, pending = await asyncio.wait(
                        tasks,
                        timeout=0.1,
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for task in done:
                        tasks.remove(task)
                
                # Log periódico
                elapsed = time.time() - (end_time - duration)
                if int(elapsed) % 30 == 0:  # A cada 30 segundos
                    if endpoint in self.metrics:
                        metrics = self.metrics[endpoint]
                        logger.info(f"   📊 {elapsed:.0f}s: "
                                  f"{metrics.total_requests} reqs, "
                                  f"{metrics.success_rate:.1f}% sucesso, "
                                  f"{metrics.avg_response_time:.2f}s médio")
            
            # Finalizar tasks restantes
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def critical_endpoints_test(self, duration: int = 180):
        """Teste dos endpoints críticos simultaneamente"""
        logger.info("🎯 Iniciando teste de endpoints críticos")
        
        critical_endpoints = [
            "/api/v1/health",
            "/api/v1/auth/login",
            "/api/v1/credentials",
            "/api/v1/costs",
            "/api/v1/system/status"
        ]
        
        # Criar tasks para cada endpoint
        tasks = []
        for endpoint in critical_endpoints:
            if endpoint == "/api/v1/auth/login":
                # Login usa POST
                task = asyncio.create_task(
                    self.login_stress_test(duration)
                )
            else:
                task = asyncio.create_task(
                    self.stress_test_endpoint(endpoint, concurrent=10, duration=duration)
                )
            tasks.append(task)
        
        # Executar todos simultaneamente
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def login_stress_test(self, duration: int):
        """Teste de stress específico para login"""
        logger.info("🔐 Iniciando teste de stress para login")
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            
            end_time = time.time() + duration
            
            while time.time() < end_time and self.running:
                await self.make_request(
                    session,
                    "/api/v1/auth/login",
                    method="POST",
                    json={
                        "username": "admin",
                        "password": "ChangeMe123!"
                    }
                )
                
                # Pequena pausa para não sobrecarregar
                await asyncio.sleep(0.1)
    
    async def memory_leak_test(self, endpoint: str, duration: int = 600):
        """Teste para detectar vazamentos de memória"""
        logger.info(f"🔍 Iniciando teste de vazamento de memória para {endpoint}")
        
        initial_memory = psutil.virtual_memory().used / (1024 * 1024)
        logger.info(f"   Memória inicial: {initial_memory:.1f} MB")
        
        request_count = 0
        start_time = time.time()
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            
            while time.time() - start_time < duration and self.running:
                await self.make_request(session, endpoint)
                request_count += 1
                
                # Verificar memória a cada 100 requisições
                if request_count % 100 == 0:
                    current_memory = psutil.virtual_memory().used / (1024 * 1024)
                    memory_growth = current_memory - initial_memory
                    
                    logger.info(f"   📊 {request_count} reqs: "
                              f"{current_memory:.1f} MB "
                              f"(+{memory_growth:.1f} MB)")
                    
                    # Alerta se crescimento excessivo
                    if memory_growth > 500:  # Mais de 500MB
                        logger.warning(f"⚠️ Possível vazamento de memória detectado: +{memory_growth:.1f} MB")
                
                await asyncio.sleep(0.01)  # Pequena pausa
        
        final_memory = psutil.virtual_memory().used / (1024 * 1024)
        total_growth = final_memory - initial_memory
        
        logger.info(f"🔍 Teste de vazamento concluído:")
        logger.info(f"   Requisições: {request_count}")
        logger.info(f"   Memória inicial: {initial_memory:.1f} MB")
        logger.info(f"   Memória final: {final_memory:.1f} MB")
        logger.info(f"   Crescimento total: {total_growth:.1f} MB")
    
    def print_live_metrics(self):
        """Imprime métricas em tempo real"""
        while self.running:
            # Limpar terminal (funciona na maioria dos sistemas)
            print("\033[2J\033[H")
            
            print("🔥 MÉTRICAS DE STRESS TEST EM TEMPO REAL")
            print("=" * 80)
            
            if self.start_time:
                elapsed = time.time() - self.start_time
                print(f"⏱️ Tempo decorrido: {elapsed:.0f}s")
            
            print()
            
            # Métricas por endpoint
            for endpoint, metrics in self.metrics.items():
                print(f"📊 {endpoint}")
                print(f"   Total: {metrics.total_requests} | "
                      f"Sucesso: {metrics.success_rate:.1f}% | "
                      f"Médio: {metrics.avg_response_time:.2f}s")
                print(f"   P95: {metrics.percentile_95:.2f}s | "
                      f"P99: {metrics.percentile_99:.2f}s")
                
                if metrics.errors:
                    print(f"   ❌ Últimos erros: {len(metrics.errors)}")
                print()
            
            # Métricas do sistema (últimas)
            if self.system_metrics:
                latest = self.system_metrics[-1]
                print(f"🖥️ SISTEMA:")
                print(f"   CPU: {latest.cpu_percent:.1f}% | "
                      f"Memória: {latest.memory_percent:.1f}% "
                      f"({latest.memory_used_mb:.1f} MB)")
                print()
            
            print("Pressione Ctrl+C para parar...")
            print("=" * 80)
            
            time.sleep(5)
    
    def generate_final_report(self):
        """Gera relatório final"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO FINAL DE STRESS TEST")
        print("=" * 80)
        
        if self.start_time:
            total_duration = time.time() - self.start_time
            print(f"⏱️ Duração total: {total_duration:.1f}s")
            print()
        
        # Relatório por endpoint
        for endpoint, metrics in self.metrics.items():
            print(f"🎯 {endpoint}")
            print(f"   Total de requisições: {metrics.total_requests}")
            print(f"   Taxa de sucesso: {metrics.success_rate:.1f}%")
            print(f"   Tempo médio de resposta: {metrics.avg_response_time:.2f}s")
            print(f"   P95: {metrics.percentile_95:.2f}s")
            print(f"   P99: {metrics.percentile_99:.2f}s")
            
            if metrics.response_times:
                print(f"   Min: {min(metrics.response_times):.2f}s")
                print(f"   Max: {max(metrics.response_times):.2f}s")
            
            print(f"   Status codes: {dict(metrics.status_codes)}")
            
            if metrics.errors:
                print(f"   ❌ Erros: {len(metrics.errors)}")
                # Mostrar últimos 3 erros
                for error in metrics.errors[-3:]:
                    print(f"      • {error}")
            
            print()
        
        # Métricas do sistema
        if self.system_metrics:
            cpu_values = [m.cpu_percent for m in self.system_metrics]
            memory_values = [m.memory_percent for m in self.system_metrics]
            
            print("🖥️ MÉTRICAS DO SISTEMA:")
            print(f"   CPU médio: {statistics.mean(cpu_values):.1f}%")
            print(f"   CPU máximo: {max(cpu_values):.1f}%")
            print(f"   Memória média: {statistics.mean(memory_values):.1f}%")
            print(f"   Memória máxima: {max(memory_values):.1f}%")
            print()
        
        # Recommendations
        print("💡 RECOMENDAÇÕES:")
        
        total_requests = sum(m.total_requests for m in self.metrics.values())
        total_failures = sum(m.failed_requests for m in self.metrics.values())
        overall_success_rate = ((total_requests - total_failures) / total_requests * 100) if total_requests > 0 else 0
        
        if overall_success_rate < 95:
            print("   ⚠️ Taxa de sucesso baixa - investigar erros e otimizar performance")
        
        avg_response_times = [m.avg_response_time for m in self.metrics.values() if m.response_times]
        if avg_response_times and max(avg_response_times) > 2.0:
            print("   ⚠️ Tempos de resposta altos detectados - otimizar endpoints lentos")
        
        if self.system_metrics:
            max_cpu = max(m.cpu_percent for m in self.system_metrics)
            max_memory = max(m.memory_percent for m in self.system_metrics)
            
            if max_cpu > 80:
                print("   ⚠️ Alto uso de CPU detectado - verificar gargalos de processamento")
            
            if max_memory > 85:
                print("   ⚠️ Alto uso de memória detectado - verificar vazamentos")
        
        print("=" * 80)

async def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Teste de stress da X Cost API")
    parser.add_argument("--base-url", default="http://localhost:8000", help="URL base da API")
    parser.add_argument("--endpoint", help="Endpoint específico para testar")
    parser.add_argument("--duration", type=int, default=300, help="Duração do teste em segundos")
    parser.add_argument("--max-concurrent", type=int, default=30, help="Máximo de usuários concorrentes")
    parser.add_argument("--test-type", choices=[
        "progressive", "stress", "critical", "memory-leak", "all"
    ], default="progressive", help="Tipo de teste")
    parser.add_argument("--no-system-metrics", action="store_true", help="Desabilitar coleta de métricas do sistema")
    
    args = parser.parse_args()
    
    # Verificar se psutil está disponível
    try:
        import psutil
    except ImportError:
        logger.error("❌ psutil não está instalado. Execute: pip install psutil")
        sys.exit(1)
    
    print("🔥 TESTADOR DE STRESS E PERFORMANCE - X COST API")
    print("=" * 80)
    print(f"URL Base: {args.base_url}")
    print(f"Tipo de teste: {args.test_type}")
    print(f"Duração: {args.duration}s")
    print(f"Max concorrente: {args.max_concurrent}")
    print("=" * 80)
    
    # Criar tester
    tester = FinOpsStressTester(args.base_url)
    
    # Autenticar
    if not await tester.authenticate():
        logger.error("❌ Falha na autenticação. Verifique se a API está rodando.")
        sys.exit(1)
    
    tester.start_time = time.time()
    
    # Tasks em background
    background_tasks = []
    
    # Coleta de métricas do sistema
    if not args.no_system_metrics:
        metrics_task = asyncio.create_task(tester.collect_system_metrics())
        background_tasks.append(metrics_task)
    
    try:
        # Executar teste baseado no tipo
        if args.test_type == "progressive":
            if args.endpoint:
                await tester.progressive_load_test(
                    args.endpoint,
                    max_concurrent=args.max_concurrent,
                    duration_per_step=min(30, args.duration // 5)
                )
            else:
                await tester.progressive_load_test(
                    "/api/v1/health",
                    max_concurrent=args.max_concurrent,
                    duration_per_step=min(30, args.duration // 5)
                )
        
        elif args.test_type == "stress":
            endpoint = args.endpoint or "/api/v1/credentials"
            await tester.stress_test_endpoint(
                endpoint,
                concurrent=args.max_concurrent,
                duration=args.duration
            )
        
        elif args.test_type == "critical":
            await tester.critical_endpoints_test(args.duration)
        
        elif args.test_type == "memory-leak":
            endpoint = args.endpoint or "/api/v1/health"
            await tester.memory_leak_test(endpoint, args.duration)
        
        elif args.test_type == "all":
            # Executar todos os tipos de teste
            logger.info("🎯 Executando bateria completa de testes...")
            
            # 1. Teste progressivo
            await tester.progressive_load_test("/api/v1/health", max_concurrent=20, duration_per_step=30)
            
            # 2. Teste de stress em endpoints críticos
            await tester.critical_endpoints_test(120)
            
            # 3. Teste de vazamento de memória
            await tester.memory_leak_test("/api/v1/credentials", 180)
    
    except KeyboardInterrupt:
        logger.info("🛑 Testes interrompidos pelo usuário")
    
    except Exception as e:
        logger.error(f"💥 Erro durante os testes: {e}")
    
    finally:
        # Parar coleta de métricas
        tester.running = False
        
        # Aguardar tasks em background
        for task in background_tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        # Gerar relatório final
        tester.generate_final_report()

if __name__ == "__main__":
    asyncio.run(main())
