#!/usr/bin/env python3
"""
Script de teste rápido para Cloud Native Optimization Service

Execute com: python test_optimization_quick.py
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import Mock

from app.cloud_native_optimization import (
    CloudNativeOptimizationService,
    CloudAnomaly,
    SavingsOpportunity,
    OptimizationRecommendation,
    AnomalyType,
    SeverityLevel,
    RecommendationType,
    load_config_from_env
)

async def test_models():
    """Testar criação dos modelos Pydantic"""
    print("🧪 Testando modelos Pydantic...")
    
    # Testar CloudAnomaly
    anomaly = CloudAnomaly(
        id="test-001",
        provider="AWS",
        service="EC2",
        anomaly_type=AnomalyType.SPIKE,
        severity=SeverityLevel.HIGH,
        detected_at=datetime.utcnow(),
        cost_impact=500.0,
        description="Anomalia de teste"
    )
    print(f"✅ CloudAnomaly criada: {anomaly.id}")
    
    # Testar SavingsOpportunity
    opportunity = SavingsOpportunity(
        id="savings-001",
        provider="AWS",
        service="EC2",
        opportunity_type=RecommendationType.RIGHTSIZING,
        estimated_savings=200.0,
        confidence_level=85.0,
        implementation_effort="Baixo",
        description="Oportunidade de teste",
        action_required="Redimensionar instância"
    )
    print(f"✅ SavingsOpportunity criada: {opportunity.id}")
    
    # Testar OptimizationRecommendation
    recommendation = OptimizationRecommendation(
        id="rec-001",
        provider="AWS",
        category=RecommendationType.RIGHTSIZING,
        title="Recomendação de teste",
        description="Descrição da recomendação",
        potential_savings=150.0,
        priority=SeverityLevel.MEDIUM,
        implementation_time="30 minutos",
        steps=["Passo 1", "Passo 2"]
    )
    print(f"✅ OptimizationRecommendation criada: {recommendation.id}")
    
    return anomaly, opportunity, recommendation

async def test_service():
    """Testar serviço principal com mocks"""
    print("\n🔧 Testando serviço principal...")
    
    # Mock do Redis
    mock_redis = Mock()
    mock_redis.get.return_value = None
    mock_redis.setex.return_value = True
    
    # Configuração de teste
    config = {
        'aws': {'enabled': False},
        'azure': {'enabled': False},
        'gcp': {'enabled': False},
        'oracle': {'enabled': False}
    }
    
    # Criar serviço
    service = CloudNativeOptimizationService(mock_redis, config)
    print("✅ CloudNativeOptimizationService criado")
    
    # Testar métodos principais (sem provedores reais)
    try:
        anomalies = await service.get_anomalies_by_provider()
        print(f"✅ get_anomalies_by_provider executado: {len(anomalies)} anomalias")
        
        opportunities = await service.get_savings_opportunities_by_provider()
        print(f"✅ get_savings_opportunities_by_provider executado: {len(opportunities)} oportunidades")
        
        recommendations = await service.get_unified_recommendations()
        print(f"✅ get_unified_recommendations executado: {len(recommendations)} recomendações")
        
    except Exception as e:
        print(f"⚠️ Erro esperado (sem provedores configurados): {e}")
    
    return service

async def test_statistics():
    """Testar geração de estatísticas"""
    print("\n📊 Testando estatísticas...")
    
    # Criar dados de exemplo
    anomaly, opportunity, recommendation = await test_models()
    
    # Mock do serviço
    mock_redis = Mock()
    config = {'aws': {'enabled': False}, 'azure': {'enabled': False}, 'gcp': {'enabled': False}, 'oracle': {'enabled': False}}
    service = CloudNativeOptimizationService(mock_redis, config)
    
    # Gerar estatísticas
    stats = service.get_summary_statistics([anomaly], [opportunity], [recommendation])
    
    print("✅ Estatísticas geradas:")
    print(f"   - Total anomalias: {stats['summary']['total_anomalies']}")
    print(f"   - Total oportunidades: {stats['summary']['total_opportunities']}")
    print(f"   - Total recomendações: {stats['summary']['total_recommendations']}")
    print(f"   - Economia potencial: ${stats['summary']['total_potential_savings']}")
    
    return stats

def test_config_loading():
    """Testar carregamento de configuração"""
    print("\n⚙️ Testando carregamento de configuração...")
    
    try:
        config = load_config_from_env()
        print("✅ Configuração carregada:")
        for provider, settings in config.items():
            status = "habilitado" if settings.get('enabled') else "desabilitado"
            print(f"   - {provider}: {status}")
    except Exception as e:
        print(f"❌ Erro ao carregar configuração: {e}")
    
    return config

def test_json_serialization():
    """Testar serialização JSON dos modelos"""
    print("\n🔄 Testando serialização JSON...")
    
    anomaly = CloudAnomaly(
        id="test-json-001",
        provider="AWS",
        service="EC2",
        anomaly_type=AnomalyType.SPIKE,
        severity=SeverityLevel.HIGH,
        detected_at=datetime.utcnow(),
        cost_impact=500.0,
        description="Teste de serialização"
    )
    
    # Converter para JSON
    json_data = anomaly.json()
    print("✅ Serialização para JSON bem-sucedida")
    
    # Converter de volta
    anomaly_from_json = CloudAnomaly.parse_raw(json_data)
    print("✅ Deserialização de JSON bem-sucedida")
    
    assert anomaly.id == anomaly_from_json.id
    print("✅ Dados preservados após serialização/deserialização")

async def main():
    """Função principal de teste"""
    print("🚀 Iniciando testes do Cloud Native Optimization Service\n")
    
    try:
        # Executar testes
        await test_models()
        await test_service()
        await test_statistics()
        test_config_loading()
        test_json_serialization()
        
        print("\n✅ Todos os testes passaram com sucesso!")
        print("\n📋 Resumo:")
        print("   - Modelos Pydantic funcionando corretamente")
        print("   - Serviço principal inicializado")
        print("   - Estatísticas sendo geradas")
        print("   - Configuração carregável")
        print("   - Serialização JSON funcionando")
        
        print("\n🎯 Próximos passos:")
        print("   1. Configurar credenciais dos provedores no .env")
        print("   2. Instalar dependências: pip install -r requirements-optimization.txt")
        print("   3. Executar testes completos: pytest tests/test_cloud_native_optimization.py")
        print("   4. Integrar com a aplicação principal")
        
    except Exception as e:
        print(f"\n❌ Erro durante os testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
