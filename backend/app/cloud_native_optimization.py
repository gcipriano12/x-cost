"""
Cloud Native Optimization Service

Este módulo implementa otimização de custos em tempo real para diferentes provedores de nuvem,
incluindo detecção de anomalias, oportunidades de economia e recomendações unificadas.

Provedores suportados:
- AWS (Cost Explorer + Compute Optimizer)
- Azure (Azure Advisor API)
- GCP (Cloud Recommender API)
- Oracle Cloud (placeholder para implementação futura)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

import redis
from fastapi import HTTPException

# Imports from new modular structure
from .cloud_optimization.factory import OptimizationServiceFactory
from .cloud_optimization.cache_manager import RedisCache
from .cloud_optimization.models import (
    CloudAnomaly, 
    SavingsOpportunity, 
    OptimizationRecommendation,
    AnomalyType,
    SeverityLevel,
    RecommendationType
)
from .cloud_optimization.decorators import retry_with_exponential_backoff

# Configurações e logging
logger = logging.getLogger(__name__)


# ============================================================================
# Classe principal do serviço de otimização
# ============================================================================

class CloudNativeOptimizationService:
    """
    Serviço principal de otimização de custos multi-cloud
    
    Esta classe orquestra a coleta e análise de dados de otimização
    de múltiplos provedores de nuvem, oferecendo uma interface unificada.
    """
    
    def __init__(self, redis_client: redis.Redis = None):
        self.logger = logging.getLogger(__name__)
        self.cache = RedisCache(redis_client) if redis_client else None
        self.services = {}  # Cache de serviços instanciados
    
    def _get_service(self, provider: str, credentials: Dict[str, Any] = None):
        """Obtém ou cria uma instância do serviço de otimização para o provedor"""
        service_key = f"{provider}_{hash(str(credentials) if credentials else 'default')}"
        
        if service_key not in self.services:
            try:
                self.services[service_key] = OptimizationServiceFactory.create_service(
                    provider, credentials
                )
            except ImportError as e:
                self.logger.warning(f"Provider {provider} não disponível: {e}")
                # Para providers sem SDK, retornar None e usar fallback de dados simulados
                self.services[service_key] = None
            except Exception as e:
                self.logger.error(f"Erro ao criar serviço {provider}: {e}")
                self.services[service_key] = None
        
        return self.services[service_key]
    
    async def get_anomalies(
        self, 
        provider: str, 
        credentials: Dict[str, Any] = None,
        use_cache: bool = True,
        **kwargs
    ) -> List[CloudAnomaly]:
        """
        Obtém anomalias de custo do provedor especificado
        
        Args:
            provider: Nome do provedor (aws, azure, gcp, oracle)
            credentials: Credenciais específicas do provedor
            use_cache: Se deve usar cache Redis
            **kwargs: Parâmetros específicos do provedor
            
        Returns:
            Lista de anomalias de custo
        """
        try:
            # Tentar cache primeiro se habilitado
            if use_cache and self.cache:
                cached_anomalies = await self.cache.get_anomalies(provider)
                if cached_anomalies:
                    self.logger.info(f"Anomalias {provider} obtidas do cache")
                    return cached_anomalies
            
            # Buscar do provedor
            service = self._get_service(provider, credentials)
            if service is None:
                # Provider não disponível, usar dados simulados se for AWS (que tem implementação)
                if provider.lower() == "aws":
                    # Usar serviço AWS que tem dados simulados multi-provider
                    aws_service = self._get_service("aws", None)
                    if aws_service:
                        anomalies = await aws_service.get_anomalies()
                    else:
                        anomalies = []
                else:
                    # Para outros providers sem SDK, retornar lista vazia
                    anomalies = []
            else:
                anomalies = await service.get_anomalies()
            
            # Salvar no cache se habilitado
            if use_cache and self.cache and anomalies:
                await self.cache.set_anomalies(anomalies, provider)
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erro ao obter anomalias {provider}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao obter anomalias do provedor {provider}"
            )
    
    async def get_savings_opportunities(
        self, 
        provider: str, 
        credentials: Dict[str, Any] = None,
        use_cache: bool = True,
        **kwargs
    ) -> List[SavingsOpportunity]:
        """
        Obtém oportunidades de economia do provedor especificado
        
        Args:
            provider: Nome do provedor (aws, azure, gcp, oracle)
            credentials: Credenciais específicas do provedor
            use_cache: Se deve usar cache Redis
            **kwargs: Parâmetros específicos do provedor
            
        Returns:
            Lista de oportunidades de economia
        """
        try:
            # Tentar cache primeiro se habilitado
            if use_cache and self.cache:
                cached_savings = await self.cache.get_savings(provider)
                if cached_savings:
                    self.logger.info(f"Oportunidades {provider} obtidas do cache")
                    return cached_savings
            
            # Buscar do provedor
            service = self._get_service(provider, credentials)
            if service is None:
                # Provider não disponível, usar dados simulados se for AWS (que tem implementação)
                if provider.lower() == "aws":
                    # Usar serviço AWS que tem dados simulados multi-provider
                    aws_service = self._get_service("aws", None)
                    if aws_service:
                        savings = await aws_service.get_savings_opportunities()
                    else:
                        savings = []
                else:
                    # Para outros providers sem SDK, retornar lista vazia
                    savings = []
            else:
                savings = await service.get_savings_opportunities()
            
            # Salvar no cache se habilitado
            if use_cache and self.cache and savings:
                await self.cache.set_savings(savings, provider)
            
            return savings
            
        except Exception as e:
            self.logger.error(f"Erro ao obter oportunidades {provider}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao obter oportunidades do provedor {provider}"
            )
    
    async def get_recommendations(
        self, 
        provider: str, 
        credentials: Dict[str, Any] = None,
        use_cache: bool = True,
        **kwargs
    ) -> List[OptimizationRecommendation]:
        """
        Obtém recomendações de otimização do provedor especificado
        
        Args:
            provider: Nome do provedor (aws, azure, gcp, oracle)
            credentials: Credenciais específicas do provedor
            use_cache: Se deve usar cache Redis
            **kwargs: Parâmetros específicos do provedor
            
        Returns:
            Lista de recomendações de otimização
        """
        try:
            # Tentar cache primeiro se habilitado
            if use_cache and self.cache:
                cached_recs = await self.cache.get_recommendations(provider)
                if cached_recs:
                    self.logger.info(f"Recomendações {provider} obtidas do cache")
                    return cached_recs
            
            # Buscar do provedor
            service = self._get_service(provider, credentials)
            if service is None:
                # Provider não disponível, usar dados simulados se for AWS (que tem implementação)
                if provider.lower() == "aws":
                    # Usar serviço AWS que tem dados simulados multi-provider
                    aws_service = self._get_service("aws", None)
                    if aws_service:
                        recommendations = await aws_service.get_recommendations()
                    else:
                        recommendations = []
                else:
                    # Para outros providers sem SDK, retornar lista vazia
                    recommendations = []
            else:
                recommendations = await service.get_recommendations()
            
            # Salvar no cache se habilitado
            if use_cache and self.cache and recommendations:
                await self.cache.set_recommendations(recommendations, provider)
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Erro ao obter recomendações {provider}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao obter recomendações do provedor {provider}"
            )
    
    async def get_multi_provider_summary(
        self, 
        providers: List[str], 
        credentials_map: Dict[str, Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Obtém resumo consolidado de múltiplos provedores
        
        Args:
            providers: Lista de provedores para consultar
            credentials_map: Mapa de credenciais por provedor
            
        Returns:
            Resumo consolidado com anomalias, oportunidades e recomendações
        """
        results = {
            "summary": {
                "total_anomalies": 0,
                "total_savings": 0.0,
                "total_recommendations": 0,
                "providers_analyzed": []
            },
            "by_provider": {},
            "aggregated": {
                "anomalies": [],
                "savings_opportunities": [],
                "recommendations": []
            }
        }
        
        credentials_map = credentials_map or {}
        
        # Processar cada provedor em paralelo
        tasks = []
        for provider in providers:
            creds = credentials_map.get(provider)
            
            # Criar tasks para execução paralela
            tasks.extend([
                self.get_anomalies(provider, creds),
                self.get_savings_opportunities(provider, creds),
                self.get_recommendations(provider, creds)
            ])
        
        try:
            # Executar todas as consultas em paralelo
            results_list = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Processar resultados
            for i, provider in enumerate(providers):
                provider_results = {
                    "anomalies": [],
                    "savings_opportunities": [],
                    "recommendations": [],
                    "errors": []
                }
                
                # Cada provedor tem 3 resultados (anomalias, oportunidades, recomendações)
                base_idx = i * 3
                
                for j, result_type in enumerate(['anomalies', 'savings_opportunities', 'recommendations']):
                    result = results_list[base_idx + j]
                    
                    if isinstance(result, Exception):
                        provider_results["errors"].append(f"{result_type}: {str(result)}")
                    else:
                        provider_results[result_type] = result
                        results["aggregated"][result_type].extend(result)
                
                results["by_provider"][provider] = provider_results
                results["summary"]["providers_analyzed"].append(provider)
            
            # Calcular totais
            results["summary"]["total_anomalies"] = len(results["aggregated"]["anomalies"])
            results["summary"]["total_recommendations"] = len(results["aggregated"]["recommendations"])
            results["summary"]["total_savings"] = sum(
                opp.estimated_savings for opp in results["aggregated"]["savings_opportunities"]
            )
            
            # Ordenar oportunidades por economia (maior primeiro)
            results["aggregated"]["savings_opportunities"].sort(
                key=lambda x: x.estimated_savings, reverse=True
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"Erro ao obter resumo multi-provedor: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao consolidar dados de múltiplos provedores"
            )
    
    def get_supported_providers(self) -> List[str]:
        """Retorna lista de provedores suportados"""
        return OptimizationServiceFactory.get_supported_providers()
    
    def is_provider_supported(self, provider: str) -> bool:
        """Verifica se um provedor é suportado"""
        return OptimizationServiceFactory.is_provider_supported(provider)
    
    async def get_anomalies_by_provider(self, provider_name: Optional[str] = None) -> List[CloudAnomaly]:
        """
        Obtém anomalias filtradas por provedor
        
        Args:
            provider_name: Nome do provedor específico ou None para todos
            
        Returns:
            Lista de anomalias filtradas
        """
        # Buscar todas as anomalias (incluindo dados simulados multi-provider)
        all_anomalies = []
        
        # Como só temos AWS provider configurado, mas os dados simulados incluem todos os providers,
        # vamos buscar de AWS que retorna dados simulados de todos os providers
        try:
            anomalies = await self.get_anomalies("aws")
            all_anomalies.extend(anomalies)
        except Exception as e:
            self.logger.warning(f"Failed to get anomalies: {e}")
        
        # Se um provider específico foi solicitado, filtrar os resultados
        if provider_name:
            provider_name_normalized = provider_name.upper()  # AWS, AZURE, GCP, ORACLE
            filtered_anomalies = [a for a in all_anomalies if a.provider.upper() == provider_name_normalized]
            return filtered_anomalies
        else:
            return all_anomalies
    
    async def get_savings_opportunities_by_provider(self, provider_name: Optional[str] = None) -> List[SavingsOpportunity]:
        """
        Obtém oportunidades de economia filtradas por provedor
        
        Args:
            provider_name: Nome do provedor específico ou None para todos
            
        Returns:
            Lista de oportunidades filtradas
        """
        # Buscar todas as oportunidades (incluindo dados simulados multi-provider)
        all_opportunities = []
        
        # Como só temos AWS provider configurado, mas os dados simulados incluem todos os providers,
        # vamos buscar de AWS que retorna dados simulados de todos os providers
        try:
            opportunities = await self.get_savings_opportunities("aws")
            all_opportunities.extend(opportunities)
        except Exception as e:
            self.logger.warning(f"Failed to get savings opportunities: {e}")
        
        # Se um provider específico foi solicitado, filtrar os resultados
        if provider_name:
            provider_name_normalized = provider_name.upper()  # AWS, AZURE, GCP, ORACLE
            filtered_opportunities = [o for o in all_opportunities if o.provider.upper() == provider_name_normalized]
            return filtered_opportunities
        else:
            return all_opportunities
    
    async def get_unified_recommendations(self, provider_name: Optional[str] = None) -> List[OptimizationRecommendation]:
        """
        Obtém recomendações unificadas baseadas em anomalias e oportunidades
        
        Args:
            provider_name: Nome do provedor específico ou None para todos
            
        Returns:
            Lista de recomendações consolidadas
        """
        if provider_name:
            return await self.get_recommendations(provider_name)
        else:
            # Se não especificado, buscar de todos os provedores suportados
            all_recommendations = []
            for provider in self.get_supported_providers():
                try:
                    recommendations = await self.get_recommendations(provider)
                    all_recommendations.extend(recommendations)
                except Exception as e:
                    self.logger.warning(f"Failed to get recommendations from {provider}: {e}")
            return all_recommendations
    
    async def invalidate_cache(self, pattern: str = "*"):
        """
        Invalida entradas de cache que correspondem ao padrão
        
        Args:
            pattern: Padrão para filtrar chaves do cache
        """
        if self.cache and hasattr(self.cache, 'redis'):
            try:
                # Buscar chaves que correspondem ao padrão
                cache_pattern = f"{self.cache.config.KEY_PREFIX}{pattern}"
                keys = self.cache.redis.keys(cache_pattern)
                
                if keys:
                    # Deletar chaves encontradas
                    self.cache.redis.delete(*keys)
                    self.logger.info(f"Invalidated {len(keys)} cache entries matching pattern: {pattern}")
                else:
                    self.logger.info(f"No cache entries found matching pattern: {pattern}")
                    
            except Exception as e:
                self.logger.error(f"Failed to invalidate cache: {e}")
                raise
        else:
            self.logger.warning("Cache not available for invalidation")


