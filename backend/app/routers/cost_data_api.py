"""
Cost Data API Router

Endpoints para recuperação de dados de custo básicos
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_cache, SessionLocal
from app.models import (
    FocusCostData, FocusCostDataResponse, CostQueryParams
)
from app.credential_models import User
from app.auth_security import get_current_active_user
from app.utils.response_helpers import StandardResponse, calculate_processing_time

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1", tags=["Cost Data"])


@router.get("/costs", response_model=List[FocusCostDataResponse])
@calculate_processing_time
async def get_costs(
    params: CostQueryParams = Depends(),
    cache = Depends(get_cache),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém dados de custo com filtros opcionais
    
    Permite filtrar por:
    - Provedor de nuvem
    - Serviço
    - Tipo de recurso
    - Período de cobrança
    - Tags personalizadas
    
    Resultados são cacheados por 15 minutos para melhor performance.
    """
    try:
        # Gerar chave de cache baseada nos parâmetros
        cache_key = f"costs:{hash(str(params.dict()))}"
        
        # Tentar obter do cache primeiro
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cost data retrieved from cache for user: {current_user.username}")
            return cached_result
        
        # Buscar dados do banco de dados
        db = SessionLocal()
        try:
            # Construir query base
            query = db.query(FocusCostData)
            
            # Aplicar filtros baseados nos parâmetros
            if params.provider_name:
                query = query.filter(FocusCostData.provider_name == params.provider_name)
            
            if params.service_name:
                query = query.filter(FocusCostData.service_name == params.service_name)
            
            if params.resource_type:
                query = query.filter(FocusCostData.resource_type == params.resource_type)
            
            if params.start_date:
                query = query.filter(FocusCostData.billing_period_start >= params.start_date)
            
            if params.end_date:
                query = query.filter(FocusCostData.billing_period_end <= params.end_date)
            
            # Filtros por tags (usando JSONB)
            if params.tags:
                for key, value in params.tags.items():
                    query = query.filter(FocusCostData.tags[key].astext == value)
            
            # Aplicar ordenação e paginação
            results = query.order_by(
                FocusCostData.billing_period_start.desc()
            ).offset(params.offset).limit(params.limit).all()
            
            # Converter para response model
            response_data = [FocusCostDataResponse.from_orm(result) for result in results]
            
            # Cachear resultado por 15 minutos
            cache.set(cache_key, response_data, ttl=900)
            
            logger.info(
                f"Cost data retrieved for user: {current_user.username}, "
                f"found {len(response_data)} records"
            )
            
            return response_data
            
        finally:
            db.close()
        
    except Exception as e:
        logger.error(f"Error fetching costs for user {current_user.username}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve cost data: {str(e)}"
        )


@router.get("/costs/summary")
@calculate_processing_time
async def get_costs_summary(
    params: CostQueryParams = Depends(),
    cache = Depends(get_cache),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém resumo dos custos agrupados por dimensões principais
    """
    try:
        # Gerar chave de cache
        cache_key = f"costs_summary:{hash(str(params.dict()))}"
        
        # Tentar obter do cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        db = SessionLocal()
        try:
            # Query base com mesmos filtros
            query = db.query(FocusCostData)
            
            # Aplicar filtros
            if params.provider_name:
                query = query.filter(FocusCostData.provider_name == params.provider_name)
            if params.service_name:
                query = query.filter(FocusCostData.service_name == params.service_name)
            if params.resource_type:
                query = query.filter(FocusCostData.resource_type == params.resource_type)
            if params.start_date:
                query = query.filter(FocusCostData.billing_period_start >= params.start_date)
            if params.end_date:
                query = query.filter(FocusCostData.billing_period_end <= params.end_date)
            
            # Calcular totais
            from sqlalchemy import func
            
            # Total geral
            total_cost = query.with_entities(
                func.sum(FocusCostData.billed_cost).label('total')
            ).scalar() or 0
            
            # Por provedor
            by_provider = query.with_entities(
                FocusCostData.provider_name,
                func.sum(FocusCostData.billed_cost).label('total_cost'),
                func.count(FocusCostData.id).label('record_count')
            ).group_by(FocusCostData.provider_name).all()
            
            # Por serviço (top 10)
            by_service = query.with_entities(
                FocusCostData.service_name,
                func.sum(FocusCostData.billed_cost).label('total_cost'),
                func.count(FocusCostData.id).label('record_count')
            ).group_by(FocusCostData.service_name).order_by(
                func.sum(FocusCostData.billed_cost).desc()
            ).limit(10).all()
            
            summary = {
                "total_cost": float(total_cost),
                "currency": "USD",  # Assumindo USD como padrão
                "record_count": query.count(),
                "by_provider": [
                    {
                        "provider": item.provider_name,
                        "total_cost": float(item.total_cost),
                        "record_count": item.record_count
                    }
                    for item in by_provider
                ],
                "by_service": [
                    {
                        "service": item.service_name,
                        "total_cost": float(item.total_cost),
                        "record_count": item.record_count
                    }
                    for item in by_service
                ]
            }
            
            # Cachear resultado por 30 minutos
            cache.set(cache_key, summary, ttl=1800)
            
            return StandardResponse.success(summary)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error fetching cost summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/costs/providers")
async def get_available_providers(
    current_user: User = Depends(get_current_active_user),
    cache = Depends(get_cache)
):
    """
    Obtém lista de provedores disponíveis nos dados de custo
    """
    try:
        cache_key = "available_providers"
        
        # Tentar obter do cache
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        db = SessionLocal()
        try:
            from sqlalchemy import func, distinct
            
            # Obter provedores únicos com contagem
            providers = db.query(
                FocusCostData.provider_name,
                func.count(FocusCostData.id).label('record_count'),
                func.sum(FocusCostData.billed_cost).label('total_cost'),
                func.min(FocusCostData.billing_period_start).label('earliest_date'),
                func.max(FocusCostData.billing_period_end).label('latest_date')
            ).group_by(FocusCostData.provider_name).all()
            
            provider_list = [
                {
                    "name": p.provider_name,
                    "record_count": p.record_count,
                    "total_cost": float(p.total_cost or 0),
                    "date_range": {
                        "earliest": p.earliest_date,
                        "latest": p.latest_date
                    }
                }
                for p in providers
            ]
            
            result = {
                "providers": provider_list,
                "total_providers": len(provider_list)
            }
            
            # Cachear por 1 hora
            cache.set(cache_key, result, ttl=3600)
            
            return StandardResponse.success(result)
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error fetching available providers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias para compatibilidade
cost_data_router = router