"""
Query Builder Module

Módulo para construção de queries SQL reutilizáveis para análise de custos
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy import func, and_, or_, text
from sqlalchemy.orm import Query

from app.models import FocusCostData


class QueryBuilder:
    """
    Construtor de queries SQL para análise de custos
    """
    
    def __init__(self, session):
        """
        Inicializa o construtor de queries
        
        Args:
            session: Sessão SQLAlchemy
        """
        self.session = session
        self.base_query = session.query(FocusCostData)
    
    def filter_by_date_range(
        self, 
        query: Query, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        date_field: str = "billing_period_start"
    ) -> Query:
        """
        Aplica filtro de range de datas
        
        Args:
            query: Query SQLAlchemy
            start_date: Data inicial
            end_date: Data final  
            date_field: Campo de data para filtrar
            
        Returns:
            Query filtrada
        """
        if start_date:
            field = getattr(FocusCostData, date_field)
            query = query.filter(field >= start_date)
        
        if end_date:
            field = getattr(FocusCostData, date_field)
            query = query.filter(field <= end_date)
        
        return query
    
    def filter_by_provider(self, query: Query, providers: List[str]) -> Query:
        """Filtra por provedores"""
        if providers:
            query = query.filter(FocusCostData.provider_name.in_(providers))
        return query
    
    def filter_by_service(self, query: Query, services: List[str]) -> Query:
        """Filtra por serviços"""
        if services:
            query = query.filter(FocusCostData.service_name.in_(services))
        return query
    
    def filter_by_region(self, query: Query, regions: List[str]) -> Query:
        """Filtra por regiões"""
        if regions:
            query = query.filter(FocusCostData.region.in_(regions))
        return query
    
    def filter_by_tags(self, query: Query, tags: Dict[str, str]) -> Query:
        """Filtra por tags"""
        if tags:
            for key, value in tags.items():
                query = query.filter(FocusCostData.tags[key].astext == value)
        return query
    
    def apply_filters(
        self,
        query: Query,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        providers: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        regions: Optional[List[str]] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> Query:
        """
        Aplica múltiplos filtros de uma vez
        
        Args:
            query: Query base
            start_date: Data inicial
            end_date: Data final
            providers: Lista de provedores
            services: Lista de serviços
            regions: Lista de regiões
            tags: Dicionário de tags
            
        Returns:
            Query filtrada
        """
        query = self.filter_by_date_range(query, start_date, end_date)
        query = self.filter_by_provider(query, providers or [])
        query = self.filter_by_service(query, services or [])
        query = self.filter_by_region(query, regions or [])
        query = self.filter_by_tags(query, tags or {})
        
        return query
    
    def get_cost_aggregations(
        self, 
        group_by_fields: List[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters
    ) -> Query:
        """
        Cria query para agregações de custo
        
        Args:
            group_by_fields: Campos para agrupamento
            start_date: Data inicial
            end_date: Data final
            **filters: Filtros adicionais
            
        Returns:
            Query com agregações
        """
        # Campos de agregação padrão
        select_fields = []
        
        # Adicionar campos de agrupamento
        for field in group_by_fields:
            if hasattr(FocusCostData, field):
                select_fields.append(getattr(FocusCostData, field))
        
        # Adicionar agregações usando effective_cost (mesmo campo do DashboardAnalyzer)
        select_fields.extend([
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.avg(FocusCostData.effective_cost).label('avg_cost'),
            func.count(FocusCostData.id).label('record_count'),
            func.min(FocusCostData.billing_period_start).label('earliest_date'),
            func.max(FocusCostData.billing_period_end).label('latest_date')
        ])
        
        query = self.session.query(*select_fields)
        
        # Aplicar filtros
        query = self.apply_filters(
            query, start_date, end_date, **filters
        )
        
        # Aplicar agrupamento
        for field in group_by_fields:
            if hasattr(FocusCostData, field):
                query = query.group_by(getattr(FocusCostData, field))
        
        return query
    
    def get_time_series_data(
        self,
        start_date: date,
        end_date: date,
        period: str = "daily",
        **filters
    ) -> Query:
        """
        Cria query para dados de série temporal
        
        Args:
            start_date: Data inicial
            end_date: Data final
            period: Período (daily, weekly, monthly)
            **filters: Filtros adicionais
            
        Returns:
            Query para série temporal
        """
        # Determinar função de agrupamento temporal
        if period == "daily":
            date_trunc = func.date(FocusCostData.billing_period_start)
        elif period == "weekly":
            date_trunc = func.date_trunc('week', FocusCostData.billing_period_start)
        elif period == "monthly":
            date_trunc = func.date_trunc('month', FocusCostData.billing_period_start)
        else:
            date_trunc = func.date(FocusCostData.billing_period_start)
        
        query = self.session.query(
            date_trunc.label('period'),
            func.sum(FocusCostData.billed_cost).label('total_cost'),
            func.count(FocusCostData.id).label('record_count')
        )
        
        # Aplicar filtros
        query = self.apply_filters(
            query, start_date, end_date, **filters
        )
        
        # Agrupar por período
        query = query.group_by(date_trunc).order_by(date_trunc)
        
        return query
    
    def get_top_spenders(
        self,
        dimension: str,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters
    ) -> Query:
        """
        Cria query para maiores gastadores por dimensão
        
        Args:
            dimension: Dimensão para análise (provider_name, service_name, region)
            limit: Número de resultados
            start_date: Data inicial
            end_date: Data final
            **filters: Filtros adicionais
            
        Returns:
            Query para top spenders
        """
        if not hasattr(FocusCostData, dimension):
            raise ValueError(f"Invalid dimension: {dimension}")
        
        dimension_field = getattr(FocusCostData, dimension)
        
        query = self.session.query(
            dimension_field.label('dimension_value'),
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count(FocusCostData.id).label('record_count'),
            func.avg(FocusCostData.effective_cost).label('avg_cost')
        )
        
        # Aplicar filtros
        query = self.apply_filters(
            query, start_date, end_date, **filters
        )
        
        # Agrupar e ordenar
        query = query.group_by(dimension_field).order_by(
            func.sum(FocusCostData.billed_cost).desc()
        ).limit(limit)
        
        return query
    
    def get_cost_distribution(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **filters
    ) -> Dict[str, Query]:
        """
        Cria queries para distribuição de custos por múltiplas dimensões
        
        Returns:
            Dicionário com queries para cada dimensão
        """
        dimensions = ['provider_name', 'service_name', 'region']
        queries = {}
        
        for dimension in dimensions:
            queries[dimension] = self.get_top_spenders(
                dimension=dimension,
                limit=20,
                start_date=start_date,
                end_date=end_date,
                **filters
            )
        
        return queries
    
    def build_cache_key(
        self,
        prefix: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **params
    ) -> str:
        """
        Constrói chave de cache para queries
        
        Args:
            prefix: Prefixo da chave
            start_date: Data inicial
            end_date: Data final
            **params: Parâmetros adicionais
            
        Returns:
            Chave de cache
        """
        key_parts = [prefix]
        
        if start_date:
            key_parts.append(f"start_{start_date.isoformat()}")
        if end_date:
            key_parts.append(f"end_{end_date.isoformat()}")
        
        # Adicionar parâmetros ordenados
        for key in sorted(params.keys()):
            value = params[key]
            if isinstance(value, list):
                value = ",".join(sorted(map(str, value)))
            key_parts.append(f"{key}_{value}")
        
        return ":".join(key_parts)


class QueryOptimizer:
    """
    Otimizador de queries para melhor performance
    """
    
    @staticmethod
    def add_indexes_hints(query: Query, table_name: str = "focus_cost_data") -> Query:
        """Adiciona hints de índice para PostgreSQL"""
        # Para PostgreSQL, podemos usar hints específicos se necessário
        return query
    
    @staticmethod
    def optimize_large_date_ranges(
        query: Query,
        start_date: date,
        end_date: date,
        chunk_size_days: int = 90
    ) -> List[Query]:
        """
        Quebra queries de grandes períodos em chunks menores
        
        Args:
            query: Query base
            start_date: Data inicial
            end_date: Data final
            chunk_size_days: Tamanho do chunk em dias
            
        Returns:
            Lista de queries menores
        """
        chunks = []
        current_start = start_date
        
        while current_start <= end_date:
            current_end = min(
                current_start + timedelta(days=chunk_size_days),
                end_date
            )
            
            # Clonar query e aplicar filtro de data
            chunk_query = query.filter(
                and_(
                    FocusCostData.billing_period_start >= current_start,
                    FocusCostData.billing_period_end <= current_end
                )
            )
            
            chunks.append(chunk_query)
            current_start = current_end + timedelta(days=1)
        
        return chunks