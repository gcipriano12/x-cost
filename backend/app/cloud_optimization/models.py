"""
Modelos Pydantic para resposta unificada das otimizações cloud
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator


class AnomalyType(str, Enum):
    """Tipos de anomalias de custo"""
    SPIKE = "spike"
    DRIFT = "drift"
    UNUSUAL_PATTERN = "unusual_pattern"
    COST_INCREASE = "cost_increase"


class SeverityLevel(str, Enum):
    """Níveis de severidade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationType(str, Enum):
    """Tipos de recomendações"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    STORAGE_OPTIMIZATION = "storage_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"
    IDLE_RESOURCES = "idle_resources"
    SCHEDULING = "scheduling"


class CloudAnomaly(BaseModel):
    """Modelo para anomalias de custo detectadas"""
    id: str = Field(..., description="ID único da anomalia")
    provider: str = Field(..., description="Provedor de nuvem")
    service: str = Field(..., description="Serviço afetado")
    region: Optional[str] = Field(None, description="Região onde ocorreu")
    anomaly_type: AnomalyType = Field(..., description="Tipo da anomalia")
    severity: SeverityLevel = Field(..., description="Nível de severidade")
    detected_at: datetime = Field(..., description="Data/hora de detecção")
    cost_impact: float = Field(..., description="Impacto financeiro estimado")
    currency: str = Field(default="USD", description="Moeda")
    description: str = Field(..., description="Descrição da anomalia")
    root_cause: Optional[str] = Field(None, description="Causa raiz identificada")
    affected_resources: List[str] = Field(default=[], description="Recursos afetados")
    
    @validator('cost_impact')
    def validate_cost_impact(cls, v):
        if v < 0:
            raise ValueError('cost_impact deve ser não-negativo')
        return v


class SavingsOpportunity(BaseModel):
    """Modelo para oportunidades de economia"""
    id: str = Field(..., description="ID único da oportunidade")
    provider: str = Field(..., description="Provedor de nuvem")
    service: str = Field(..., description="Serviço com oportunidade")
    region: Optional[str] = Field(None, description="Região")
    opportunity_type: RecommendationType = Field(..., description="Tipo de oportunidade")
    title: str = Field(..., description="Título da oportunidade")
    description: str = Field(..., description="Descrição da oportunidade")
    category: str = Field(..., description="Categoria da oportunidade")
    
    # Savings fields - support both frontend and backend naming
    monthly_savings: float = Field(..., description="Economia mensal em USD")
    estimated_savings: float = Field(..., description="Economia estimada mensal (legacy)")
    annual_savings: Optional[float] = Field(None, description="Economia anual calculada")
    potential_savings: float = Field(..., description="Economia potencial (internal)")
    
    currency: str = Field(default="USD", description="Moeda")
    
    # Confidence fields - support both string and numeric
    confidence_level: str = Field(..., description="Nível de confiança (high/medium/low)")
    confidence: float = Field(..., ge=0, le=100, description="Nível de confiança (%)")
    
    # Implementation fields
    implementation_effort: str = Field(..., description="Esforço de implementação (low/medium/high)")
    implementation_effort_hours: Optional[float] = Field(None, description="Horas estimadas")
    
    # Risk and resources
    risk_level: str = Field(default="low", description="Nível de risco (low/medium/high)")
    affected_resources: List[str] = Field(default=[], description="Recursos afetados")
    resources_affected: List[str] = Field(default=[], description="Recursos afetados (legacy)")
    resource_name: Optional[str] = Field(None, description="Nome principal do recurso")
    
    # Actions and metadata
    action_required: str = Field(..., description="Ação necessária")
    detected_at: datetime = Field(default_factory=datetime.utcnow, description="Data de detecção")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Data de criação")
    
    def __init__(self, **data):
        # Ensure compatibility between different field names
        if 'monthly_savings' in data and 'estimated_savings' not in data:
            data['estimated_savings'] = data['monthly_savings']
        elif 'estimated_savings' in data and 'monthly_savings' not in data:
            data['monthly_savings'] = data['estimated_savings']
        
        if 'monthly_savings' in data and 'potential_savings' not in data:
            data['potential_savings'] = data['monthly_savings']
        
        if 'monthly_savings' in data and 'annual_savings' not in data:
            data['annual_savings'] = data['monthly_savings'] * 12
        
        if 'affected_resources' in data and 'resources_affected' not in data:
            data['resources_affected'] = data['affected_resources']
        elif 'resources_affected' in data and 'affected_resources' not in data:
            data['affected_resources'] = data['resources_affected']
        
        if 'confidence' in data and 'confidence_level' not in data:
            # Convert numeric confidence to string level
            conf_num = data['confidence']
            if conf_num >= 80:
                data['confidence_level'] = 'high'
            elif conf_num >= 50:
                data['confidence_level'] = 'medium'
            else:
                data['confidence_level'] = 'low'
        elif 'confidence_level' in data and 'confidence' not in data:
            # Convert string level to numeric confidence
            conf_str = data['confidence_level'].lower()
            if conf_str == 'high':
                data['confidence'] = 85.0
            elif conf_str == 'medium':
                data['confidence'] = 65.0
            else:
                data['confidence'] = 35.0
        
        super().__init__(**data)


class OptimizationRecommendation(BaseModel):
    """Modelo para recomendações de otimização"""
    id: str = Field(..., description="ID único da recomendação")
    provider: str = Field(..., description="Provedor de nuvem")
    category: RecommendationType = Field(..., description="Categoria da recomendação")
    title: str = Field(..., description="Título da recomendação")
    description: str = Field(..., description="Descrição detalhada")
    potential_savings: float = Field(..., description="Economia potencial")
    currency: str = Field(default="USD", description="Moeda")
    priority: SeverityLevel = Field(..., description="Prioridade")
    implementation_time: str = Field(..., description="Tempo estimado de implementação")
    prerequisites: List[str] = Field(default=[], description="Pré-requisitos")
    steps: List[str] = Field(..., description="Passos para implementação")
    impact_areas: List[str] = Field(default=[], description="Áreas de impacto")
    resources: List[str] = Field(default=[], description="Recursos relacionados")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")