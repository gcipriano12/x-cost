"""
Cloud Provider Implementations

Este módulo contém implementações específicas para diferentes provedores de nuvem.
"""

from .base import BaseOptimizationService
from .aws import AWSOptimizationService
from .azure import AzureOptimizationService
from .gcp import GCPOptimizationService
from .oracle import OracleOptimizationService

__all__ = [
    'BaseOptimizationService',
    'AWSOptimizationService',
    'AzureOptimizationService',
    'GCPOptimizationService',
    'OracleOptimizationService'
]