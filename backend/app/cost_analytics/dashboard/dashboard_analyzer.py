"""
Dashboard Analyzer Module

Analisador de dashboards com arquitetura modular
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.database import cached
from ..analytics.cost_analyzer import CostAnalyzer
from ..budget.budget_analyzer import BudgetAnalyzer
from ..utils.date_utils import DatePeriodHelper

logger = logging.getLogger(__name__)


class DashboardAnalyzer:
    """
    Analisador de dashboards que coordena outros analisadores
    
    TODO: Implementar análise completa de dashboard
    Esta é uma implementação placeholder que será expandida
    """
    
    def __init__(self, db: Session, cache_client=None):
        """
        Inicializa o analisador de dashboard
        
        Args:
            db: Sessão do banco de dados
            cache_client: Cliente de cache (opcional)
        """
        self.db = db
        self.cost_analyzer = CostAnalyzer(db, cache_client)
        self.budget_analyzer = BudgetAnalyzer(db, cache_client)
    
    @cached(ttl=600, key_prefix="dashboard_summary")
    def get_dashboard_summary(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        providers: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Gera resumo completo para dashboard
        
        Args:
            start_date: Data inicial
            end_date: Data final
            providers: Lista de provedores
            
        Returns:
            Resumo completo do dashboard
        """
        try:
            # Usar período padrão se não especificado
            if not start_date or not end_date:
                end_date = date.today()
                start_date = end_date.replace(day=1)  # Primeiro dia do mês
            
            summary = {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date,
                    'label': DatePeriodHelper.get_period_label(start_date, end_date)
                },
                'generated_at': datetime.utcnow()
            }
            
            # Resumo de custos por provedor
            if providers:
                cost_summaries = []
                for provider in providers:
                    provider_summary = self.cost_analyzer.get_cost_summary(
                        start_date=start_date,
                        end_date=end_date,
                        provider_name=provider
                    )
                    if 'error' not in provider_summary:
                        cost_summaries.append(provider_summary)
                
                summary['cost_by_provider'] = cost_summaries
            else:
                # Resumo geral
                summary['cost_summary'] = self.cost_analyzer.get_cost_summary(
                    start_date=start_date,
                    end_date=end_date
                )
            
            # Análise por serviços (top 10)
            summary['top_services'] = self.cost_analyzer.analyze_costs_by_service(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )
            
            # Análise por regiões (top 10)
            summary['top_regions'] = self.cost_analyzer.analyze_costs_by_region(
                start_date=start_date,
                end_date=end_date,
                limit=10
            )
            
            # Resumo de orçamentos
            summary['budget_summary'] = self.budget_analyzer.get_budget_summary()
            
            # Tendência do período
            summary['cost_trend'] = self.cost_analyzer.calculate_cost_trend(
                start_date=start_date,
                end_date=end_date,
                period="daily"
            )
            
            logger.info(f"Generated dashboard summary for period {start_date} to {end_date}")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}")
            return {'error': str(e)}
    
    def get_cost_distribution(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Gera distribuição de custos por múltiplas dimensões
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Distribuição de custos
        """
        try:
            return {
                'by_service': self.cost_analyzer.analyze_costs_by_service(
                    start_date=start_date,
                    end_date=end_date,
                    limit=20
                ),
                'by_region': self.cost_analyzer.analyze_costs_by_region(
                    start_date=start_date,
                    end_date=end_date,
                    limit=20
                ),
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting cost distribution: {str(e)}")
            return {'error': str(e)}
    
    def get_monthly_comparison(self, months_back: int = 6) -> Dict[str, Any]:
        """
        Gera comparação de custos dos últimos meses
        
        Args:
            months_back: Número de meses para comparar
            
        Returns:
            Comparação mensal
        """
        try:
            current_date = date.today()
            monthly_data = []
            
            for i in range(months_back):
                # Calcular mês
                if current_date.month - i <= 0:
                    month = 12 + (current_date.month - i)
                    year = current_date.year - 1
                else:
                    month = current_date.month - i
                    year = current_date.year
                
                month_start, month_end = DatePeriodHelper.get_month_boundaries(
                    date(year, month, 1)
                )
                
                # Obter dados do mês
                month_summary = self.cost_analyzer.get_cost_summary(
                    start_date=month_start,
                    end_date=month_end
                )
                
                if 'error' not in month_summary:
                    monthly_data.append({
                        'year': year,
                        'month': month,
                        'month_name': DatePeriodHelper.get_month_name(month),
                        'period_label': month_summary['period']['label'],
                        'total_cost': month_summary['totals']['total_cost'],
                        'record_count': month_summary['totals']['record_count']
                    })
            
            return {
                'monthly_comparison': list(reversed(monthly_data)),  # Ordem cronológica
                'months_analyzed': len(monthly_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting monthly comparison: {str(e)}")
            return {'error': str(e)}