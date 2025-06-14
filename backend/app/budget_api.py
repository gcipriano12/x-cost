"""
API endpoints para gerenciamento de budgets
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import logging

from app.database import get_database
from app.models import Budget, BudgetCreate, BudgetResponse
from app.credential_models import User
from app.auth_security import get_current_active_user
from app.cost_analytics import BudgetAnalyzer
from decimal import Decimal
from sqlalchemy import func

logger = logging.getLogger(__name__)

# Router para budgets
budget_router = APIRouter(prefix="/api/v1/budgets", tags=["budgets"])

# Modelo de resposta para lista de budgets com resumo
class BudgetListResponse(BaseModel):
    budgets: List[BudgetResponse]
    total_count: int
    total_budget_amount: str
    total_consumption: str  
    overall_consumption_percentage: str

@budget_router.get("", response_model=BudgetListResponse)
async def list_budgets(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user),
    provider_name: Optional[str] = None,
    service_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    budget_period: Optional[str] = None
):
    """
    Lista todos os budgets do usuário com filtros opcionais e dados agregados
    """
    try:
        query = db.query(Budget)
        
        # Aplicar filtros
        if provider_name:
            query = query.filter(Budget.provider_name == provider_name)
        if service_name:
            query = query.filter(Budget.service_name == service_name)
        if is_active is not None:
            query = query.filter(Budget.is_active == is_active)
        if budget_period:
            query = query.filter(Budget.budget_period == budget_period)
        
        budgets = query.order_by(Budget.created_at.desc()).all()
        
        # Calcular dados agregados
        total_count = len(budgets)
        total_budget_amount = sum(budget.budget_amount for budget in budgets)
        
        # Calcular consumo total usando BudgetAnalyzer
        total_consumption = Decimal('0')
        total_consumption_percentage = Decimal('0')
        
        if budgets:
            analyzer = BudgetAnalyzer(db)
            for budget in budgets:
                try:
                    consumption_data = analyzer.get_budget_consumption(budget.id)
                    if consumption_data and consumption_data.get('current_consumption'):
                        total_consumption += Decimal(str(consumption_data['current_consumption']))
                except Exception as e:
                    logger.warning(f"Error calculating consumption for budget {budget.id}: {e}")
            
            # Calcular percentual geral
            if total_budget_amount > 0:
                total_consumption_percentage = (total_consumption / total_budget_amount) * 100
        
        response = BudgetListResponse(
            budgets=[BudgetResponse.from_orm(budget) for budget in budgets],
            total_count=total_count,
            total_budget_amount=str(total_budget_amount),
            total_consumption=str(total_consumption),
            overall_consumption_percentage=f"{total_consumption_percentage:.2f}"
        )
        
        logger.info(f"User {current_user.username} retrieved {total_count} budgets with aggregated data")
        return response
        
    except Exception as e:
        logger.error(f"Error listing budgets: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao listar budgets"
        )

@budget_router.post("", response_model=BudgetResponse)
async def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cria um novo budget
    """
    try:
        # Verificar se já existe um budget com o mesmo nome
        existing_budget = db.query(Budget).filter(
            Budget.budget_name == budget_data.budget_name
        ).first()
        
        if existing_budget:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Budget com nome '{budget_data.budget_name}' já existe"
            )
        
        # Validar dados
        if budget_data.budget_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O valor do budget deve ser maior que zero"
            )
        
        if budget_data.alert_threshold <= 0 or budget_data.alert_threshold > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O threshold de alerta deve estar entre 0 e 100"
            )
        
        if budget_data.budget_period not in ["monthly", "quarterly", "annual"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Período do budget deve ser 'monthly', 'quarterly' ou 'annual'"
            )
        
        # Criar novo budget
        new_budget = Budget(
            budget_name=budget_data.budget_name,
            provider_name=budget_data.provider_name,
            service_name=budget_data.service_name,
            budget_amount=budget_data.budget_amount,
            budget_period=budget_data.budget_period,
            alert_threshold=budget_data.alert_threshold,
            is_active=budget_data.is_active,
            tags=budget_data.tags or {}
        )
        
        db.add(new_budget)
        db.commit()
        db.refresh(new_budget)
        
        logger.info(f"User {current_user.username} created budget: {new_budget.budget_name}")
        return new_budget
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating budget: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao criar budget"
        )

