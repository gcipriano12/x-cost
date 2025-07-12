# Backend - Implementação do Sistema de KPIs

## 📋 Visão Geral

Implementar sistema completo de KPIs para X Cost, permitindo configuração, cálculo e visualização de métricas avançadas de FinOps.

## 🏗️ Arquitetura Proposta

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Cloud APIs    │────▶│  KPI Calculator  │────▶│   KPI Storage   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                          │
         ▼                       ▼                          ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Resource Data   │     │  KPI Service     │     │    KPI APIs     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

## 📁 Estrutura de Arquivos

```
backend/app/
├── kpi/
│   ├── __init__.py
│   ├── models.py          # Modelos de KPIs
│   ├── calculator.py      # Lógica de cálculo
│   ├── service.py         # Serviço principal
│   └── collectors/        # Coletores de dados
│       ├── resource_collector.py
│       ├── compliance_collector.py
│       └── commitment_collector.py
├── routers/
│   └── kpi_api.py         # Endpoints REST
└── migrations/
    └── add_kpi_tables.sql # DDL das tabelas
```

## 🗄️ Modelo de Dados

### 1. Tabela de Definições de KPIs

```sql
-- Tabela principal de definições de KPIs
CREATE TABLE finops.kpi_definitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(20) NOT NULL CHECK (category IN ('efficiency', 'pricing', 'planning', 'governance')),
    description TEXT,
    formula TEXT,
    unit VARCHAR(20),
    target_value DECIMAL(15,4),
    is_good_when_higher BOOLEAN DEFAULT true,
    calculation_frequency VARCHAR(20) DEFAULT 'daily',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de resultados calculados
CREATE TABLE finops.kpi_results (
    id BIGSERIAL PRIMARY KEY,
    kpi_id UUID REFERENCES finops.kpi_definitions(id),
    calculation_date DATE NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    trend DECIMAL(5,2), -- Percentual de mudança
    metadata JSONB, -- Dados adicionais do cálculo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(kpi_id, calculation_date)
);

-- Tabela de configurações por empresa
CREATE TABLE finops.kpi_company_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_id UUID REFERENCES finops.kpi_definitions(id),
    company_id UUID NOT NULL, -- Referência futura para multi-tenant
    target_value DECIMAL(15,4),
    warning_threshold DECIMAL(15,4),
    critical_threshold DECIMAL(15,4),
    is_enabled BOOLEAN DEFAULT true,
    notification_settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(kpi_id, company_id)
);

-- Índices para performance
CREATE INDEX idx_kpi_results_date ON finops.kpi_results(calculation_date DESC);
CREATE INDEX idx_kpi_results_kpi_date ON finops.kpi_results(kpi_id, calculation_date DESC);
```

### 2. Dados Iniciais de KPIs

```sql
-- Inserir definições padrão de KPIs
INSERT INTO finops.kpi_definitions (code, name, category, description, formula, unit, target_value, is_good_when_higher) VALUES
-- Efficiency
('resource_utilization_rate', 'Resource Utilization Rate', 'efficiency', 
 'Percentual de recursos provisionados que estão sendo efetivamente utilizados', 
 '(consumed_capacity / allocated_capacity) * 100', '%', 75, true),

('cloud_waste_percentage', 'Cloud Waste Percentage', 'efficiency',
 'Percentual do gasto em recursos ociosos ou subutilizados',
 '(idle_resource_cost / total_cloud_spend) * 100', '%', 15, false),

('power_schedule_adherence', 'Power Schedule Adherence Rate', 'efficiency',
 'Aderência ao agendamento de liga/desliga de recursos não-produtivos',
 '(scheduled_hours / total_hours) * 100', '%', 95, true),

('legacy_resources_percentage', 'Legacy Resources Percentage', 'efficiency',
 'Percentual de recursos em gerações antigas menos eficientes',
 '(legacy_instance_count / total_instances) * 100', '%', 20, false),

-- Pricing
('effective_savings_rate', 'Effective Savings Rate (ESR)', 'pricing',
 'Taxa de economia real comparada com preços on-demand',
 '(total_savings / on_demand_equivalent) * 100', '%', 30, true),

('commitment_discount_waste', 'Commitment Discount Waste', 'pricing',
 'Percentual de commitments não utilizados',
 '(unused_commitment_cost / total_commitment_cost) * 100', '%', 10, false),

('compute_covered_by_commitments', 'Compute Covered by Commitments', 'pricing',
 'Cobertura de instâncias por reservas ou savings plans',
 '(committed_compute_cost / total_compute_cost) * 100', '%', 80, true),

('cost_per_vcpu_hour', 'Cost per vCPU/GPU Hour', 'pricing',
 'Custo normalizado por unidade de computação',
 'total_compute_cost / total_vcpu_hours', '$/h', 0.35, false),

-- Planning
('budget_forecast_variation', 'Budget vs. Forecast Variation', 'planning',
 'Variação entre orçamento e previsão',
 'ABS((budget - forecast) / budget) * 100', '%', 5, false),

('cloud_spend_variation', 'Cloud Spend Variation', 'planning',
 'Variação do gasto real vs orçado',
 '((actual - budget) / budget) * 100', '%', 7, false),

('forecast_accuracy_rate', 'Forecast Accuracy Rate', 'planning',
 'Precisão das previsões de custo',
 '(1 - ABS(forecast - actual) / actual) * 100', '%', 90, true),

-- Governance
('unallocated_cost_percentage', 'Unallocated Cost Percentage', 'governance',
 'Percentual de custos sem alocação ou tags',
 '(untagged_cost / total_cost) * 100', '%', 5, false),

('tag_compliance_rate', 'Tag Policy Compliance Rate', 'governance',
 'Aderência às políticas de tagging',
 '(compliant_resources / total_resources) * 100', '%', 95, true),

('anomaly_detection_savings', 'Anomaly Detection Savings', 'governance',
 'Economias realizadas através de detecção de anomalias',
 'SUM(anomaly_prevented_cost)', '$', 50000, true);
```

## 🐍 Modelos Python

### models.py

```python
"""
KPI Models - X Cost
Modelos para o sistema de Key Performance Indicators
"""

from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, Numeric, ForeignKey, JSON, Enum as SQLEnum
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
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    category = Column(SQLEnum(KPICategory), nullable=False, index=True)
    description = Column(Text)
    formula = Column(Text)
    unit = Column(String(20))
    target_value = Column(Numeric(15, 4))
    is_good_when_higher = Column(Boolean, default=True)
    calculation_frequency = Column(String(20), default="daily")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")
    
    # Relationships
    results = relationship("KPIResult", back_populates="definition")
    company_configs = relationship("KPICompanyConfig", back_populates="definition")

class KPIResult(Base):
    __tablename__ = "kpi_results"
    __table_args__ = {"schema": "finops"}
    
    id = Column(Integer, primary_key=True)
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("finops.kpi_definitions.id"), nullable=False)
    calculation_date = Column(DateTime, nullable=False, index=True)
    value = Column(Numeric(15, 4), nullable=False)
    trend = Column(Numeric(5, 2))
    metadata = Column(JSONB)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    
    # Relationships
    definition = relationship("KPIDefinition", back_populates="results")

class KPICompanyConfig(Base):
    __tablename__ = "kpi_company_configs"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    kpi_id = Column(UUID(as_uuid=True), ForeignKey("finops.kpi_definitions.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), nullable=False)  # Para futuro multi-tenant
    target_value = Column(Numeric(15, 4))
    warning_threshold = Column(Numeric(15, 4))
    critical_threshold = Column(Numeric(15, 4))
    is_enabled = Column(Boolean, default=True)
    notification_settings = Column(JSONB)
    created_at = Column(DateTime, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(DateTime, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")
    
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
    target_value: Optional[Decimal] = None
    is_good_when_higher: bool = True
    calculation_frequency: CalculationFrequency = CalculationFrequency.DAILY
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
    calculation_date: datetime
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
```

## 🧮 Calculadora de KPIs

### calculator.py

