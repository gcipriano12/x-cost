"""
KPI Models - X Cost
Modelos para o sistema de Key Performance Indicators
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Numeric, ForeignKey, Date, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from uuid import UUID as PyUUID

from app.models import Base

# Enums
class KPICategory(str, Enum):
    EFFICIENCY = "efficiency"
    PRICING = "pricing"
    PLANNING = "planning"
    GOVERNANCE = "governance"

class CalculationFrequency(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

# SQLAlchemy Models
class KPIDefinition(Base):
    __tablename__ = "kpi_definitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False, index=True)  # Usar string em vez de enum SQL
    description = Column(Text)
    formula = Column(Text)
    unit = Column(String(20))
    is_good_when_higher = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")
    
    # Relationships
    results = relationship("KPIResult", back_populates="definition", cascade="all, delete-orphan")
    company_configs = relationship("KPICompanyConfig", back_populates="definition", cascade="all, delete-orphan")

class KPIResult(Base):
    __tablename__ = "kpi_results"
    
    id = Column(Integer, primary_key=True)
    kpi_definition_id = Column(UUID(as_uuid=True), ForeignKey("kpi_definitions.id"), nullable=False)
    company_id = Column(String(100), nullable=False, default='default')
    calculation_date = Column(Date, nullable=False, index=True)
    value = Column(Numeric(15, 4), nullable=False)
    trend = Column(Numeric(5, 2))
    status = Column(String(20), default='neutral')
    meta_data = Column(JSONB)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    
    # Relationships
    definition = relationship("KPIDefinition", back_populates="results")

class KPICompanyConfig(Base):
    __tablename__ = "kpi_company_configs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    kpi_definition_id = Column(UUID(as_uuid=True), ForeignKey("kpi_definitions.id"), nullable=False)
    company_id = Column(String(100), nullable=False, default='default')
    target_value = Column(Numeric(15, 4))
    warning_threshold = Column(Numeric(15, 4))
    critical_threshold = Column(Numeric(15, 4))
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")
    
    # Relationships
    definition = relationship("KPIDefinition", back_populates="company_configs")
    
    # Relationships
    definition = relationship("KPIDefinition", back_populates="company_configs")

# Pydantic Models
class KPIDefinitionBase(BaseModel):
    code: str
    name: str
    category: KPICategory
    description: Optional[str] = None
    formula: Optional[str] = None
    unit: Optional[str] = None
    is_good_when_higher: bool = True
    is_active: bool = True

class KPIDefinitionResponse(KPIDefinitionBase):
    id: PyUUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class KPIResultBase(BaseModel):
    kpi_id: PyUUID
    value: Decimal
    trend: Optional[Decimal] = None
    metadata: Optional[Dict[str, Any]] = None

class KPIResultResponse(KPIResultBase):
    id: int
    calculation_date: date
    created_at: datetime
    
    class Config:
        from_attributes = True

class KPIValueResponse(BaseModel):
    """Resposta para valor atual de KPI com contexto"""
    kpi_id: PyUUID
    code: str
    name: str
    category: KPICategory
    value: Decimal
    unit: Optional[str]
    target: Optional[Decimal]
    trend: Optional[Decimal]
    is_good_when_higher: bool
    status: str  # "good", "warning", "critical"
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = None

class KPICategoryResponse(BaseModel):
    """Resposta agrupada por categoria"""
    category: KPICategory
    kpis: List[KPIValueResponse]
    summary: Dict[str, Any]  # Resumo da categoria

class KPIHistoryResponse(BaseModel):
    """Resposta para histórico de KPI"""
    date: date
    value: float
    trend: float
    metadata: Optional[Dict[str, Any]] = None

class KPICompanyConfigBase(BaseModel):
    kpi_id: PyUUID
    company_id: PyUUID
    target_value: Optional[Decimal] = None
    warning_threshold: Optional[Decimal] = None
    critical_threshold: Optional[Decimal] = None
    is_enabled: bool = True
    notification_settings: Optional[Dict[str, Any]] = None

class KPICompanyConfigResponse(KPICompanyConfigBase):
    id: PyUUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
