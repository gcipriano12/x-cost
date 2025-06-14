import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import os

# IMPORTANTE: Remover TODOS os imports que podem causar recursão
# import boto3  # Comentado temporariamente
# import requests  # Comentado temporariamente

logger = logging.getLogger(__name__)

class SecretsManagerSimple:
    """Versão ultra-simplificada para debug de recursão"""
    
    def __init__(self, region_name: str = None, kms_key_id: str = None):
        self.region_name = region_name or os.getenv('AWS_REGION', 'us-east-1')
        self.kms_key_id = kms_key_id or os.getenv('FINOPS_KMS_KEY_ID')
        self.is_localstack = self._is_localstack_environment()
        
        # Por enquanto, apenas simular sucesso
        self.access_method = "debug_mode"
        
        logger.info(f"✅ SecretsManagerSimple inicializado em modo debug")
        logger.info(f"   - Região: {self.region_name}")
        logger.info(f"   - LocalStack: {self.is_localstack}")
    
    def _is_localstack_environment(self) -> bool:
        """Detecta se estamos usando LocalStack"""
        environment = os.getenv('ENVIRONMENT', 'production').lower()
        aws_endpoint = os.getenv('AWS_ENDPOINT_URL', '')
        
        return (
            environment in ['development', 'dev', 'local'] or
            'localhost' in aws_endpoint or
            '4566' in aws_endpoint
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Health check simplificado"""
        try:
            # Apenas retornar sucesso para debug
            return {
                "status": "healthy",
                "access_method": "debug_mode",
                "is_localstack": self.is_localstack,
                "region": self.region_name,
                "endpoint": "debug_mode",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Debug mode - sem conexões reais"
            }
        except Exception as e:
            logger.error(f"Erro no health check debug: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "access_method": "debug_mode",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def create_test_secret(self, name: str = "test-secret") -> str:
        """Mock de criação de secret"""
        logger.info(f"🧪 Mock: criando secret de teste '{name}'")
        return f"arn:aws:secretsmanager:{self.region_name}:000000000000:secret:debug/{name}"
    
    def store_credentials(self, credential_name: str, provider_type: str, credentials: dict, description: str = None, expires_at=None) -> Tuple[str, str]:
        """Mock de armazenamento de credenciais"""
        logger.info(f"🧪 Mock: armazenando credencial '{credential_name}' para {provider_type}")
        if expires_at:
            logger.info(f"🧪 Mock: credencial expira em {expires_at}")
        secret_name = f"finops/credentials/{provider_type.lower()}/{credential_name}"
        arn = f"arn:aws:secretsmanager:{self.region_name}:000000000000:secret:{secret_name}"
        return arn, secret_name
    
    def retrieve_credentials(self, secret_arn: str) -> Dict[str, Any]:
        """Mock de recuperação de credenciais"""
        logger.info(f"🧪 Mock: recuperando credencial {secret_arn}")
        return {
            'provider_type': 'AWS',
            'credential_name': 'debug-credential',
            'credentials': {'access_key_id': 'MOCK_KEY'},
            'created_at': datetime.utcnow().isoformat()
        }
    
    def delete_credentials(self, secret_arn: str, force_delete: bool = False) -> bool:
        """Mock de remoção de credenciais"""
        logger.info(f"🧪 Mock: removendo credencial {secret_arn}")
        return True
    
    def validate_credentials(self, secret_arn: str) -> Dict[str, Any]:
        """Mock de validação de credenciais"""
        logger.info(f"🧪 Mock: validando credencial {secret_arn}")
        return {
            'is_valid': True,
            'provider_type': 'AWS',
            'validation_timestamp': datetime.utcnow(),
            'account_info': {'account_id': 'debug-mode'},
            'access_method': 'debug_mode'
        }

# ========= SEÇÃO CRÍTICA: EVITAR RECURSÃO =========

# Variável global para singleton
_secrets_manager_instance = None
_initialization_in_progress = False  # Flag para evitar recursão

def get_secrets_manager():
    """
    Factory function com proteção anti-recursão
    """
    global _secrets_manager_instance, _initialization_in_progress
    
    # PROTEÇÃO ANTI-RECURSÃO
    if _initialization_in_progress:
        logger.error("🚨 RECURSÃO DETECTADA em get_secrets_manager!")
        raise RuntimeError("Recursion detected in get_secrets_manager initialization")
    
    if _secrets_manager_instance is None:
        try:
            _initialization_in_progress = True
            logger.info("🔧 Inicializando SecretsManagerSimple (modo debug)...")
            
            _secrets_manager_instance = SecretsManagerSimple()
            
            logger.info("✅ SecretsManagerSimple inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro inicializando SecretsManagerSimple: {e}")
            _secrets_manager_instance = None
            raise
        finally:
            _initialization_in_progress = False
    
    return _secrets_manager_instance

def reset_secrets_manager():
    """Reseta a instância global"""
    global _secrets_manager_instance, _initialization_in_progress
    _secrets_manager_instance = None
    _initialization_in_progress = False
    logger.info("🔄 SecretsManager resetado")

# Aliases para compatibilidade - TODOS apontam para a mesma função
def get_secrets_manager_hybrid():
    """Alias para compatibilidade"""
    return get_secrets_manager()

def get_secrets_manager_hybrid_isolated():
    """Alias para compatibilidade"""
    return get_secrets_manager()

def get_secrets_manager_hybrid_workaround():
    """Alias para compatibilidade"""
    return get_secrets_manager()

# Health check standalone sem criar singleton
def secrets_manager_health_check() -> Dict[str, Any]:
    """Health check direto sem singleton"""
    try:
        # Criar instância temporária SEM usar o singleton
        temp_manager = SecretsManagerSimple()
        return temp_manager.health_check()
    except Exception as e:
        logger.error(f"Health check standalone falhou: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

# Função de debug para identificar recursão
def debug_call_stack():
    """Função para debug de call stack"""
    import traceback
    logger.info("🔍 Call stack atual:")
    for line in traceback.format_stack():
        if 'secrets_manager' in line:
            logger.info(f"   {line.strip()}")

# Verificação de inicialização
logger.info("📋 secrets_manager.py carregado - versão debug anti-recursão")
logger.info(f"   - Modo LocalStack: {os.getenv('ENVIRONMENT', 'production') in ['development', 'dev', 'local']}")
logger.info(f"   - AWS_ENDPOINT_URL: {os.getenv('AWS_ENDPOINT_URL', 'não definido')}")