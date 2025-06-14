import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from app.models import FocusCostData, CostAnalysis, AnalysisType
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging
from app.database import cached

logger = logging.getLogger(__name__)

class CostAnalyzer:
    """Classe principal para análises de custo"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @cached(ttl=1800, key_prefix="cost_trend")
    def calculate_cost_trend(
        self,
        provider_name: Optional[str] = None,
        service_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "daily"
    ) -> List[Dict[str, Any]]:
        """Calcula tendência de custos"""
        try:
            query = self.db.query(FocusCostData)
            
            # Aplicar filtros
            if provider_name:
                query = query.filter(FocusCostData.provider_name == provider_name)
            if service_name:
                query = query.filter(FocusCostData.service_name == service_name)
            if start_date:
                query = query.filter(FocusCostData.billing_period_start >= start_date)
            if end_date:
                query = query.filter(FocusCostData.billing_period_end <= end_date)
            
            # Agrupar por período
            if period == "daily":
                date_trunc = func.date(FocusCostData.charge_period_start)
            elif period == "weekly":
                date_trunc = func.date_trunc('week', FocusCostData.charge_period_start)
            elif period == "monthly":
                date_trunc = func.date_trunc('month', FocusCostData.charge_period_start)
            else:
                date_trunc = func.date(FocusCostData.charge_period_start)
            
            results = query.with_entities(
                date_trunc.label('period'),
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.count(FocusCostData.id).label('record_count')
            ).group_by(date_trunc).order_by(date_trunc).all()
            
            trend_data = []
            previous_cost = None
            
            for result in results:
                cost = float(result.total_cost or 0)
                trend_percentage = None
                
                if previous_cost is not None and previous_cost > 0:
                    trend_percentage = ((cost - previous_cost) / previous_cost) * 100
                
                trend_data.append({
                    'period': result.period,
                    'total_cost': cost,
                    'record_count': result.record_count,
                    'trend_percentage': trend_percentage,
                    'cost_change': cost - previous_cost if previous_cost else 0
                })
                
                previous_cost = cost
            
            logger.info(f"Calculated trend for {len(trend_data)} periods")
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating cost trend: {str(e)}")
            return []
    
    @cached(ttl=3600, key_prefix="cost_delta")
    def calculate_cost_delta(
        self,
        provider_name: Optional[str] = None,
        service_name: Optional[str] = None,
        current_period_start: date = None,
        current_period_end: date = None,
        comparison_period_start: date = None,
        comparison_period_end: date = None
    ) -> Dict[str, Any]:
        """Calcula delta de custo entre períodos"""
        try:
            # Custo do período atual
            current_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
                and_(
                    FocusCostData.billing_period_start >= current_period_start,
                    FocusCostData.billing_period_end <= current_period_end
                )
            )
            
            # Custo do período de comparação
            comparison_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
                and_(
                    FocusCostData.billing_period_start >= comparison_period_start,
                    FocusCostData.billing_period_end <= comparison_period_end
                )
            )
            
            # Aplicar filtros adicionais
            if provider_name:
                current_query = current_query.filter(FocusCostData.provider_name == provider_name)
                comparison_query = comparison_query.filter(FocusCostData.provider_name == provider_name)
            if service_name:
                current_query = current_query.filter(FocusCostData.service_name == service_name)
                comparison_query = comparison_query.filter(FocusCostData.service_name == service_name)
            
            current_cost = float(current_query.scalar() or 0)
            comparison_cost = float(comparison_query.scalar() or 0)
            
            delta = current_cost - comparison_cost
            percentage_change = (delta / comparison_cost * 100) if comparison_cost > 0 else 0
            
            return {
                'current_period': {
                    'start': current_period_start,
                    'end': current_period_end,
                    'cost': current_cost
                },
                'comparison_period': {
                    'start': comparison_period_start,
                    'end': comparison_period_end,
                    'cost': comparison_cost
                },
                'delta': delta,
                'percentage_change': percentage_change,
                'trend': 'increase' if delta > 0 else 'decrease' if delta < 0 else 'stable'
            }
            
        except Exception as e:
            logger.error(f"Error calculating cost delta: {str(e)}")
            return {}
    
    def analyze_by_tags(
        self,
        provider_name: Optional[str] = None,
        service_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tag_keys: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Analisa custos por tags"""
        try:
            query = self.db.query(FocusCostData)
            
            # Aplicar filtros
            if provider_name:
                query = query.filter(FocusCostData.provider_name == provider_name)
            if service_name:
                query = query.filter(FocusCostData.service_name == service_name)
            if start_date:
                query = query.filter(FocusCostData.billing_period_start >= start_date)
            if end_date:
                query = query.filter(FocusCostData.billing_period_end <= end_date)
            
            results = query.all()
            
            # Análise por tags
            tag_analysis = {}
            total_cost = 0
            
            for record in results:
                cost = float(record.effective_cost or 0)
                total_cost += cost
                
                if record.tags:
                    for key, value in record.tags.items():
                        if not tag_keys or key in tag_keys:
                            tag_key = f"{key}:{value}"
                            if tag_key not in tag_analysis:
                                tag_analysis[tag_key] = {
                                    'tag_key': key,
                                    'tag_value': value,
                                    'total_cost': 0,
                                    'record_count': 0
                                }
                            tag_analysis[tag_key]['total_cost'] += cost
                            tag_analysis[tag_key]['record_count'] += 1
            
            # Calcular percentuais
            for tag_data in tag_analysis.values():
                tag_data['percentage_of_total'] = (
                    tag_data['total_cost'] / total_cost * 100
                ) if total_cost > 0 else 0
            
            # Ordenar por custo
            sorted_analysis = sorted(
                tag_analysis.values(),
                key=lambda x: x['total_cost'],
                reverse=True
            )
            
            logger.info(f"Analyzed {len(sorted_analysis)} tag combinations")
            return sorted_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing by tags: {str(e)}")
            return []
    
    def analyze_by_service(
        self,
        provider_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Analisa custos por serviço"""
        try:
            query = self.db.query(
                FocusCostData.service_name,
                FocusCostData.provider_name,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.avg(FocusCostData.effective_cost).label('avg_cost'),
                func.count(FocusCostData.id).label('record_count')
            )
            
            # Aplicar filtros
            if provider_name:
                query = query.filter(FocusCostData.provider_name == provider_name)
            if start_date:
                query = query.filter(FocusCostData.billing_period_start >= start_date)
            if end_date:
                query = query.filter(FocusCostData.billing_period_end <= end_date)
            
            results = query.group_by(
                FocusCostData.service_name,
                FocusCostData.provider_name
            ).order_by(
                func.sum(FocusCostData.effective_cost).desc()
            ).limit(top_n).all()
            
            service_analysis = []
            total_cost = sum(float(r.total_cost or 0) for r in results)
            
            for result in results:
                cost = float(result.total_cost or 0)
                service_analysis.append({
                    'service_name': result.service_name,
                    'provider_name': result.provider_name,
                    'total_cost': cost,
                    'avg_cost': float(result.avg_cost or 0),
                    'record_count': result.record_count,
                    'percentage_of_total': (cost / total_cost * 100) if total_cost > 0 else 0
                })
            
            logger.info(f"Analyzed top {len(service_analysis)} services")
            return service_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing by service: {str(e)}")
            return []
    
    def forecast_costs(
        self,
        provider_name: Optional[str] = None,
        service_name: Optional[str] = None,
        forecast_days: int = 30,
        historical_days: int = 90
    ) -> Dict[str, Any]:
        """Prevê custos futuros baseado em dados históricos"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=historical_days)
            
            # Obter dados históricos
            query = self.db.query(
                func.date(FocusCostData.charge_period_start).label('date'),
                func.sum(FocusCostData.effective_cost).label('daily_cost')
            )
            
            if provider_name:
                query = query.filter(FocusCostData.provider_name == provider_name)
            if service_name:
                query = query.filter(FocusCostData.service_name == service_name)
            
            query = query.filter(
                and_(
                    FocusCostData.billing_period_start >= start_date,
                    FocusCostData.billing_period_end <= end_date
                )
            ).group_by(
                func.date(FocusCostData.charge_period_start)
            ).order_by(
                func.date(FocusCostData.charge_period_start)
            )
            
            results = query.all()
            
            if len(results) < 7:  # Mínimo de dados necessários
                return {
                    'error': 'Insufficient historical data for forecasting',
                    'required_days': 7,
                    'available_days': len(results)
                }
            
            # Preparar dados para ML
            df = pd.DataFrame([
                {
                    'date': r.date,
                    'daily_cost': float(r.daily_cost or 0),
                    'day_number': (r.date - results[0].date).days
                }
                for r in results
            ])
            
            # Modelo de regressão linear simples
            X = df[['day_number']].values
            y = df['daily_cost'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            # Calcular métricas do modelo
            y_pred = model.predict(X)
            mae = mean_absolute_error(y, y_pred)
            r2 = r2_score(y, y_pred)
            
            # Gerar previsões
            last_day = df['day_number'].max()
            future_days = np.array([[last_day + i + 1] for i in range(forecast_days)])
            forecasts = model.predict(future_days)
            
            # Calcular intervalos de confiança (simplificado)
            std_error = np.std(y - y_pred)
            confidence_interval = 1.96 * std_error  # 95% de confiança
            
            forecast_data = []
            for i, forecast in enumerate(forecasts):
                forecast_date = end_date + timedelta(days=i + 1)
                forecast_data.append({
                    'date': forecast_date,
                    'forecasted_cost': max(0, float(forecast)),  # Evitar custos negativos
                    'confidence_lower': max(0, float(forecast - confidence_interval)),
                    'confidence_upper': float(forecast + confidence_interval)
                })
            
            total_forecasted_cost = sum(f['forecasted_cost'] for f in forecast_data)
            
            return {
                'forecast_period_days': forecast_days,
                'historical_period_days': len(results),
                'total_forecasted_cost': total_forecasted_cost,
                'average_daily_forecast': total_forecasted_cost / forecast_days,
                'model_accuracy': {
                    'r_squared': float(r2),
                    'mean_absolute_error': float(mae),
                    'confidence_level': 0.95
                },
                'daily_forecasts': forecast_data,
                'trend': 'increasing' if model.coef_[0] > 0 else 'decreasing'
            }
            
        except Exception as e:
            logger.error(f"Error forecasting costs: {str(e)}")
            return {'error': str(e)}
    
    def calculate_anomalies(
        self,
        provider_name: Optional[str] = None,
        service_name: Optional[str] = None,
        lookback_days: int = 30,
        threshold_std: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detecta anomalias nos custos"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=lookback_days)
            
            query = self.db.query(
                func.date(FocusCostData.charge_period_start).label('date'),
                func.sum(FocusCostData.effective_cost).label('daily_cost')
            )
            
            if provider_name:
                query = query.filter(FocusCostData.provider_name == provider_name)
            if service_name:
                query = query.filter(FocusCostData.service_name == service_name)
            
            query = query.filter(
                and_(
                    FocusCostData.billing_period_start >= start_date,
                    FocusCostData.billing_period_end <= end_date
                )
            ).group_by(
                func.date(FocusCostData.charge_period_start)
            ).order_by(
                func.date(FocusCostData.charge_period_start)
            )
            
            results = query.all()
            
            if len(results) < 7:
                return []
            
            # Calcular estatísticas
            costs = [float(r.daily_cost or 0) for r in results]
            mean_cost = np.mean(costs)
            std_cost = np.std(costs)
            threshold_upper = mean_cost + (threshold_std * std_cost)
            threshold_lower = max(0, mean_cost - (threshold_std * std_cost))
            
            anomalies = []
            for result in results:
                daily_cost = float(result.daily_cost or 0)
                
                if daily_cost > threshold_upper or daily_cost < threshold_lower:
                    anomaly_type = 'spike' if daily_cost > threshold_upper else 'dip'
                    severity = abs(daily_cost - mean_cost) / std_cost if std_cost > 0 else 0
                    
                    anomalies.append({
                        'date': result.date,
                        'daily_cost': daily_cost,
                        'expected_cost': mean_cost,
                        'deviation': daily_cost - mean_cost,
                        'severity': float(severity),
                        'type': anomaly_type,
                        'threshold_upper': threshold_upper,
                        'threshold_lower': threshold_lower
                    })
            
            logger.info(f"Detected {len(anomalies)} anomalies")
            return anomalies
            
        except Exception as e:
            logger.error(f"Error calculating anomalies: {str(e)}")
            return []
    
    def generate_cost_report(
        self,
        provider_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Gera relatório completo de custos"""
        try:
            if not start_date:
                start_date = date.today() - timedelta(days=30)
            if not end_date:
                end_date = date.today()
            
            # Resumo geral
            total_cost_query = self.db.query(func.sum(FocusCostData.effective_cost))
            
            if provider_name:
                total_cost_query = total_cost_query.filter(FocusCostData.provider_name == provider_name)
            
            total_cost_query = total_cost_query.filter(
                and_(
                    FocusCostData.billing_period_start >= start_date,
                    FocusCostData.billing_period_end <= end_date
                )
            )
            
            total_cost = float(total_cost_query.scalar() or 0)
            
            # Período anterior para comparação
            previous_start = start_date - (end_date - start_date)
            previous_end = start_date
            
            delta_data = self.calculate_cost_delta(
                provider_name=provider_name,
                current_period_start=start_date,
                current_period_end=end_date,
                comparison_period_start=previous_start,
                comparison_period_end=previous_end
            )
            
            # Top serviços
            top_services = self.analyze_by_service(
                provider_name=provider_name,
                start_date=start_date,
                end_date=end_date,
                top_n=10
            )
            
            # Tendência
            trend_data = self.calculate_cost_trend(
                provider_name=provider_name,
                start_date=start_date,
                end_date=end_date,
                period="daily"
            )
            
            # Previsão
            forecast_data = self.forecast_costs(
                provider_name=provider_name,
                forecast_days=30,
                historical_days=60
            )
            
            # Anomalias
            anomalies = self.calculate_anomalies(
                provider_name=provider_name,
                lookback_days=30
            )
            
            return {
                'report_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': (end_date - start_date).days
                },
                'summary': {
                    'total_cost': total_cost,
                    'average_daily_cost': total_cost / max(1, (end_date - start_date).days),
                    'provider_name': provider_name
                },
                'comparison': delta_data,
                'top_services': top_services,
                'trend': trend_data[-7:] if len(trend_data) >= 7 else trend_data,  # Últimos 7 dias
                'forecast': forecast_data,
                'anomalies': anomalies,
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error generating cost report: {str(e)}")
            return {'error': str(e)}

class BudgetAnalyzer:
    """Classe para análise de orçamentos"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_budget_alerts(self) -> List[Dict[str, Any]]:
        """Verifica alertas de orçamento"""
        try:
            from app.models import Budget
            
            active_budgets = self.db.query(Budget).filter(Budget.is_active == True).all()
            alerts = []
            
            for budget in active_budgets:
                # Calcular período atual baseado no tipo de orçamento
                if budget.budget_period == 'monthly':
                    period_start = date.today().replace(day=1)
                    next_month = period_start.replace(month=period_start.month + 1) if period_start.month < 12 else period_start.replace(year=period_start.year + 1, month=1)
                    period_end = next_month - timedelta(days=1)
                elif budget.budget_period == 'quarterly':
                    # Lógica para trimestre
                    current_quarter = (date.today().month - 1) // 3 + 1
                    period_start = date(date.today().year, (current_quarter - 1) * 3 + 1, 1)
                    period_end = date(date.today().year, current_quarter * 3, 1) + timedelta(days=31)
                    period_end = period_end.replace(day=1) - timedelta(days=1)
                else:  # yearly
                    period_start = date(date.today().year, 1, 1)
                    period_end = date(date.today().year, 12, 31)
                
                # Consultar custo atual
                cost_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
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
                
                if usage_percentage >= float(budget.alert_threshold):
                    alerts.append({
                        'budget_id': budget.id,
                        'budget_name': budget.budget_name,
                        'provider_name': budget.provider_name,
                        'service_name': budget.service_name,
                        'budget_amount': budget_amount,
                        'current_spend': current_spend,
                        'usage_percentage': usage_percentage,
                        'threshold': float(budget.alert_threshold),
                        'period_start': period_start,
                        'period_end': period_end,
                        'alert_level': 'critical' if usage_percentage >= 100 else 'warning'
                    })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking budget alerts: {str(e)}")
            return []