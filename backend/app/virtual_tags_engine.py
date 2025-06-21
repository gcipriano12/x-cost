"""
Virtual Tags Engine - X Cost
Engine para processar regras de Virtual Tags e alocar custos
"""

import re
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, text

from app.virtual_tags_models import (
    VirtualTag, VirtualTagRule, VirtualTagAllocation, VirtualTagProcessingLog,
    RuleCondition, RuleAction, LogicalOperator, ConditionOperator, ActionType,
    AllocationResult, AllocationPreview, DateRangeFilter, CoverageMetrics,
    AllocationBreakdown, UnallocatedCost, RuleConflict, AvailableField
)
from app.models import FocusCostData

logger = logging.getLogger(__name__)

class VirtualTagEngine:
    """Engine para processar regras de Virtual Tags"""
    
    def __init__(self, db: Session):
        self.db = db
        
    async def process_allocation(
        self,
        date_range: DateRangeFilter,
        virtual_tags: Optional[List[VirtualTag]] = None,
        force_reprocess: bool = False
    ) -> AllocationResult:
        """
        Processar alocação de custos baseada em regras de Virtual Tags
        """
        processing_id = uuid4()
        start_time = datetime.utcnow()
        
        try:
            # Log início do processamento
            log_entry = VirtualTagProcessingLog(
                processing_id=processing_id,
                start_date=date_range.start_date,
                end_date=date_range.end_date,
                status="processing"
            )
            self.db.add(log_entry)
            self.db.commit()
            
            # Obter Virtual Tags para processar
            if virtual_tags is None:
                virtual_tags = self.db.query(VirtualTag).filter(
                    VirtualTag.is_active == True
                ).order_by(VirtualTag.priority.asc()).all()
            
            # Obter registros de custo no período
            cost_records_query = self.db.query(FocusCostData).filter(
                and_(
                    FocusCostData.billing_period_start >= date_range.start_date.date(),
                    FocusCostData.billing_period_start <= date_range.end_date.date()
                )
            )
            
            cost_records = cost_records_query.all()
            logger.info(f"Processing {len(cost_records)} cost records for {len(virtual_tags)} virtual tags")
            
            # Limpar alocações existentes se force_reprocess
            if force_reprocess:
                self.db.query(VirtualTagAllocation).filter(
                    VirtualTagAllocation.cost_record_id.in_([r.id for r in cost_records])
                ).delete(synchronize_session=False)
                self.db.commit()
            
            # Processar cada registro de custo
            total_processed = 0
            total_allocated = 0
            total_cost_allocated = Decimal('0')
            virtual_tags_applied = set()
            
            for cost_record in cost_records:
                allocations = await self._process_cost_record(cost_record, virtual_tags)
                
                for allocation in allocations:
                    self.db.add(allocation)
                    total_cost_allocated += allocation.allocated_cost
                    virtual_tags_applied.add(allocation.virtual_tag_id)
                
                total_processed += 1
                if allocations:
                    total_allocated += 1
                
                # Commit em lotes para performance
                if total_processed % 1000 == 0:
                    self.db.commit()
                    logger.info(f"Processed {total_processed} records...")
            
            self.db.commit()
            
            # Calcular métricas finais
            total_cost = sum(r.effective_cost or 0 for r in cost_records)
            unallocated_cost = total_cost - total_cost_allocated
            allocation_percentage = (float(total_cost_allocated) / float(total_cost) * 100) if total_cost > 0 else 0
            
            # Atualizar log de processamento
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            log_entry.status = "completed"
            log_entry.records_processed = total_processed
            log_entry.records_allocated = total_allocated
            log_entry.total_cost_allocated = total_cost_allocated
            log_entry.processing_time_seconds = int(processing_time)
            log_entry.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Processing completed: {total_allocated}/{total_processed} records allocated")
            
            return AllocationResult(
                processing_id=processing_id,
                total_records_processed=total_processed,
                total_records_allocated=total_allocated,
                total_cost_allocated=total_cost_allocated,
                unallocated_cost=unallocated_cost,
                allocation_percentage=allocation_percentage,
                processing_time_seconds=int(processing_time),
                virtual_tags_applied=list(virtual_tags_applied)
            )
            
        except Exception as e:
            # Log erro
            log_entry.status = "failed"
            log_entry.error_message = str(e)
            log_entry.processing_time_seconds = int((datetime.utcnow() - start_time).total_seconds())
            self.db.commit()
            
            logger.error(f"Processing failed: {str(e)}")
            raise
    
    async def _process_cost_record(
        self,
        cost_record: FocusCostData,
        virtual_tags: List[VirtualTag]
    ) -> List[VirtualTagAllocation]:
        """
        Processar um registro de custo específico contra todas as Virtual Tags
        """
        allocations = []
        
        for virtual_tag in virtual_tags:
            if not virtual_tag.is_active:
                continue
                
            tag_value = await self.evaluate_rules(cost_record, virtual_tag)
            
            if tag_value:
                allocation = VirtualTagAllocation(
                    cost_record_id=cost_record.id,
                    virtual_tag_id=virtual_tag.id,
                    tag_value=tag_value,
                    allocated_cost=cost_record.effective_cost or 0,
                    allocation_percentage=Decimal('100.0'),
                    allocation_date=datetime.utcnow()
                )
                allocations.append(allocation)
        
        return allocations
    
    async def evaluate_rules(
        self,
        cost_record: FocusCostData,
        virtual_tag: VirtualTag
    ) -> Optional[str]:
        """
        Avaliar regras de uma Virtual Tag para um registro de custo
        """
        # Ordenar regras por prioridade
        rules = sorted(virtual_tag.rules, key=lambda r: r.priority)
        
        for rule in rules:
            if not rule.is_active:
                continue
                
            # Verificar se as condições da regra são atendidas
            conditions_met = await self.apply_conditions(
                cost_record,
                rule.conditions,
                rule.logical_operator
            )
            
            if conditions_met:
                # Executar ação da regra
                tag_value = await self.execute_action(cost_record, rule.action)
                if tag_value:
                    return tag_value
        
        # Se nenhuma regra aplicou, usar valor padrão
        return virtual_tag.default_value
    
    async def apply_conditions(
        self,
        cost_record: FocusCostData,
        conditions: List[Dict[str, Any]],
        logical_operator: LogicalOperator
    ) -> bool:
        """
        Aplicar condições de uma regra
        """
        if not conditions:
            return True
        
        results = []
        
        for condition_data in conditions:
            condition = RuleCondition(**condition_data)
            result = await self._evaluate_condition(cost_record, condition)
            results.append(result)
        
        # Aplicar operador lógico
        if logical_operator == LogicalOperator.AND:
            return all(results)
        else:  # OR
            return any(results)
    
    async def _evaluate_condition(
        self,
        cost_record: FocusCostData,
        condition: RuleCondition
    ) -> bool:
        """
        Avaliar uma condição individual
        """
        # Obter valor do campo
        field_value = getattr(cost_record, condition.field, None)
        
        if field_value is None:
            if condition.operator == ConditionOperator.IS_NULL:
                return True
            elif condition.operator == ConditionOperator.IS_NOT_NULL:
                return False
            else:
                return False
        
        # Converter para string se necessário
        field_str = str(field_value)
        condition_value = condition.value
        
        # Aplicar case sensitivity
        if not condition.case_sensitive and isinstance(field_str, str):
            field_str = field_str.lower()
            if isinstance(condition_value, str):
                condition_value = condition_value.lower()
            elif isinstance(condition_value, list):
                condition_value = [str(v).lower() for v in condition_value]
        
        # Avaliar condição baseada no operador
        if condition.operator == ConditionOperator.EQUALS:
            return field_str == str(condition_value)
        
        elif condition.operator == ConditionOperator.NOT_EQUALS:
            return field_str != str(condition_value)
        
        elif condition.operator == ConditionOperator.CONTAINS:
            return str(condition_value) in field_str
        
        elif condition.operator == ConditionOperator.NOT_CONTAINS:
            return str(condition_value) not in field_str
        
        elif condition.operator == ConditionOperator.STARTS_WITH:
            return field_str.startswith(str(condition_value))
        
        elif condition.operator == ConditionOperator.ENDS_WITH:
            return field_str.endswith(str(condition_value))
        
        elif condition.operator == ConditionOperator.IN:
            return field_str in [str(v) for v in condition_value]
        
        elif condition.operator == ConditionOperator.NOT_IN:
            return field_str not in [str(v) for v in condition_value]
        
        elif condition.operator == ConditionOperator.GREATER_THAN:
            try:
                return float(field_value) > float(condition_value)
            except (ValueError, TypeError):
                return False
        
        elif condition.operator == ConditionOperator.LESS_THAN:
            try:
                return float(field_value) < float(condition_value)
            except (ValueError, TypeError):
                return False
        
        elif condition.operator == ConditionOperator.REGEX:
            try:
                pattern = re.compile(str(condition_value))
                return bool(pattern.search(field_str))
            except re.error:
                return False
        
        elif condition.operator == ConditionOperator.IS_NOT_NULL:
            return True  # Já verificamos que não é None acima
        
        return False
    
    async def execute_action(
        self,
        cost_record: FocusCostData,
        action_data: Dict[str, Any]
    ) -> Optional[str]:
        """
        Executar ação de uma regra
        """
        action = RuleAction(**action_data)
        
        if action.type == ActionType.SET_VALUE:
            return action.value
        
        elif action.type == ActionType.EXTRACT_FROM_FIELD:
            field_value = getattr(cost_record, action.field, None)
            if field_value is None:
                return action.default_value
            
            if action.pattern:
                # Usar regex para extrair valor
                try:
                    match = re.search(action.pattern, str(field_value))
                    if match:
                        return match.group(1) if match.groups() else match.group(0)
                except re.error:
                    pass
            
            return str(field_value)
        
        elif action.type == ActionType.MAP_VALUE:
            field_value = getattr(cost_record, action.field, None)
            if field_value is None:
                return action.default_value
            
            field_str = str(field_value)
            return action.mapping.get(field_str, action.default_value)
        
        elif action.type == ActionType.DEFAULT:
            return action.default_value
        
        elif action.type == ActionType.CALCULATE:
            # Implementar lógica de cálculo se necessário
            return action.value
        
        return action.default_value
    
    async def get_allocation_preview(
        self,
        virtual_tag: VirtualTag,
        date_range: DateRangeFilter,
        limit: int = 100
    ) -> List[AllocationPreview]:
        """
        Gerar preview de alocação para uma Virtual Tag
        """
        # Obter amostra de registros de custo
        cost_records = self.db.query(FocusCostData).filter(
            and_(
                FocusCostData.billing_period_start >= date_range.start_date.date(),
                FocusCostData.billing_period_start <= date_range.end_date.date()
            )
        ).limit(limit).all()
        
        previews = []
        
        for cost_record in cost_records:
            tag_value = await self.evaluate_rules(cost_record, virtual_tag)
            
            if tag_value:
                # Calcular confidence score baseado na especificidade das regras
                confidence_score = self._calculate_confidence_score(virtual_tag, cost_record)
                
                preview = AllocationPreview(
                    cost_record_id=cost_record.id,
                    provider_name=cost_record.provider_name,
                    service_name=cost_record.service_name,
                    resource_id=cost_record.resource_id,
                    current_cost=cost_record.effective_cost or 0,
                    allocated_value=tag_value,
                    confidence_score=confidence_score,
                    billing_period_start=datetime.combine(cost_record.billing_period_start, datetime.min.time())
                )
                previews.append(preview)
        
        return previews
    
    def _calculate_confidence_score(self, virtual_tag: VirtualTag, cost_record: FocusCostData) -> float:
        """
        Calcular score de confiança para uma alocação
        """
        # Score básico baseado no número de condições atendidas
        base_score = 0.7
        
        # Adicionar score baseado na especificidade das regras
        for rule in virtual_tag.rules:
            if rule.is_active and rule.conditions:
                # Score mais alto para regras com mais condições
                condition_score = min(len(rule.conditions) * 0.1, 0.3)
                base_score += condition_score
        
        return min(base_score, 1.0)
    
    async def get_available_fields(self) -> List[AvailableField]:
        """
        Obter campos disponíveis para criação de regras
        """
        # Campos do modelo FocusCostData que podem ser usados em regras
        fields = [
            AvailableField(
                field_name="provider_name",
                display_name="Provider",
                field_type="string",
                sample_values=self._get_sample_values("provider_name"),
                is_nullable=False,
                description="Nome do provedor cloud (AWS, Azure, GCP, etc.)"
            ),
            AvailableField(
                field_name="service_name",
                display_name="Service",
                field_type="string",
                sample_values=self._get_sample_values("service_name"),
                is_nullable=False,
                description="Nome do serviço (EC2, S3, VPC, etc.)"
            ),
            AvailableField(
                field_name="service_category",
                display_name="Service Category",
                field_type="string",
                sample_values=self._get_sample_values("service_category"),
                is_nullable=True,
                description="Categoria do serviço"
            ),
            AvailableField(
                field_name="resource_id",
                display_name="Resource ID",
                field_type="string",
                sample_values=self._get_sample_values("resource_id"),
                is_nullable=True,
                description="ID do recurso"
            ),
            AvailableField(
                field_name="resource_name",
                display_name="Resource Name",
                field_type="string",
                sample_values=self._get_sample_values("resource_name"),
                is_nullable=True,
                description="Nome do recurso"
            ),
            AvailableField(
                field_name="resource_type",
                display_name="Resource Type",
                field_type="string",
                sample_values=self._get_sample_values("resource_type"),
                is_nullable=True,
                description="Tipo do recurso"
            ),
            AvailableField(
                field_name="region",
                display_name="Region",
                field_type="string",
                sample_values=self._get_sample_values("region"),
                is_nullable=True,
                description="Região do recurso"
            ),
            AvailableField(
                field_name="availability_zone",
                display_name="Availability Zone",
                field_type="string",
                sample_values=self._get_sample_values("availability_zone"),
                is_nullable=True,
                description="Zona de disponibilidade"
            ),
            AvailableField(
                field_name="billing_account_id",
                display_name="Billing Account ID",
                field_type="string",
                sample_values=self._get_sample_values("billing_account_id"),
                is_nullable=True,
                description="ID da conta de billing"
            ),
            AvailableField(
                field_name="billing_account_name",
                display_name="Billing Account Name",
                field_type="string",
                sample_values=self._get_sample_values("billing_account_name"),
                is_nullable=True,
                description="Nome da conta de billing"
            ),
            AvailableField(
                field_name="effective_cost",
                display_name="Effective Cost",
                field_type="decimal",
                sample_values=[],
                is_nullable=True,
                description="Custo efetivo do recurso"
            )
        ]
        
        return fields
    
    def _get_sample_values(self, field_name: str, limit: int = 10) -> List[str]:
        """
        Obter valores de amostra para um campo
        """
        try:
            result = self.db.query(getattr(FocusCostData, field_name)).distinct().limit(limit).all()
            return [str(row[0]) for row in result if row[0] is not None]
        except Exception:
            return []
