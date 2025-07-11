#!/usr/bin/env python3
"""
Teste de performance para o endpoint de anomalies otimizado
"""

import asyncio
import httpx
import time
import json

async def test_anomalies_performance():
    """Testa a performance do endpoint de anomalies otimizado"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 TESTE DE PERFORMANCE - ANOMALIES ENDPOINT")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30) as client:
        # Autenticação
        login_data = {"username": "finops_admin", "password": "Password123!"}
        login_response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print("❌ Falha na autenticação")
            return
            
        token = login_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Teste 1: Primeira chamada (sem cache)
        print("\n🔸 Teste 1: Primeira chamada (sem cache)")
        start_time = time.time()
        
        response1 = await client.get(
            f"{base_url}/api/v1/anomalies",
            headers=headers,
            params={"per_page": 20}
        )
        
        end_time = time.time()
        time1 = end_time - start_time
        
        print(f"   Status: {response1.status_code}")
        print(f"   Tempo: {time1:.3f}s")
        
        if response1.status_code == 200:
            data1 = response1.json()
            anomalies_count = len(data1.get("data", {}).get("anomalies", []))
            print(f"   Anomalias retornadas: {anomalies_count}")
        
        # Teste 2: Segunda chamada (com cache)
        print("\n🔸 Teste 2: Segunda chamada (com cache)")
        start_time = time.time()
        
        response2 = await client.get(
            f"{base_url}/api/v1/anomalies",
            headers=headers,
            params={"per_page": 20}
        )
        
        end_time = time.time()
        time2 = end_time - start_time
        
        print(f"   Status: {response2.status_code}")
        print(f"   Tempo: {time2:.3f}s")
        print(f"   Speedup: {time1/time2:.1f}x mais rápido")
        
        # Teste 3: Chamada com filtros
        print("\n🔸 Teste 3: Chamada com filtros")
        start_time = time.time()
        
        response3 = await client.get(
            f"{base_url}/api/v1/anomalies",
            headers=headers,
            params={
                "provider": "AWS",
                "severity": "high",
                "per_page": 20
            }
        )
        
        end_time = time.time()
        time3 = end_time - start_time
        
        print(f"   Status: {response3.status_code}")
        print(f"   Tempo: {time3:.3f}s")
        
        if response3.status_code == 200:
            data3 = response3.json()
            filtered_count = len(data3.get("data", {}).get("anomalies", []))
            print(f"   Anomalias filtradas: {filtered_count}")
        
        # Teste 4: Verificar estatísticas do cache
        print("\n🔸 Teste 4: Estatísticas do cache")
        stats_response = await client.get(
            f"{base_url}/api/v1/cache/stats",
            headers=headers
        )
        
        if stats_response.status_code == 200:
            stats = stats_response.json()
            cache_stats = stats.get("data", {}).get("cache_stats", {})
            print(f"   Cache size: {cache_stats.get('cache_size', 0)}")
            print(f"   Cache keys: {len(cache_stats.get('cache_keys', []))}")
        
        # Teste 5: Múltiplas chamadas paralelas
        print("\n🔸 Teste 5: 5 chamadas paralelas")
        start_time = time.time()
        
        tasks = []
        for i in range(5):
            task = client.get(
                f"{base_url}/api/v1/anomalies",
                headers=headers,
                params={"per_page": 10, "page": i+1}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        end_time = time.time()
        parallel_time = end_time - start_time
        
        successful_requests = sum(1 for r in responses if r.status_code == 200)
        print(f"   Requisições bem-sucedidas: {successful_requests}/5")
        print(f"   Tempo total: {parallel_time:.3f}s")
        print(f"   Tempo médio por requisição: {parallel_time/5:.3f}s")
        
        # Comparação de performance
        print("\n📊 RESUMO DE PERFORMANCE:")
        print(f"   Primeira chamada: {time1:.3f}s")
        print(f"   Segunda chamada (cache): {time2:.3f}s") 
        print(f"   Melhoria de cache: {((time1-time2)/time1)*100:.1f}%")
        print(f"   Chamada com filtros: {time3:.3f}s")
        print(f"   Chamadas paralelas: {parallel_time/5:.3f}s média")
        
        if time2 < time1 * 0.8:
            print("✅ Cache funcionando efetivamente!")
        else:
            print("⚠️ Cache pode não estar otimizado")
        
        # Teste 6: Limpar cache
        print("\n🔸 Teste 6: Limpeza de cache")
        clear_response = await client.post(
            f"{base_url}/api/v1/cache/clear",
            headers=headers
        )
        
        if clear_response.status_code == 200:
            clear_data = clear_response.json()
            print("   ✅ Cache limpo com sucesso")
            before_size = clear_data.get("data", {}).get("cache_stats_before", {}).get("cache_size", 0)
            after_size = clear_data.get("data", {}).get("cache_stats_after", {}).get("cache_size", 0)
            print(f"   Cache antes: {before_size} itens")
            print(f"   Cache depois: {after_size} itens")

if __name__ == "__main__":
    asyncio.run(test_anomalies_performance())
