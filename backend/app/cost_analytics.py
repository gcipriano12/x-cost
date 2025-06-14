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
                query = query.filter(FocusCostData.charge_period_start >= start_date)
            if end_date:
                query = query.filter(FocusCostData.charge_period_start <= end_date)
            
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
                    FocusCostData.charge_period_start >= current_period_start,
                    FocusCostData.charge_period_start <= current_period_end
                )
            )
            
            # Custo do período de comparação
            comparison_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
                and_(
                    FocusCostData.charge_period_start >= comparison_period_start,
                    FocusCostData.charge_period_start <= comparison_period_end
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
                query = query.filter(FocusCostData.charge_period_start >= start_date)
            if end_date:
                query = query.filter(FocusCostData.charge_period_start <= end_date)
            
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
                query = query.filter(FocusCostData.charge_period_start >= start_date)
            if end_date:
                query = query.filter(FocusCostData.charge_period_start <= end_date)
            
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
    
    def analyze_by_region(
        self,
        provider_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Analisa custos por região"""
        try:
            query = self.db.query(
                FocusCostData.region,
                FocusCostData.provider_name,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.avg(FocusCostData.effective_cost).label('avg_cost'),
                func.count(FocusCostData.id).label('record_count')
            )
            
            # Aplicar filtros
            if provider_name:
                query = query.filter(FocusCostData.provider_name == provider_name)
            if start_date:
                query = query.filter(FocusCostData.charge_period_start >= start_date)
            if end_date:
                query = query.filter(FocusCostData.charge_period_start <= end_date)
            
            # Filtrar regiões não nulas
            query = query.filter(FocusCostData.region.isnot(None))
            
            results = query.group_by(
                FocusCostData.region,
                FocusCostData.provider_name
            ).order_by(
                func.sum(FocusCostData.effective_cost).desc()
            ).limit(top_n).all()
            
            region_analysis = []
            total_cost = sum(float(r.total_cost or 0) for r in results)
            
            for result in results:
                cost = float(result.total_cost or 0)
                region_analysis.append({
                    'region': result.region,
                    'provider_name': result.provider_name,
                    'total_cost': cost,
                    'avg_cost': float(result.avg_cost or 0),
                    'record_count': result.record_count,
                    'percentage_of_total': (cost / total_cost * 100) if total_cost > 0 else 0
                })
            
            logger.info(f"Analyzed top {len(region_analysis)} regions")
            return region_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing by region: {str(e)}")
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
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date
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
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date
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
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date
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
        """Verifica alertas de orçamento com cálculos detalhados"""
        try:
            from app.models import Budget
            
            active_budgets = self.db.query(Budget).filter(Budget.is_active == True).all()
            alerts = []
            
            for budget in active_budgets:
                alert_data = self._calculate_budget_alert_data(budget)
                
                # Só adicionar se excedeu o threshold ou está próximo (acima de 80% do threshold)
                if alert_data and (
                    alert_data['usage_percentage'] >= alert_data['threshold'] or
                    alert_data['usage_percentage'] >= (alert_data['threshold'] * 0.8)
                ):
                    alerts.append(alert_data)
            
            # Ordenar por severidade (maior percentual primeiro)
            alerts.sort(key=lambda x: x['usage_percentage'], reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error checking budget alerts: {str(e)}")
            return []
    
    def _calculate_budget_alert_data(self, budget) -> Optional[Dict[str, Any]]:
        """Calcula dados detalhados de alerta para um budget específico"""
        try:
            # Calcular período atual baseado no tipo de orçamento
            today = date.today()
            
            if budget.budget_period == 'monthly':
                period_start = today.replace(day=1)
                if today.month == 12:
                    next_month = date(today.year + 1, 1, 1)
                else:
                    next_month = date(today.year, today.month + 1, 1)
                period_end = next_month - timedelta(days=1)
            elif budget.budget_period == 'quarterly':
                # Lógica para trimestre
                current_quarter = (today.month - 1) // 3 + 1
                period_start = date(today.year, (current_quarter - 1) * 3 + 1, 1)
                if current_quarter == 4:
                    period_end = date(today.year, 12, 31)
                else:
                    next_quarter_start = date(today.year, current_quarter * 3 + 1, 1)
                    period_end = next_quarter_start - timedelta(days=1)
            else:  # yearly
                period_start = date(today.year, 1, 1)
                period_end = date(today.year, 12, 31)
            
            # Consultar custo atual
            cost_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
                and_(
                    FocusCostData.charge_period_start >= period_start,
                    FocusCostData.charge_period_start <= period_end
                )
            )
            
            if budget.provider_name:
                cost_query = cost_query.filter(FocusCostData.provider_name == budget.provider_name)
            if budget.service_name:
                cost_query = cost_query.filter(FocusCostData.service_name == budget.service_name)
            
            current_spend = float(cost_query.scalar() or 0)
            budget_amount = float(budget.budget_amount)
            threshold = float(budget.alert_threshold)
            
            # Cálculos de percentuais
            usage_percentage = (current_spend / budget_amount * 100) if budget_amount > 0 else 0
            threshold_amount = budget_amount * (threshold / 100)
            amount_over_threshold = max(0, current_spend - threshold_amount)
            remaining_budget = budget_amount - current_spend
            
            # Cálculos de tempo
            total_days = (period_end - period_start).days + 1
            elapsed_days = (today - period_start).days + 1
            remaining_days = max(0, (period_end - today).days)
            
            # Projeção baseada na taxa atual
            if elapsed_days > 0:
                daily_rate = current_spend / elapsed_days
                projected_spend = daily_rate * total_days
                projected_percentage = (projected_spend / budget_amount * 100) if budget_amount > 0 else 0
            else:
                projected_spend = current_spend
                projected_percentage = usage_percentage
            
            # Determinar nível de alerta
            if usage_percentage >= 100:
                alert_level = 'critical'
                alert_message = f"Orçamento excedido em {usage_percentage - 100:.1f}%"
            elif usage_percentage >= threshold:
                alert_level = 'warning'
                alert_message = f"Orçamento {usage_percentage:.1f}% consumido (limite: {threshold}%)"
            elif usage_percentage >= (threshold * 0.8):
                alert_level = 'info'
                alert_message = f"Aproximando do limite: {usage_percentage:.1f}% consumido"
            else:
                return None
            
            # Calcular velocidade de queima (burn rate)
            burn_rate_monthly = (current_spend / elapsed_days) * 30 if elapsed_days > 0 else 0
            
            return {
                'budget_id': budget.id,
                'budget_name': budget.budget_name,
                'provider_name': budget.provider_name,
                'service_name': budget.service_name,
                'budget_amount': str(budget_amount),
                'current_spend': str(current_spend),
                'usage_percentage': round(usage_percentage, 2),
                'threshold': threshold,
                'threshold_amount': str(threshold_amount),
                'amount_over_threshold': str(amount_over_threshold),
                'remaining_budget': str(remaining_budget),
                'projected_spend': str(projected_spend),
                'projected_percentage': round(projected_percentage, 2),
                'period_start': period_start.isoformat(),
                'period_end': period_end.isoformat(),
                'total_days': total_days,
                'elapsed_days': elapsed_days,
                'remaining_days': remaining_days,
                'daily_burn_rate': str(round(daily_rate, 2)) if elapsed_days > 0 else "0",
                'monthly_burn_rate': str(round(burn_rate_monthly, 2)),
                'alert_level': alert_level,
                'alert_message': alert_message,
                'created_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating alert data for budget {budget.id}: {str(e)}")
            return None
    
    def get_budget_consumption(self, budget_id: int, period_days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Calcula o consumo de um budget específico baseado no período
        """
        try:
            from app.models import Budget
            
            # Buscar o budget específico
            budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
            if not budget:
                logger.warning(f"Budget {budget_id} not found")
                return None
            
            # Definir período de análise baseado no tipo de budget
            end_date = date.today()
            
            if budget.budget_period == 'monthly':
                # Para orçamento mensal, usar o mês atual
                start_date = end_date.replace(day=1)
            elif budget.budget_period == 'quarterly':
                # Para orçamento trimestral, usar o trimestre atual
                current_quarter = (end_date.month - 1) // 3 + 1
                start_date = date(end_date.year, (current_quarter - 1) * 3 + 1, 1)
            elif budget.budget_period == 'annual':
                # Para orçamento anual, usar o ano atual
                start_date = date(end_date.year, 1, 1)
            else:
                # Fallback para período personalizado
                start_date = end_date - timedelta(days=period_days)
            
            # Consultar custo atual do período
            cost_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
                and_(
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date
                )
            )
            
            # Aplicar filtros do budget
            if budget.provider_name:
                cost_query = cost_query.filter(FocusCostData.provider_name == budget.provider_name)
            if budget.service_name:
                cost_query = cost_query.filter(FocusCostData.service_name == budget.service_name)
            
            current_consumption = float(cost_query.scalar() or 0)
            budget_amount = float(budget.budget_amount)
            
            # Calcular percentual de consumo
            consumption_percentage = (current_consumption / budget_amount * 100) if budget_amount > 0 else 0
            
            # Projeção para o final do período (se aplicável)
            days_in_period = (end_date - start_date).days + 1
            days_elapsed = (date.today() - start_date).days + 1
            
            projected_consumption = 0
            if days_elapsed > 0 and days_in_period > days_elapsed:
                daily_rate = current_consumption / days_elapsed
                projected_consumption = daily_rate * days_in_period
            else:
                projected_consumption = current_consumption
            
            logger.info(f"Budget {budget_id} consumption - Current: {current_consumption:.2f}, Budget: {budget_amount:.2f}, Percentage: {consumption_percentage:.1f}%")
            
            return {
                'budget_id': budget_id,
                'budget_name': budget.budget_name,
                'budget_amount': str(budget_amount),
                'current_consumption': str(current_consumption),
                'projected_consumption': str(projected_consumption),
                'consumption_percentage': f"{consumption_percentage:.2f}",
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'remaining_budget': str(budget_amount - current_consumption)
            }
            
        except Exception as e:
            logger.error(f"Error calculating consumption for budget {budget_id}: {str(e)}")
            return None

class DashboardAnalyzer:
    """Classe especializada para análises do dashboard"""
    
    def __init__(self, db: Session):
        self.db = db
        self.cost_analyzer = CostAnalyzer(db)
        self.budget_analyzer = BudgetAnalyzer(db)
    
    @cached(ttl=900, key_prefix="dashboard_summary")  # Cache por 15 minutos
    def get_dashboard_summary(self, period_days: int = 30) -> Dict[str, Any]:
        """Gera resumo completo para o dashboard"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=period_days)
            
            # Período anterior para comparação
            previous_start = start_date - timedelta(days=period_days)
            previous_end = start_date
            
            # 1. Métricas principais
            metrics = self._calculate_main_metrics(start_date, end_date, previous_start, previous_end, period_days)
            
            # 2. Distribuição por provedor
            provider_distribution = self._calculate_provider_distribution(start_date, end_date)
            
            # 3. Highlights especiais
            highlights = self._calculate_highlights(start_date, end_date)
            
            return {
                'metrics': metrics,
                'provider_distribution': provider_distribution,
                'highlights': highlights,
                'generated_at': datetime.utcnow(),
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': period_days
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_main_metrics(self, start_date: date, end_date: date, 
                               previous_start: date, previous_end: date, period_days: int) -> Dict[str, Any]:
        """Calcula métricas principais do dashboard"""
        
        # Custo total do período atual
        current_cost_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date
            )
        )
        total_cost = float(current_cost_query.scalar() or 0)
        
        # Custo do período anterior
        previous_cost_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
            and_(
                FocusCostData.charge_period_start >= previous_start,
                FocusCostData.charge_period_start <= previous_end
            )
        )
        previous_cost = float(previous_cost_query.scalar() or 0)
        
        # Variação percentual
        cost_change_percentage = 0
        if previous_cost > 0:
            cost_change_percentage = ((total_cost - previous_cost) / previous_cost) * 100
        
        # Média mensal (aproximada)
        days_in_period = (end_date - start_date).days
        monthly_average = (total_cost / days_in_period) * 30 if days_in_period > 0 else 0
        
        # Maior gasto por serviço
        top_service = self._get_top_service(start_date, end_date)
        
        # Projeção anual
        annual_projection = monthly_average * 12
        
        # Consumo de orçamento
        budget_consumption = self._get_budget_consumption(period_days)
        
        return {
            'total_cost': total_cost,
            'cost_change_percentage': cost_change_percentage,
            'monthly_average': monthly_average,
            'top_service': top_service,
            'annual_projection': annual_projection,
            'budget_consumption': budget_consumption
        }
    
    def _get_top_service(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Encontra o serviço com maior gasto"""
        query = self.db.query(
            FocusCostData.service_name,
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date
            )
        ).group_by(
            FocusCostData.service_name,
            FocusCostData.provider_name
        ).order_by(
            func.sum(FocusCostData.effective_cost).desc()
        ).first()
        
        if query:
            return {
                'service_name': query.service_name,
                'provider_name': query.provider_name,
                'total_cost': float(query.total_cost or 0)
            }
        
        return {'service_name': 'N/A', 'provider_name': 'N/A', 'total_cost': 0}
    
    def _get_budget_consumption(self, period_days: int = 30) -> Optional[Dict[str, Any]]:
        """Calcula o consumo total de orçamento baseado no período selecionado"""
        try:
            from app.models import Budget
            
            # Definir período de análise
            end_date = date.today()
            start_date = end_date - timedelta(days=period_days)
            
            # Buscar orçamentos ativos
            active_budgets = self.db.query(Budget).filter(
                Budget.is_active == True
            ).all()
            
            if not active_budgets:
                logger.info("No active budgets found")
                return None
            
            # Calcular orçamento total (proporcional ao período se necessário)
            total_budget = 0
            for budget in active_budgets:
                budget_amount = float(budget.budget_amount)
                
                # Ajustar orçamento baseado no período
                if budget.budget_period == 'monthly':
                    # Orçamento mensal - calcular proporcional aos dias
                    days_in_month = 30  # Simplificado
                    proportion = min(period_days / days_in_month, 1.0)
                    total_budget += budget_amount * proportion
                elif budget.budget_period == 'annual':
                    # Orçamento anual - calcular proporcional aos dias
                    proportion = period_days / 365
                    total_budget += budget_amount * proportion
                else:
                    # Para outros períodos, usar valor integral
                    total_budget += budget_amount
            
            # Calcular gasto real no período especificado
            current_spend_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
                and_(
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date
                )
            )
            current_spend = float(current_spend_query.scalar() or 0)
            
            consumption_percentage = (current_spend / total_budget * 100) if total_budget > 0 else 0
            remaining_budget = total_budget - current_spend
            
            logger.info(f"Budget calculation - Period: {period_days} days, Total Budget: {total_budget:.2f}, Spent: {current_spend:.2f}, Consumption: {consumption_percentage:.1f}%")
            
            return {
                'total_budget': round(total_budget, 2),
                'current_spend': round(current_spend, 2),
                'consumption_percentage': round(consumption_percentage, 1),
                'remaining_budget': round(remaining_budget, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating budget consumption: {str(e)}")
            return None
    
    def _calculate_provider_distribution(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Calcula distribuição de custos por provedor"""
        query = self.db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date
            )
        ).group_by(
            FocusCostData.provider_name
        ).order_by(
            func.sum(FocusCostData.effective_cost).desc()
        ).all()
        
        total_cost = sum(float(r.total_cost or 0) for r in query)
        
        distribution = []
        for result in query:
            cost = float(result.total_cost or 0)
            percentage = (cost / total_cost * 100) if total_cost > 0 else 0
            
            distribution.append({
                'provider_name': result.provider_name,
                'total_cost': cost,
                'percentage': percentage
            })
        
        return distribution
    
    def _calculate_highlights(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calcula highlights especiais do dashboard"""
        
        # 1. Previsão próximo mês
        forecast_data = self.cost_analyzer.forecast_costs(forecast_days=30, historical_days=60)
        next_month_forecast = {
            'amount': forecast_data.get('total_forecasted_cost', 0),
            'change_percentage': 0  # Será calculado baseado na tendência
        }
        
        # 2. Desperdício estimado (recursos com baixa utilização)
        estimated_waste = self._calculate_estimated_waste(start_date, end_date)
        
        # 3. Economias realizadas (comparação com período anterior)
        savings_achieved = self._calculate_savings_achieved(start_date, end_date)
        
        return {
            'next_month_forecast': next_month_forecast,
            'estimated_waste': estimated_waste,
            'savings_achieved': savings_achieved
        }
    
    def _calculate_estimated_waste(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calcula desperdício estimado baseado em anomalias e padrões"""
        
        # Detectar anomalias como indicador de desperdício
        anomalies = self.cost_analyzer.calculate_anomalies(lookback_days=30)
        
        # Calcular desperdício baseado em anomalias de alta (spikes não explicados)
        waste_amount = 0
        for anomaly in anomalies:
            if anomaly.get('type') == 'spike' and anomaly.get('severity', 0) > 2:
                # Considerar parte do spike como desperdício
                deviation = anomaly.get('deviation', 0)
                if deviation > 0:
                    waste_amount += deviation * 0.7  # 70% do spike como desperdício estimado
        
        # Calcular custo total para percentual
        total_cost_query = self.db.query(func.sum(FocusCostData.effective_cost)).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date
            )
        )
        total_cost = float(total_cost_query.scalar() or 0)
        
        waste_percentage = (waste_amount / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'amount': waste_amount,
            'percentage': waste_percentage,
            'total_cost': total_cost
        }
    
    def _calculate_savings_achieved(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Calcula economias realizadas comparando com período anterior"""
        
        # Período anterior
        period_length = (end_date - start_date).days
        previous_start = start_date - timedelta(days=period_length)
        previous_end = start_date
        
        # Usar delta já existente
        delta_data = self.cost_analyzer.calculate_cost_delta(
            current_period_start=start_date,
            current_period_end=end_date,
            comparison_period_start=previous_start,
            comparison_period_end=previous_end
        )
        
        savings_amount = 0
        savings_percentage = 0
        
        if delta_data:
            delta = delta_data.get('delta', 0)
            if delta < 0:  # Custo diminuiu = economia
                savings_amount = abs(delta)
                current_cost = delta_data.get('current_period', {}).get('cost', 0)
                savings_percentage = (savings_amount / current_cost * 100) if current_cost > 0 else 0
        
        return {
            'amount': savings_amount,
            'percentage': savings_percentage
        }