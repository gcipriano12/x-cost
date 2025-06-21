"""
Virtual Tags Models - X Cost
Sistema de alocação dinâmica de custos através de regras
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Numeric, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import uuid4, UUID as PyUUID

from app.credential_models import Base

# Enums para padronização
class VirtualTagCategory(str, Enum):
    BUSINESS_UNIT = "business_unit"
    PROJECT = "project"
    ENVIRONMENT = "environment"
    COST_CENTER = "cost_center"
    DEPARTMENT = "department"
    TEAM = "team"
    APPLICATION = "application"
    OWNER = "owner"
    CUSTOM = "custom"

class LogicalOperator(str, Enum):
    AND = "AND"
    OR = "OR"

class ConditionOperator(str, Enum):
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    REGEX = "regex"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"

class ActionType(str, Enum):
    SET_VALUE = "set_value"
    EXTRACT_FROM_FIELD = "extract_from_field"
    MAP_VALUE = "map_value"
    CALCULATE = "calculate"
    DEFAULT = "default"

# SQLAlchemy Models
class VirtualTag(Base):
    __tablename__ = "virtual_tags"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    category = Column(SQLEnum(VirtualTagCategory), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, nullable=False, default=100)
    default_value = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(UUID(as_uuid=True), ForeignKey("finops.users.id"))
    
    # Relationships
    rules = relationship("VirtualTagRule", back_populates="virtual_tag", cascade="all, delete-orphan")
    allocations = relationship("VirtualTagAllocation", back_populates="virtual_tag")

class VirtualTagRule(Base):
    __tablename__ = "virtual_tag_rules"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    virtual_tag_id = Column(UUID(as_uuid=True), ForeignKey("finops.virtual_tags.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    conditions = Column(JSONB)  # Array de condições
    action = Column(JSONB)      # Ação a executar
    priority = Column(Integer, nullable=False, default=100)
    logical_operator = Column(SQLEnum(LogicalOperator), default=LogicalOperator.AND)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    virtual_tag = relationship("VirtualTag", back_populates="rules")

class VirtualTagAllocation(Base):
    __tablename__ = "virtual_tag_allocations"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    cost_record_id = Column(Integer, ForeignKey("finops.focus_cost_data.id"), nullable=False)
    virtual_tag_id = Column(UUID(as_uuid=True), ForeignKey("finops.virtual_tags.id"), nullable=False)
    tag_value = Column(String(255), nullable=False)
    allocated_cost = Column(Numeric(15, 4), nullable=False)
    allocation_percentage = Column(Numeric(5, 2), default=100.0)
    allocation_date = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    virtual_tag = relationship("VirtualTag", back_populates="allocations")

class VirtualTagProcessingLog(Base):
    __tablename__ = "virtual_tag_processing_logs"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    processing_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    virtual_tag_id = Column(UUID(as_uuid=True), ForeignKey("finops.virtual_tags.id"))
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, default="processing")  # processing, completed, failed
    records_processed = Column(Integer, default=0)
    records_allocated = Column(Integer, default=0)
    total_cost_allocated = Column(Numeric(15, 4), default=0)
    error_message = Column(Text)
    processing_time_seconds = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

# Pydantic Models para API
class RuleCondition(BaseModel):
    field: str
    operator: ConditionOperator
    value: Union[str, int, float, List[str], None]
    case_sensitive: bool = False

class RuleAction(BaseModel):
    type: ActionType
    value: Optional[str] = None
    field: Optional[str] = None
    mapping: Optional[Dict[str, str]] = None
    pattern: Optional[str] = None
    default_value: Optional[str] = None

class VirtualTagRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    conditions: List[RuleCondition]
    action: RuleAction
    priority: int = 100
    logical_operator: LogicalOperator = LogicalOperator.AND
    is_active: bool = True

class VirtualTagRuleCreate(VirtualTagRuleBase):
    pass

class VirtualTagRuleUpdate(VirtualTagRuleBase):
    name: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class VirtualTagRuleResponse(VirtualTagRuleBase):
    id: PyUUID
    virtual_tag_id: PyUUID
    created_at: datetime
    
    class Config:
        from_attributes = True

class VirtualTagBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: VirtualTagCategory
    is_active: bool = True
    priority: int = 100
    default_value: Optional[str] = None

class VirtualTagCreate(VirtualTagBase):
    rules: List[VirtualTagRuleCreate] = []

class VirtualTagUpdate(VirtualTagBase):
    name: Optional[str] = None
    category: Optional[VirtualTagCategory] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None
    rules: Optional[List[VirtualTagRuleUpdate]] = None

class VirtualTagResponse(VirtualTagBase):
    id: PyUUID
    created_at: datetime
    updated_at: datetime
    created_by: Optional[PyUUID]
    rules: List[VirtualTagRuleResponse] = []
    
    class Config:
        from_attributes = True

class AllocationPreview(BaseModel):
    cost_record_id: int
    provider_name: str
    service_name: str
    resource_id: Optional[str]
    current_cost: Decimal
    allocated_value: str
    confidence_score: float
    billing_period_start: datetime

class AllocationResult(BaseModel):
    processing_id: PyUUID
    total_records_processed: int
    total_records_allocated: int
    total_cost_allocated: Decimal
    unallocated_cost: Decimal
    allocation_percentage: float
    processing_time_seconds: int
    virtual_tags_applied: List[PyUUID]

class DateRangeFilter(BaseModel):
    start_date: datetime
    end_date: datetime

class CoverageMetrics(BaseModel):
    total_cost: Decimal
    allocated_cost: Decimal
    unallocated_cost: Decimal
    allocation_percentage: float
    total_records: int
    allocated_records: int
    virtual_tags_count: int
    rules_count: int

class AllocationBreakdown(BaseModel):
    virtual_tag_name: str
    category: VirtualTagCategory
    total_cost: Decimal
    record_count: int
    percentage_of_total: float
    top_values: List[Dict[str, Any]]

class UnallocatedCost(BaseModel):
    provider_name: str
    service_name: str
    resource_type: Optional[str]
    cost_amount: Decimal
    record_count: int
    percentage_of_unallocated: float

class RuleConflict(BaseModel):
    virtual_tag1_id: PyUUID
    virtual_tag1_name: str
    virtual_tag2_id: PyUUID
    virtual_tag2_name: str
    conflict_type: str
    description: str
    sample_records: int

class AvailableField(BaseModel):
    field_name: str
    display_name: str
    field_type: str  # Renomeado de data_type para field_type
    sample_values: List[str]
    is_nullable: bool
    description: Optional[str]

class DashboardMetrics(BaseModel):
    coverage_metrics: CoverageMetrics
    allocation_breakdown: List[AllocationBreakdown]
    recent_processing: List[Dict[str, Any]]
    rule_conflicts: List[RuleConflict]
    unallocated_summary: Dict[str, Any]