```python
"""
KPI Calculator - X Cost
Motor de cálculo para Key Performance Indicators
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, text

from app.models import FocusCostData
from app.kpi.models import KPIDefinition, KPIResult, KPICategory
from app.kpi.collectors import (
    ResourceUtilizationCollector,
    ComplianceCollector,
    CommitmentCollector
)
from app.virtual_tags_models import VirtualTagAllocation

logger = logging.getLogger(__name__)

class KPICalculator:
    """Calculadora principal de KPIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.resource_collector = ResourceUtilizationCollector(db)
        self.compliance_collector = ComplianceCollector(db)
        self.commitment_collector = CommitmentCollector(db)
        
    def calculate_all_kpis(self, calculation_date: date) -> Dict[str, Any]:
        """Calcula todos os KPIs ativos para uma data"""
        results = {}
        
        # Buscar KPIs ativos
        active_kpis = self.db.query(KPIDefinition).filter(
            KPIDefinition.is_active == True
        ).all()
        
        for kpi in active_kpis:
            try:
                value = self._calculate_kpi(kpi, calculation_date)
                if value is not None:
                    # Calcular tendência
                    trend = self._calculate_trend(kpi.id, value, calculation_date)
                    
                    # Salvar resultado
                    self._save_result(kpi.id, calculation_date, value, trend)
                    
                    results[kpi.code] = {
                        'value': value,
                        'trend': trend,
                        'status': self._get_status(kpi, value)
                    }
                    
            except Exception as e:
                logger.error(f"Error calculating KPI {kpi.code}: {str(e)}")
                
        return results
    
    def _calculate_kpi(self, kpi: KPIDefinition, calculation_date: date) -> Optional[Decimal]:
        """Calcula um KPI específico"""
        
        # Mapear código do KPI para método de cálculo
        calculation_methods = {
            # Efficiency
            'resource_utilization_rate': self._calc_resource_utilization,
            'cloud_waste_percentage': self._calc_cloud_waste,
            'power_schedule_adherence': self._calc_power_schedule,
            'legacy_resources_percentage': self._calc_legacy_resources,
            
            # Pricing
            'effective_savings_rate': self._calc_effective_savings,
            'commitment_discount_waste': self._calc_commitment_waste,
            'compute_covered_by_commitments': self._calc_compute_coverage,
            'cost_per_vcpu_hour': self._calc_cost_per_vcpu,
            
            # Planning
            'budget_forecast_variation': self._calc_budget_forecast_variation,
            'cloud_spend_variation': self._calc_cloud_spend_variation,
            'forecast_accuracy_rate': self._calc_forecast_accuracy,
            
            # Governance
            'unallocated_cost_percentage': self._calc_unallocated_cost,
            'tag_compliance_rate': self._calc_tag_compliance,
            'anomaly_detection_savings': self._calc_anomaly_savings
        }
        
        calc_method = calculation_methods.get(kpi.code)
        if calc_method:
            return calc_method(calculation_date)
        
        return None
    
    # ===== EFFICIENCY KPIs =====
    
    def _calc_resource_utilization(self, calc_date: date) -> Decimal:
        """Calcula taxa de utilização de recursos"""
        utilization_data = self.resource_collector.get_utilization_metrics(
            start_date=calc_date - timedelta(days=7),
            end_date=calc_date
        )
        
        if not utilization_data:
            return Decimal('0')
            
        total_allocated = sum(d.get('allocated_capacity', 0) for d in utilization_data)
        total_consumed = sum(d.get('consumed_capacity', 0) for d in utilization_data)
        
        if total_allocated == 0:
            return Decimal('0')
            
        return Decimal(str((total_consumed / total_allocated) * 100))
    
    def _calc_cloud_waste(self, calc_date: date) -> Decimal:
        """Calcula percentual de desperdício na nuvem"""
        # Buscar recursos identificados como ociosos
        idle_resources = self.resource_collector.identify_idle_resources(
            threshold_days=7,
            as_of_date=calc_date
        )
        
        # Calcular custo dos recursos ociosos
        idle_cost = sum(r.get('monthly_cost', 0) for r in idle_resources)
        
        # Buscar custo total do período
        total_cost = self.db.query(
            func.sum(FocusCostData.effective_cost)
        ).filter(
            FocusCostData.billing_period_start == calc_date.replace(day=1)
        ).scalar() or 0
        
        if total_cost == 0:
            return Decimal('0')
            
        return Decimal(str((idle_cost / float(total_cost)) * 100))
    
    def _calc_power_schedule(self, calc_date: date) -> Decimal:
        """Calcula aderência ao power scheduling"""
        schedule_data = self.resource_collector.get_power_schedule_metrics(
            date=calc_date
        )
        
        if not schedule_data:
            return Decimal('100')  # Assume 100% se não há dados
            
        total_scheduled_hours = schedule_data.get('total_scheduled_hours', 0)
        actual_runtime_hours = schedule_data.get('actual_runtime_hours', 0)
        
        if total_scheduled_hours == 0:
            return Decimal('100')
            
        adherence = min(100, (actual_runtime_hours / total_scheduled_hours) * 100)
        return Decimal(str(adherence))
    
    def _calc_legacy_resources(self, calc_date: date) -> Decimal:
        """Calcula percentual de recursos legacy"""
        legacy_data = self.resource_collector.identify_legacy_resources(
            as_of_date=calc_date
        )
        
        total_instances = legacy_data.get('total_instances', 0)
        legacy_instances = legacy_data.get('legacy_instances', 0)
        
        if total_instances == 0:
            return Decimal('0')
            
        return Decimal(str((legacy_instances / total_instances) * 100))
    
    # ===== PRICING KPIs =====
    
    def _calc_effective_savings(self, calc_date: date) -> Decimal:
        """Calcula taxa efetiva de economia"""
        commitment_data = self.commitment_collector.get_savings_summary(
            start_date=calc_date.replace(day=1),
            end_date=calc_date
        )
        
        on_demand_equivalent = commitment_data.get('on_demand_equivalent', 0)
        actual_cost = commitment_data.get('actual_cost', 0)
        
        if on_demand_equivalent == 0:
            return Decimal('0')
            
        savings = on_demand_equivalent - actual_cost
        return Decimal(str((savings / on_demand_equivalent) * 100))
    
    def _calc_commitment_waste(self, calc_date: date) -> Decimal:
        """Calcula desperdício de commitments"""
        waste_data = self.commitment_collector.get_commitment_utilization(
            as_of_date=calc_date
        )
        
        total_commitment_cost = waste_data.get('total_commitment_cost', 0)
        unused_commitment_cost = waste_data.get('unused_commitment_cost', 0)
        
        if total_commitment_cost == 0:
            return Decimal('0')
            
        return Decimal(str((unused_commitment_cost / total_commitment_cost) * 100))
    
    def _calc_compute_coverage(self, calc_date: date) -> Decimal:
        """Calcula cobertura de compute por commitments"""
        coverage_data = self.commitment_collector.get_compute_coverage(
            date=calc_date
        )
        
        total_compute_cost = coverage_data.get('total_compute_cost', 0)
        committed_compute_cost = coverage_data.get('committed_compute_cost', 0)
        
        if total_compute_cost == 0:
            return Decimal('0')
            
        return Decimal(str((committed_compute_cost / total_compute_cost) * 100))
    
    def _calc_cost_per_vcpu(self, calc_date: date) -> Decimal:
        """Calcula custo por vCPU/hora"""
        # Este cálculo requer dados de utilização detalhados
        vcpu_data = self.resource_collector.get_vcpu_metrics(
            date=calc_date
        )
        
        total_compute_cost = vcpu_data.get('total_compute_cost', 0)
        total_vcpu_hours = vcpu_data.get('total_vcpu_hours', 1)  # Evitar divisão por zero
        
        return Decimal(str(total_compute_cost / total_vcpu_hours))
    
    # ===== PLANNING KPIs =====
    
    def _calc_budget_forecast_variation(self, calc_date: date) -> Decimal:
        """Calcula variação entre budget e forecast"""
        # Buscar dados de budget e forecast
        from app.cost_analytics import CostAnalyzer
        
        analyzer = CostAnalyzer(self.db)
        
        # Obter forecast para o mês atual
        forecast_data = analyzer.forecast_costs(
            forecast_days=30,
            historical_days=90
        )
        
        # Buscar budget do mês
        from app.models import Budget
        current_budget = self.db.query(Budget).filter(
            and_(
                Budget.period_start <= calc_date,
                Budget.period_end >= calc_date,
                Budget.is_active == True
            )
        ).first()
        
        if not current_budget or not forecast_data:
            return Decimal('0')
            
        budget_amount = float(current_budget.budget_amount)
        forecast_amount = forecast_data.get('total_forecasted_cost', 0)
        
        if budget_amount == 0:
            return Decimal('0')
            
        variation = abs((budget_amount - forecast_amount) / budget_amount) * 100
        return Decimal(str(variation))
    
    def _calc_cloud_spend_variation(self, calc_date: date) -> Decimal:
        """Calcula variação do gasto real vs orçado"""
        # Buscar gasto real do mês
        actual_spend = self.db.query(
            func.sum(FocusCostData.effective_cost)
        ).filter(
            FocusCostData.billing_period_start == calc_date.replace(day=1)
        ).scalar() or 0
        
        # Buscar budget
        from app.models import Budget
        current_budget = self.db.query(Budget).filter(
            and_(
                Budget.period_start <= calc_date,
                Budget.period_end >= calc_date,
                Budget.is_active == True
            )
        ).first()
        
        if not current_budget:
            return Decimal('0')
            
        budget_amount = float(current_budget.budget_amount)
        
        if budget_amount == 0:
            return Decimal('0')
            
        variation = ((float(actual_spend) - budget_amount) / budget_amount) * 100
        return Decimal(str(variation))
    
    def _calc_forecast_accuracy(self, calc_date: date) -> Decimal:
        """Calcula precisão do forecast"""
        # Este KPI precisa comparar forecast anterior com real
        # Por enquanto, retornar valor mock
        # TODO: Implementar histórico de forecasts
        return Decimal('84')
    
    # ===== GOVERNANCE KPIs =====
    
    def _calc_unallocated_cost(self, calc_date: date) -> Decimal:
        """Calcula percentual de custos não alocados"""
        # Buscar custos sem tags essenciais
        untagged_query = self.db.query(
            func.sum(FocusCostData.effective_cost)
        ).filter(
            and_(
                FocusCostData.billing_period_start == calc_date.replace(day=1),
                or_(
                    FocusCostData.tags == None,
                    text("NOT (tags ? 'project' AND tags ? 'environment' AND tags ? 'owner')")
                )
            )
        )
        
        untagged_cost = untagged_query.scalar() or 0
        
        # Custo total
        total_cost = self.db.query(
            func.sum(FocusCostData.effective_cost)
        ).filter(
            FocusCostData.billing_period_start == calc_date.replace(day=1)
        ).scalar() or 0
        
        if total_cost == 0:
            return Decimal('0')
            
        # Considerar também Virtual Tags
        virtual_tagged_cost = self.db.query(
            func.sum(VirtualTagAllocation.allocated_cost)
        ).filter(
            VirtualTagAllocation.allocation_date == calc_date.replace(day=1)
        ).scalar() or 0
        
        actually_unallocated = float(untagged_cost) - float(virtual_tagged_cost)
        
        return Decimal(str(max(0, (actually_unallocated / float(total_cost)) * 100)))
    
    def _calc_tag_compliance(self, calc_date: date) -> Decimal:
        """Calcula taxa de compliance de tags"""
        compliance_data = self.compliance_collector.get_tag_compliance_metrics(
            date=calc_date
        )
        
        total_resources = compliance_data.get('total_resources', 0)
        compliant_resources = compliance_data.get('compliant_resources', 0)
        
        if total_resources == 0:
            return Decimal('100')
            
        return Decimal(str((compliant_resources / total_resources) * 100))
    
    def _calc_anomaly_savings(self, calc_date: date) -> Decimal:
        """Calcula economias por detecção de anomalias"""
        # Buscar anomalias detectadas e ações tomadas
        from app.cost_analytics import CostAnalyzer
        
        analyzer = CostAnalyzer(self.db)
        anomalies = analyzer.calculate_anomalies(
            lookback_days=30,
            threshold_std=2.0
        )
        
        # Somar economias estimadas
        # Por enquanto, usar cálculo simplificado
        total_savings = sum(
            a.get('deviation', 0) * 0.7  # 70% do desvio como economia
            for a in anomalies 
            if a.get('type') == 'spike' and a.get('action_taken', False)
        )
        
        return Decimal(str(total_savings))
    
    def _calculate_trend(self, kpi_id: str, current_value: Decimal, calc_date: date) -> Decimal:
        """Calcula tendência comparando com período anterior"""
        # Buscar valor do período anterior
        previous_result = self.db.query(KPIResult).filter(
            and_(
                KPIResult.kpi_id == kpi_id,
                KPIResult.calculation_date < calc_date
            )
        ).order_by(KPIResult.calculation_date.desc()).first()
        
        if not previous_result:
            return Decimal('0')
            
        previous_value = previous_result.value
        
        if previous_value == 0:
            return Decimal('0')
            
        trend = ((current_value - previous_value) / previous_value) * 100
        return Decimal(str(trend))
    
    def _save_result(self, kpi_id: str, calc_date: date, value: Decimal, trend: Decimal):
        """Salva resultado do KPI no banco"""
        # Verificar se já existe resultado para esta data
        existing = self.db.query(KPIResult).filter(
            and_(
                KPIResult.kpi_id == kpi_id,
                KPIResult.calculation_date == calc_date
            )
        ).first()
        
        if existing:
            existing.value = value
            existing.trend = trend
            existing.metadata = {'updated_at': datetime.utcnow().isoformat()}
        else:
            result = KPIResult(
                kpi_id=kpi_id,
                calculation_date=calc_date,
                value=value,
                trend=trend,
                metadata={'calculated_at': datetime.utcnow().isoformat()}
            )
            self.db.add(result)
            
        self.db.commit()
    
    def _get_status(self, kpi: KPIDefinition, value: Decimal) -> str:
        """Determina status do KPI baseado no valor e target"""
        if not kpi.target_value:
            return 'neutral'
            
        target = float(kpi.target_value)
        current = float(value)
        
        # Buscar configuração específica da empresa (se existir)
        # Por enquanto, usar lógica simples
        
        if kpi.is_good_when_higher:
            if current >= target:
                return 'good'
            elif current >= target * 0.8:
                return 'warning'
            else:
                return 'critical'
        else:
            if current <= target:
                return 'good'
            elif current <= target * 1.2:
                return 'warning'
            else:
                return 'critical'
```

