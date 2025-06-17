"""
Analytics API Router

Endpoints para análise avançada de custos e dashboards
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_database
from app.models import DashboardSummary
from app.credential_models import User
from app.auth_security import get_current_active_user
from app.cost_analytics import CostAnalyzer, DashboardAnalyzer
from app.utils.response_helpers import StandardResponse, calculate_processing_time
from app.utils.validators import validate_date_range

logger = logging.getLogger(__name__)

# Criar router
router = APIRouter(prefix="/api/v1", tags=["Analytics"])


@router.get("/analytics/trend")
@calculate_processing_time
async def get_cost_trend(
    provider_name: Optional[str] = None,
    service_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    period: str = "daily",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Obtém tendência de custos ao longo do tempo
    
    Permite analisar a evolução dos custos por:
    - Provedor específico ou todos
    - Serviço específico ou todos
    - Período customizável (daily, weekly, monthly)
    - Range de datas flexível
    """
    try:
        # Validar parâmetros
        if period not in ["daily", "weekly", "monthly"]:
            raise HTTPException(
                status_code=400,
                detail="Period must be 'daily', 'weekly', or 'monthly'"
            )
        
        # Validar range de datas se fornecido
        if start_date and end_date:
            validate_date_range(start_date.date(), end_date.date(), max_days=365)
        
        analyzer = CostAnalyzer(db)
        trend_data = analyzer.calculate_cost_trend(
            provider_name=provider_name,
            service_name=service_name,
            start_date=start_date.date() if start_date else None,
            end_date=end_date.date() if end_date else None,
            period=period
        )
        
        return StandardResponse.success({
            "trend_data": trend_data,
            "period": period,
            "filters": {
                "provider_name": provider_name,
                "service_name": service_name,
                "start_date": start_date,
                "end_date": end_date
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating trend: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/by-service")
@calculate_processing_time
async def get_cost_by_service(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_n: Optional[int] = 10,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Obtém breakdown de custos por serviço
    
    Analisa a distribuição de custos entre diferentes serviços cloud,
    permitindo identificar os maiores gastadores e otimizar recursos.
    """
    try:
        # Determinar período: usar start_date/end_date se fornecidos, senão usar 'days'
        if start_date and end_date:
            validate_date_range(start_date, end_date, max_days=365)
            period_start = start_date
            period_end = end_date
            period_days = (end_date - start_date).days + 1
        else:
            # Usar lógica baseada em 'days'
            period_end = date.today()
            period_start = period_end - timedelta(days=days-1)
            period_days = days
        
        # Validar top_n
        if top_n and (top_n < 1 or top_n > 100):
            raise HTTPException(
                status_code=400,
                detail="top_n must be between 1 and 100"
            )
        
        analyzer = CostAnalyzer(db)
        
        # Usar provider_name passado como parâmetro
        effective_provider_name = provider_name
        if credential_id and not provider_name:
            # TODO: Buscar provider_name baseado no credential_id se necessário
            effective_provider_name = None
        
        service_data = analyzer.analyze_costs_by_service(
            provider_name=effective_provider_name,
            start_date=period_start,
            end_date=period_end,
            limit=top_n or 10
        )
        
        return StandardResponse.success({
            "service_breakdown": service_data,
            "period": {
                "start_date": period_start,
                "end_date": period_end,
                "days": period_days
            },
            "filters": {
                "credential_id": credential_id,
                "provider_name": effective_provider_name,
                "top_n": top_n
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating service breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/by-region")
@calculate_processing_time
async def get_cost_by_region(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_n: Optional[int] = 10,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Obtém breakdown de custos por região
    
    Analisa a distribuição geográfica dos custos, permitindo otimizar
    a distribuição de recursos entre diferentes regiões.
    """
    try:
        # Determinar período
        if start_date and end_date:
            validate_date_range(start_date, end_date, max_days=365)
            period_start = start_date
            period_end = end_date
            period_days = (end_date - start_date).days + 1
        else:
            period_end = date.today()
            period_start = period_end - timedelta(days=days-1)
            period_days = days
        
        analyzer = CostAnalyzer(db)
        
        effective_provider_name = provider_name
        if credential_id and not provider_name:
            effective_provider_name = None
        
        region_data = analyzer.analyze_costs_by_region(
            provider_name=effective_provider_name,
            start_date=period_start,
            end_date=period_end,
            limit=top_n or 10
        )
        
        return StandardResponse.success({
            "region_breakdown": region_data,
            "period": {
                "start_date": period_start,
                "end_date": period_end,
                "days": period_days
            },
            "filters": {
                "credential_id": credential_id,
                "provider_name": effective_provider_name,
                "top_n": top_n
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating region breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/by-category")
@calculate_processing_time
async def get_cost_by_category(
    credential_id: Optional[str] = None,
    days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    top_n: Optional[int] = 10,
    provider_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Obtém breakdown de custos por categoria de serviço
    
    Agrupa serviços em categorias funcionais (Computation, Storage, Database, etc.)
    para análise estratégica de gastos por tipo de recurso.
    """
    try:
        # Determinar período
        if start_date and end_date:
            validate_date_range(start_date, end_date, max_days=365)
            period_start = start_date
            period_end = end_date
            period_days = (end_date - start_date).days + 1
        else:
            period_end = date.today()
            period_start = period_end - timedelta(days=days-1)
            period_days = days
        
        analyzer = CostAnalyzer(db)
        
        # Obter dados por serviço primeiro
        service_data = analyzer.analyze_costs_by_service(
            provider_name=provider_name,
            start_date=period_start,
            end_date=period_end,
            limit=100  # Buscar mais serviços para agrupamento
        )
        
        # Agrupar por categoria
        from app.cost_analytics.core.data_processing import get_service_category
        
        category_totals = {}
        total_cost = 0
        
        for service in service_data:
            category = service['category']  # Já vem categorizado do analyzer
            cost = service['total_cost']
            total_cost += cost
            
            if category not in category_totals:
                category_totals[category] = {
                    'category': category,
                    'total_cost': 0,
                    'service_count': 0,
                    'services': []
                }
            
            category_totals[category]['total_cost'] += cost
            category_totals[category]['service_count'] += 1
            category_totals[category]['services'].append({
                'service_name': service['service_name'],
                'cost': cost
            })
        
        # Converter para lista e ordenar
        category_data = list(category_totals.values())
        category_data.sort(key=lambda x: x['total_cost'], reverse=True)
        
        # Limitar resultados
        if top_n:
            category_data = category_data[:top_n]
        
        # Adicionar percentuais
        for category in category_data:
            category['percentage_of_total'] = (
                (category['total_cost'] / total_cost * 100) if total_cost > 0 else 0
            )
        
        return StandardResponse.success({
            "category_breakdown": category_data,
            "period": {
                "start_date": period_start,
                "end_date": period_end,
                "days": period_days
            },
            "totals": {
                "total_cost": total_cost,
                "categories_count": len(category_data)
            },
            "filters": {
                "credential_id": credential_id,
                "provider_name": provider_name,
                "top_n": top_n
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating category breakdown: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/forecast")
@calculate_processing_time
async def get_cost_forecast(
    provider_name: Optional[str] = None,
    service_name: Optional[str] = None,
    historical_days: Optional[int] = 30,
    forecast_days: Optional[int] = 30,
    method: str = "linear",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Gera previsão de custos futuros
    
    Utiliza dados históricos para prever custos futuros usando
    algoritmos de machine learning simples.
    """
    try:
        # Validar parâmetros
        if method not in ["linear", "exponential"]:
            raise HTTPException(
                status_code=400,
                detail="Method must be 'linear' or 'exponential'"
            )
        
        if historical_days < 7 or historical_days > 365:
            raise HTTPException(
                status_code=400,
                detail="historical_days must be between 7 and 365"
            )
        
        if forecast_days < 1 or forecast_days > 90:
            raise HTTPException(
                status_code=400,
                detail="forecast_days must be between 1 and 90"
            )
        
        analyzer = CostAnalyzer(db)
        forecast_result = analyzer.forecast_costs(
            historical_days=historical_days or 30,
            forecast_days=forecast_days or 30,
            provider_name=provider_name,
            service_name=service_name,
            method=method
        )
        
        if 'error' in forecast_result:
            raise HTTPException(status_code=400, detail=forecast_result['error'])
        
        return StandardResponse.success({
            **forecast_result,
            "filters": {
                "provider_name": provider_name,
                "service_name": service_name,
                "method": method
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating forecast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/comparison")
@calculate_processing_time
async def get_cost_comparison(
    current_start: date,
    current_end: date,
    comparison_start: date,
    comparison_end: date,
    provider_name: Optional[str] = None,
    service_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Compara custos entre dois períodos
    
    Permite análise de mudanças de custo entre períodos específicos,
    identificando tendências e variações significativas.
    """
    try:
        # Validar datas
        validate_date_range(current_start, current_end, max_days=365)
        validate_date_range(comparison_start, comparison_end, max_days=365)
        
        analyzer = CostAnalyzer(db)
        delta_result = analyzer.calculate_cost_delta(
            provider_name=provider_name,
            service_name=service_name,
            current_period_start=current_start,
            current_period_end=current_end,
            comparison_period_start=comparison_start,
            comparison_period_end=comparison_end
        )
        
        if not delta_result:
            raise HTTPException(
                status_code=404,
                detail="No data found for the specified periods"
            )
        
        return StandardResponse.success({
            **delta_result,
            "filters": {
                "provider_name": provider_name,
                "service_name": service_name
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/summary")
@calculate_processing_time
async def get_dashboard_summary(
    period_days: Optional[int] = 30,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    providers: Optional[str] = None,  # Comma-separated list
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Obtém resumo consolidado para dashboard
    
    Agrega múltiplas métricas e análises em um único endpoint
    otimizado para exibição em dashboards.
    """
    try:
        # Determinar período
        if start_date and end_date:
            validate_date_range(start_date, end_date, max_days=365)
            calculated_days = (end_date - start_date).days + 1
        else:
            calculated_days = period_days or 30
            end_date = date.today()
            start_date = end_date - timedelta(days=calculated_days - 1)
        
        # Processar lista de provedores
        provider_list = None
        if providers:
            provider_list = [p.strip() for p in providers.split(',') if p.strip()]
        
        dashboard_analyzer = DashboardAnalyzer(db)
        summary = dashboard_analyzer.get_dashboard_summary(
            start_date=start_date,
            end_date=end_date,
            providers=provider_list
        )
        
        if 'error' in summary:
            raise HTTPException(status_code=500, detail=summary['error'])
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/tags/{tag_key}")
@calculate_processing_time
async def get_cost_by_tag(
    tag_key: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: Optional[int] = 20,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """
    Analisa custos por tag específica
    
    Permite análise de custos baseada em tags customizadas,
    útil para análise por projetos, departamentos ou ambientes.
    """
    try:
        # Validar parâmetros
        if not tag_key.strip():
            raise HTTPException(
                status_code=400,
                detail="tag_key cannot be empty"
            )
        
        if limit and (limit < 1 or limit > 100):
            raise HTTPException(
                status_code=400,
                detail="limit must be between 1 and 100"
            )
        
        # Usar período padrão se não especificado
        if not start_date or not end_date:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        else:
            validate_date_range(start_date, end_date, max_days=365)
        
        analyzer = CostAnalyzer(db)
        tag_analysis = analyzer.analyze_costs_by_tags(
            start_date=start_date,
            end_date=end_date,
            tag_key=tag_key,
            limit=limit or 20
        )
        
        return StandardResponse.success({
            "tag_analysis": tag_analysis,
            "tag_key": tag_key,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "requested_by": current_user.username
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing costs by tag: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Alias para compatibilidade
analytics_router = router