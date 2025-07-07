"""
Services API Router

Endpoints específicos para análise de serviços cloud
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_database
from app.credential_models import User
from app.auth_security import get_current_active_user
from app.top_services_analytics import TopServicesAnalyzer
from app.top_services_models import TopServicesResponse, TopServicesData
from app.utils.response_helpers import StandardResponse, calculate_processing_time
from app.utils.validators import validate_date_range

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1/services", tags=["Services"])


@router.get("/top", response_model=TopServicesResponse)
@calculate_processing_time
async def get_top_services(
    credential_id: str = Query(..., description="ID da credencial cloud"),
    start_date: Optional[date] = Query(None, description="Data início do período (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="Data fim do período (YYYY-MM-DD)"),
    provider_name: Optional[str] = Query(None, description="Filtro por provider específico"),
    page: int = Query(1, ge=1, description="Número da página (inicia em 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página (1-100)"),
    sort_by: str = Query("cost", description="Campo para ordenação: cost, service_name, provider, change_from_previous"),
    sort_order: str = Query("desc", description="Ordem: asc (crescente) ou desc (decrescente)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
) -> TopServicesResponse:
    """
    Obtém os principais serviços por custo com paginação e ordenação
    
    **Funcionalidade:**
    - Retorna todos os serviços com paginação (em vez de limite fixo)
    - Calcula variação percentual em relação ao período anterior
    - Suporta filtros por provider e período customizável
    - Agrega custos por serviço+provider (soma diferentes regiões)
    - Suporta ordenação por qualquer campo
    
    **Paginação:**
    - page: número da página (começa em 1)
    - page_size: itens por página (padrão: 10, máximo: 100)
    
    **Ordenação:**
    - sort_by: campo para ordenação (cost, service_name, provider, change_from_previous)
    - sort_order: ordem crescente (asc) ou decrescente (desc)
    - Padrão: ordenação por cost desc (maior custo primeiro)
    
    **Lógica de Variação:**
    - Compara período atual com período anterior de mesma duração
    - Exemplo: período de 30 dias compara com 30 dias anteriores
    - Serviços novos aparecem com variação de +100%
    - Variação negativa indica redução de custos
    
    **Providers Suportados:**
    - AWS, Azure, GCP, Oracle Cloud
    
    **Validações:**
    - credential_id deve existir e estar ativo
    - Datas devem estar em formato válido (YYYY-MM-DD)
    - provider_name deve ser válido se especificado
    - page deve ser >= 1
    - page_size deve estar entre 1 e 100
    - sort_by deve ser um campo válido
    - sort_order deve ser 'asc' ou 'desc'
    """
    
    try:
        # Validações iniciais
        if start_date and end_date:
            validate_date_range(start_date, end_date, max_days=365)
        
        # Validar provider_name se fornecido
        supported_providers = ["AWS", "Azure", "GCP", "Oracle Cloud"]
        if provider_name and provider_name not in supported_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Provider '{provider_name}' não suportado. Suportados: {supported_providers}"
            )
        
        # Validar parâmetros de ordenação
        valid_sort_fields = ["cost", "service_name", "provider", "change_from_previous"]
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Campo de ordenação '{sort_by}' inválido. Válidos: {valid_sort_fields}"
            )
        
        valid_sort_orders = ["asc", "desc"]
        if sort_order not in valid_sort_orders:
            raise HTTPException(
                status_code=400,
                detail=f"Ordem de ordenação '{sort_order}' inválida. Válidas: {valid_sort_orders}"
            )
        
        # Definir período padrão se não fornecido
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)  # 30 dias padrão
        
        # Validar período mínimo
        period_days = (end_date - start_date).days + 1
        if period_days < 1:
            raise HTTPException(
                status_code=400,
                detail="Período deve ter pelo menos 1 dia"
            )
        
        logger.info(f"Getting services with pagination for user {current_user.username}")
        logger.info(f"Page: {page}, Page size: {page_size}")
        logger.info(f"Sorting: {sort_by} {sort_order}")
        logger.info(f"Period: {start_date} to {end_date} ({period_days} days)")
        logger.info(f"Provider filter: {provider_name or 'All'}")
        logger.info(f"Credential ID: {credential_id}")
        
        # Criar analyzer
        analyzer = TopServicesAnalyzer(db)
        
        # Validar credencial (placeholder por enquanto)
        if not analyzer.validate_credential(credential_id):
            raise HTTPException(
                status_code=404,
                detail=f"Credencial '{credential_id}' não encontrada ou inativa"
            )
        
        # Obter dados dos top services com paginação e ordenação
        top_services_data = analyzer.get_top_services(
            credential_id=credential_id,
            start_date=start_date,
            end_date=end_date,
            provider_name=provider_name,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        logger.info(f"Found {len(top_services_data.services)} services, total unique services: {top_services_data.total_services}")
        
        # Log dos resultados para debug
        for i, service in enumerate(top_services_data.services):
            logger.debug(f"Service {i+1}: {service.service_name} ({service.provider}) - ${service.cost:,.2f} ({service.change_from_previous:+.1f}%)")
        
        return TopServicesResponse(
            status="success",
            data=top_services_data
        )
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.warning(f"Validation error in top services: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting top services: {str(e)}")
        logger.exception("Full error traceback:")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter top services"
        )