## 🔄 Serviço de KPIs

### service.py

```python
"""
KPI Service - X Cost
Serviço principal para gerenciamento de KPIs
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.kpi.models import (
    KPIDefinition, KPIResult, KPICompanyConfig,
    KPICategory, KPIValueResponse, KPICategoryResponse
)
from app.kpi.calculator import KPICalculator
from app.database import cache_manager

logger = logging.getLogger(__name__)

class KPIService:
    """Serviço principal de KPIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.calculator = KPICalculator(db)
        self.cache = cache_manager
        
    def get_current_kpis(self, category: Optional[KPICategory] = None) -> List[KPIValueResponse]:
        """Obtém valores atuais de todos os KPIs"""
        cache_key = f"kpis:current:{category or 'all'}"
        
        # Tentar cache primeiro
        cached = self.cache.get(cache_key)
        if cached:
            return cached
            
        # Buscar KPIs
        query = self.db.query(KPIDefinition).filter(
            KPIDefinition.is_active == True
        )
        
        if category:
            query = query.filter(KPIDefinition.category == category)
            
        kpis = query.all()
        
        # Buscar últimos resultados
        results = []
        for kpi in kpis:
            # Buscar último resultado
            last_result = self.db.query(KPIResult).filter(
                KPIResult.kpi_id == kpi.id
            ).order_by(KPIResult.calculation_date.desc()).first()
            
            if last_result:
                results.append(KPIValueResponse(
                    kpi_id=kpi.id,
                    code=kpi.code,
                    name=kpi.name,
                    category=kpi.category,
                    value=last_result.value,
                    unit=kpi.unit,
                    target=kpi.target_value,
                    trend=last_result.trend,
                    is_good_when_higher=kpi.is_good_when_higher,
                    status=self.calculator._get_status(kpi, last_result.value),
                    last_updated=last_result.calculation_date,
                    metadata=last_result.metadata
                ))
            else:
                # Se não há resultado, calcular agora
                value = self.calculator._calculate_kpi(kpi, date.today())
                if value is not None:
                    results.append(KPIValueResponse(
                        kpi_id=kpi.id,
                        code=kpi.code,
                        name=kpi.name,
                        category=kpi.category,
                        value=value,
                        unit=kpi.unit,
                        target=kpi.target_value,
                        trend=0,
                        is_good_when_higher=kpi.is_good_when_higher,
                        status=self.calculator._get_status(kpi, value),
                        last_updated=datetime.utcnow(),
                        metadata={}
                    ))
        
        # Cachear por 5 minutos
        self.cache.set(cache_key, results, expire=300)
        
        return results
    
    def get_kpis_by_category(self) -> List[KPICategoryResponse]:
        """Obtém KPIs agrupados por categoria"""
        categories = []
        
        for category in KPICategory:
            kpis = self.get_current_kpis(category=category)
            
            if kpis:
                # Calcular resumo da categoria
                summary = self._calculate_category_summary(kpis)
                
                categories.append(KPICategoryResponse(
                    category=category,
                    kpis=kpis,
                    summary=summary
                ))
                
        return categories
    
    def calculate_kpis(self, calculation_date: Optional[date] = None) -> Dict[str, Any]:
        """Executa cálculo de todos os KPIs"""
        if not calculation_date:
            calculation_date = date.today()
            
        results = self.calculator.calculate_all_kpis(calculation_date)
        
        # Invalidar cache
        self.cache.delete_pattern("kpis:*")
        
        return {
            'calculation_date': calculation_date,
            'results': results,
            'success_count': len([r for r in results.values() if r.get('value') is not None]),
            'error_count': len(results) - len([r for r in results.values() if r.get('value') is not None])
        }
    
    def get_kpi_history(
        self, 
        kpi_code: str, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Obtém histórico de um KPI"""
        # Buscar definição
        kpi = self.db.query(KPIDefinition).filter(
            KPIDefinition.code == kpi_code
        ).first()
        
        if not kpi:
            return []
            
        # Buscar resultados
        results = self.db.query(KPIResult).filter(
            and_(
                KPIResult.kpi_id == kpi.id,
                KPIResult.calculation_date >= start_date,
                KPIResult.calculation_date <= end_date
            )
        ).order_by(KPIResult.calculation_date).all()
        
        return [
            {
                'date': r.calculation_date,
                'value': float(r.value),
                'trend': float(r.trend) if r.trend else 0,
                'metadata': r.metadata
            }
            for r in results
        ]
    
    def update_kpi_config(
        self,
        kpi_code: str,
        company_id: str,
        target_value: Optional[float] = None,
        warning_threshold: Optional[float] = None,
        critical_threshold: Optional[float] = None
    ) -> KPICompanyConfig:
        """Atualiza configuração de KPI para empresa"""
        # Buscar KPI
        kpi = self.db.query(KPIDefinition).filter(
            KPIDefinition.code == kpi_code
        ).first()
        
        if not kpi:
            raise ValueError(f"KPI {kpi_code} not found")
            
        # Buscar ou criar config
        config = self.db.query(KPICompanyConfig).filter(
            and_(
                KPICompanyConfig.kpi_id == kpi.id,
                KPICompanyConfig.company_id == company_id
            )
        ).first()
        
        if not config:
            config = KPICompanyConfig(
                kpi_id=kpi.id,
                company_id=company_id
            )
            self.db.add(config)
            
        # Atualizar valores
        if target_value is not None:
            config.target_value = target_value
        if warning_threshold is not None:
            config.warning_threshold = warning_threshold
        if critical_threshold is not None:
            config.critical_threshold = critical_threshold
            
        self.db.commit()
        
        return config
    
    def _calculate_category_summary(self, kpis: List[KPIValueResponse]) -> Dict[str, Any]:
        """Calcula resumo de uma categoria de KPIs"""
        total = len(kpis)
        good = len([k for k in kpis if k.status == 'good'])
        warning = len([k for k in kpis if k.status == 'warning'])
        critical = len([k for k in kpis if k.status == 'critical'])
        
        # Calcular score geral (0-100)
        score = (good / total * 100) if total > 0 else 0
        
        # Trend médio
        avg_trend = sum(k.trend or 0 for k in kpis) / total if total > 0 else 0
        
        return {
            'total_kpis': total,
            'status_distribution': {
                'good': good,
                'warning': warning,
                'critical': critical
            },
            'health_score': round(score, 1),
            'average_trend': round(avg_trend, 2)
        }
```

