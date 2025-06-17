"""
Decorators para retry e tratamento de erros
"""

import asyncio
import logging
import random
from functools import wraps
from typing import Union

try:
    from botocore.exceptions import BotoCoreError, ClientError
    AWS_AVAILABLE = True
except ImportError:
    # Fallback para quando boto3 não estiver disponível
    class ClientError(Exception):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.response = kwargs.get('response', {})
    
    class BotoCoreError(Exception):
        pass
    
    AWS_AVAILABLE = False


def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Decorator para retry com exponential backoff
    
    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        exponential_base: Base para exponential backoff
        jitter: Adicionar jitter para evitar thundering herd
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (ClientError, BotoCoreError) as e:
                    last_exception = e
                    
                    # Não fazer retry para alguns tipos de erro
                    if isinstance(e, ClientError):
                        error_code = e.response.get('Error', {}).get('Code', '')
                        
                        # Erros que não devem ser retentados
                        if error_code in [
                            'AccessDenied', 'InvalidUserID.NotFound', 'Forbidden',
                            'UnauthorizedOperation', 'NoCredentialsError', 'InvalidParameterValue'
                        ]:
                            raise e
                    
                    if attempt == max_retries:
                        break
                    
                    # Calcular delay com exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Adicionar jitter se solicitado
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    # Log do retry
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"API call failed (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )
                    
                    await asyncio.sleep(delay)
                except Exception as e:
                    # Para outras exceções, não fazer retry
                    raise e
            
            # Se chegou aqui, todas as tentativas falharam
            raise last_exception
        
        return wrapper
    return decorator