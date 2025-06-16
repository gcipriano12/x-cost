"""
Testes para Cloud Native Optimization Service

Execute com: python -m pytest tests/test_cloud_native_optimization.py -v
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from typing import List

import redis

from app.cloud_native_optimization import (
    CloudNativeOptimizationService,
    CloudAnomaly,
    SavingsOpportunity,
    OptimizationRecommendation,
    AnomalyType,
    SeverityLevel,
    RecommendationType,
    RedisCache,
    load_config_from_env
)

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_redis():
    """Mock do cliente Redis"""
    return Mock(spec=redis.Redis)

@pytest.fixture
def sample_config():
    """Configuração de exemplo para testes"""
    return {
        'aws': {
            'enabled': True,
            'access_key': 'test_key',
            'secret_key': 'test_secret',
            'region': 'us-east-1'
        },
        'azure': {
            'enabled': True,
            'subscription_id': 'test_sub_id',
            'tenant_id': 'test_tenant',
            'client_id': 'test_client',
            'client_secret': 'test_secret'
        },
        'gcp': {
            'enabled': True,
            'project_id': 'test_project',
            'credentials_path': '/path/to/creds.json'
        },
        'oracle': {
            'enabled': False,
            'config_file_path': None
        }
    }

@pytest.fixture
def sample_anomaly():
    """Anomalia de exemplo"""
    return CloudAnomaly(
        id="test-anomaly-001",
        provider="AWS",
        service="EC2",
        anomaly_type=AnomalyType.SPIKE,
        severity=SeverityLevel.HIGH,
        detected_at=datetime.utcnow(),
        cost_impact=500.0,
        description="Test anomaly"
    )

@pytest.fixture
def sample_savings_opportunity():
    """Oportunidade de economia de exemplo"""
    return SavingsOpportunity(
        id="test-savings-001",
        provider="AWS",
        service="EC2",
        opportunity_type=RecommendationType.RIGHTSIZING,
        estimated_savings=200.0,
        confidence_level=85.0,
        implementation_effort="Low",
        description="Test savings opportunity",
        action_required="Resize instance"
    )

@pytest.fixture
def sample_recommendation():
    """Recomendação de exemplo"""
    return OptimizationRecommendation(
        id="test-rec-001",
        provider="AWS",
        category=RecommendationType.RIGHTSIZING,
        title="Test Recommendation",
        description="Test recommendation description",
        potential_savings=150.0,
        priority=SeverityLevel.MEDIUM,
        implementation_time="30 minutes",
        steps=["Step 1", "Step 2"]
    )

# ============================================================================
# Testes dos Modelos Pydantic
# ============================================================================

class TestPydanticModels:
    """Testes para validação dos modelos Pydantic"""
    
    def test_cloud_anomaly_validation(self):
        """Testa validação do modelo CloudAnomaly"""
        # Teste com dados válidos
        anomaly = CloudAnomaly(
            id="test-001",
            provider="AWS",
            service="EC2",
            anomaly_type=AnomalyType.SPIKE,
            severity=SeverityLevel.HIGH,
            detected_at=datetime.utcnow(),
            cost_impact=100.0,
            description="Test anomaly"
        )
        assert anomaly.id == "test-001"
        assert anomaly.cost_impact == 100.0
        
        # Teste com cost_impact negativo (deve falhar)
        with pytest.raises(ValueError):
            CloudAnomaly(
                id="test-002",
                provider="AWS",
                service="EC2",
                anomaly_type=AnomalyType.SPIKE,
                severity=SeverityLevel.HIGH,
                detected_at=datetime.utcnow(),
                cost_impact=-50.0,
                description="Invalid anomaly"
            )
    
    def test_savings_opportunity_validation(self):
        """Testa validação do modelo SavingsOpportunity"""
        opportunity = SavingsOpportunity(
            id="test-savings-001",
            provider="Azure",
            service="VM",
            opportunity_type=RecommendationType.RESERVED_INSTANCES,
            estimated_savings=300.0,
            confidence_level=90.0,
            implementation_effort="Medium",
            description="Test opportunity",
            action_required="Purchase RI"
        )
        assert opportunity.confidence_level == 90.0
        assert opportunity.estimated_savings == 300.0
        
        # Teste com confidence_level inválido
        with pytest.raises(ValueError):
            SavingsOpportunity(
                id="test-invalid",
                provider="Azure",
                service="VM",
                opportunity_type=RecommendationType.RESERVED_INSTANCES,
                estimated_savings=300.0,
                confidence_level=150.0,  # Inválido (> 100)
                implementation_effort="Medium",
                description="Invalid opportunity",
                action_required="Test"
            )

# ============================================================================
# Testes do Redis Cache
# ============================================================================

class TestRedisCache:
    """Testes para o sistema de cache Redis"""
    
    @pytest.mark.asyncio
    async def test_cache_anomalies(self, mock_redis, sample_anomaly):
        """Testa cache de anomalias"""
        cache = RedisCache(mock_redis)
        anomalies = [sample_anomaly]
        
        # Simular dados no Redis
        mock_redis.get.return_value = json.dumps([sample_anomaly.dict()], default=str)
        
        # Testar recuperação
        cached_anomalies = await cache.get_anomalies("AWS")
        assert len(cached_anomalies) == 1
        assert cached_anomalies[0].id == sample_anomaly.id
        
        # Testar armazenamento
        await cache.set_anomalies(anomalies, "AWS")
        mock_redis.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self, mock_redis):
        """Testa geração de chaves do cache"""
        cache = RedisCache(mock_redis)
        
        # Chave sem provedor
        key1 = cache._get_key("anomalies")
        assert key1 == "cloud_optimization:anomalies"
        
        # Chave com provedor
        key2 = cache._get_key("anomalies", "AWS")
        assert key2 == "cloud_optimization:anomalies:AWS"
    
    @pytest.mark.asyncio
    async def test_cache_error_handling(self, mock_redis):
        """Testa tratamento de erros do cache"""
        cache = RedisCache(mock_redis)
        
        # Simular erro no Redis
        mock_redis.get.side_effect = Exception("Redis error")
        
        # Deve retornar None em caso de erro
        result = await cache.get_anomalies("AWS")
        assert result is None

# ============================================================================
# Testes do Serviço Principal
# ============================================================================

class TestCloudNativeOptimizationService:
    """Testes para o serviço principal de otimização"""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, mock_redis, sample_config):
        """Testa inicialização do serviço"""
        service = CloudNativeOptimizationService(mock_redis, sample_config)
        
        # Verificar se o cache foi configurado
        assert service.cache is not None
        assert service.config == sample_config
    
    @pytest.mark.asyncio
    async def test_get_anomalies_from_cache(self, mock_redis, sample_config, sample_anomaly):
        """Testa recuperação de anomalias do cache"""
        service = CloudNativeOptimizationService(mock_redis, sample_config)
        
        # Mock do cache retornando dados
        service.cache.get_anomalies = AsyncMock(return_value=[sample_anomaly])
        
        # Executar
        anomalies = await service.get_anomalies_by_provider("AWS")
        
        # Verificar
        assert len(anomalies) == 1
        assert anomalies[0].id == sample_anomaly.id
        service.cache.get_anomalies.assert_called_once_with("AWS")
    
    @pytest.mark.asyncio
    async def test_get_anomalies_provider_not_found(self, mock_redis, sample_config):
        """Testa erro quando provedor não é encontrado"""
        service = CloudNativeOptimizationService(mock_redis, sample_config)
        
        with pytest.raises(Exception):  # HTTPException em produção
            await service.get_anomalies_by_provider("INVALID_PROVIDER")
    
    @pytest.mark.asyncio
    async def test_summary_statistics(self, mock_redis, sample_config, sample_anomaly, 
                                    sample_savings_opportunity, sample_recommendation):
        """Testa geração de estatísticas resumidas"""
        service = CloudNativeOptimizationService(mock_redis, sample_config)
        
        anomalies = [sample_anomaly]
        opportunities = [sample_savings_opportunity]
        recommendations = [sample_recommendation]
        
        stats = service.get_summary_statistics(anomalies, opportunities, recommendations)
        
        # Verificar estrutura das estatísticas
        assert "summary" in stats
        assert "anomaly_severity_distribution" in stats
        assert "recommendation_priority_distribution" in stats
        assert "provider_statistics" in stats
        
        # Verificar valores
        assert stats["summary"]["total_anomalies"] == 1
        assert stats["summary"]["total_opportunities"] == 1
        assert stats["summary"]["total_recommendations"] == 1
        assert stats["summary"]["total_anomaly_impact"] == 500.0
        assert stats["summary"]["total_savings_potential"] == 200.0

# ============================================================================
# Testes de Integração
# ============================================================================

class TestIntegration:
    """Testes de integração para cenários complexos"""
    
    @pytest.mark.asyncio
    async def test_full_optimization_report(self, mock_redis, sample_config):
        """Testa geração de relatório completo"""
        service = CloudNativeOptimizationService(mock_redis, sample_config)
        
        # Mock dos métodos principais
        service.get_anomalies_by_provider = AsyncMock(return_value=[])
        service.get_savings_opportunities_by_provider = AsyncMock(return_value=[])
        service.get_unified_recommendations = AsyncMock(return_value=[])
        
        # Executar
        report = await service.get_full_optimization_report("AWS")
        
        # Verificar estrutura do relatório
        assert "anomalies" in report
        assert "savings_opportunities" in report
        assert "recommendations" in report
        assert "statistics" in report
        
        # Verificar que os métodos foram chamados
        service.get_anomalies_by_provider.assert_called_once_with("AWS")
        service.get_savings_opportunities_by_provider.assert_called_once_with("AWS")
        service.get_unified_recommendations.assert_called_once_with("AWS")

# ============================================================================
# Testes Utilitários
# ============================================================================

class TestUtilities:
    """Testes para funções utilitárias"""
    
    @patch.dict('os.environ', {
        'AWS_OPTIMIZATION_ENABLED': 'true',
        'AWS_ACCESS_KEY_ID': 'test_key',
        'AWS_SECRET_ACCESS_KEY': 'test_secret',
        'AZURE_OPTIMIZATION_ENABLED': 'false'
    })
    def test_load_config_from_env(self):
        """Testa carregamento de configuração das variáveis de ambiente"""
        config = load_config_from_env()
        
        assert config['aws']['enabled'] is True
        assert config['aws']['access_key'] == 'test_key'
        assert config['aws']['secret_key'] == 'test_secret'
        assert config['azure']['enabled'] is False
    
    def test_config_defaults(self):
        """Testa valores padrão da configuração"""
        config = load_config_from_env()
        
        # Verificar estrutura básica
        assert 'aws' in config
        assert 'azure' in config
        assert 'gcp' in config
        assert 'oracle' in config
        
        # Verificar valores padrão
        assert config['aws']['region'] == 'us-east-1'

# ============================================================================
# Testes de Performance
# ============================================================================

class TestPerformance:
    """Testes de performance e concorrência"""
    
    @pytest.mark.asyncio
    async def test_concurrent_provider_queries(self, mock_redis, sample_config):
        """Testa consultas concorrentes a múltiplos provedores"""
        service = CloudNativeOptimizationService(mock_redis, sample_config)
        
        # Mock para simular que todos os provedores estão disponíveis
        service.providers = {
            'AWS': Mock(),
            'Azure': Mock(),
            'GCP': Mock()
        }
        
        # Configurar mocks para retornar dados de forma assíncrona
        for provider_service in service.providers.values():
            provider_service.get_anomalies = AsyncMock(return_value=[])
        
        # Mock do cache para retornar None (forçar consulta aos provedores)
        service.cache.get_anomalies = AsyncMock(return_value=None)
        service.cache.set_anomalies = AsyncMock()
        
        # Executar consulta para todos os provedores
        start_time = datetime.utcnow()
        anomalies = await service.get_anomalies_by_provider(None)
        end_time = datetime.utcnow()
        
        # Verificar que todas as consultas foram executadas
        for provider_service in service.providers.values():
            provider_service.get_anomalies.assert_called_once()
        
        # Verificar que foi executado em tempo razoável (< 1 segundo para mocks)
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 1.0

if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])