## 🌐 API Endpoints

### routers/kpi_api.py

```python
"""
KPI API Router - X Cost
Endpoints para Key Performance Indicators
"""

import logging
from datetime import date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks

from app.database import get_database
from app.auth_security import get_current_active_user
from app.credential_models import User
from app.kpi.models import (
    KPICategory, KPIValueResponse, KPICategoryResponse,
    KPIDefinitionResponse
)
from app.kpi.service import KPIService
from app.utils.response_helpers import StandardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/kpis", tags=["KPIs"])

@router.get("/current", response_model=StandardResponse)
async def get_current_kpis(
    category: Optional[KPICategory] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém valores atuais dos KPIs
    
    - **category**: Filtrar por categoria (efficiency, pricing, planning, governance)
    """
    try:
        service = KPIService(db)
        kpis = service.get_current_kpis(category=category)
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(kpis)} KPIs",
            data={'kpis': kpis}
        )
        
    except Exception as e:
        logger.error(f"Error getting current KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-category", response_model=StandardResponse)
async def get_kpis_by_category(
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém KPIs agrupados por categoria com resumo
    """
    try:
        service = KPIService(db)
        categories = service.get_kpis_by_category()
        
        return StandardResponse(
            success=True,
            message="KPIs grouped by category",
            data={'categories': categories}
        )
        
    except Exception as e:
        logger.error(f"Error getting KPIs by category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{kpi_code}", response_model=StandardResponse)
async def get_kpi_history(
    kpi_code: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém histórico de um KPI específico
    
    - **kpi_code**: Código do KPI (ex: resource_utilization_rate)
    - **days**: Número de dias de histórico (padrão: 30)
    """
    try:
        service = KPIService(db)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        history = service.get_kpi_history(kpi_code, start_date, end_date)
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(history)} data points",
            data={
                'kpi_code': kpi_code,
                'period': {'start': start_date, 'end': end_date},
                'history': history
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting KPI history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate", response_model=StandardResponse)
async def calculate_kpis(
    background_tasks: BackgroundTasks,
    calculation_date: Optional[date] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Executa cálculo de KPIs (admin only)
    
    - **calculation_date**: Data para cálculo (padrão: hoje)
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = KPIService(db)
        
        # Executar em background para não bloquear
        background_tasks.add_task(
            service.calculate_kpis,
            calculation_date
        )
        
        return StandardResponse(
            success=True,
            message="KPI calculation started",
            data={'calculation_date': calculation_date or date.today()}
        )
        
    except Exception as e:
        logger.error(f"Error calculating KPIs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/config/{kpi_code}", response_model=StandardResponse)
async def update_kpi_config(
    kpi_code: str,
    target_value: Optional[float] = None,
    warning_threshold: Optional[float] = None,
    critical_threshold: Optional[float] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Atualiza configuração de KPI para a empresa (admin only)
    
    - **kpi_code**: Código do KPI
    - **target_value**: Novo valor alvo
    - **warning_threshold**: Limite para warning
    - **critical_threshold**: Limite para critical
    """
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
            
        service = KPIService(db)
        
        # Por enquanto, usar company_id fixo
        # TODO: Implementar multi-tenant
        company_id = "default-company"
        
        config = service.update_kpi_config(
            kpi_code=kpi_code,
            company_id=company_id,
            target_value=target_value,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        
        return StandardResponse(
            success=True,
            message="KPI configuration updated",
            data={'config': config}
        )
        
    except Exception as e:
        logger.error(f"Error updating KPI config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/definitions", response_model=StandardResponse)
async def get_kpi_definitions(
    category: Optional[KPICategory] = None,
    db: Session = Depends(get_database),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista todas as definições de KPIs disponíveis
    
    - **category**: Filtrar por categoria
    """
    try:
        query = db.query(KPIDefinition).filter(
            KPIDefinition.is_active == True
        )
        
        if category:
            query = query.filter(KPIDefinition.category == category)
            
        definitions = query.all()
        
        return StandardResponse(
            success=True,
            message=f"Retrieved {len(definitions)} KPI definitions",
            data={'definitions': definitions}
        )
        
    except Exception as e:
        logger.error(f"Error getting KPI definitions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

## 🔧 Integração com Main

### Adicionar ao main.py

```python
# Importar router de KPIs
from app.routers.kpi_api import router as kpi_router

# Registrar router
app.include_router(kpi_router)

# Adicionar job de cálculo periódico (opcional)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.kpi.service import KPIService

scheduler = AsyncIOScheduler()

