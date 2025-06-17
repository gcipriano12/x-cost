"""
Factory para criação de serviços de otimização
"""

import logging
from typing import Dict, Optional, Any, List

from .providers.base import BaseOptimizationService
from .providers.aws import AWSOptimizationService
from .providers.azure import AzureOptimizationService
from .providers.gcp import GCPOptimizationService
from .providers.oracle import OracleOptimizationService

logger = logging.getLogger(__name__)


class OptimizationServiceFactory:
    """Factory para criar instâncias de serviços de otimização"""
    
    _services = {
        "aws": AWSOptimizationService,
        "azure": AzureOptimizationService,
        "gcp": GCPOptimizationService,
        "oracle": OracleOptimizationService,
    }
    
    @classmethod
    def create_service(
        self, 
        provider: str, 
        credentials: Optional[Dict[str, Any]] = None
    ) -> BaseOptimizationService:
        """
        Cria uma instância do serviço de otimização para o provedor especificado
        
        Args:
            provider: Nome do provedor (aws, azure, gcp, oracle)
            credentials: Credenciais específicas do provedor
            
        Returns:
            Instância do serviço de otimização
            
        Raises:
            ValueError: Se o provedor não for suportado
            ImportError: Se as dependências do provedor não estiverem disponíveis
        """
        provider_lower = provider.lower()
        
        if provider_lower not in self._services:
            available = ", ".join(self._services.keys())
            raise ValueError(f"Provedor '{provider}' não suportado. Disponíveis: {available}")
        
        service_class = self._services[provider_lower]
        credentials = credentials or {}
        
        try:
            if provider_lower == "aws":
                return service_class(
                    access_key=credentials.get("access_key"),
                    secret_key=credentials.get("secret_key"),
                    region=credentials.get("region", "us-east-1")
                )
            elif provider_lower == "azure":
                return service_class(
                    subscription_id=credentials.get("subscription_id"),
                    tenant_id=credentials.get("tenant_id")
                )
            elif provider_lower == "gcp":
                return service_class(
                    project_id=credentials.get("project_id"),
                    credentials_path=credentials.get("credentials_path")
                )
            elif provider_lower == "oracle":
                return service_class(
                    config_file=credentials.get("config_file"),
                    profile=credentials.get("profile")
                )
            
        except ImportError as e:
            logger.error(f"Dependências para {provider} não disponíveis: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao criar serviço {provider}: {e}")
            raise
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Retorna lista de provedores suportados"""
        return list(cls._services.keys())
    
    @classmethod
    def is_provider_supported(cls, provider: str) -> bool:
        """Verifica se um provedor é suportado"""
        return provider.lower() in cls._services