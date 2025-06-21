"""
Virtual Tags Analytics - X Cost
Módulo para análise e métricas de Virtual Tags
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, distinct, text

from app.virtual_tags_models import (
    VirtualTag, VirtualTagAllocation, VirtualTagProcessingLog,
    CoverageMetrics, AllocationBreakdown, UnallocatedCost, RuleConflict,
    DateRangeFilter, DashboardMetrics, VirtualTagCategory
)
from app.models import FocusCostData

logger = logging.getLogger(__name__)

class VirtualTagAnalytics:
    """Classe para análises e métricas de Virtual Tags"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_coverage_metrics(self, date_range: DateRangeFilter) -> CoverageMetrics:
        """
        Calcular métricas de cobertura de alocação
        """
        try:
            # Total de custos no período
            total_cost_query = self.db.query(
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.count(FocusCostData.id).label('total_records')
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= date_range.start_date.date(),
                    FocusCostData.billing_period_start <= date_range.end_date.date()
                )
            )
            
            total_result = total_cost_query.first()
            total_cost = total_result.total_cost or Decimal('0')
            total_records = total_result.total_records or 0
            
            # Custos alocados
            allocated_query = self.db.query(
                func.sum(VirtualTagAllocation.allocated_cost).label('allocated_cost'),
                func.count(distinct(VirtualTagAllocation.cost_record_id)).label('allocated_records')
            ).join(
                FocusCostData, VirtualTagAllocation.cost_record_id == FocusCostData.id
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= date_range.start_date.date(),
                    FocusCostData.billing_period_start <= date_range.end_date.date()
                )
            )
            
            allocated_result = allocated_query.first()
            allocated_cost = allocated_result.allocated_cost or Decimal('0')
            allocated_records = allocated_result.allocated_records or 0
            
            # Contar Virtual Tags e regras ativas
            virtual_tags_count = self.db.query(VirtualTag).filter(
                VirtualTag.is_active == True
            ).count()
            
            rules_count = self.db.query(VirtualTag).join(
                VirtualTag.rules
            ).filter(
                VirtualTag.is_active == True
            ).count()
            
            # Calcular métricas
            unallocated_cost = total_cost - allocated_cost
            allocation_percentage = (float(allocated_cost) / float(total_cost) * 100) if total_cost > 0 else 0
            
            return CoverageMetrics(
                total_cost=total_cost,
                allocated_cost=allocated_cost,
                unallocated_cost=unallocated_cost,
                allocation_percentage=allocation_percentage,
                total_records=total_records,
                allocated_records=allocated_records,
                virtual_tags_count=virtual_tags_count,
                rules_count=rules_count
            )
            
        except Exception as e:
            logger.error(f"Error calculating coverage metrics: {str(e)}")
            raise
    
    async def get_allocation_breakdown(self, date_range: DateRangeFilter) -> List[AllocationBreakdown]:
        """
        Obter breakdown de alocação por Virtual Tag
        """
        try:
            # Query para obter breakdown por Virtual Tag
            breakdown_query = self.db.query(
                VirtualTag.name,
                VirtualTag.category,
                func.sum(VirtualTagAllocation.allocated_cost).label('total_cost'),
                func.count(VirtualTagAllocation.id).label('record_count')
            ).join(
                VirtualTagAllocation, VirtualTag.id == VirtualTagAllocation.virtual_tag_id
            ).join(
                FocusCostData, VirtualTagAllocation.cost_record_id == FocusCostData.id
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= date_range.start_date.date(),
                    FocusCostData.billing_period_start <= date_range.end_date.date()
                )
            ).group_by(
                VirtualTag.id, VirtualTag.name, VirtualTag.category
            ).order_by(
                func.sum(VirtualTagAllocation.allocated_cost).desc()
            )
            
            results = breakdown_query.all()
            
            # Calcular total geral para percentuais
            total_allocated = sum(r.total_cost for r in results)
            
            breakdowns = []
            for result in results:
                percentage = (float(result.total_cost) / float(total_allocated) * 100) if total_allocated > 0 else 0
                
                # Obter top valores para esta Virtual Tag
                top_values = await self._get_top_values_for_tag(
                    result.name, date_range, limit=5
                )
                
                breakdown = AllocationBreakdown(
                    virtual_tag_name=result.name,
                    category=result.category,
                    total_cost=result.total_cost,
                    record_count=result.record_count,
                    percentage_of_total=percentage,
                    top_values=top_values
                )
                breakdowns.append(breakdown)
            
            return breakdowns
            
        except Exception as e:
            logger.error(f"Error calculating allocation breakdown: {str(e)}")
            raise
    
    async def _get_top_values_for_tag(
        self, 
        virtual_tag_name: str, 
        date_range: DateRangeFilter,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Obter top valores para uma Virtual Tag específica
        """
        try:
            top_values_query = self.db.query(
                VirtualTagAllocation.tag_value,
                func.sum(VirtualTagAllocation.allocated_cost).label('cost'),
                func.count(VirtualTagAllocation.id).label('count')
            ).join(
                VirtualTag, VirtualTagAllocation.virtual_tag_id == VirtualTag.id
            ).join(
                FocusCostData, VirtualTagAllocation.cost_record_id == FocusCostData.id
            ).filter(
                and_(
                    VirtualTag.name == virtual_tag_name,
                    FocusCostData.billing_period_start >= date_range.start_date.date(),
                    FocusCostData.billing_period_start <= date_range.end_date.date()
                )
            ).group_by(
                VirtualTagAllocation.tag_value
            ).order_by(
                func.sum(VirtualTagAllocation.allocated_cost).desc()
            ).limit(limit)
            
            results = top_values_query.all()
            
            return [
                {
                    'value': result.tag_value,
                    'cost': float(result.cost),
                    'count': result.count
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error getting top values for tag {virtual_tag_name}: {str(e)}")
            return []
    
    async def get_unallocated_costs(self, date_range: DateRangeFilter) -> List[UnallocatedCost]:
        """
        Obter custos não alocados agrupados por provider e serviço
        """
        try:
            # Subquery para obter IDs de registros alocados
            allocated_record_ids = self.db.query(
                distinct(VirtualTagAllocation.cost_record_id)
            ).join(
                FocusCostData, VirtualTagAllocation.cost_record_id == FocusCostData.id
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= date_range.start_date.date(),
                    FocusCostData.billing_period_start <= date_range.end_date.date()
                )
            ).subquery()
            
            # Query para registros não alocados
            unallocated_query = self.db.query(
                FocusCostData.provider_name,
                FocusCostData.service_name,
                FocusCostData.resource_type,
                func.sum(FocusCostData.effective_cost).label('cost_amount'),
                func.count(FocusCostData.id).label('record_count')
            ).filter(
                and_(
                    FocusCostData.billing_period_start >= date_range.start_date.date(),
                    FocusCostData.billing_period_start <= date_range.end_date.date(),
                    ~FocusCostData.id.in_(allocated_record_ids)
                )
            ).group_by(
                FocusCostData.provider_name,
                FocusCostData.service_name,
                FocusCostData.resource_type
            ).order_by(
                func.sum(FocusCostData.effective_cost).desc()
            )
            
            results = unallocated_query.all()
            
            # Calcular total não alocado para percentuais
            total_unallocated = sum(r.cost_amount for r in results)
            
            unallocated_costs = []
            for result in results:
                percentage = (float(result.cost_amount) / float(total_unallocated) * 100) if total_unallocated > 0 else 0
                
                unallocated_cost = UnallocatedCost(
                    provider_name=result.provider_name,
                    service_name=result.service_name,
                    resource_type=result.resource_type,
                    cost_amount=result.cost_amount,
                    record_count=result.record_count,
                    percentage_of_unallocated=percentage
                )
                unallocated_costs.append(unallocated_cost)
            
            return unallocated_costs
            
        except Exception as e:
            logger.error(f"Error getting unallocated costs: {str(e)}")
            raise
    
    async def detect_rule_conflicts(self) -> List[RuleConflict]:
        """
        Detectar conflitos potenciais entre regras de Virtual Tags
        """
        try:
            conflicts = []
            
            # Obter todas as Virtual Tags ativas
            virtual_tags = self.db.query(VirtualTag).filter(
                VirtualTag.is_active == True
            ).all()
            
            # Comparar pares de Virtual Tags para detectar conflitos
            for i, tag1 in enumerate(virtual_tags):
                for tag2 in virtual_tags[i+1:]:
                    conflict = await self._check_tag_conflict(tag1, tag2)
                    if conflict:
                        conflicts.append(conflict)
            
            return conflicts
            
        except Exception as e:
            logger.error(f"Error detecting rule conflicts: {str(e)}")
            return []
    
    async def _check_tag_conflict(self, tag1: VirtualTag, tag2: VirtualTag) -> Optional[RuleConflict]:
        """
        Verificar se duas Virtual Tags têm conflito
        """
        try:
            # Verificar se têm mesma categoria (potencial conflito)
            if tag1.category == tag2.category:
                # Contar registros que seriam afetados por ambas
                # Esta é uma verificação simplificada - em produção seria mais complexa
                sample_count = await self._count_overlapping_records(tag1, tag2)
                
                if sample_count > 0:
                    return RuleConflict(
                        virtual_tag1_id=tag1.id,
                        virtual_tag1_name=tag1.name,
                        virtual_tag2_id=tag2.id,
                        virtual_tag2_name=tag2.name,
                        conflict_type="category_overlap",
                        description=f"Tags da mesma categoria '{tag1.category}' podem gerar alocações conflitantes",
                        sample_records=sample_count
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking conflict between {tag1.name} and {tag2.name}: {str(e)}")
            return None
    
    async def _count_overlapping_records(self, tag1: VirtualTag, tag2: VirtualTag) -> int:
        """
        Contar registros que podem ser afetados por ambas as tags
        """
        try:
            # Implementação simplificada - em produção seria mais sofisticada
            # Por enquanto, retorna uma estimativa baseada na categoria
            if tag1.category == tag2.category:
                return 10  # Valor exemplo
            return 0
            
        except Exception as e:
            logger.error(f"Error counting overlapping records: {str(e)}")
            return 0
    
    async def get_dashboard_metrics(self, date_range: DateRangeFilter) -> DashboardMetrics:
        """
        Obter métricas consolidadas para dashboard
        """
        try:
            # Obter todas as métricas
            coverage_metrics = await self.get_coverage_metrics(date_range)
            allocation_breakdown = await self.get_allocation_breakdown(date_range)
            rule_conflicts = await self.detect_rule_conflicts()
            
            # Obter processamentos recentes
            recent_processing = await self._get_recent_processing()
            
            # Resumo de custos não alocados
            unallocated_costs = await self.get_unallocated_costs(date_range)
            unallocated_summary = {
                'total_unallocated': float(coverage_metrics.unallocated_cost),
                'top_unallocated_services': unallocated_costs[:5],
                'unallocated_percentage': 100 - coverage_metrics.allocation_percentage
            }
            
            return DashboardMetrics(
                coverage_metrics=coverage_metrics,
                allocation_breakdown=allocation_breakdown,
                recent_processing=recent_processing,
                rule_conflicts=rule_conflicts,
                unallocated_summary=unallocated_summary
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard metrics: {str(e)}")
            raise
    
    async def _get_recent_processing(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obter processamentos recentes
        """
        try:
            recent_logs = self.db.query(VirtualTagProcessingLog).order_by(
                VirtualTagProcessingLog.created_at.desc()
            ).limit(limit).all()
            
            processing_list = []
            for log in recent_logs:
                processing_list.append({
                    'processing_id': str(log.processing_id),
                    'status': log.status,
                    'start_date': log.start_date.isoformat(),
                    'end_date': log.end_date.isoformat(),
                    'records_processed': log.records_processed,
                    'records_allocated': log.records_allocated,
                    'total_cost_allocated': float(log.total_cost_allocated or 0),
                    'processing_time_seconds': log.processing_time_seconds,
                    'created_at': log.created_at.isoformat(),
                    'error_message': log.error_message
                })
            
            return processing_list
            
        except Exception as e:
            logger.error(f"Error getting recent processing: {str(e)}")
            return []
    
    async def get_allocation_history(
        self,
        virtual_tag_id: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Obter histórico de alocações
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.query(
                func.date(VirtualTagAllocation.allocation_date).label('date'),
                func.sum(VirtualTagAllocation.allocated_cost).label('total_cost'),
                func.count(VirtualTagAllocation.id).label('allocation_count')
            )
            
            if virtual_tag_id:
                query = query.filter(VirtualTagAllocation.virtual_tag_id == virtual_tag_id)
            
            query = query.filter(
                VirtualTagAllocation.allocation_date >= start_date
            ).group_by(
                func.date(VirtualTagAllocation.allocation_date)
            ).order_by(
                func.date(VirtualTagAllocation.allocation_date)
            )
            
            results = query.all()
            
            history = []
            for result in results:
                history.append({
                    'date': result.date.isoformat(),
                    'total_cost': float(result.total_cost),
                    'allocation_count': result.allocation_count
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting allocation history: {str(e)}")
            return []
