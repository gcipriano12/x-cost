"""
Rate Limiting Utilities

Utilitários para limitação de taxa de requisições (rate limiting)
"""

import time
import logging
from collections import defaultdict
from functools import wraps
from typing import Dict, List

from fastapi import HTTPException

logger = logging.getLogger(__name__)

# Armazenamento em memória para rate limiting
# Em produção, usar Redis ou similar
_rate_limit_storage: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))


def rate_limit(max_requests: int, window_minutes: int = 1):
    """
    Rate limiting decorator
    
    Limita o número de requisições por usuário em uma janela de tempo.
    
    Args:
        max_requests: Número máximo de requisições permitidas
        window_minutes: Janela de tempo em minutos
    
    Usage:
        @rate_limit(max_requests=100, window_minutes=1)
        async def my_endpoint():
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extrair current_user dos kwargs se disponível
            current_user = kwargs.get('current_user')
            if not current_user:
                # Se não houver usuário, pular rate limiting
                return await func(*args, **kwargs)
            
            user_id = current_user.username
            endpoint = func.__name__
            window_seconds = window_minutes * 60
            current_time = time.time()
            
            # Limpar requisições antigas
            _rate_limit_storage[user_id][endpoint] = [
                req_time for req_time in _rate_limit_storage[user_id][endpoint]
                if current_time - req_time < window_seconds
            ]
            
            # Verificar se excedeu o limite
            if len(_rate_limit_storage[user_id][endpoint]) >= max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id} on endpoint {endpoint}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_minutes} minute(s)."
                )
            
            # Registrar a requisição atual
            _rate_limit_storage[user_id][endpoint].append(current_time)
            
            # Executar a função
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator


def get_rate_limit_status(user_id: str, endpoint: str, window_minutes: int = 1) -> Dict:
    """
    Obtém o status atual do rate limiting para um usuário/endpoint
    
    Args:
        user_id: ID do usuário
        endpoint: Nome do endpoint
        window_minutes: Janela de tempo em minutos
    
    Returns:
        Dicionário com informações do rate limiting
    """
    window_seconds = window_minutes * 60
    current_time = time.time()
    
    # Limpar requisições antigas
    if user_id in _rate_limit_storage and endpoint in _rate_limit_storage[user_id]:
        _rate_limit_storage[user_id][endpoint] = [
            req_time for req_time in _rate_limit_storage[user_id][endpoint]
            if current_time - req_time < window_seconds
        ]
        
        requests_in_window = len(_rate_limit_storage[user_id][endpoint])
    else:
        requests_in_window = 0
    
    return {
        "user_id": user_id,
        "endpoint": endpoint,
        "requests_in_window": requests_in_window,
        "window_minutes": window_minutes,
        "last_request": _rate_limit_storage[user_id][endpoint][-1] if requests_in_window > 0 else None
    }


def clear_rate_limit_data(user_id: str = None, endpoint: str = None):
    """
    Limpa dados de rate limiting
    
    Args:
        user_id: ID do usuário (opcional, se não fornecido limpa todos)
        endpoint: Nome do endpoint (opcional, se não fornecido limpa todos)
    """
    if user_id and endpoint:
        # Limpar endpoint específico de usuário específico
        if user_id in _rate_limit_storage:
            _rate_limit_storage[user_id].pop(endpoint, None)
    elif user_id:
        # Limpar todos os endpoints de usuário específico
        _rate_limit_storage.pop(user_id, None)
    else:
        # Limpar todos os dados
        _rate_limit_storage.clear()
    
    logger.info(f"Rate limit data cleared for user_id={user_id}, endpoint={endpoint}")


def get_all_rate_limit_stats() -> Dict:
    """
    Obtém estatísticas gerais de rate limiting
    
    Returns:
        Dicionário com estatísticas gerais
    """
    total_users = len(_rate_limit_storage)
    total_endpoints = sum(len(endpoints) for endpoints in _rate_limit_storage.values())
    total_requests_tracked = sum(
        len(requests) for user_data in _rate_limit_storage.values()
        for requests in user_data.values()
    )
    
    return {
        "total_users_tracked": total_users,
        "total_endpoints_tracked": total_endpoints,
        "total_requests_tracked": total_requests_tracked,
        "storage_size_bytes": len(str(_rate_limit_storage))
    }