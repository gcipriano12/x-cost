#!/usr/bin/env python3
"""
Otimizações para o endpoint de anomalies
"""

from functools import lru_cache
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

# Cache global para anomalias simuladas (lifetime de 1 hora)
_anomalies_cache = {}
_cache_lifetime = 3600  # 1 hora em segundos

async def get_optimized_anomalies(
    provider_name: Optional[str] = None,
    severity: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    service_name: Optional[str] = None,
    min_cost_impact: Optional[float] = None,
    max_cost_impact: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None,
    service = None
) -> List[Any]:
    """
    Versão otimizada para buscar anomalias com cache e filtros eficientes
    """
    
    # Gerar chave de cache baseada nos parâmetros
    cache_key = f"anomalies_{provider_name}_{severity}_{anomaly_type}_{service_name}_{min_cost_impact}_{max_cost_impact}"
    current_time = datetime.utcnow()
    
    # Verificar cache
    if cache_key in _anomalies_cache:
        cached_data, cached_time = _anomalies_cache[cache_key]
        if (current_time - cached_time).total_seconds() < _cache_lifetime:
            logger.info(f"Retornando anomalias do cache: {cache_key}")
            return cached_data
    
    # Se não estiver em cache, buscar e aplicar filtros de forma otimizada
    try:
        # Buscar todas as anomalias uma única vez
        all_anomalies = await service.get_anomalies_by_provider(provider_name=provider_name)
        
        # Aplicar filtros de forma otimizada (usando list comprehension)
        filtered_anomalies = [
            anomaly for anomaly in all_anomalies
            if _passes_filters(
                anomaly, severity, anomaly_type, service_name,
                min_cost_impact, max_cost_impact, start_date, end_date, search
            )
        ]
        
        # Salvar no cache
        _anomalies_cache[cache_key] = (filtered_anomalies, current_time)
        
        logger.info(f"Anomalias filtradas e cacheadas: {len(filtered_anomalies)} resultados")
        return filtered_anomalies
        
    except Exception as e:
        logger.error(f"Erro ao buscar anomalias otimizadas: {e}")
        return []

def _passes_filters(
    anomaly,
    severity: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    service_name: Optional[str] = None,
    min_cost_impact: Optional[float] = None,
    max_cost_impact: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
) -> bool:
    """
    Função otimizada para verificar se uma anomalia passa pelos filtros
    """
    
    # Filtro por severidade
    if severity and hasattr(anomaly, 'severity'):
        if anomaly.severity.lower() != severity.lower():
            return False
    
    # Filtro por tipo de anomalia
    if anomaly_type and hasattr(anomaly, 'anomaly_type'):
        if anomaly_type.lower() not in anomaly.anomaly_type.lower():
            return False
    
    # Filtro por nome do serviço
    if service_name and hasattr(anomaly, 'service'):
        if service_name.lower() not in anomaly.service.lower():
            return False
    
    # Filtro por impacto de custo
    if min_cost_impact is not None and hasattr(anomaly, 'cost_impact'):
        if anomaly.cost_impact < min_cost_impact:
            return False
    
    if max_cost_impact is not None and hasattr(anomaly, 'cost_impact'):
        if anomaly.cost_impact > max_cost_impact:
            return False
    
    # Filtro por data
    if start_date and hasattr(anomaly, 'detected_at'):
        anomaly_date = anomaly.detected_at.date() if hasattr(anomaly.detected_at, 'date') else anomaly.detected_at
        if anomaly_date < start_date:
            return False
    
    if end_date and hasattr(anomaly, 'detected_at'):
        anomaly_date = anomaly.detected_at.date() if hasattr(anomaly.detected_at, 'date') else anomaly.detected_at
        if anomaly_date > end_date:
            return False
    
    # Filtro de busca
    if search:
        search_term = search.lower()
        searchable_fields = [
            str(getattr(anomaly, 'resource_name', '')).lower(),
            str(getattr(anomaly, 'description', '')).lower(),
            str(getattr(anomaly, 'service', '')).lower(),
            str(getattr(anomaly, 'anomaly_type', '')).lower()
        ]
        
        if not any(search_term in field for field in searchable_fields):
            return False
    
    return True

def clear_anomalies_cache():
    """Limpa o cache de anomalias"""
    global _anomalies_cache
    _anomalies_cache.clear()
    logger.info("Cache de anomalias limpo")

def get_cache_stats():
    """Retorna estatísticas do cache"""
    return {
        "cache_size": len(_anomalies_cache),
        "cache_keys": list(_anomalies_cache.keys())
    }
