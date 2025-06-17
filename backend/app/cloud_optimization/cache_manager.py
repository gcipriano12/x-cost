"""
Gerenciador de cache Redis para otimização cloud
"""

import json
import logging
from dataclasses import dataclass
from typing import List, Optional

import redis

from .models import CloudAnomaly, SavingsOpportunity, OptimizationRecommendation

logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Configuração do cache Redis"""
    ANOMALIES_TTL: int = 3600  # 1 hora
    SAVINGS_TTL: int = 14400   # 4 horas
    RECOMMENDATIONS_TTL: int = 21600  # 6 horas
    KEY_PREFIX: str = "cloud_optimization:"


class RedisCache:
    """Gerenciador de cache Redis para otimização"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.config = CacheConfig()
    
    def _get_key(self, category: str, provider: Optional[str] = None) -> str:
        """Gera chave do cache"""
        base_key = f"{self.config.KEY_PREFIX}{category}"
        if provider:
            base_key += f":{provider}"
        return base_key
    
    async def get_anomalies(self, provider: Optional[str] = None) -> Optional[List[CloudAnomaly]]:
        """Recupera anomalias do cache"""
        try:
            key = self._get_key("anomalies", provider)
            data = self.redis.get(key)
            if data:
                anomalies_data = json.loads(data)
                return [CloudAnomaly(**item) for item in anomalies_data]
        except Exception as e:
            logger.error(f"Erro ao recuperar anomalias do cache: {e}")
        return None
    
    async def set_anomalies(self, anomalies: List[CloudAnomaly], provider: Optional[str] = None):
        """Armazena anomalias no cache"""
        try:
            key = self._get_key("anomalies", provider)
            data = [anomaly.dict() for anomaly in anomalies]
            self.redis.setex(key, self.config.ANOMALIES_TTL, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Erro ao armazenar anomalias no cache: {e}")
    
    async def get_savings(self, provider: Optional[str] = None) -> Optional[List[SavingsOpportunity]]:
        """Recupera oportunidades do cache"""
        try:
            key = self._get_key("savings", provider)
            data = self.redis.get(key)
            if data:
                savings_data = json.loads(data)
                return [SavingsOpportunity(**item) for item in savings_data]
        except Exception as e:
            logger.error(f"Erro ao recuperar savings do cache: {e}")
        return None
    
    async def set_savings(self, savings: List[SavingsOpportunity], provider: Optional[str] = None):
        """Armazena oportunidades no cache"""
        try:
            key = self._get_key("savings", provider)
            data = [saving.dict() for saving in savings]
            self.redis.setex(key, self.config.SAVINGS_TTL, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Erro ao armazenar savings no cache: {e}")
    
    async def get_recommendations(self, provider: Optional[str] = None) -> Optional[List[OptimizationRecommendation]]:
        """Recupera recomendações do cache"""
        try:
            key = self._get_key("recommendations", provider)
            data = self.redis.get(key)
            if data:
                rec_data = json.loads(data)
                return [OptimizationRecommendation(**item) for item in rec_data]
        except Exception as e:
            logger.error(f"Erro ao recuperar recommendations do cache: {e}")
        return None
    
    async def set_recommendations(self, recommendations: List[OptimizationRecommendation], provider: Optional[str] = None):
        """Armazena recomendações no cache"""
        try:
            key = self._get_key("recommendations", provider)
            data = [rec.dict() for rec in recommendations]
            self.redis.setex(key, self.config.RECOMMENDATIONS_TTL, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Erro ao armazenar recommendations no cache: {e}")