async def calculate_daily_kpis():
    """Job para calcular KPIs diariamente"""
    async with db_manager.get_session() as db:
        service = KPIService(db)
        await service.calculate_kpis()

# Agendar para rodar todos os dias às 2AM
scheduler.add_job(
    calculate_daily_kpis,
    'cron',
    hour=2,
    minute=0
)

scheduler.start()
```

## 📊 Exemplo de Resposta da API

```json
{
  "success": true,
  "message": "KPIs grouped by category",
  "data": {
    "categories": [
      {
        "category": "efficiency",
        "kpis": [
          {
            "kpi_id": "123e4567-e89b-12d3-a456-426614174000",
            "code": "resource_utilization_rate",
            "name": "Resource Utilization Rate",
            "category": "efficiency",
            "value": 68.5,
            "unit": "%",
            "target": 75.0,
            "trend": 3.2,
            "is_good_when_higher": true,
            "status": "warning",
            "last_updated": "2024-01-15T10:30:00Z",
            "metadata": {
              "total_resources": 1250,
              "utilized_resources": 856
            }
          }
        ],
        "summary": {
          "total_kpis": 4,
          "status_distribution": {
            "good": 1,
            "warning": 2,
            "critical": 1
          },
          "health_score": 62.5,
          "average_trend": 2.8
        }
      }
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "processing_time_ms": 145
}
```

## 🎯 Próximos Passos Recomendados

1. **Implementar Coletores de Dados**
   - Integrar com APIs de cloud providers para dados de utilização
   - Coletar métricas de recursos (CPU, memória, storage)
   - Implementar análise de compliance de tags

2. **Configuração Inicial**
   - Criar interface para configurar metas por empresa
   - Permitir customização de fórmulas de cálculo
   - Definir alertas e notificações

3. **Otimizações**
   - Implementar cache distribuído
   - Criar views materializadas para queries complexas
   - Adicionar processamento assíncrono

4. **Expansão**
   - Adicionar novos KPIs conforme demanda
   - Implementar benchmarking entre empresas
   - Criar sistema de recomendações baseado em KPIs

# Frontend - Implementação da Visualização de KPIs

## 📋 Visão Geral

Implementar componentes React para exibição e gerenciamento dos KPIs no dashboard X Cost.

## 🏗️ Arquitetura de Componentes

```
src/
├── components/
│   ├── kpi/
│   │   ├── KPICard.tsx              # Card individual de KPI
│   │   ├── KPICategorySection.tsx   # Seção por categoria
│   │   ├── KPIIndicators.tsx        # Container principal
│   │   ├── KPIDetailModal.tsx       # Modal com detalhes
│   │   └── KPIConfigModal.tsx       # Modal de configuração
├── hooks/
│   └── useKPIs.ts                   # Hook para dados de KPIs
├── api/
│   └── kpiService.ts                # Serviço de API
└── types/
    └── kpi.types.ts                 # Tipos TypeScript
```

## 📝 Tipos TypeScript

### types/kpi.types.ts

```typescript
// Enums para categorias
export enum KPICategory {
  EFFICIENCY = 'efficiency',
  PRICING = 'pricing',
  PLANNING = 'planning',
  GOVERNANCE = 'governance'
}

// Status do KPI
export type KPIStatus = 'good' | 'warning' | 'critical' | 'neutral';

// Interface principal do KPI
export interface KPIValue {
  kpi_id: string;
  code: string;
  name: string;
  category: KPICategory;
  value: number;
  unit?: string;
  target?: number;
  trend?: number;
  is_good_when_higher: boolean;
  status: KPIStatus;
  last_updated: string;
  metadata?: Record<string, any>;
}

// Resposta agrupada por categoria
export interface KPICategoryResponse {
  category: KPICategory;
  kpis: KPIValue[];
  summary: {
    total_kpis: number;
    status_distribution: {
      good: number;
      warning: number;
      critical: number;
    };
    health_score: number;
    average_trend: number;
  };
}

// Configuração de KPI
export interface KPIConfig {
  kpi_id: string;
  target_value?: number;
  warning_threshold?: number;
  critical_threshold?: number;
  is_enabled: boolean;
}

// Mapeamento de cores por categoria
export const KPI_CATEGORY_COLORS: Record<KPICategory, string> = {
  [KPICategory.EFFICIENCY]: '#3b82f6', // blue
  [KPICategory.PRICING]: '#8b5cf6',    // purple
  [KPICategory.PLANNING]: '#f97316',   // orange
  [KPICategory.GOVERNANCE]: '#10b981'  // green
};

// Mapeamento de ícones por status
export const KPI_STATUS_ICONS = {
  good: 'CheckCircle',
  warning: 'AlertTriangle',
  critical: 'XCircle',
  neutral: 'Circle'
};
```

## 🔌 Serviço de API

### api/kpiService.ts

```typescript
import apiClient from '@/api/client';
import { KPIValue, KPICategoryResponse, KPIConfig, KPICategory } from '@/types/kpi.types';

class KPIService {
  private baseUrl = '/api/v1/kpis';

  /**
   * Obtém KPIs atuais
   */
  async getCurrentKPIs(category?: KPICategory): Promise<KPIValue[]> {
    const params = category ? { category } : undefined;
    const response = await apiClient.get(`${this.baseUrl}/current`, { params });
    return response.data.data.kpis;
  }

  /**
   * Obtém KPIs agrupados por categoria
   */
  async getKPIsByCategory(): Promise<KPICategoryResponse[]> {
    const response = await apiClient.get(`${this.baseUrl}/by-category`);
    return response.data.data.categories;
  }

  /**
   * Obtém histórico de um KPI
   */
  async getKPIHistory(kpiCode: string, days: number = 30) {
    const response = await apiClient.get(`${this.baseUrl}/history/${kpiCode}`, {
      params: { days }
    });
    return response.data.data;
  }

  /**
   * Atualiza configuração de KPI
   */
  async updateKPIConfig(kpiCode: string, config: Partial<KPIConfig>) {
    const response = await apiClient.put(`${this.baseUrl}/config/${kpiCode}`, config);
    return response.data.data;
  }

  /**
   * Força recálculo de KPIs (admin)
   */
  async calculateKPIs(date?: string) {
    const response = await apiClient.post(`${this.baseUrl}/calculate`, { 
      calculation_date: date 
    });
    return response.data;
  }
}

export default new KPIService();
```

## 🪝 Hook Customizado

### hooks/useKPIs.ts

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import kpiService from '@/api/kpiService';
import { KPICategory } from '@/types/kpi.types';
import { toast } from '@/components/ui/use-toast';

export const useKPIs = (category?: KPICategory) => {
  const queryClient = useQueryClient();
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);

  // Query para KPIs por categoria
  const {
    data: categorizedKPIs,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['kpis', 'categorized'],
    queryFn: () => kpiService.getKPIsByCategory(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000, // 10 minutos
  });

  // Query para histórico de KPI específico
  const {
    data: kpiHistory,
    isLoading: isLoadingHistory,
  } = useQuery({
    queryKey: ['kpi-history', selectedKPI],
    queryFn: () => selectedKPI ? kpiService.getKPIHistory(selectedKPI, 30) : null,
    enabled: !!selectedKPI,
  });

  // Mutation para atualizar configuração
  const updateConfig = useMutation({
    mutationFn: ({ kpiCode, config }: { kpiCode: string; config: any }) =>
      kpiService.updateKPIConfig(kpiCode, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kpis'] });
      toast({
        title: 'Configuração atualizada',
        description: 'As metas do KPI foram atualizadas com sucesso.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao atualizar',
        description: error.message || 'Ocorreu um erro ao atualizar a configuração.',
        variant: 'destructive',
      });
    },
  });

  // Mutation para recalcular KPIs
  const recalculate = useMutation({
    mutationFn: (date?: string) => kpiService.calculateKPIs(date),
    onSuccess: () => {
      toast({
        title: 'Recálculo iniciado',
        description: 'O recálculo dos KPIs foi iniciado em segundo plano.',
      });
      // Aguardar um pouco e recarregar
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['kpis'] });
      }, 3000);
    },
  });

  // Filtrar por categoria se especificado
  const filteredData = category && categorizedKPIs
    ? categorizedKPIs.filter(cat => cat.category === category)
    : categorizedKPIs;

  // Calcular estatísticas gerais
  const overallStats = categorizedKPIs?.reduce((acc, cat) => {
    acc.total += cat.summary.total_kpis;
    acc.good += cat.summary.status_distribution.good;
    acc.warning += cat.summary.status_distribution.warning;
    acc.critical += cat.summary.status_distribution.critical;
    return acc;
  }, { total: 0, good: 0, warning: 0, critical: 0 });

  return {
    categorizedKPIs: filteredData,
    overallStats,
    isLoading,
    error,
    refetch,
    selectedKPI,
    setSelectedKPI,
    kpiHistory,
    isLoadingHistory,
    updateConfig: updateConfig.mutate,
    recalculate: recalculate.mutate,
    isUpdating: updateConfig.isLoading,
    isRecalculating: recalculate.isLoading,
  };
};
```

## 🎨 Componentes React

### components/kpi/KPICard.tsx

```tsx
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Info,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Circle
} from 'lucide-react';
import { KPIValue, KPI_STATUS_ICONS } from '@/types/kpi.types';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';

interface KPICardProps {
  kpi: KPIValue;
  onClick?: () => void;
  compact?: boolean;
}

export const KPICard: React.FC<KPICardProps> = ({ kpi, onClick, compact = false }) => {
  const { isDark } = useTheme();
  
  // Ícone de status
  const StatusIcon = {
    good: CheckCircle,
    warning: AlertTriangle,
    critical: XCircle,
    neutral: Circle
  }[kpi.status];
  
  // Cor do status
  const statusColor = {
    good: 'text-green-500',
    warning: 'text-yellow-500',
    critical: 'text-red-500',
    neutral: 'text-gray-500'
  }[kpi.status];
  
  // Ícone de tendência
  const TrendIcon = kpi.trend && kpi.trend > 0 ? TrendingUp : 
                   kpi.trend && kpi.trend < 0 ? TrendingDown : Minus;
  
  // Cor da tendência baseada em is_good_when_higher
  const getTrendColor = () => {
    if (!kpi.trend || kpi.trend === 0) return 'text-gray-500';
    
    const isPositiveTrend = kpi.trend > 0;
    const isGoodTrend = kpi.is_good_when_higher ? isPositiveTrend : !isPositiveTrend;
    
    return isGoodTrend ? 'text-green-500' : 'text-red-500';
  };
  
  // Calcular progresso em relação ao target
  const progress = kpi.target ? (kpi.value / kpi.target) * 100 : 0;
  const progressCapped = Math.min(Math.max(progress, 0), 100);
  
  if (compact) {
    return (
      <div 
        className={cn(
          "flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors",
          isDark ? "hover:bg-gray-800" : "hover:bg-gray-100"
        )}
        onClick={onClick}
      >
        <div className="flex items-center gap-3">
          <StatusIcon className={cn("h-4 w-4", statusColor)} />
          <span className="text-sm font-medium">{kpi.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-mono">
            {kpi.value.toFixed(kpi.unit === '%' ? 1 : 2)}{kpi.unit}
          </span>
          <TrendIcon className={cn("h-4 w-4", getTrendColor())} />
        </div>
      </div>
    );
  }
  
  return (
    <Card 
      className={cn(
        "cursor-pointer transition-all hover:shadow-lg",
        isDark ? "hover:border-gray-600" : "hover:border-gray-300"
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <StatusIcon className={cn("h-5 w-5", statusColor)} />
            <h3 className="font-medium text-sm line-clamp-1">{kpi.name}</h3>
          </div>
          <Info className="h-4 w-4 text-gray-400" />
        </div>
        
        <div className="space-y-3">
          {/* Valor principal */}
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold">
              {kpi.value.toFixed(kpi.unit === '%' ? 1 : 2)}
            </span>
            <span className="text-sm text-gray-500">{kpi.unit}</span>
          </div>
          
          {/* Tendência */}
          <div className="flex items-center gap-2">
            <TrendIcon className={cn("h-4 w-4", getTrendColor())} />
            <span className={cn("text-sm", getTrendColor())}>
              {kpi.trend && kpi.trend > 0 ? '+' : ''}{kpi.trend?.toFixed(1)}%
            </span>
          </div>
          
          {/* Progresso em relação ao target */}
          {kpi.target && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-gray-500">
                <span>Target: {kpi.target}{kpi.unit}</span>
                <span>{progressCapped.toFixed(0)}%</span>
              </div>
              <Progress 
                value={progressCapped} 
                className="h-2"
                indicatorClassName={cn(
                  kpi.status === 'good' && "bg-green-500",
                  kpi.status === 'warning' && "bg-yellow-500",
                  kpi.status === 'critical' && "bg-red-500"
                )}
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
```

### components/kpi/KPICategorySection.tsx

```tsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Settings } from 'lucide-react';
import { KPICategoryResponse, KPI_CATEGORY_COLORS } from '@/types/kpi.types';
import { KPICard } from './KPICard';
import { KPIDetailModal } from './KPIDetailModal';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';

interface KPICategorySectionProps {
  categoryData: KPICategoryResponse;
  onConfigClick?: (kpiCode: string) => void;
  defaultExpanded?: boolean;
}

export const KPICategorySection: React.FC<KPICategorySectionProps> = ({ 
  categoryData, 
  onConfigClick,
  defaultExpanded = true 
}) => {
  const { isDark } = useTheme();
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);
  
  const categoryColor = KPI_CATEGORY_COLORS[categoryData.category];
  const { summary } = categoryData;
  
  // Tradução das categorias
  const categoryNames = {
    efficiency: 'Eficiência',
    pricing: 'Tarifação',
    planning: 'Planejamento',
    governance: 'Governança'
  };
  
  return (
    <>
      <Card className="overflow-hidden">
        <CardHeader 
          className={cn(
            "cursor-pointer select-none",
            isDark ? "hover:bg-gray-800" : "hover:bg-gray-50"
          )}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div 
                className="w-1 h-8 rounded-full" 
                style={{ backgroundColor: categoryColor }}
              />
              <CardTitle className="text-lg">
                {categoryNames[categoryData.category]}
              </CardTitle>
              <Badge variant="secondary" className="ml-2">
                {summary.total_kpis} KPIs
              </Badge>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Mini status summary */}
              <div className="flex gap-2 text-sm">
                <span className="text-green-500">●{summary.status_distribution.good}</span>
                <span className="text-yellow-500">●{summary.status_distribution.warning}</span>
                <span className="text-red-500">●{summary.status_distribution.critical}</span>
              </div>
              
              {/* Health score */}
              <Badge 
                variant={
                  summary.health_score >= 80 ? 'default' :
                  summary.health_score >= 60 ? 'secondary' : 'destructive'
                }
              >
                {summary.health_score.toFixed(0)}%
              </Badge>
              
              {isExpanded ? <ChevronUp /> : <ChevronDown />}
            </div>
          </div>
        </CardHeader>
        
        {isExpanded && (
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
              {categoryData.kpis.map((kpi) => (
                <KPICard
                  key={kpi.kpi_id}
                  kpi={kpi}
                  onClick={() => setSelectedKPI(kpi.code)}
                />
              ))}
            </div>
          </CardContent>
        )}
      </Card>
      
      {/* Modal de detalhes */}
      {selectedKPI && (
        <KPIDetailModal
          kpiCode={selectedKPI}
          isOpen={!!selectedKPI}
          onClose={() => setSelectedKPI(null)}
          onConfigClick={onConfigClick}
        />
      )}
    </>
  );
};
```

### components/kpi/KPIIndicators.tsx

```tsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  BarChart3, 
  RefreshCw, 
  Settings, 
  AlertTriangle,
  CheckCircle,
  XCircle 
} from 'lucide-react';
import { useKPIs } from '@/hooks/useKPIs';
import { KPICategorySection } from './KPICategorySection';
import { KPIConfigModal } from './KPIConfigModal';
import { KPICategory } from '@/types/kpi.types';
import { cn } from '@/lib/utils';

export const KPIIndicators: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<KPICategory | 'all'>('all');
  const [configKPI, setConfigKPI] = useState<string | null>(null);
  
  const {
    categorizedKPIs,
    overallStats,
    isLoading,
    error,
    refetch,
    recalculate,
    isRecalculating
  } = useKPIs(selectedCategory === 'all' ? undefined : selectedCategory);
  
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Erro ao carregar KPIs. Por favor, tente novamente.
        </AlertDescription>
      </Alert>
    );
  }
  
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <Skeleton className="h-32" />
                <Skeleton className="h-32" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header com estatísticas gerais */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-6 w-6 text-primary" />
              <CardTitle>Key Performance Indicators</CardTitle>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                <RefreshCw className={cn("h-4 w-4 mr-2", isLoading && "animate-spin")} />
                Atualizar
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => recalculate()}
                disabled={isRecalculating}
              >
                <Settings className={cn("h-4 w-4 mr-2", isRecalculating && "animate-spin")} />
                Recalcular
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {/* Resumo geral */}
          {overallStats && (
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold">{overallStats.total}</div>
                <div className="text-sm text-gray-500">Total KPIs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-500">{overallStats.good}</div>
                <div className="text-sm text-gray-500">No Target</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-500">{overallStats.warning}</div>
                <div className="text-sm text-gray-500">Atenção</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-500">{overallStats.critical}</div>
                <div className="text-sm text-gray-500">Crítico</div>
              </div>
            </div>
          )}
          
          {/* Filtro por categoria */}
          <Tabs value={selectedCategory} onValueChange={(v) => setSelectedCategory(v as any)}>
            <TabsList className="grid grid-cols-5 w-full">
              <TabsTrigger value="all">Todos</TabsTrigger>
              <TabsTrigger value="efficiency">Eficiência</TabsTrigger>
              <TabsTrigger value="pricing">Tarifação</TabsTrigger>
              <TabsTrigger value="planning">Planejamento</TabsTrigger>
              <TabsTrigger value="governance">Governança</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* KPIs por categoria */}
      <div className="space-y-4">
        {categorizedKPIs?.map((category) => (
          <KPICategorySection
            key={category.category}
            categoryData={category}
            onConfigClick={setConfigKPI}
            defaultExpanded={selectedCategory === 'all' || selectedCategory === category.category}
          />
        ))}
      </div>
      
      {/* Modal de configuração */}
      {configKPI && (
        <KPIConfigModal
          kpiCode={configKPI}
          isOpen={!!configKPI}
          onClose={() => setConfigKPI(null)}
        />
      )}
    </div>
  );
};
```

### components/kpi/KPIDetailModal.tsx

```tsx
import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Settings, TrendingUp, TrendingDown, Info } from 'lucide-react';
import { useKPIs } from '@/hooks/useKPIs';
import { KPIValue } from '@/types/kpi.types';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useTheme } from '@/hooks/useTheme';

interface KPIDetailModalProps {
  kpiCode: string;
  isOpen: boolean;
  onClose: () => void;
  onConfigClick?: (kpiCode: string) => void;
}

export const KPIDetailModal: React.FC<KPIDetailModalProps> = ({
  kpiCode,
  isOpen,
  onClose,
  onConfigClick
}) => {
  const { isDark } = useTheme();
  const { categorizedKPIs, kpiHistory, setSelectedKPI } = useKPIs();
  
  // Buscar KPI nos dados categorizados
  const kpi = categorizedKPIs?.flatMap(cat => cat.kpis).find(k => k.code === kpiCode);
  
  React.useEffect(() => {
    if (isOpen && kpiCode) {
      setSelectedKPI(kpiCode);
    }
  }, [isOpen, kpiCode, setSelectedKPI]);
  
  if (!kpi) return null;
  
  // Formatar dados do histórico para o gráfico
  const chartData = kpiHistory?.history?.map((h: any) => ({
    date: format(new Date(h.date), 'dd/MM', { locale: ptBR }),
    value: h.value,
    trend: h.trend
  })) || [];
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <DialogTitle>{kpi.name}</DialogTitle>
              <DialogDescription>
                Detalhes e histórico do indicador
              </DialogDescription>
            </div>
            
            {onConfigClick && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  onConfigClick(kpiCode);
                  onClose();
                }}
              >
                <Settings className="h-4 w-4 mr-2" />
                Configurar
              </Button>
            )}
          </div>
        </DialogHeader>
        
        <Tabs defaultValue="overview" className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="history">Histórico</TabsTrigger>
            <TabsTrigger value="details">Detalhes</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            {/* Valor atual e status */}
            <Card>
              <CardContent className="pt-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Valor Atual</p>
                    <p className="text-3xl font-bold">
                      {kpi.value.toFixed(kpi.unit === '%' ? 1 : 2)}{kpi.unit}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      {kpi.trend && kpi.trend > 0 ? (
                        <TrendingUp className="h-4 w-4 text-green-500" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-500" />
                      )}
                      <span className="text-sm">
                        {kpi.trend && kpi.trend > 0 ? '+' : ''}{kpi.trend?.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-500">Meta</p>
                    <p className="text-3xl font-bold">
                      {kpi.target?.toFixed(kpi.unit === '%' ? 1 : 2)}{kpi.unit}
                    </p>
                    <Badge 
                      className="mt-2"
                      variant={
                        kpi.status === 'good' ? 'default' :
                        kpi.status === 'warning' ? 'secondary' : 'destructive'
                      }
                    >
                      {kpi.status === 'good' ? 'No Target' :
                       kpi.status === 'warning' ? 'Atenção' : 'Crítico'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Descrição e fórmula */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Sobre este KPI</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Descrição</p>
                  <p className="text-sm">
                    {getKPIDescription(kpi.code)}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500 mb-1">Fórmula</p>
                  <code className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded block">
                    {getKPIFormula(kpi.code)}
                  </code>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500 mb-1">Direção Positiva</p>
                  <p className="text-sm">
                    {kpi.is_good_when_higher ? 
                      'Quanto maior, melhor ↑' : 
                      'Quanto menor, melhor ↓'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Últimos 30 dias</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        stroke={isDark ? '#94a3b8' : '#64748b'}
                      />
                      <YAxis 
                        stroke={isDark ? '#94a3b8' : '#64748b'}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: isDark ? '#1e293b' : '#ffffff',
                          border: '1px solid #e2e8f0'
                        }}
                      />
                      {kpi.target && (
                        <ReferenceLine 
                          y={kpi.target} 
                          stroke="#ef4444" 
                          strokeDasharray="5 5"
                          label="Meta"
                        />
                      )}
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="details">
            <Card>
              <CardContent className="pt-6">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm text-gray-500">Categoria</dt>
                    <dd className="text-sm font-medium capitalize">{kpi.category}</dd>
                  </div>
                  
                  <div>
                    <dt className="text-sm text-gray-500">Última Atualização</dt>
                    <dd className="text-sm font-medium">
                      {format(new Date(kpi.last_updated), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                    </dd>
                  </div>
                  
                  <div>
                    <dt className="text-sm text-gray-500">Frequência de Cálculo</dt>
                    <dd className="text-sm font-medium">Diária</dd>
                  </div>
                  
                  {kpi.metadata && (
                    <div>
                      <dt className="text-sm text-gray-500">Metadados</dt>
                      <dd className="text-sm">
                        <pre className="bg-gray-100 dark:bg-gray-800 p-2 rounded text-xs overflow-x-auto">
                          {JSON.stringify(kpi.metadata, null, 2)}
                        </pre>
                      </dd>
                    </div>
                  )}
                </dl>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

// Funções auxiliares para descrições e fórmulas
const getKPIDescription = (code: string): string => {
  const descriptions: Record<string, string> = {
    'resource_utilization_rate': 'Mede o percentual de recursos provisionados que estão sendo efetivamente utilizados. Ajuda a identificar superprovisionamento.',
    'cloud_waste_percentage': 'Identifica a porção do gasto em recursos ociosos como VMs paradas, volumes não anexados e snapshots órfãos.',
    'power_schedule_adherence': 'Verifica se a automação de start/stop está funcionando conforme planejado para workloads não-produtivos.',
    'legacy_resources_percentage': 'Quantifica quantas instâncias ainda estão em famílias antigas e menos eficientes.',
    'effective_savings_rate': 'Economia líquida comparada com preços on-demand, unificando cobertura e utilização de RI/SP/CUD.',
    'commitment_discount_waste': 'Quanto da capacidade de RI/SP/CUD comprada permanece não utilizada.',
    'compute_covered_by_commitments': 'Profundidade da cobertura de taxa; valores baixos sinalizam vazamento de instâncias on-demand.',
    'cost_per_vcpu_hour': 'Normaliza o custo para uma unidade técnica, ideal para comparações de preço entre provedores.',
    'budget_forecast_variation': 'Quão próximo seu forecast contínuo está do orçamento acumulado no ano.',
    'cloud_spend_variation': 'O sinal clássico de gasto acima/abaixo do orçamento.',
    'forecast_accuracy_rate': 'Precisão preditiva para capacidade ou valores; orienta ajustes no modelo de previsão.',
    'unallocated_cost_percentage': 'Quanto do gasto ainda não possui tag ou proprietário.',
    'tag_compliance_rate': 'Saúde da sua disciplina de tagging; valores baixos comprometem todos os outros KPIs.',
    'anomaly_detection_savings': 'Economias realizadas ao detectar picos de gasto antecipadamente com alertas.'
  };
  
  return descriptions[code] || 'Descrição não disponível.';
};

const getKPIFormula = (code: string): string => {
  const formulas: Record<string, string> = {
    'resource_utilization_rate': '(Capacidade Consumida ÷ Capacidade Alocada) × 100',
    'cloud_waste_percentage': '(Custo de Recursos Ociosos ÷ Gasto Total na Nuvem) × 100',
    'power_schedule_adherence': '(Horas de Runtime Planejadas ÷ Horas de Runtime Reais) × 100',
    'legacy_resources_percentage': '(Contagem de Instâncias Legacy ÷ Total de Instâncias) × 100',
    'effective_savings_rate': '(Economias de Todos os Instrumentos de Desconto ÷ Gasto On-Demand Equivalente)',
    'commitment_discount_waste': '(Custo de Commitment Não Usado ÷ Custo Total de Commitment) × 100',
    'compute_covered_by_commitments': '(Gasto de Compute com Desconto de Commitment ÷ Gasto Total de Compute) × 100',
    'cost_per_vcpu_hour': '(Custo de Compute por Hora ÷ Número de vCPUs ou GPUs)',
    'budget_forecast_variation': '((Orçado - Previsto) ÷ Orçado) × 100',
    'cloud_spend_variation': '((Orçado - Real) ÷ Orçado) × 100',
    'forecast_accuracy_rate': '100 - abs((Previsto - Real) ÷ Previsto) × 100',
    'unallocated_cost_percentage': '(Custos Não Alocados ÷ Gasto Total na Nuvem) × 100',
    'tag_compliance_rate': '(Recursos Tagueados Corretamente ÷ Total de Recursos) × 100',
    'anomaly_detection_savings': 'Soma de (Custo de Pico Previsto - Custo no Desligamento)'
  };
  
  return formulas[code] || 'Fórmula não disponível.';
};
```

## 🔄 Integração com Dashboard

### Adicionar ao Dashboard Principal

```tsx
// Em src/pages/Home.tsx ou Dashboard.tsx

import { KPIIndicators } from '@/components/kpi/KPIIndicators';

// Adicionar uma nova seção no dashboard
<section className="mb-8">
  <h2 className="text-2xl font-bold mb-4">Key Performance Indicators</h2>
  <KPIIndicators />
</section>

// Ou adicionar como uma aba
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Visão Geral</TabsTrigger>
    <TabsTrigger value="kpis">KPIs</TabsTrigger>
    <TabsTrigger value="costs">Custos</TabsTrigger>
  </TabsList>
  
  <TabsContent value="kpis">
    <KPIIndicators />
  </TabsContent>
</Tabs>
```

## 📱 Responsividade

```tsx
// Ajustes para mobile em KPICard
<div className={cn(
  "grid gap-4",
  "grid-cols-1",
  "sm:grid-cols-2",
  "lg:grid-cols-3",
  "xl:grid-cols-4"
)}>
  {kpis.map(kpi => (
    <KPICard key={kpi.id} kpi={kpi} />
  ))}
</div>

// Versão compacta para mobile
{isMobile ? (
  <KPICard compact kpi={kpi} />
) : (
  <KPICard kpi={kpi} />
)}
```

## 🔧 Configuração Inicial

### Formulário de Setup Inicial

```tsx
// components/kpi/KPISetupWizard.tsx

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

const setupSchema = z.object({
  resourceUtilizationTarget: z.number().min(0).max(100),
  wasteReductionTarget: z.number().min(0).max(100),
  commitmentCoverageTarget: z.number().min(0).max(100),
  complianceTarget: z.number().min(0).max(100),
  monthlyBudget: z.number().positive(),
  companySize: z.enum(['small', 'medium', 'large', 'enterprise']),
});

type SetupFormData = z.infer<typeof setupSchema>;

export const KPISetupWizard: React.FC = () => {
  const [step, setStep] = useState(1);
  const totalSteps = 4;
  
  const form = useForm<SetupFormData>({
    resolver: zodResolver(setupSchema),
    defaultValues: {
      resourceUtilizationTarget: 75,
      wasteReductionTarget: 15,
      commitmentCoverageTarget: 80,
      complianceTarget: 95,
      monthlyBudget: 50000,
      companySize: 'medium'
    }
  });
  
  const onSubmit = async (data: SetupFormData) => {
    // Enviar configurações para o backend
    console.log('Setup data:', data);
    // TODO: Implementar chamada API
  };
  
  const progress = (step / totalSteps) * 100;
  
  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Configuração de KPIs</CardTitle>
        <CardDescription>
          Vamos configurar as metas iniciais para seus indicadores
        </CardDescription>
        <Progress value={progress} className="mt-4" />
      </CardHeader>
      
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <CardContent className="space-y-6">
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Metas de Eficiência</h3>
              
              <div className="space-y-2">
                <Label>Taxa de Utilização de Recursos Alvo (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('resourceUtilizationTarget', { valueAsNumber: true })}
                    defaultValue={[75]}
                    max={100}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('resourceUtilizationTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Meta recomendada: 70-80% para ambientes de produção
                </p>
              </div>
              
              <div className="space-y-2">
                <Label>Meta de Redução de Desperdício (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('wasteReductionTarget', { valueAsNumber: true })}
                    defaultValue={[15]}
                    max={50}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('wasteReductionTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Empresas maduras em FinOps alcançam menos de 10%
                </p>
              </div>
            </div>
          )}
          
          {step === 2 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Estratégia de Tarifação</h3>
              
              <div className="space-y-2">
                <Label>Meta de Cobertura por Commitments (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('commitmentCoverageTarget', { valueAsNumber: true })}
                    defaultValue={[80]}
                    max={100}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('commitmentCoverageTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Workloads estáveis devem ter alta cobertura (70-90%)
                </p>
              </div>
            </div>
          )}
          
          {step === 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Planejamento Financeiro</h3>
              
              <div className="space-y-2">
                <Label>Orçamento Mensal de Cloud (R$)</Label>
                <Input
                  type="number"
                  {...form.register('monthlyBudget', { valueAsNumber: true })}
                  placeholder="50000"
                />
                <p className="text-sm text-gray-500">
                  Base para cálculo de variações e alertas
                </p>
              </div>
              
              <div className="space-y-2">
                <Label>Porte da Empresa</Label>
                <select
                  {...form.register('companySize')}
                  className="w-full p-2 border rounded"
                >
                  <option value="small">Pequena (até 50 funcionários)</option>
                  <option value="medium">Média (50-250 funcionários)</option>
                  <option value="large">Grande (250-1000 funcionários)</option>
                  <option value="enterprise">Enterprise (1000+ funcionários)</option>
                </select>
              </div>
            </div>
          )}
          
          {step === 4 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Governança</h3>
              
              <div className="space-y-2">
                <Label>Meta de Compliance de Tags (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('complianceTarget', { valueAsNumber: true })}
                    defaultValue={[95]}
                    max={100}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('complianceTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Tags essenciais: owner, environment, project, cost-center
                </p>
              </div>
            </div>
          )}
        </CardContent>
        
        <CardFooter className="flex justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={() => setStep(Math.max(1, step - 1))}
            disabled={step === 1}
          >
            Anterior
          </Button>
          
          {step < totalSteps ? (
            <Button
              type="button"
              onClick={() => setStep(step + 1)}
            >
              Próximo
            </Button>
          ) : (
            <Button type="submit">
              Finalizar Configuração
            </Button>
          )}
        </CardFooter>
      </form>
    </Card>
  );
};
```

## 🚀 Próximas Etapas

1. **Testes**
   - Criar testes unitários para componentes
   - Testes de integração com API
   - Testes de performance

2. **Otimizações**
   - Implementar lazy loading
   - Adicionar skeleton loaders
   - Otimizar queries com React Query

3. **Features Avançadas**
   - Exportação de relatórios
   - Comparação temporal
   - Alertas em tempo real
   - Dashboard customizável