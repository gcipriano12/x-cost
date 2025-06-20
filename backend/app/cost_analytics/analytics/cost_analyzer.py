"""
Cost Analyzer Module

Analisador principal de custos usando arquitetura modular
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import cached
from app.models import FocusCostData
from ..core.query_builder import QueryBuilder
from ..core.calculations import StatisticalCalculations, CostCalculations
from ..core.data_processing import get_service_category
from ..utils.date_utils import DatePeriodHelper
from ..utils.cache_utils import AnalyticsCache

logger = logging.getLogger(__name__)


class CostAnalyzer:
    """
    Analisador principal de custos com arquitetura modular
    """
    
    def __init__(self, db: Session, cache_client=None):
        """
        Inicializa o analisador de custos
        
        Args:
            db: Sessão do banco de dados
            cache_client: Cliente de cache (opcional)
        """
        self.db = db
        self.query_builder = QueryBuilder(db)
        self.cache = AnalyticsCache(cache_client)
    
    @cached(ttl=1800, key_prefix="cost_trend")
    def calculate_cost_trend(
        self,
        provider_name: Optional[str] = None,
        service_name: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Calcula tendência de custos usando QueryBuilder
        
        Args:
            provider_name: Nome do provedor
            service_name: Nome do serviço
            start_date: Data inicial
            end_date: Data final
            period: Período de agrupamento (daily, weekly, monthly)
            
        Returns:
            Lista com dados de tendência
        """
        try:
            # Usar QueryBuilder para criar query de série temporal
            query = self.query_builder.get_time_series_data(
                start_date=start_date,
                end_date=end_date,
                period=period,
                providers=[provider_name] if provider_name else None,
                services=[service_name] if service_name else None
            )
            
            results = query.all()
            
            # Processar resultados com cálculos estatísticos
            trend_data = []
            costs = []
            
            for result in results:
                cost = float(result.total_cost or 0)
                costs.append(cost)
                
                trend_data.append({
                    'period': result.period,
                    'total_cost': cost,
                    'record_count': result.record_count
                })
            
            # Adicionar cálculos de tendência
            self._add_trend_calculations(trend_data, costs)
            
            logger.info(f"Calculated trend for {len(trend_data)} periods")
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating cost trend: {str(e)}")
            return []
    
    def _add_trend_calculations(self, trend_data: List[Dict], costs: List[float]):
        """Adiciona cálculos de tendência aos dados"""
        if len(costs) < 2:
            return
        
        # Calcular mudanças percentuais
        for i, item in enumerate(trend_data):
            if i > 0:
                previous_cost = costs[i - 1]
                current_cost = costs[i]
                
                item['trend_percentage'] = StatisticalCalculations.calculate_percentage_change(
                    current_cost, previous_cost
                )
                item['cost_change'] = current_cost - previous_cost
            else:
                item['trend_percentage'] = None
                item['cost_change'] = 0
        
        # Adicionar análise geral da tendência
        trend_direction = StatisticalCalculations.calculate_trend_direction(costs)
        growth_rate = StatisticalCalculations.calculate_growth_rate(costs)
        
        for item in trend_data:
            item['trend_direction'] = trend_direction
            item['growth_rate'] = growth_rate
    
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
        """
        Calcula delta de custo entre períodos
        
        Args:
            provider_name: Nome do provedor
            service_name: Nome do serviço
            current_period_start: Início período atual
            current_period_end: Fim período atual
            comparison_period_start: Início período comparação
            comparison_period_end: Fim período comparação
            
        Returns:
            Dicionário com análise de delta
        """
        try:
            # Filtros comuns
            filters = {}
            if provider_name:
                filters['providers'] = [provider_name]
            if service_name:
                filters['services'] = [service_name]
            
            # Custo do período atual
            current_query = self.query_builder.get_cost_aggregations(
                group_by_fields=[],
                start_date=current_period_start,
                end_date=current_period_end,
                **filters
            )
            
            # Custo do período de comparação
            comparison_query = self.query_builder.get_cost_aggregations(
                group_by_fields=[],
                start_date=comparison_period_start,
                end_date=comparison_period_end,
                **filters
            )
            
            current_result = current_query.first()
            comparison_result = comparison_query.first()
            
            current_cost = float(current_result.total_cost or 0) if current_result else 0
            comparison_cost = float(comparison_result.total_cost or 0) if comparison_result else 0
            
            # Calcular métricas usando StatisticalCalculations
            percentage_change = StatisticalCalculations.calculate_percentage_change(
                current_cost, comparison_cost
            )
            
            absolute_change = current_cost - comparison_cost
            
            # Determinar status do delta
            if percentage_change is None:
                status = "no_comparison_data"
            elif abs(percentage_change) <= 5:
                status = "stable"
            elif percentage_change > 5:
                status = "increase"
            else:
                status = "decrease"
            
            return {
                'current_period': {
                    'start': current_period_start,
                    'end': current_period_end,
                    'cost': current_cost,
                    'label': DatePeriodHelper.get_period_label(current_period_start, current_period_end)
                },
                'comparison_period': {
                    'start': comparison_period_start,
                    'end': comparison_period_end,
                    'cost': comparison_cost,
                    'label': DatePeriodHelper.get_period_label(comparison_period_start, comparison_period_end)
                },
                'delta': {
                    'absolute_change': absolute_change,
                    'percentage_change': percentage_change,
                    'status': status
                },
                'summary': DatePeriodHelper.format_period_comparison(
                    current_period_start, current_period_end,
                    comparison_period_start, comparison_period_end
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating cost delta: {str(e)}")
            return {}
    
    @cached(ttl=1800, key_prefix="cost_by_tags")
    def analyze_costs_by_tags(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        tag_key: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Analisa custos por tags
        
        Args:
            start_date: Data inicial
            end_date: Data final
            tag_key: Chave da tag para análise
            limit: Limite de resultados
            
        Returns:
            Lista com análise por tags
        """
        try:
            if not tag_key:
                return []
            
            # Query base com filtros de data
            query = self.db.query(FocusCostData)
            query = self.query_builder.filter_by_date_range(query, start_date, end_date)
            
            # Agrupar por valor da tag
            results = query.with_entities(
                FocusCostData.tags[tag_key].astext.label('tag_value'),
                func.sum(FocusCostData.billed_cost).label('total_cost'),
                func.count(FocusCostData.id).label('record_count'),
                func.avg(FocusCostData.billed_cost).label('avg_cost')
            ).filter(
                FocusCostData.tags[tag_key].astext.isnot(None)
            ).group_by(
                FocusCostData.tags[tag_key].astext
            ).order_by(
                func.sum(FocusCostData.billed_cost).desc()
            ).limit(limit).all()
            
            # Processar resultados
            tag_analysis = []
            total_cost = sum(float(r.total_cost or 0) for r in results)
            
            for result in results:
                cost = float(result.total_cost or 0)
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                
                tag_analysis.append({
                    'tag_key': tag_key,
                    'tag_value': result.tag_value or 'Untagged',
                    'total_cost': cost,
                    'avg_cost': float(result.avg_cost or 0),
                    'record_count': result.record_count,
                    'percentage_of_total': round(percentage, 2)
                })
            
            logger.info(f"Analyzed costs by tag '{tag_key}' for {len(tag_analysis)} values")
            return tag_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing costs by tags: {str(e)}")
            return []
    
    @cached(ttl=1800, key_prefix="cost_by_service")
    def analyze_costs_by_service(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider_name: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Analisa custos por serviço com categorização
        
        Args:
            start_date: Data inicial
            end_date: Data final
            provider_name: Nome do provedor
            limit: Limite de resultados
            
        Returns:
            Lista com análise por serviço
        """
        try:
            # Usar QueryBuilder para top spenders por serviço
            query = self.query_builder.get_top_spenders(
                dimension='service_name',
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                providers=[provider_name] if provider_name else None
            )
            
            results = query.all()
            
            # Processar resultados com categorização
            service_analysis = []
            total_cost = sum(float(r.total_cost or 0) for r in results)
            
            for result in results:
                cost = float(result.total_cost or 0)
                service_name = result.dimension_value
                
                # Usar módulo de categorização
                category = get_service_category(service_name)
                
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                
                service_analysis.append({
                    'service_name': service_name,
                    'category': category,
                    'total_cost': cost,
                    'avg_cost': float(result.avg_cost or 0),
                    'record_count': result.record_count,
                    'percentage_of_total': round(percentage, 2)
                })
            
            logger.info(f"Analyzed costs by service for {len(service_analysis)} services")
            return service_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing costs by service: {str(e)}")
            return []
    
    @cached(ttl=1800, key_prefix="cost_by_region")
    def analyze_costs_by_region(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider_name: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Analisa custos por região
        
        Args:
            start_date: Data inicial
            end_date: Data final
            provider_name: Nome do provedor
            limit: Limite de resultados
            
        Returns:
            Lista com análise por região
        """
        try:
            # Usar QueryBuilder para top spenders por região
            query = self.query_builder.get_top_spenders(
                dimension='region',
                limit=limit,
                start_date=start_date,
                end_date=end_date,
                providers=[provider_name] if provider_name else None
            )
            
            results = query.all()
            
            # Processar resultados
            region_analysis = []
            total_cost = sum(float(r.total_cost or 0) for r in results)
            
            for result in results:
                cost = float(result.total_cost or 0)
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                
                region_analysis.append({
                    'region': result.dimension_value or 'Unknown',
                    'total_cost': cost,
                    'avg_cost': float(result.avg_cost or 0),
                    'record_count': result.record_count,
                    'percentage_of_total': round(percentage, 2)
                })
            
            logger.info(f"Analyzed costs by region for {len(region_analysis)} regions")
            return region_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing costs by region: {str(e)}")
            return []
    
    @cached(ttl=1800, key_prefix="cost_by_provider")
    def analyze_costs_by_provider(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Analisa custos por provedor de cloud
        
        Args:
            start_date: Data inicial
            end_date: Data final
            limit: Limite de resultados
            
        Returns:
            Dicionário com análise por provedor
        """
        try:
            # Usar QueryBuilder para top spenders por provedor
            query = self.query_builder.get_top_spenders(
                dimension='provider_name',
                limit=limit,
                start_date=start_date,
                end_date=end_date
            )
            
            results = query.all()
            
            # Processar resultados
            provider_analysis = []
            total_cost = sum(float(r.total_cost or 0) for r in results)
            
            for result in results:
                cost = float(result.total_cost or 0)
                percentage = (cost / total_cost * 100) if total_cost > 0 else 0
                
                provider_analysis.append({
                    'provider_name': result.dimension_value or 'Unknown',
                    'total_cost': cost,
                    'avg_cost': float(result.avg_cost or 0),
                    'record_count': result.record_count,
                    'percentage_of_total': round(percentage, 2),
                    'region_count': 0  # Will be filled later in the endpoint
                })
            
            logger.info(f"Analyzed costs by provider for {len(provider_analysis)} providers")
            return {
                'providers': provider_analysis,
                'total_cost': total_cost,
                'analysis_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing costs by provider: {str(e)}")
            return {'error': str(e)}
    
    @cached(ttl=3600, key_prefix="cost_forecast")
    def forecast_costs(
        self,
        historical_days: int = 30,
        forecast_days: int = 30,
        provider_name: Optional[str] = None,
        service_name: Optional[str] = None,
        method: str = "linear"
    ) -> Dict[str, Any]:
        """
        Gera previsão de custos
        
        Args:
            historical_days: Dias históricos para análise
            forecast_days: Dias para prever
            provider_name: Nome do provedor
            service_name: Nome do serviço
            method: Método de previsão (linear, exponential)
            
        Returns:
            Dicionário com previsão
        """
        try:
            # Calcular período histórico
            end_date = date.today()
            start_date = end_date - datetime.timedelta(days=historical_days)
            
            # Obter dados históricos
            trend_data = self.calculate_cost_trend(
                provider_name=provider_name,
                service_name=service_name,
                start_date=start_date,
                end_date=end_date,
                period="daily"
            )
            
            if not trend_data:
                return {'error': 'No historical data available'}
            
            # Extrair custos históricos
            historical_costs = [item['total_cost'] for item in trend_data]
            
            # Usar CostCalculations para previsão
            forecast_periods = forecast_days
            forecast_result = CostCalculations.calculate_cost_forecast(
                historical_costs=historical_costs,
                periods_ahead=forecast_periods,
                method=method
            )
            
            # Calcular datas futuras
            forecast_dates = []
            current_date = end_date
            for i in range(forecast_periods):
                current_date += datetime.timedelta(days=1)
                forecast_dates.append(current_date)
            
            # Combinar previsões com datas
            forecast_data = []
            for i, (date_val, cost) in enumerate(zip(forecast_dates, forecast_result['forecast'])):
                forecast_data.append({
                    'date': date_val,
                    'predicted_cost': cost,
                    'period_ahead': i + 1
                })
            
            return {
                'historical_period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'days': historical_days
                },
                'forecast_period': {
                    'start_date': forecast_dates[0] if forecast_dates else None,
                    'end_date': forecast_dates[-1] if forecast_dates else None,
                    'days': forecast_days
                },
                'forecast_data': forecast_data,
                'confidence': forecast_result['confidence'],
                'method': forecast_result['method'],
                'metadata': {
                    'total_predicted_cost': sum(forecast_result['forecast']),
                    'avg_daily_cost': sum(forecast_result['forecast']) / len(forecast_result['forecast']) if forecast_result['forecast'] else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error forecasting costs: {str(e)}")
            return {'error': str(e)}
    
    def get_cost_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        provider_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Gera resumo de custos
        
        Args:
            start_date: Data inicial
            end_date: Data final
            provider_name: Nome do provedor
            
        Returns:
            Resumo de custos
        """
        try:
            filters = {}
            if provider_name:
                filters['providers'] = [provider_name]
            
            # Usar QueryBuilder para agregações
            query = self.query_builder.get_cost_aggregations(
                group_by_fields=[],
                start_date=start_date,
                end_date=end_date,
                **filters
            )
            
            result = query.first()
            
            if not result:
                return {'error': 'No data found'}
            
            total_cost = float(result.total_cost or 0)
            avg_cost = float(result.avg_cost or 0)
            record_count = result.record_count
            
            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'label': DatePeriodHelper.get_period_label(start_date, end_date) if start_date and end_date else "All Time"
                },
                'totals': {
                    'total_cost': total_cost,
                    'average_cost': avg_cost,
                    'record_count': record_count
                },
                'provider': provider_name or 'All Providers',
                'generated_at': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Error getting cost summary: {str(e)}")
            return {'error': str(e)}