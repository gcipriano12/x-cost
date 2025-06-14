from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Text, Date, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum

Base = declarative_base()

# Enums para padronização
class ChargeCategory(str, Enum):
    USAGE = "Usage"
    PURCHASE = "Purchase"
    TAX = "Tax"
    CREDIT = "Credit"
    ADJUSTMENT = "Adjustment"

class ChargeFrequency(str, Enum):
    ONE_TIME = "One-Time"
    RECURRING = "Recurring"
    USAGE_BASED = "Usage-Based"

class PricingCategory(str, Enum):
    ON_DEMAND = "On-Demand"
    RESERVED = "Reserved"
    SPOT = "Spot"
    SAVINGS_PLAN = "Savings Plan"

class AnalysisType(str, Enum):
    TREND = "trend"
    DELTA = "delta"
    FORECAST = "forecast"
    BUDGET = "budget"

# SQLAlchemy Models
class CloudProvider(Base):
    __tablename__ = "cloud_providers"
    __table_args__ = {"schema": "finops"}
    
    id = Column(Integer, primary_key=True, index=True)
    provider_name = Column(String(50), unique=True, nullable=False, index=True)
    api_endpoint = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class FocusCostData(Base):
    __tablename__ = "focus_cost_data"
    __table_args__ = (
        Index('idx_billing_period', 'billing_period_start', 'billing_period_end'),
        Index('idx_provider_service', 'provider_name', 'service_name'),
        Index('idx_resource', 'resource_id', 'resource_type'),
        Index('idx_cost_date', 'charge_period_start', 'charge_period_end'),
        Index('idx_tags_gin', 'tags', postgresql_using='gin'),
        {"schema": "finops"}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    
    # FOCUS Core Dimensions
    billing_account_id = Column(String(255), index=True)
    billing_account_name = Column(String(255))
    billing_currency = Column(String(3), default="USD")
    billing_period_start = Column(Date, nullable=False, index=True)
    billing_period_end = Column(Date, nullable=False)
    charge_category = Column(String(50), index=True)
    charge_description = Column(Text)
    charge_frequency = Column(String(20))
    charge_period_start = Column(DateTime(timezone=True), index=True)
    charge_period_end = Column(DateTime(timezone=True))
    
    # Cost and Usage
    billed_cost = Column(Numeric(15, 4), default=0)
    effective_cost = Column(Numeric(15, 4), default=0, index=True)
    list_cost = Column(Numeric(15, 4), default=0)
    list_unit_price = Column(Numeric(15, 4))
    pricing_category = Column(String(50), index=True)
    pricing_quantity = Column(Numeric(15, 6))
    pricing_unit = Column(String(50))
    usage_quantity = Column(Numeric(15, 6))
    usage_unit = Column(String(50))
    
    # Provider Information
    provider_name = Column(String(50), ForeignKey("finops.cloud_providers.provider_name"), nullable=False, index=True)
    publisher_name = Column(String(100))
    service_category = Column(String(100), index=True)
    service_name = Column(String(100), nullable=False, index=True)
    
    # Resource Information
    resource_id = Column(String(255), index=True)
    resource_name = Column(String(255))
    resource_type = Column(String(100), index=True)
    availability_zone = Column(String(50))
    region = Column(String(50), index=True)
    
    # Invoice Information
    invoice_issuer_name = Column(String(100))
    
    # Metadata
    tags = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    data_source = Column(String(50))

class CostAnalysis(Base):
    __tablename__ = "cost_analysis"
    __table_args__ = {"schema": "finops"}
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(50), nullable=False, index=True)
    provider_name = Column(String(50), index=True)
    service_name = Column(String(100), index=True)
    resource_type = Column(String(100))
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Métricas calculadas
    total_cost = Column(Numeric(15, 4))
    average_daily_cost = Column(Numeric(15, 4))
    cost_trend = Column(Numeric(5, 2))  # Percentual
    cost_delta = Column(Numeric(15, 4))
    forecasted_cost = Column(Numeric(15, 4))
    
    # Metadados
    calculation_date = Column(DateTime(timezone=True), server_default=func.now())
    tags = Column(JSONB)

