"""
Cache Utilities Module

Utilitários para cache de análises de custo
"""

import hashlib
import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union


class AnalyticsCache:
    """
    Gerenciador de cache específico para análises de custo
    """
    
    # TTL padrão por tipo de análise (em segundos)
    DEFAULT_TTL = {
        "cost_trends": 1800,      # 30 minutos
        "budget_analysis": 900,   # 15 minutos
        "dashboard_summary": 600, # 10 minutos
        "forecasting": 3600,      # 1 hora
        "comparisons": 1800,      # 30 minutos
        "aggregations": 900,      # 15 minutos
        "distribution": 1200,     # 20 minutos
    }
    
    def __init__(self, cache_client=None):
        """
        Inicializa o gerenciador de cache
        
        Args:
            cache_client: Cliente de cache (Redis, etc.)
        """
        self.cache = cache_client
        self.prefix = "cost_analytics"
    
    def generate_key(
        self,
        analysis_type: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        providers: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> str:
        """
        Gera chave de cache baseada nos parâmetros
        
        Args:
            analysis_type: Tipo de análise
            start_date: Data inicial
            end_date: Data final
            providers: Lista de provedores
            services: Lista de serviços
            regions: Lista de regiões
            tags: Dicionário de tags
            **kwargs: Parâmetros adicionais
            
        Returns:
            Chave de cache
        """
        key_components = {
            "type": analysis_type,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "providers": sorted(providers) if providers else None,
            "services": sorted(services) if services else None,
            "regions": sorted(regions) if regions else None,
            "tags": dict(sorted(tags.items())) if tags else None,
        }
        
        # Adicionar parâmetros extras ordenados
        for key in sorted(kwargs.keys()):
            key_components[key] = kwargs[key]
        
        # Filtrar valores None
        filtered_components = {
            k: v for k, v in key_components.items() if v is not None
        }
        
        # Gerar hash MD5 para chave estável
        key_string = json.dumps(filtered_components, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{self.prefix}:{analysis_type}:{key_hash}"
    
    def get(self, key: str) -> Any:
        """
        Recupera dados do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Dados do cache ou None
        """
        if not self.cache:
            return None
        
        try:
            cached_data = self.cache.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set(
        self,
        key: str,
        data: Any,
        ttl: Optional[int] = None,
        analysis_type: Optional[str] = None
    ) -> bool:
        """
        Armazena dados no cache
        
        Args:
            key: Chave do cache
            data: Dados para armazenar
            ttl: Time to live em segundos
            analysis_type: Tipo de análise para TTL automático
            
        Returns:
            True se armazenado com sucesso
        """
        if not self.cache:
            return False
        
        # Determinar TTL
        if ttl is None and analysis_type:
            ttl = self.DEFAULT_TTL.get(analysis_type, 900)
        elif ttl is None:
            ttl = 900  # 15 minutos padrão
        
        try:
            serialized_data = json.dumps(data, default=self._json_serializer)
            self.cache.setex(key, ttl, serialized_data)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Remove dados do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            True se removido com sucesso
        """
        if not self.cache:
            return False
        
        try:
            self.cache.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Remove múltiplas chaves baseadas em padrão
        
        Args:
            pattern: Padrão de chaves (ex: "cost_analytics:trends:*")
            
        Returns:
            Número de chaves removidas
        """
        if not self.cache:
            return 0
        
        try:
            keys = self.cache.keys(pattern)
            if keys:
                return self.cache.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache clear pattern error: {e}")
            return 0
    
    def clear_analysis_type(self, analysis_type: str) -> int:
        """
        Remove todas as chaves de um tipo de análise
        
        Args:
            analysis_type: Tipo de análise
            
        Returns:
            Número de chaves removidas
        """
        pattern = f"{self.prefix}:{analysis_type}:*"
        return self.clear_pattern(pattern)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        if not self.cache:
            return {"status": "disabled"}
        
        try:
            info = self.cache.info()
            analytics_keys = len(self.cache.keys(f"{self.prefix}:*"))
            
            return {
                "status": "enabled",
                "total_keys": info.get("db0", {}).get("keys", 0),
                "analytics_keys": analytics_keys,
                "memory_usage": info.get("used_memory_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0)
            }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def warmup_cache(
        self,
        common_queries: List[Dict[str, Any]]
    ) -> Dict[str, bool]:
        """
        Pré-aquece o cache com queries comuns
        
        Args:
            common_queries: Lista de queries para pré-carregar
            
        Returns:
            Resultado do warmup por query
        """
        results = {}
        
        for i, query in enumerate(common_queries):
            query_id = f"warmup_query_{i}"
            try:
                key = self.generate_key(**query)
                # Aqui você executaria a query real e armazenaria o resultado
                # Por agora, apenas marcamos como preparado
                results[query_id] = True
            except Exception as e:
                results[query_id] = False
                print(f"Warmup error for query {query_id}: {e}")
        
        return results
    
    def _json_serializer(self, obj):
        """Serializer personalizado para objetos especiais"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, timedelta):
            return obj.total_seconds()
        elif hasattr(obj, 'dict'):  # Pydantic models
            return obj.dict()
        elif hasattr(obj, '__dict__'):  # Classes customizadas
            return obj.__dict__
        else:
            return str(obj)
    
    def create_cache_key_builder(self, base_type: str):
        """
        Cria um builder de chaves específico para um tipo
        
        Args:
            base_type: Tipo base para o builder
            
        Returns:
            Função builder
        """
        def builder(**kwargs):
            return self.generate_key(base_type, **kwargs)
        
        return builder


class CacheDecorator:
    """
    Decorator para cache automático de métodos de análise
    """
    
    def __init__(
        self,
        cache_manager: AnalyticsCache,
        analysis_type: str,
        ttl: Optional[int] = None
    ):
        """
        Inicializa o decorator
        
        Args:
            cache_manager: Gerenciador de cache
            analysis_type: Tipo de análise
            ttl: Time to live customizado
        """
        self.cache = cache_manager
        self.analysis_type = analysis_type
        self.ttl = ttl
    
    def __call__(self, func):
        """
        Aplica cache ao método
        
        Args:
            func: Função a ser decorada
            
        Returns:
            Função decorada
        """
        def wrapper(*args, **kwargs):
            # Gerar chave baseada nos argumentos
            cache_key = self.cache.generate_key(
                self.analysis_type,
                **kwargs
            )
            
            # Tentar recuperar do cache
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            self.cache.set(
                cache_key,
                result,
                ttl=self.ttl,
                analysis_type=self.analysis_type
            )
            
            return result
        
        return wrapper