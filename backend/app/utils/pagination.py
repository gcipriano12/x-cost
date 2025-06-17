"""
Pagination Utilities

Utilitários para paginação consistente em toda a API
"""

from typing import Dict, List, Any, Optional
from fastapi import Query
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Parâmetros de paginação"""
    page: int = 1
    per_page: int = 20
    
    def __init__(self, page: int = 1, per_page: int = 20):
        super().__init__(page=max(1, page), per_page=min(max(1, per_page), 100))
    
    @property
    def offset(self) -> int:
        """Calcula o offset para a query"""
        return (self.page - 1) * self.per_page
    
    @property
    def limit(self) -> int:
        """Retorna o limite para a query"""
        return self.per_page


def get_pagination_params(
    page: int = Query(1, ge=1, description="Número da página (começa em 1)"),
    per_page: int = Query(20, ge=1, le=100, description="Items por página (max 100)")
) -> PaginationParams:
    """Dependency para obter parâmetros de paginação"""
    return PaginationParams(page=page, per_page=per_page)


def apply_pagination(
    query_result: List[Any], 
    pagination: PaginationParams
) -> List[Any]:
    """
    Aplica paginação a uma lista de resultados
    
    Args:
        query_result: Lista de resultados da query
        pagination: Parâmetros de paginação
        
    Returns:
        Lista paginada
    """
    start = pagination.offset
    end = start + pagination.limit
    return query_result[start:end]


def get_pagination_metadata(
    total_items: int,
    pagination: PaginationParams,
    processing_time: Optional[float] = None
) -> Dict[str, Any]:
    """
    Gera metadados de paginação para a resposta
    
    Args:
        total_items: Total de items disponíveis
        pagination: Parâmetros de paginação utilizados
        processing_time: Tempo de processamento em segundos
        
    Returns:
        Dicionário com metadados de paginação
    """
    total_pages = max(1, (total_items + pagination.per_page - 1) // pagination.per_page)
    
    metadata = {
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": pagination.page < total_pages,
            "has_previous": pagination.page > 1
        }
    }
    
    if processing_time is not None:
        metadata["processing_time"] = round(processing_time, 3)
    
    return metadata


class PaginatedResponse(BaseModel):
    """Modelo base para respostas paginadas"""
    data: List[Any]
    metadata: Dict[str, Any]
    
    @classmethod
    def create(
        cls,
        items: List[Any],
        total_items: int,
        pagination: PaginationParams,
        processing_time: Optional[float] = None
    ):
        """Cria uma resposta paginada"""
        paginated_items = apply_pagination(items, pagination)
        metadata = get_pagination_metadata(total_items, pagination, processing_time)
        
        return cls(
            data=paginated_items,
            metadata=metadata
        )