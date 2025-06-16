#!/usr/bin/env python3
"""
Script para testar se o serviço de otimização está gerando dados mockados corretamente
"""

import asyncio
import os
import sys

# Adicionar o diretório atual ao PYTHONPATH
sys.path.insert(0, '/Users/gcipriano/Repositories/x-cost/backend')

os.environ['USE_LOCALSTACK'] = 'true'
os.environ['LOCALSTACK_ENDPOINT'] = 'http://localhost:4566'

async def test_optimization_service():
    """Testa se o serviço de otimização está funcionando"""
    try:
        print("🔧 Testando serviço de otimização...")
        
        # Importar e criar o serviço
        from app.cloud_native_optimization import create_optimization_service
        import redis
        
        # Criar cliente Redis (pode falhar, mas o serviço deve funcionar mesmo assim)
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            redis_client.ping()
            print("✅ Redis conectado")
        except:
            print("⚠️ Redis não disponível, usando fallback")
            redis_client = None
        
        # Carregar configuração
        config = {
            'aws': {
                'enabled': True,
                'use_localstack': True,
                'region': 'us-east-1'
            }
        }
        
        # Criar serviço
        service = create_optimization_service(redis_client, config)
        print(f"✅ Serviço criado: {type(service)}")
        
        # Testar anomalias
        print("🔍 Testando anomalias...")
        anomalies = await service.get_anomalies_by_provider()
        print(f"📊 Anomalias encontradas: {len(anomalies)}")
        
        if anomalies:
            print("🎯 Primeira anomalia:")
            anomaly = anomalies[0]
            print(f"   ID: {anomaly.id}")
            print(f"   Provider: {anomaly.provider}")
            print(f"   Severity: {anomaly.severity}")
            print(f"   Cost Impact: ${anomaly.cost_impact}")
            print(f"   Description: {anomaly.description}")
        
        # Testar savings opportunities
        print("\n💰 Testando oportunidades de economia...")
        opportunities = await service.get_savings_opportunities_by_provider()
        print(f"📊 Oportunidades encontradas: {len(opportunities)}")
        
        if opportunities:
            print("🎯 Primeira oportunidade:")
            opp = opportunities[0]
            print(f"   ID: {opp.id}")
            print(f"   Provider: {opp.provider}")
            print(f"   Category: {opp.category}")
            print(f"   Potential Savings: ${opp.potential_savings}")
            print(f"   Description: {opp.description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar serviço: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_optimization_service())
    if success:
        print("\n🎉 Teste concluído com sucesso!")
    else:
        print("\n💥 Teste falhou!")
        sys.exit(1)
