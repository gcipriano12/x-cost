"""
Resource Utilization Collector - X Cost
Coleta dados de utilização de recursos para KPIs
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from app.models import FocusCostData

logger = logging.getLogger(__name__)

class ResourceUtilizationCollector:
    """Coletor de dados de utilização de recursos"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_utilization_metrics(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Coleta métricas de utilização de recursos"""
        try:
            # Por enquanto, simular dados de utilização baseados em custo
            # TODO: Integrar com APIs dos provedores para dados reais de utilização
            
            # Buscar dados de custo por serviço
            cost_data = self.db.query(
                FocusCostData.service_name,
                FocusCostData.resource_id,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.count(FocusCostData.resource_id).label('resource_count')
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= start_date,
                    FocusCostData.billing_period_start <= end_date
                )
            ).group_by(
                FocusCostData.service_name,
                FocusCostData.resource_id
            ).all()
            
            utilization_data = []
            for row in cost_data:
                # Simular utilização baseada no padrão de custo
                # Recursos com custo baixo = possível baixa utilização
                estimated_allocated = float(row.total_cost) * 1.3  # 30% overhead estimado
                estimated_consumed = float(row.total_cost)
                
                utilization_data.append({
                    'service_name': row.service_name,
                    'resource_id': row.resource_id,
                    'allocated_capacity': estimated_allocated,
                    'consumed_capacity': estimated_consumed,
                    'utilization_rate': (estimated_consumed / estimated_allocated) * 100 if estimated_allocated > 0 else 0
                })
                
            return utilization_data
            
        except Exception as e:
            logger.error(f"Error collecting utilization metrics: {str(e)}")
            return []
    
    def identify_idle_resources(
        self, 
        threshold_days: int = 7,
        as_of_date: date = None
    ) -> List[Dict[str, Any]]:
        """Identifica recursos ociosos"""
        try:
            if not as_of_date:
                as_of_date = date.today()
                
            cutoff_date = as_of_date - timedelta(days=threshold_days)
            
            # Buscar recursos com custo muito baixo (possível idle)
            idle_resources = self.db.query(
                FocusCostData.service_name,
                FocusCostData.resource_id,
                FocusCostData.provider_name,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.avg(FocusCostData.effective_cost).label('avg_daily_cost')
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= cutoff_date,
                    FocusCostData.billing_period_start <= as_of_date,
                    FocusCostData.effective_cost < 1.0  # Recursos com custo muito baixo
                )
            ).group_by(
                FocusCostData.service_name,
                FocusCostData.resource_id,
                FocusCostData.provider_name
            ).having(
                func.sum(FocusCostData.effective_cost) > 0
            ).all()
            
            idle_list = []
            for resource in idle_resources:
                # Estimar custo mensal
                monthly_cost = float(resource.avg_daily_cost) * 30
                
                idle_list.append({
                    'service_name': resource.service_name,
                    'resource_id': resource.resource_id,
                    'provider': resource.provider_name,
                    'total_cost': float(resource.total_cost),
                    'monthly_cost': monthly_cost,
                    'idle_reason': 'low_cost_pattern'
                })
                
            return idle_list
            
        except Exception as e:
            logger.error(f"Error identifying idle resources: {str(e)}")
            return []
    
    def get_power_schedule_metrics(self, date: date) -> Dict[str, Any]:
        """Coleta métricas de power scheduling"""
        try:
            # Simular dados de power scheduling
            # TODO: Implementar integração real com sistemas de automação
            
            # Por enquanto, assumir que temos algumas informações nos tags
            scheduled_resources = self.db.query(
                func.count(FocusCostData.resource_id).label('resource_count'),
                func.sum(FocusCostData.effective_cost).label('total_cost')
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    or_(
                        FocusCostData.tags.like('%schedule%'),
                        FocusCostData.tags.like('%auto%'),
                        FocusCostData.tags.like('%dev%'),
                        FocusCostData.tags.like('%test%')
                    )
                )
            ).first()
            
            if scheduled_resources.resource_count:
                # Simular aderência baseada no padrão de uso
                return {
                    'total_scheduled_hours': 16 * scheduled_resources.resource_count,  # 16h úteis
                    'actual_runtime_hours': 14 * scheduled_resources.resource_count,  # 87.5% aderência
                    'scheduled_resources': scheduled_resources.resource_count,
                    'adherence_rate': 87.5
                }
            
            return {
                'total_scheduled_hours': 0,
                'actual_runtime_hours': 0,
                'scheduled_resources': 0,
                'adherence_rate': 100.0
            }
            
        except Exception as e:
            logger.error(f"Error getting power schedule metrics: {str(e)}")
            return {}
    
    def identify_legacy_resources(self, as_of_date: date) -> Dict[str, Any]:
        """Identifica recursos legacy"""
        try:
            # Buscar instâncias por tipo
            instance_data = self.db.query(
                FocusCostData.instance_type,
                func.count(FocusCostData.resource_id).label('instance_count'),
                func.sum(FocusCostData.effective_cost).label('total_cost')
            ).filter(
                and_(
                    FocusCostData.billing_period_start == as_of_date,
                    FocusCostData.instance_type.isnot(None),
                    FocusCostData.instance_type != ''
                )
            ).group_by(
                FocusCostData.instance_type
            ).all()
            
            total_instances = 0
            legacy_instances = 0
            
            # Patterns para identificar tipos legacy
            legacy_patterns = [
                't1', 't2.nano', 't2.micro', 'm1', 'm2', 'm3', 
                'c1', 'c3', 'r3', 'i2', 'd2', 'Standard_A',
                'Standard_D1', 'Basic_A', 'f1-micro', 'g1-small'
            ]
            
            for row in instance_data:
                total_instances += row.instance_count
                
                instance_type = row.instance_type.lower()
                if any(pattern.lower() in instance_type for pattern in legacy_patterns):
                    legacy_instances += row.instance_count
            
            return {
                'total_instances': total_instances,
                'legacy_instances': legacy_instances,
                'legacy_percentage': (legacy_instances / total_instances * 100) if total_instances > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error identifying legacy resources: {str(e)}")
            return {'total_instances': 0, 'legacy_instances': 0}
    
    def get_vcpu_metrics(self, date: date) -> Dict[str, Any]:
        """Coleta métricas de vCPU/GPU"""
        try:
            # Simular cálculo de vCPU baseado em tipos de instância conhecidos
            compute_data = self.db.query(
                FocusCostData.instance_type,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.count(FocusCostData.resource_id).label('instance_count')
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    FocusCostData.service_name.in_(['Amazon Elastic Compute Cloud - Compute', 'Virtual Machines', 'Compute Engine']),
                    FocusCostData.instance_type.isnot(None)
                )
            ).group_by(
                FocusCostData.instance_type
            ).all()
            
            total_vcpu_hours = 0
            total_compute_cost = 0
            
            # Mapear tipos de instância para vCPUs (simplificado)
            vcpu_mapping = {
                't2.micro': 1, 't2.small': 1, 't2.medium': 2, 't2.large': 2,
                't3.micro': 2, 't3.small': 2, 't3.medium': 2, 't3.large': 2,
                'm5.large': 2, 'm5.xlarge': 4, 'm5.2xlarge': 8, 'm5.4xlarge': 16,
                'c5.large': 2, 'c5.xlarge': 4, 'c5.2xlarge': 8, 'c5.4xlarge': 16,
                'Standard_B1s': 1, 'Standard_B2s': 2, 'Standard_D2s_v3': 2,
                'n1-standard-1': 1, 'n1-standard-2': 2, 'n1-standard-4': 4
            }
            
            for row in compute_data:
                total_compute_cost += float(row.total_cost)
                vcpus = vcpu_mapping.get(row.instance_type, 2)  # Default 2 vCPUs
                total_vcpu_hours += vcpus * row.instance_count * 24  # 24 horas por dia
            
            return {
                'total_compute_cost': total_compute_cost,
                'total_vcpu_hours': total_vcpu_hours,
                'cost_per_vcpu_hour': total_compute_cost / total_vcpu_hours if total_vcpu_hours > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting vCPU metrics: {str(e)}")
            return {'total_compute_cost': 0, 'total_vcpu_hours': 1}
