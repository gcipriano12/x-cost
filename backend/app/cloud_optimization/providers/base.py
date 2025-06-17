"""
Classe base para serviços de otimização de provedores cloud
"""

import logging
from abc import ABC, abstractmethod
from typing import List

from ..models import CloudAnomaly, SavingsOpportunity, OptimizationRecommendation


class BaseOptimizationService(ABC):
    """Classe base abstrata para serviços de otimização"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = logging.getLogger(f"{__name__}.{provider_name}")
    
    @abstractmethod
    async def get_anomalies(self) -> List[CloudAnomaly]:
        """Método base para obter anomalias - deve ser sobrescrito"""
        raise NotImplementedError
    
    @abstractmethod
    async def get_savings_opportunities(self) -> List[SavingsOpportunity]:
        """Método base para obter oportunidades - deve ser sobrescrito"""
        raise NotImplementedError
    
    @abstractmethod
    async def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Método base para obter recomendações - deve ser sobrescrito"""
        raise NotImplementedError