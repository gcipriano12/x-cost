"""
Rate Limiting Middleware

Middleware para controle de taxa de requisições por usuário
"""

import time
import functools
from collections import defaultdict
from typing import Dict, Any, Callable
from fastapi import HTTPException, Request
from fastapi.responses import Response


class RateLimiter:
    """
    Rate limiter em memória (para produção, usar Redis)
    """
    
    def __init__(self):
        self._storage: Dict[str, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
    
    def is_allowed(
        self, 
        user_id: str, 
        endpoint: str, 
        max_requests: int, 
        window_minutes: int
    ) -> bool:
        """
        Verifica se uma requisição é permitida dentro do rate limit
        
        Args:
            user_id: ID do usuário
            endpoint: Nome do endpoint
            max_requests: Máximo de requisições permitidas
            window_minutes: Janela de tempo em minutos
            
        Returns:
            True se a requisição é permitida, False caso contrário
        """
        now = time.time()
        window_start = now - (window_minutes * 60)
        
        # Limpar requests antigos
        self._storage[user_id][endpoint] = [
            req_time for req_time in self._storage[user_id][endpoint]
            if req_time > window_start
        ]
        
        # Verificar limite
        if len(self._storage[user_id][endpoint]) >= max_requests:
            return False
        
        # Registrar request atual
        self._storage[user_id][endpoint].append(now)
        return True
    
    def get_remaining_requests(
        self, 
        user_id: str, 
        endpoint: str, 
        max_requests: int
    ) -> int:
        """
        Retorna o número de requisições restantes
        """
        current_requests = len(self._storage[user_id][endpoint])
        return max(0, max_requests - current_requests)
    
    def get_reset_time(
        self, 
        user_id: str, 
        endpoint: str, 
        window_minutes: int
    ) -> float:
        """
        Retorna o timestamp quando o rate limit será resetado
        """
        if not self._storage[user_id][endpoint]:
            return time.time()
        
        oldest_request = min(self._storage[user_id][endpoint])
        return oldest_request + (window_minutes * 60)


# Instância global do rate limiter
_rate_limiter = RateLimiter()


def rate_limit(max_requests: int, window_minutes: int = 1):
    """
    Rate limiting decorator para endpoints
    
    Args:
        max_requests: Máximo de requisições permitidas
        window_minutes: Janela de tempo em minutos
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Encontrar o request e current_user nos argumentos
            request = None
            current_user = None
            
            for arg in args:
                if hasattr(arg, 'method') and hasattr(arg, 'url'):  # Request object
                    request = arg
                elif hasattr(arg, 'username'):  # User object
                    current_user = arg
                    
            for value in kwargs.values():
                if hasattr(value, 'method') and hasattr(value, 'url'):  # Request object
                    request = value
                elif hasattr(value, 'username'):  # User object
                    current_user = value
            
            if current_user:
                user_id = current_user.username
                endpoint = func.__name__
                
                # Verificar rate limit
                if not _rate_limiter.is_allowed(user_id, endpoint, max_requests, window_minutes):
                    remaining = _rate_limiter.get_remaining_requests(user_id, endpoint, max_requests)
                    reset_time = _rate_limiter.get_reset_time(user_id, endpoint, window_minutes)
                    
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_minutes} minute(s)",
                        headers={
                            "X-RateLimit-Limit": str(max_requests),
                            "X-RateLimit-Remaining": str(remaining),
                            "X-RateLimit-Reset": str(int(reset_time))
                        }
                    )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def rate_limit_middleware(request: Request, call_next) -> Response:
    """
    Middleware global de rate limiting (opcional)
    
    Args:
        request: Requisição HTTP
        call_next: Próximo middleware na cadeia
        
    Returns:
        Response com headers de rate limiting
    """
    response = await call_next(request)
    
    # Adicionar headers informativos sobre rate limiting
    response.headers["X-RateLimit-Policy"] = "Applied per endpoint"
    
    return response


def get_rate_limiter() -> RateLimiter:
    """
    Dependency para obter instância do rate limiter
    """
    return _rate_limiter


class RedisRateLimiter:
    """
    Rate limiter usando Redis (para produção)
    """
    
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(
        self, 
        user_id: str, 
        endpoint: str, 
        max_requests: int, 
        window_minutes: int
    ) -> bool:
        """
        Implementação com Redis para ambientes distribuídos
        """
        key = f"rate_limit:{user_id}:{endpoint}"
        window_seconds = window_minutes * 60
        
        # Usar pipeline para operações atômicas
        pipe = self.redis.pipeline()
        
        # Adicionar timestamp atual
        now = time.time()
        pipe.zadd(key, {str(now): now})
        
        # Remover entradas antigas
        pipe.zremrangebyscore(key, 0, now - window_seconds)
        
        # Contar entradas no período
        pipe.zcard(key)
        
        # Definir expiração
        pipe.expire(key, window_seconds)
        
        results = pipe.execute()
        current_count = results[2]  # Resultado do zcard
        
        return current_count <= max_requests