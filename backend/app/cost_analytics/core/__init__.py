"""
Core Analytics Module

Módulo com funcionalidades base para análise de custos
"""

from .data_processing import get_service_category, ServiceCategoryMapper
from .query_builder import QueryBuilder
from .calculations import StatisticalCalculations

__all__ = [
    'get_service_category',
    'ServiceCategoryMapper',
    'QueryBuilder', 
    'StatisticalCalculations'
]