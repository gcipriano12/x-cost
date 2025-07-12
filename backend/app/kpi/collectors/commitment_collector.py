"""
Commitment Collector - X Cost
Coleta dados de commitments (reservas, savings plans) para KPIs
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case

from app.models import FocusCostData

logger = logging.getLogger(__name__)

class CommitmentCollector:
    """Coletor de dados de commitments e savings"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_savings_summary(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """Coleta resumo de economias por commitments"""
        try:
            # Buscar custos com diferentes tipos de pricing
            pricing_data = self.db.query(
                FocusCostData.pricing_term,
                FocusCostData.purchase_option,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.sum(FocusCostData.on_demand_cost).label('on_demand_equivalent'),
                func.count(FocusCostData.resource_id).label('resource_count')
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= start_date,
                    FocusCostData.billing_period_start <= end_date
                )
            ).group_by(
                FocusCostData.pricing_term,
                FocusCostData.purchase_option
            ).all()
            
            total_actual_cost = 0
            total_on_demand_equivalent = 0
            total_savings = 0
            
            commitment_types = {
                'reserved': 0,
                'savings_plan': 0,
                'spot': 0,
                'on_demand': 0
            }
            
            for row in pricing_data:
                actual_cost = float(row.total_cost or 0)
                on_demand_cost = float(row.on_demand_equivalent or actual_cost)
                
                total_actual_cost += actual_cost
                total_on_demand_equivalent += on_demand_cost
                
                # Classificar tipo de commitment
                pricing_term = (row.pricing_term or '').lower()
                purchase_option = (row.purchase_option or '').lower()
                
                if 'reserved' in pricing_term or 'reserved' in purchase_option:
                    commitment_types['reserved'] += actual_cost
                elif 'savings' in pricing_term or 'savings' in purchase_option:
                    commitment_types['savings_plan'] += actual_cost
                elif 'spot' in pricing_term or 'spot' in purchase_option:
                    commitment_types['spot'] += actual_cost
                else:
                    commitment_types['on_demand'] += actual_cost
            
            total_savings = total_on_demand_equivalent - total_actual_cost
            savings_rate = (total_savings / total_on_demand_equivalent * 100) if total_on_demand_equivalent > 0 else 0
            
            return {
                'actual_cost': total_actual_cost,
                'on_demand_equivalent': total_on_demand_equivalent,
                'total_savings': total_savings,
                'savings_rate': savings_rate,
                'commitment_breakdown': commitment_types,
                'period_days': (end_date - start_date).days + 1
            }
            
        except Exception as e:
            logger.error(f"Error getting savings summary: {str(e)}")
            return {'actual_cost': 0, 'on_demand_equivalent': 0, 'total_savings': 0}
    
    def get_commitment_utilization(self, as_of_date: date) -> Dict[str, Any]:
        """Analisa utilização de commitments"""
        try:
            # Buscar commitments ativos (simplificado)
            commitment_data = self.db.query(
                FocusCostData.pricing_term,
                FocusCostData.purchase_option,
                func.sum(FocusCostData.effective_cost).label('actual_cost'),
                func.sum(FocusCostData.commitment_fee).label('commitment_cost'),
                func.count(FocusCostData.resource_id).label('resource_count')
            ).filter(
                and_(
                    FocusCostData.billing_period_start == as_of_date,
                    or_(
                        FocusCostData.pricing_term.ilike('%reserved%'),
                        FocusCostData.pricing_term.ilike('%savings%'),
                        FocusCostData.purchase_option.ilike('%reserved%'),
                        FocusCostData.purchase_option.ilike('%savings%')
                    )
                )
            ).group_by(
                FocusCostData.pricing_term,
                FocusCostData.purchase_option
            ).all()
            
            total_commitment_cost = 0
            total_actual_usage = 0
            unused_commitment_cost = 0
            
            for row in commitment_data:
                commitment_cost = float(row.commitment_cost or row.actual_cost)
                actual_cost = float(row.actual_cost or 0)
                
                total_commitment_cost += commitment_cost
                total_actual_usage += actual_cost
                
                # Se commitment > usage, há desperdício
                if commitment_cost > actual_cost:
                    unused_commitment_cost += (commitment_cost - actual_cost)
            
            utilization_rate = (total_actual_usage / total_commitment_cost * 100) if total_commitment_cost > 0 else 0
            waste_rate = (unused_commitment_cost / total_commitment_cost * 100) if total_commitment_cost > 0 else 0
            
            return {
                'total_commitment_cost': total_commitment_cost,
                'total_actual_usage': total_actual_usage,
                'unused_commitment_cost': unused_commitment_cost,
                'utilization_rate': utilization_rate,
                'waste_rate': waste_rate,
                'recommendations': self._generate_commitment_recommendations(utilization_rate)
            }
            
        except Exception as e:
            logger.error(f"Error getting commitment utilization: {str(e)}")
            return {'total_commitment_cost': 0, 'unused_commitment_cost': 0}
    
    def get_compute_coverage(self, date: date) -> Dict[str, Any]:
        """Analisa cobertura de compute por commitments"""
        try:
            # Compute services principais
            compute_services = [
                'Amazon Elastic Compute Cloud - Compute',
                'Amazon EC2-Instance',
                'Virtual Machines',
                'Compute Engine'
            ]
            
            # Total de custo de compute
            total_compute = self.db.query(
                func.sum(FocusCostData.effective_cost)
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    FocusCostData.service_name.in_(compute_services)
                )
            ).scalar() or 0
            
            # Compute coberto por commitments
            committed_compute = self.db.query(
                func.sum(FocusCostData.effective_cost)
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    FocusCostData.service_name.in_(compute_services),
                    or_(
                        FocusCostData.pricing_term.ilike('%reserved%'),
                        FocusCostData.pricing_term.ilike('%savings%'),
                        FocusCostData.purchase_option.ilike('%reserved%'),
                        FocusCostData.purchase_option.ilike('%savings%')
                    )
                )
            ).scalar() or 0
            
            coverage_rate = (float(committed_compute) / float(total_compute) * 100) if total_compute > 0 else 0
            uncovered_compute = float(total_compute) - float(committed_compute)
            
            # Calcular potential savings
            potential_savings = uncovered_compute * 0.3  # Assumir 30% de economia potencial
            
            return {
                'total_compute_cost': float(total_compute),
                'committed_compute_cost': float(committed_compute),
                'uncovered_compute_cost': uncovered_compute,
                'coverage_rate': coverage_rate,
                'potential_savings': potential_savings,
                'recommendations': self._generate_coverage_recommendations(coverage_rate)
            }
            
        except Exception as e:
            logger.error(f"Error getting compute coverage: {str(e)}")
            return {'total_compute_cost': 0, 'committed_compute_cost': 0}
    
    def get_commitment_portfolio_analysis(self, date: date) -> Dict[str, Any]:
        """Análise do portfólio de commitments"""
        try:
            # Analisar diferentes tipos de commitments
            portfolio_data = self.db.query(
                FocusCostData.pricing_term,
                FocusCostData.purchase_option,
                FocusCostData.provider_name,
                func.sum(FocusCostData.effective_cost).label('cost'),
                func.count(func.distinct(FocusCostData.resource_id)).label('resources'),
                func.avg(FocusCostData.effective_cost).label('avg_cost')
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    or_(
                        FocusCostData.pricing_term.ilike('%reserved%'),
                        FocusCostData.pricing_term.ilike('%savings%')
                    )
                )
            ).group_by(
                FocusCostData.pricing_term,
                FocusCostData.purchase_option,
                FocusCostData.provider_name
            ).all()
            
            portfolio_summary = {}
            total_commitment_value = 0
            
            for row in portfolio_data:
                provider = row.provider_name or 'Unknown'
                commitment_type = self._classify_commitment_type(row.pricing_term, row.purchase_option)
                
                key = f"{provider}_{commitment_type}"
                if key not in portfolio_summary:
                    portfolio_summary[key] = {
                        'provider': provider,
                        'type': commitment_type,
                        'cost': 0,
                        'resources': 0,
                        'avg_resource_cost': 0
                    }
                
                portfolio_summary[key]['cost'] += float(row.cost)
                portfolio_summary[key]['resources'] += row.resources
                portfolio_summary[key]['avg_resource_cost'] = float(row.avg_cost)
                total_commitment_value += float(row.cost)
            
            # Calcular distribuição
            for key in portfolio_summary:
                portfolio_summary[key]['percentage'] = (
                    portfolio_summary[key]['cost'] / total_commitment_value * 100
                ) if total_commitment_value > 0 else 0
            
            return {
                'total_commitment_value': total_commitment_value,
                'portfolio_distribution': list(portfolio_summary.values()),
                'diversification_score': len(portfolio_summary),
                'recommendations': self._generate_portfolio_recommendations(portfolio_summary)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing commitment portfolio: {str(e)}")
            return {'total_commitment_value': 0, 'portfolio_distribution': []}
    
    def _classify_commitment_type(self, pricing_term: str, purchase_option: str) -> str:
        """Classifica tipo de commitment"""
        term_str = (pricing_term or '').lower()
        option_str = (purchase_option or '').lower()
        
        if 'savings' in term_str or 'savings' in option_str:
            return 'Savings Plan'
        elif 'reserved' in term_str or 'reserved' in option_str:
            if 'convertible' in term_str or 'convertible' in option_str:
                return 'Convertible Reserved'
            else:
                return 'Standard Reserved'
        else:
            return 'Other Commitment'
    
    def _generate_commitment_recommendations(self, utilization_rate: float) -> List[str]:
        """Gera recomendações para commitments"""
        recommendations = []
        
        if utilization_rate < 70:
            recommendations.append("Revisar commitments - baixa utilização detectada")
            recommendations.append("Considerar convertible RIs para mais flexibilidade")
        elif utilization_rate > 95:
            recommendations.append("Excelente utilização! Considerar expandir commitments")
            recommendations.append("Avaliar oportunidades para novos savings plans")
        else:
            recommendations.append("Utilização boa - monitorar tendências")
        
        return recommendations
    
    def _generate_coverage_recommendations(self, coverage_rate: float) -> List[str]:
        """Gera recomendações para cobertura"""
        recommendations = []
        
        if coverage_rate < 60:
            recommendations.append("Baixa cobertura de commitments - oportunidade de economia")
            recommendations.append("Analisar padrões de uso para Reserved Instances")
        elif coverage_rate < 80:
            recommendations.append("Cobertura moderada - avaliar expansion de commitments")
        else:
            recommendations.append("Boa cobertura de commitments")
        
        return recommendations
    
    def _generate_portfolio_recommendations(self, portfolio: Dict) -> List[str]:
        """Gera recomendações para portfólio"""
        recommendations = []
        
        if len(portfolio) < 2:
            recommendations.append("Diversificar tipos de commitments")
        
        # Verificar concentração em um provider
        provider_concentration = {}
        for item in portfolio.values():
            provider = item['provider']
            provider_concentration[provider] = provider_concentration.get(provider, 0) + item['percentage']
        
        max_concentration = max(provider_concentration.values()) if provider_concentration else 0
        if max_concentration > 80:
            recommendations.append("Alta concentração em um provider - considerar diversificação")
        
        return recommendations