class Budget(Base):
    __tablename__ = "budgets"
    __table_args__ = {"schema": "finops"}
    
    id = Column(Integer, primary_key=True, index=True)
    budget_name = Column(String(100), nullable=False)
    provider_name = Column(String(50))
    service_name = Column(String(100))
    budget_amount = Column(Numeric(15, 4), nullable=False)
    budget_period = Column(String(20), default="monthly")
    alert_threshold = Column(Numeric(5, 2), default=80.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    tags = Column(JSONB)

# Pydantic Models (para API)
class FocusCostDataBase(BaseModel):
    billing_account_id: Optional[str] = None
    billing_account_name: Optional[str] = None
    billing_currency: str = "USD"
    billing_period_start: date
    billing_period_end: date
    charge_category: Optional[ChargeCategory] = None
    charge_description: Optional[str] = None
    charge_frequency: Optional[ChargeFrequency] = None
    charge_period_start: Optional[datetime] = None
    charge_period_end: Optional[datetime] = None
    
    billed_cost: Optional[Decimal] = Field(default=0, decimal_places=4)
    effective_cost: Optional[Decimal] = Field(default=0, decimal_places=4)
    list_cost: Optional[Decimal] = Field(default=0, decimal_places=4)
    list_unit_price: Optional[Decimal] = Field(default=None, decimal_places=4)
    pricing_category: Optional[PricingCategory] = None
    pricing_quantity: Optional[Decimal] = Field(default=None, decimal_places=6)
    pricing_unit: Optional[str] = None
    usage_quantity: Optional[Decimal] = Field(default=None, decimal_places=6)
    usage_unit: Optional[str] = None
    
    provider_name: str
    publisher_name: Optional[str] = None
    service_category: Optional[str] = None
    service_name: str
    
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    availability_zone: Optional[str] = None
    region: Optional[str] = None
    
    invoice_issuer_name: Optional[str] = None
    tags: Optional[Dict[str, Any]] = {}
    data_source: Optional[str] = None

class FocusCostDataCreate(FocusCostDataBase):
    pass

class FocusCostDataResponse(FocusCostDataBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CostAnalysisBase(BaseModel):
    analysis_type: AnalysisType
    provider_name: Optional[str] = None
    service_name: Optional[str] = None
    resource_type: Optional[str] = None
    period_start: date
    period_end: date
    total_cost: Optional[Decimal] = Field(default=None, decimal_places=4)
    average_daily_cost: Optional[Decimal] = Field(default=None, decimal_places=4)
    cost_trend: Optional[Decimal] = Field(default=None, decimal_places=2)
    cost_delta: Optional[Decimal] = Field(default=None, decimal_places=4)
    forecasted_cost: Optional[Decimal] = Field(default=None, decimal_places=4)
    tags: Optional[Dict[str, Any]] = {}

class CostAnalysisResponse(CostAnalysisBase):
    id: int
    calculation_date: datetime
    
    class Config:
        from_attributes = True

class BudgetBase(BaseModel):
    budget_name: str
    provider_name: Optional[str] = None
    service_name: Optional[str] = None
    budget_amount: Decimal = Field(decimal_places=4)
    budget_period: str = "monthly"
    alert_threshold: Decimal = Field(default=80.0, decimal_places=2)
    is_active: bool = True
    tags: Optional[Dict[str, Any]] = {}

class BudgetCreate(BudgetBase):
    pass

class BudgetResponse(BudgetBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response Models para API
class CostSummary(BaseModel):
    provider_name: str
    service_name: str
    period_start: date
    period_end: date
    total_cost: Decimal
    record_count: int

class CostTrend(BaseModel):
    date: date
    cost: Decimal
    trend_percentage: Optional[Decimal] = None

class CostByTag(BaseModel):
    tag_key: str
    tag_value: str
    total_cost: Decimal
    percentage_of_total: Decimal

class MonthlyCostResponse(BaseModel):
    provider_name: str
    service_name: str
    month: date
    total_cost: Decimal
    avg_cost: Decimal
    record_count: int

class CostForecast(BaseModel):
    provider_name: str
    service_name: Optional[str] = None
    forecast_date: date
    forecasted_cost: Decimal
    confidence_interval: Dict[str, Decimal]
    model_accuracy: Optional[Decimal] = None

# Query Parameters
class CostQueryParams(BaseModel):
    provider_name: Optional[str] = None
    service_name: Optional[str] = None
    resource_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    tags: Optional[Dict[str, str]] = {}
    limit: int = Field(default=100, ge=1, le=10000)
    offset: int = Field(default=0, ge=0)

class AnalysisQueryParams(BaseModel):
    analysis_type: Optional[AnalysisType] = None
    provider_name: Optional[str] = None
    service_name: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)

# Dashboard Models
class DashboardMetrics(BaseModel):
    total_cost: Decimal
    cost_change_percentage: Decimal
    monthly_average: Decimal
    top_service: Dict[str, Any]
    annual_projection: Decimal
    budget_consumption: Optional[Dict[str, Any]] = None

class ProviderDistribution(BaseModel):
    provider_name: str
    total_cost: Decimal
    percentage: Decimal
    cost_change: Optional[Decimal] = None

class DashboardHighlights(BaseModel):
    next_month_forecast: Dict[str, Any]
    estimated_waste: Dict[str, Any]
    savings_achieved: Dict[str, Any]

class DashboardSummary(BaseModel):
    metrics: DashboardMetrics
    provider_distribution: List[ProviderDistribution]
    highlights: DashboardHighlights
    generated_at: datetime
    period: Dict[str, Any]