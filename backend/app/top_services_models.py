"""
Modelos Pydantic para Top Services endpoint
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class TopServiceItem(BaseModel):
    """Item individual do top services"""
    id: str = Field(..., description="ID único do serviço (service-{index})")
    service_name: str = Field(..., description="Nome do serviço (ex: EC2, S3)")
    provider: str = Field(..., description="Provedor cloud (AWS, Azure, GCP)")
    cost: float = Field(..., description="Custo atual do período")
    change_from_previous: float = Field(..., description="Variação % do período anterior")
    region: Optional[str] = Field(None, description="Região principal do serviço")
    currency: str = Field(default="USD", description="Moeda dos valores")


class TopServicesPeriod(BaseModel):
    """Período analisado"""
    start_date: str = Field(..., description="Data início (YYYY-MM-DD)")
    end_date: str = Field(..., description="Data fim (YYYY-MM-DD)")


class PaginationInfo(BaseModel):
    """Informações de paginação"""
    page: int = Field(..., description="Página atual")
    page_size: int = Field(..., description="Itens por página")
    total_items: int = Field(..., description="Total de itens disponíveis")
    total_pages: int = Field(..., description="Total de páginas")
    has_next: bool = Field(..., description="Há próxima página")
    has_previous: bool = Field(..., description="Há página anterior")


class TopServicesData(BaseModel):
    """Dados dos top services"""
    services: List[TopServiceItem] = Field(..., description="Lista dos top services")
    total_services: int = Field(..., description="Total de serviços únicos encontrados")
    period: TopServicesPeriod = Field(..., description="Período analisado")
    pagination: PaginationInfo = Field(..., description="Informações de paginação")


class TopServicesResponse(BaseModel):
    """Resposta completa do endpoint top services"""
    status: str = Field(default="success", description="Status da resposta")
    data: TopServicesData = Field(..., description="Dados dos top services")
