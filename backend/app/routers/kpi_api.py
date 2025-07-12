"""
KPI API Router - X Cost
Endpoints para Key Performance Indicators
"""

import logging
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_database
from app.auth_security import get_current_active_user
from app.credential_models import User
from app.kpi.models import (
    KPICategory, KPIValueResponse, KPICategoryResponse,
    KPIDefinitionResponse, KPIHistoryResponse
)
from app.kpi.service import KPIService
from app.utils.response_helpers import StandardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/kpis", tags=["KPIs"])

@router.get("/current")
async def get_current_kpis(
    category: Optional[KPICategory] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém valores atuais dos KPIs
    
    - **category**: Filtrar por categoria (efficiency, pricing, planning, governance)
    """
    try:
        service = KPIService(db)
        kpis = service.get_current_kpis(category=category)
        
        return StandardResponse.success(
            data={'kpis': kpis},
            message=f"Retrieved {len(kpis)} KPIs"
        )
        
    except Exception as e:
        logger.error(f"Error getting current KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-category")
async def get_kpis_by_category(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém KPIs agrupados por categoria com resumo
    """
    try:
        service = KPIService(db)
        categories = service.get_kpis_by_category()
        
        return StandardResponse.success(
            data={'categories': categories},
            message="KPIs grouped by category"
        )
        
    except Exception as e:
        logger.error(f"Error getting KPIs by category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-summary")
async def get_kpi_dashboard_summary(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém resumo geral dos KPIs para dashboard
    """
    try:
        service = KPIService(db)
        summary = service.get_kpi_dashboard_summary()
        
        return StandardResponse.success(
            
            message="KPI dashboard summary",
            data=summary
        )
        
    except Exception as e:
        logger.error(f"Error getting KPI dashboard summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{kpi_code}")
async def get_kpi_history(
    kpi_code: str,
    days: int = Query(30, ge=1, le=365, description="Number of days of history"),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém histórico de um KPI específico
    
    - **kpi_code**: Código do KPI (ex: resource_utilization_rate)
    - **days**: Número de dias de histórico (padrão: 30, máximo: 365)
    """
    try:
        service = KPIService(db)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        history = service.get_kpi_history(kpi_code, start_date, end_date)
        
        return StandardResponse.success(
            
            message=f"Retrieved {len(history)} data points for {kpi_code}",
            data={
                'kpi_code': kpi_code,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'history': history
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting KPI history for {kpi_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/details/{kpi_code}")
async def get_kpi_details(
    kpi_code: str,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém detalhes completos de um KPI específico
    
    - **kpi_code**: Código do KPI
    """
    try:
        service = KPIService(db)
        kpi = service.get_kpi_by_code(kpi_code)
        
        if not kpi:
            raise HTTPException(status_code=404, detail=f"KPI {kpi_code} not found")
        
        # Buscar histórico dos últimos 30 dias para contexto
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        history = service.get_kpi_history(kpi_code, start_date, end_date)
        
        return StandardResponse.success(
            
            message=f"KPI details for {kpi_code}",
            data={
                'kpi': kpi,
                'recent_history': history[-7:] if history else [],  # Últimos 7 pontos
                'total_history_points': len(history)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting KPI details for {kpi_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate")
async def calculate_kpis(
    background_tasks: BackgroundTasks,
    calculation_date: Optional[date] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Executa cálculo de KPIs (admin only)
    
    - **calculation_date**: Data para cálculo (padrão: hoje)
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = KPIService(db)
        
        # Para cálculos pequenos, executar sincrono
        # Para datasets grandes, usar background task
        calc_date = calculation_date or date.today()
        
        def calculate_task():
            return service.calculate_kpis(calc_date)
        
        # Executar em background para não bloquear
        background_tasks.add_task(calculate_task)
        
        return StandardResponse.success(
            
            message="KPI calculation started in background",
            data={
                'calculation_date': calc_date.isoformat(),
                'status': 'started'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting KPI calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-sync")
async def calculate_kpis_sync(
    calculation_date: Optional[date] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Executa cálculo de KPIs sincrono (admin only)
    
    - **calculation_date**: Data para cálculo (padrão: hoje)
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = KPIService(db)
        
        calc_date = calculation_date or date.today()
        result = service.calculate_kpis(calc_date)
        
        return StandardResponse.success(
            
            message=f"KPI calculation completed: {result.get('success_count', 0)} success, {result.get('error_count', 0)} errors",
            data=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating KPIs sync: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config/{kpi_code}")
async def update_kpi_config(
    kpi_code: str,
    target_value: Optional[float] = None,
    warning_threshold: Optional[float] = None,
    critical_threshold: Optional[float] = None,
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza configuração de KPI para a empresa (admin only)
    
    - **kpi_code**: Código do KPI
    - **target_value**: Novo valor alvo
    - **warning_threshold**: Limite para warning
    - **critical_threshold**: Limite para critical
    - **is_enabled**: Se o KPI está habilitado
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = KPIService(db)
        
        # Por enquanto, usar company_id fixo
        # TODO: Implementar multi-tenant real
        company_id = "default-company"
        
        config = service.update_kpi_config(
            kpi_code=kpi_code,
            company_id=company_id,
            target_value=target_value,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            is_enabled=is_enabled
        )
        
        if not config:
            raise HTTPException(status_code=404, detail=f"KPI {kpi_code} not found")
        
        return StandardResponse.success(
            
            message=f"KPI configuration updated for {kpi_code}",
            data={'config': config}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating KPI config for {kpi_code}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/definitions")
async def get_kpi_definitions(
    category: Optional[KPICategory] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas as definições de KPIs disponíveis
    
    - **category**: Filtrar por categoria (efficiency, pricing, planning, governance)
    """
    try:
        service = KPIService(db)
        definitions = service.get_kpi_definitions(category=category)
        
        # Converter para formato de resposta
        definition_responses = []
        for definition in definitions:
            definition_responses.append(KPIDefinitionResponse(
                id=definition.id,
                code=definition.code,
                name=definition.name,
                category=definition.category,
                description=definition.description,
                formula=definition.formula,
                unit=definition.unit,
                target_value=definition.target_value,
                is_good_when_higher=definition.is_good_when_higher,
                calculation_frequency=definition.calculation_frequency,
                is_active=definition.is_active,
                created_at=definition.created_at,
                updated_at=definition.updated_at
            ))
        
        return StandardResponse.success(
            
            message=f"Retrieved {len(definitions)} KPI definitions",
            data={'definitions': definition_responses}
        )
        
    except Exception as e:
        logger.error(f"Error getting KPI definitions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_kpi_categories(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas as categorias de KPIs disponíveis
    """
    try:
        categories = [
            {
                'value': category.value,
                'label': category.value.title(),
                'description': _get_category_description(category)
            }
            for category in KPICategory
        ]
        
        return StandardResponse.success(
            
            message="KPI categories",
            data={'categories': categories}
        )
        
    except Exception as e:
        logger.error(f"Error getting KPI categories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_category_description(category: KPICategory) -> str:
    """Retorna descrição da categoria"""
    descriptions = {
        KPICategory.EFFICIENCY: "Métricas de eficiência e utilização de recursos",
        KPICategory.PRICING: "Métricas de economia e pricing de cloud",
        KPICategory.PLANNING: "Métricas de planejamento e previsão de custos",
        KPICategory.GOVERNANCE: "Métricas de governança e compliance"
    }
    return descriptions.get(category, "")

# Health check endpoint
@router.get("/health")
async def kpi_health_check(
    db: Session = Depends(get_database)
):
    """
    Verifica saúde do sistema de KPIs
    """
    try:
        # Verificar se as tabelas existem
        from app.kpi.models import KPIDefinition
        
        count = db.query(KPIDefinition).count()
        
        return StandardResponse.success(
            
            message="KPI system is healthy",
            data={
                'kpi_definitions_count': count,
                'system_status': 'operational'
            }
        )
        
    except Exception as e:
        logger.error(f"KPI health check failed: {str(e)}")
        return StandardResponse.success(
            success=False,
            message="KPI system health check failed",
            data={
                'error': str(e),
                'system_status': 'error'
            }
        )
