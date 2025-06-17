"""
Filtering Utilities

Utilitários para filtros consistentes em toda a API
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime, date
from fastapi import Query
from pydantic import BaseModel


class DateRangeFilter(BaseModel):
    """Filtro de range de datas"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    
    def is_valid(self) -> bool:
        """Verifica se o range de datas é válido"""
        if self.start_date and self.end_date:
            return self.start_date <= self.end_date
        return True
    
    def to_datetime_range(self) -> tuple[Optional[datetime], Optional[datetime]]:
        """Converte para datetime range"""
        start_dt = datetime.combine(self.start_date, datetime.min.time()) if self.start_date else None
        end_dt = datetime.combine(self.end_date, datetime.max.time()) if self.end_date else None
        return start_dt, end_dt


class SearchFilter(BaseModel):
    """Filtro de busca textual"""
    query: Optional[str] = None
    fields: List[str] = []
    
    def matches(self, item: Dict[str, Any]) -> bool:
        """Verifica se um item corresponde ao filtro de busca"""
        if not self.query:
            return True
        
        query_lower = self.query.lower()
        
        # Se não há campos específicos, busca em todos os campos string
        search_fields = self.fields if self.fields else [
            k for k, v in item.items() if isinstance(v, str)
        ]
        
        for field in search_fields:
            if field in item and isinstance(item[field], str):
                if query_lower in item[field].lower():
                    return True
        
        return False


class NumericRangeFilter(BaseModel):
    """Filtro de range numérico"""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    
    def matches(self, value: Union[int, float]) -> bool:
        """Verifica se um valor está no range"""
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True


class ListFilter(BaseModel):
    """Filtro para valores em lista"""
    values: List[str] = []
    
    def matches(self, value: str) -> bool:
        """Verifica se o valor está na lista"""
        if not self.values:
            return True
        return value in self.values


def get_date_range_filter(
    start_date: Optional[date] = Query(None, description="Data de início (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data de fim (YYYY-MM-DD)")
) -> DateRangeFilter:
    """Dependency para obter filtro de range de datas"""
    return DateRangeFilter(start_date=start_date, end_date=end_date)


def get_search_filter(
    search: Optional[str] = Query(None, description="Termo de busca")
) -> SearchFilter:
    """Dependency para obter filtro de busca"""
    return SearchFilter(query=search)


def apply_filters(
    items: List[Dict[str, Any]],
    filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Aplica múltiplos filtros a uma lista de items
    
    Args:
        items: Lista de items para filtrar
        filters: Dicionário com filtros a aplicar
        
    Returns:
        Lista filtrada
    """
    filtered_items = items.copy()
    
    for filter_name, filter_obj in filters.items():
        if filter_obj is None:
            continue
            
        if isinstance(filter_obj, SearchFilter):
            filtered_items = [item for item in filtered_items if filter_obj.matches(item)]
        elif isinstance(filter_obj, DateRangeFilter) and filter_obj.start_date and filter_obj.end_date:
            start_dt, end_dt = filter_obj.to_datetime_range()
            filtered_items = [
                item for item in filtered_items
                if 'date' in item and start_dt <= item['date'] <= end_dt
            ]
        elif isinstance(filter_obj, NumericRangeFilter):
            # Aplicar filtro numérico baseado no nome do filtro
            field_name = filter_name.replace('_filter', '')
            filtered_items = [
                item for item in filtered_items
                if field_name in item and filter_obj.matches(item[field_name])
            ]
        elif isinstance(filter_obj, ListFilter):
            # Aplicar filtro de lista baseado no nome do filtro
            field_name = filter_name.replace('_filter', '')
            filtered_items = [
                item for item in filtered_items
                if field_name in item and filter_obj.matches(item[field_name])
            ]
    
    return filtered_items


def create_numeric_range_filter(
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> NumericRangeFilter:
    """Cria um filtro de range numérico"""
    return NumericRangeFilter(min_value=min_value, max_value=max_value)


def create_list_filter(values: List[str]) -> ListFilter:
    """Cria um filtro de lista"""
    return ListFilter(values=values)