@budget_router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém um budget específico por ID
    """
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget com ID {budget_id} não encontrado"
            )
        
        logger.info(f"User {current_user.username} retrieved budget: {budget.budget_name}")
        return budget
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving budget {budget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter budget"
        )

@budget_router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int,
    budget_data: BudgetCreate,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza um budget existente
    """
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget com ID {budget_id} não encontrado"
            )
        
        # Verificar se nome duplicado (exceto o próprio budget)
        existing_budget = db.query(Budget).filter(
            and_(
                Budget.budget_name == budget_data.budget_name,
                Budget.id != budget_id
            )
        ).first()
        
        if existing_budget:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Budget com nome '{budget_data.budget_name}' já existe"
            )
        
        # Validar dados
        if budget_data.budget_amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O valor do budget deve ser maior que zero"
            )
        
        if budget_data.alert_threshold <= 0 or budget_data.alert_threshold > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O threshold de alerta deve estar entre 0 e 100"
            )
        
        # Atualizar campos
        budget.budget_name = budget_data.budget_name
        budget.provider_name = budget_data.provider_name
        budget.service_name = budget_data.service_name
        budget.budget_amount = budget_data.budget_amount
        budget.budget_period = budget_data.budget_period
        budget.alert_threshold = budget_data.alert_threshold
        budget.is_active = budget_data.is_active
        budget.tags = budget_data.tags or {}
        
        db.commit()
        db.refresh(budget)
        
        logger.info(f"User {current_user.username} updated budget: {budget.budget_name}")
        return budget
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating budget {budget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao atualizar budget"
        )

