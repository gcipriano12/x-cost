"""
Cloud Optimization Module

Este módulo implementa otimização de custos em tempo real para diferentes provedores de nuvem,
incluindo detecção de anomalias, oportunidades de economia e recomendações unificadas.

Provedores suportados:
- AWS (Cost Explorer + Compute Optimizer)
- Azure (Azure Advisor API)
- GCP (Cloud Recommender API)
- Oracle Cloud (placeholder para implementação futura)
"""

from .factory import OptimizationServiceFactory
from .models import (
    CloudAnomaly,
    SavingsOpportunity,
    OptimizationRecommendation,
    AnomalyType,
    SeverityLevel,
    RecommendationType
)
from .cache_manager import RedisCache, CacheConfig

__all__ = [
    'OptimizationServiceFactory',
    'CloudAnomaly',
    'SavingsOpportunity',
    'OptimizationRecommendation',
    'AnomalyType',
    'SeverityLevel',
    'RecommendationType',
    'RedisCache',
    'CacheConfig'
]