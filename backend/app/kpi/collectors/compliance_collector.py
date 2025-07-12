"""
Compliance Collector - X Cost
Coleta dados de compliance e governança para KPIs
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text

from app.models import FocusCostData
from app.virtual_tags_models import VirtualTagAllocation

logger = logging.getLogger(__name__)

class ComplianceCollector:
    """Coletor de dados de compliance e governança"""
    
    def __init__(self, db: Session):
        self.db = db
        
    def get_tag_compliance_metrics(self, date: date) -> Dict[str, Any]:
        """Coleta métricas de compliance de tags"""
        try:
            # Tags obrigatórias que consideramos essenciais
            required_tags = ['Environment', 'Project', 'Owner', 'CostCenter', 'Application']
            
            # Buscar total de recursos
            total_resources = self.db.query(
                func.count(func.distinct(FocusCostData.resource_id))
            ).filter(
                FocusCostData.billing_period_start == date
            ).scalar() or 0
            
            if total_resources == 0:
                return {'total_resources': 0, 'compliant_resources': 0}
            
            # Analisar compliance de tags
            compliant_count = 0
            
            # Buscar recursos com tags
            resources_with_tags = self.db.query(
                FocusCostData.resource_id,
                FocusCostData.tags
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    FocusCostData.tags.isnot(None),
                    FocusCostData.tags != ''
                )
            ).distinct().all()
            
            for resource in resources_with_tags:
                tags_str = resource.tags or ''
                tags_lower = tags_str.lower()
                
                # Verificar se tem pelo menos 2 das tags obrigatórias
                tag_count = 0
                for required_tag in required_tags:
                    if required_tag.lower() in tags_lower:
                        tag_count += 1
                
                if tag_count >= 2:  # Pelo menos 2 tags obrigatórias
                    compliant_count += 1
            
            # Considerar também recursos com Virtual Tags
            virtual_tagged_resources = self.db.query(
                func.count(func.distinct(VirtualTagAllocation.resource_id))
            ).filter(
                VirtualTagAllocation.allocation_date == date
            ).scalar() or 0
            
            # Ajustar compliance considerando virtual tags
            total_compliant = min(compliant_count + virtual_tagged_resources, total_resources)
            
            return {
                'total_resources': total_resources,
                'compliant_resources': total_compliant,
                'compliance_rate': (total_compliant / total_resources * 100) if total_resources > 0 else 0,
                'virtual_tagged_resources': virtual_tagged_resources,
                'natively_tagged_resources': compliant_count
            }
            
        except Exception as e:
            logger.error(f"Error getting tag compliance metrics: {str(e)}")
            return {'total_resources': 0, 'compliant_resources': 0}
    
    def get_unallocated_cost_metrics(self, date: date) -> Dict[str, Any]:
        """Coleta métricas de custos não alocados"""
        try:
            # Custo total
            total_cost = self.db.query(
                func.sum(FocusCostData.effective_cost)
            ).filter(
                FocusCostData.billing_period_start == date
            ).scalar() or 0
            
            if total_cost == 0:
                return {'total_cost': 0, 'unallocated_cost': 0}
            
            # Custos sem tags essenciais
            untagged_cost = self.db.query(
                func.sum(FocusCostData.effective_cost)
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    or_(
                        FocusCostData.tags.is_(None),
                        FocusCostData.tags == '',
                        ~FocusCostData.tags.ilike('%environment%'),
                        ~FocusCostData.tags.ilike('%project%')
                    )
                )
            ).scalar() or 0
            
            # Subtrair custos cobertos por Virtual Tags
            virtual_tagged_cost = self.db.query(
                func.sum(VirtualTagAllocation.allocated_cost)
            ).filter(
                VirtualTagAllocation.allocation_date == date
            ).scalar() or 0
            
            # Custo realmente não alocado
            actually_unallocated = max(0, float(untagged_cost) - float(virtual_tagged_cost))
            
            return {
                'total_cost': float(total_cost),
                'untagged_cost': float(untagged_cost),
                'virtual_tagged_cost': float(virtual_tagged_cost),
                'unallocated_cost': actually_unallocated,
                'unallocated_percentage': (actually_unallocated / float(total_cost) * 100) if total_cost > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting unallocated cost metrics: {str(e)}")
            return {'total_cost': 0, 'unallocated_cost': 0}
    
    def get_security_compliance_metrics(self, date: date) -> Dict[str, Any]:
        """Coleta métricas de compliance de segurança"""
        try:
            # Analisar recursos com possíveis problemas de segurança baseado em padrões
            security_issues = []
            
            # Recursos sem encryption (baseado em nomes de serviço)
            unencrypted_resources = self.db.query(
                func.count(FocusCostData.resource_id),
                func.sum(FocusCostData.effective_cost)
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    FocusCostData.service_name.in_([
                        'Amazon Simple Storage Service',
                        'Amazon Elastic Block Store',
                        'Azure Storage',
                        'Cloud Storage'
                    ]),
                    ~FocusCostData.tags.ilike('%encrypt%')
                )
            ).first()
            
            # Recursos em zonas públicas (padrão simples)
            public_resources = self.db.query(
                func.count(FocusCostData.resource_id),
                func.sum(FocusCostData.effective_cost)
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    or_(
                        FocusCostData.tags.ilike('%public%'),
                        FocusCostData.resource_id.ilike('%public%')
                    )
                )
            ).first()
            
            total_resources = self.db.query(
                func.count(FocusCostData.resource_id)
            ).filter(
                FocusCostData.billing_period_start == date
            ).scalar() or 0
            
            return {
                'total_resources': total_resources,
                'unencrypted_resources': unencrypted_resources[0] or 0,
                'unencrypted_cost': float(unencrypted_resources[1] or 0),
                'public_resources': public_resources[0] or 0,
                'public_cost': float(public_resources[1] or 0),
                'security_score': max(0, 100 - ((unencrypted_resources[0] or 0) + (public_resources[0] or 0)) / max(1, total_resources) * 100)
            }
            
        except Exception as e:
            logger.error(f"Error getting security compliance metrics: {str(e)}")
            return {'total_resources': 0, 'security_score': 100}
    
    def get_cost_allocation_coverage(self, date: date) -> Dict[str, Any]:
        """Calcula cobertura de alocação de custos"""
        try:
            # Análise por diferentes métodos de alocação
            
            # 1. Alocação por tags nativas
            native_tagged = self.db.query(
                func.sum(FocusCostData.effective_cost)
            ).filter(
                and_(
                    FocusCostData.billing_period_start == date,
                    FocusCostData.tags.isnot(None),
                    FocusCostData.tags != '',
                    or_(
                        FocusCostData.tags.ilike('%project%'),
                        FocusCostData.tags.ilike('%application%'),
                        FocusCostData.tags.ilike('%team%')
                    )
                )
            ).scalar() or 0
            
            # 2. Alocação por Virtual Tags
            virtual_tagged = self.db.query(
                func.sum(VirtualTagAllocation.allocated_cost)
            ).filter(
                VirtualTagAllocation.allocation_date == date
            ).scalar() or 0
            
            # 3. Custo total
            total_cost = self.db.query(
                func.sum(FocusCostData.effective_cost)
            ).filter(
                FocusCostData.billing_period_start == date
            ).scalar() or 0
            
            if total_cost == 0:
                return {'coverage_percentage': 100}
            
            # Evitar dupla contagem entre native e virtual tags
            total_allocated = min(float(native_tagged) + float(virtual_tagged), float(total_cost))
            coverage_percentage = (total_allocated / float(total_cost)) * 100
            
            return {
                'total_cost': float(total_cost),
                'native_tagged_cost': float(native_tagged),
                'virtual_tagged_cost': float(virtual_tagged),
                'total_allocated_cost': total_allocated,
                'coverage_percentage': coverage_percentage,
                'unallocated_cost': float(total_cost) - total_allocated
            }
            
        except Exception as e:
            logger.error(f"Error getting cost allocation coverage: {str(e)}")
            return {'coverage_percentage': 0}
    
    def get_governance_score(self, date: date) -> Dict[str, Any]:
        """Calcula score geral de governança"""
        try:
            # Combinar diferentes métricas de governança
            tag_metrics = self.get_tag_compliance_metrics(date)
            allocation_metrics = self.get_cost_allocation_coverage(date)
            security_metrics = self.get_security_compliance_metrics(date)
            
            # Calcular score ponderado
            tag_score = tag_metrics.get('compliance_rate', 0)
            allocation_score = allocation_metrics.get('coverage_percentage', 0)
            security_score = security_metrics.get('security_score', 0)
            
            # Pesos: 40% tags, 40% allocation, 20% security
            governance_score = (tag_score * 0.4 + allocation_score * 0.4 + security_score * 0.2)
            
            return {
                'governance_score': round(governance_score, 2),
                'tag_compliance_score': round(tag_score, 2),
                'allocation_coverage_score': round(allocation_score, 2),
                'security_compliance_score': round(security_score, 2),
                'recommendations': self._generate_governance_recommendations(
                    tag_score, allocation_score, security_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error calculating governance score: {str(e)}")
            return {'governance_score': 0}
    
    def _generate_governance_recommendations(
        self, 
        tag_score: float, 
        allocation_score: float, 
        security_score: float
    ) -> List[str]:
        """Gera recomendações baseadas nos scores"""
        recommendations = []
        
        if tag_score < 80:
            recommendations.append("Implementar política de tags obrigatórias")
        
        if allocation_score < 85:
            recommendations.append("Expandir uso de Virtual Tags para melhor alocação")
        
        if security_score < 90:
            recommendations.append("Revisar configurações de segurança e encryption")
        
        if tag_score > 95 and allocation_score > 95:
            recommendations.append("Excelente governança! Manter boas práticas")
        
        return recommendations