@budget_router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Deleta um budget
    """
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget com ID {budget_id} não encontrado"
            )
        
        budget_name = budget.budget_name
        db.delete(budget)
        db.commit()
        
        logger.info(f"User {current_user.username} deleted budget: {budget_name}")
        return {"message": f"Budget '{budget_name}' deletado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting budget {budget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao deletar budget"
        )

@budget_router.get("/{budget_id}/alerts")
async def get_budget_alerts(
    budget_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Verifica alertas detalhados de um budget específico
    """
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget com ID {budget_id} não encontrado"
            )
        
        # Usar BudgetAnalyzer para calcular dados detalhados de alerta
        budget_analyzer = BudgetAnalyzer(db)
        alert_data = budget_analyzer._calculate_budget_alert_data(budget)
        
        logger.info(f"User {current_user.username} checked alerts for budget: {budget.budget_name}")
        
        if alert_data:
            return {
                "has_alerts": True,
                "budget_id": budget_id,
                "budget_name": budget.budget_name,
                "alert_data": alert_data,
                "recommendations": _generate_budget_recommendations(alert_data)
            }
        else:
            # Calcular dados básicos mesmo sem alerta
            consumption_data = budget_analyzer.get_budget_consumption(budget_id)
            return {
                "has_alerts": False,
                "budget_id": budget_id,
                "budget_name": budget.budget_name,
                "message": "Budget dentro dos limites estabelecidos",
                "current_status": consumption_data
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking alerts for budget {budget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao verificar alertas do budget"
        )

def _generate_budget_recommendations(alert_data: Dict[str, Any]) -> List[str]:
    """Gera recomendações baseadas nos dados de alerta"""
    recommendations = []
    
    usage_percentage = alert_data.get('usage_percentage', 0)
    projected_percentage = alert_data.get('projected_percentage', 0)
    remaining_days = alert_data.get('remaining_days', 0)
    alert_level = alert_data.get('alert_level', '')
    
    if usage_percentage >= 100:
        recommendations.append("⚠️ Orçamento excedido! Revise imediatamente os gastos.")
        recommendations.append("🔍 Analise os custos por serviço para identificar gastos inesperados.")
    elif usage_percentage >= 90:
        recommendations.append("🚨 Orçamento quase esgotado. Considere ajustar o limite ou reduzir gastos.")
    elif projected_percentage >= 100:
        recommendations.append(f"📈 Projeção indica que o orçamento será excedido em {remaining_days} dias.")
        recommendations.append("💡 Considere implementar controles de custo preventivos.")
    elif usage_percentage >= 80:
        recommendations.append("⚡ Monitore os gastos de perto nos próximos dias.")
    
    if remaining_days <= 7 and usage_percentage < 50:
        recommendations.append("✅ Ótimo controle de custos! O orçamento está bem gerenciado.")
    
    monthly_burn_rate = float(alert_data.get('monthly_burn_rate', 0))
    budget_amount = float(alert_data.get('budget_amount', 0))
    
    if monthly_burn_rate > 0 and budget_amount > 0:
        months_at_current_rate = budget_amount / monthly_burn_rate
        if months_at_current_rate < 1:
            recommendations.append(f"🔥 Taxa de queima alta: orçamento durará apenas {months_at_current_rate:.1f} meses.")
    
    return recommendations

@budget_router.get("/{budget_id}/usage")
async def get_budget_usage(
    budget_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém informações de uso/gasto atual de um budget
    """
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget com ID {budget_id} não encontrado"
            )
        
        # Calcular período atual baseado no tipo de orçamento
        today = date.today()
        
        if budget.budget_period == 'monthly':
            period_start = today.replace(day=1)
            if period_start.month == 12:
                period_end = period_start.replace(year=period_start.year + 1, month=1) - timedelta(days=1)
            else:
                period_end = period_start.replace(month=period_start.month + 1) - timedelta(days=1)
        elif budget.budget_period == 'quarterly':
            current_quarter = (today.month - 1) // 3 + 1
            period_start = date(today.year, (current_quarter - 1) * 3 + 1, 1)
            if current_quarter == 4:
                period_end = date(today.year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end = date(today.year, current_quarter * 3 + 1, 1) - timedelta(days=1)
        else:  # annual
            period_start = date(today.year, 1, 1)
            period_end = date(today.year, 12, 31)
        
        # Consultar custo atual
        from app.models import FocusCostData
        
        cost_query = db.query(func.sum(FocusCostData.effective_cost)).filter(
            and_(
                FocusCostData.billing_period_start >= period_start,
                FocusCostData.billing_period_end <= period_end
            )
        )
        
        if budget.provider_name:
            cost_query = cost_query.filter(FocusCostData.provider_name == budget.provider_name)
        if budget.service_name:
            cost_query = cost_query.filter(FocusCostData.service_name == budget.service_name)
        
        current_spend = float(cost_query.scalar() or 0)
        budget_amount = float(budget.budget_amount)
        usage_percentage = (current_spend / budget_amount * 100) if budget_amount > 0 else 0
        remaining_budget = budget_amount - current_spend
        
        # Calcular dias restantes no período
        days_in_period = (period_end - period_start).days + 1
        days_elapsed = (today - period_start).days + 1
        days_remaining = (period_end - today).days
        
        # Calcular burn rate (gasto por dia)
        daily_burn_rate = current_spend / days_elapsed if days_elapsed > 0 else 0
        projected_spend = daily_burn_rate * days_in_period
        
        # Determinar status baseado no consumo
        if usage_percentage >= float(budget.alert_threshold):
            if usage_percentage >= 100:
                status = "over_budget"
            else:
                status = "warning"
        else:
            status = "under_budget"
        
        result = {
            "id": budget.id,
            "budget_name": budget.budget_name,
            "provider_name": budget.provider_name,
            "service_name": budget.service_name,
            "budget_amount": str(budget_amount),
            "budget_period": budget.budget_period,
            "alert_threshold": str(budget.alert_threshold),
            "is_active": budget.is_active,
            "created_at": budget.created_at.isoformat() if budget.created_at else None,
            "tags": budget.tags or {},
            "current_consumption": str(current_spend),
            "consumption_percentage": str(round(usage_percentage, 2)),
            "remaining_budget": str(remaining_budget),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "status": status,
            "days_remaining": days_remaining,
            "projected_consumption": str(round(projected_spend, 2)) if projected_spend > 0 else None
        }
        
        logger.info(f"User {current_user.username} retrieved usage for budget: {budget.budget_name}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting budget usage {budget_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao obter uso do budget"
        )

@budget_router.post("/{budget_id}/activate")
async def activate_budget(
    budget_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ativa um budget específico
    """
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget com ID {budget_id} não encontrado"
            )
        
        budget.is_active = True
        db.commit()
        
        logger.info(f"User {current_user.username} activated budget {budget_id}")
        return {"message": f"Budget {budget.budget_name} ativado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating budget {budget_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao ativar budget"
        )

@budget_router.post("/{budget_id}/deactivate")
async def deactivate_budget(
    budget_id: int,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Desativa um budget específico
    """
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Budget com ID {budget_id} não encontrado"
            )
        
        budget.is_active = False
        db.commit()
        
        logger.info(f"User {current_user.username} deactivated budget {budget_id}")
        return {"message": f"Budget {budget.budget_name} desativado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating budget {budget_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao desativar budget"
        )

@budget_router.get("/alerts/all")
async def get_all_budget_alerts(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user),
    alert_level: Optional[str] = None
):
    """
    Verifica alertas de todos os budgets ativos com cálculos detalhados
    """
    try:
        # Usar BudgetAnalyzer para verificar alertas
        budget_analyzer = BudgetAnalyzer(db)
        all_alerts = budget_analyzer.check_budget_alerts()
        
        # Filtrar por nível de alerta se especificado
        if alert_level:
            all_alerts = [alert for alert in all_alerts if alert.get('alert_level') == alert_level]
        
        # Calcular estatísticas resumidas
        critical_alerts = [a for a in all_alerts if a.get('alert_level') == 'critical']
        warning_alerts = [a for a in all_alerts if a.get('alert_level') == 'warning']
        info_alerts = [a for a in all_alerts if a.get('alert_level') == 'info']
        
        total_budget_amount = sum(float(a.get('budget_amount', 0)) for a in all_alerts)
        total_current_spend = sum(float(a.get('current_spend', 0)) for a in all_alerts)
        total_projected_spend = sum(float(a.get('projected_spend', 0)) for a in all_alerts)
        
        providers_with_alerts = list(set([
            a.get('provider_name') for a in all_alerts 
            if a.get('provider_name')
        ]))
        
        services_with_alerts = list(set([
            a.get('service_name') for a in all_alerts 
            if a.get('service_name')
        ]))
        
        # Calcular total em risco (budgets que podem exceder 100%)
        budgets_at_risk = [
            a for a in all_alerts 
            if a.get('projected_percentage', 0) >= 100
        ]
        
        logger.info(f"User {current_user.username} checked all budget alerts - Found {len(all_alerts)} alerts")
        
        return {
            "total_alerts": len(all_alerts),
            "alerts": all_alerts,
            "summary": {
                "critical_alerts": len(critical_alerts),
                "warning_alerts": len(warning_alerts),
                "info_alerts": len(info_alerts),
                "budgets_at_risk": len(budgets_at_risk),
                "total_budget_amount": str(total_budget_amount),
                "total_current_spend": str(total_current_spend),
                "total_projected_spend": str(total_projected_spend),
                "overall_consumption_percentage": round(
                    (total_current_spend / total_budget_amount * 100) if total_budget_amount > 0 else 0, 2
                ),
                "providers_with_alerts": providers_with_alerts,
                "services_with_alerts": services_with_alerts
            },
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error checking all budget alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao verificar alertas de budgets"
        )