# ============================================================================
# Instância global do serviço
# ============================================================================

# Instância global que pode ser importada por outros módulos
optimization_service = None

def create_optimization_service(redis_client: redis.Redis = None) -> CloudNativeOptimizationService:
    """Factory function para criar instância do serviço de otimização com Redis client personalizado"""
    return CloudNativeOptimizationService(redis_client)


def get_optimization_service() -> CloudNativeOptimizationService:
    """Factory function para obter instância do serviço de otimização (dependência do FastAPI)"""
    global optimization_service
    
    if optimization_service is None:
        # Inicializar sem Redis client específico - será configurado automaticamente
        optimization_service = CloudNativeOptimizationService(None)
    
    return optimization_service


# ============================================================================
# Funcões auxiliares para compatibilidade (deprecated)
# ============================================================================

async def get_aws_savings(
    access_key: str = None, 
    secret_key: str = None, 
    region: str = "us-east-1",
    min_savings: float = 50.0
) -> List[SavingsOpportunity]:
    """
    Função auxiliar para compatibilidade - use get_optimization_service() preferencialmente
    """
    service = get_optimization_service()
    credentials = {}
    if access_key and secret_key:
        credentials = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region
        }
    
    return await service.get_savings_opportunities("aws", credentials)


async def get_aws_anomalies(
    access_key: str = None, 
    secret_key: str = None, 
    region: str = "us-east-1",
    days: int = 30
) -> List[CloudAnomaly]:
    """
    Função auxiliar para compatibilidade - use get_optimization_service() preferencialmente
    """
    service = get_optimization_service()
    credentials = {}
    if access_key and secret_key:
        credentials = {
            "access_key": access_key,
            "secret_key": secret_key,
            "region": region
        }
    
    return await service.get_anomalies("aws", credentials)