"""
Modelos para API de Sazonalidade de Custos
"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field


class SeasonalityMetadata(BaseModel):
    """Metadados da análise de sazonalidade"""
    historicalMonths: int = Field(..., description="Quantidade de meses de histórico usado", alias="historical_months")
    dataQuality: Literal["Good", "Fair", "Poor"] = Field(..., description="Qualidade dos dados históricos", alias="data_quality")
    nextPeakExpected: Optional[str] = Field(None, description="Data esperada do próximo pico sazonal", alias="next_peak_expected")
    analysisPeriod: str = Field(..., description="Período usado para análise", alias="analysis_period")
    confidenceLevel: float = Field(..., description="Nível de confiança da análise (0-1)", alias="confidence_level")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        
        # Configurar para usar alias (camelCase) na serialização
        alias_generator = lambda string: string
        by_alias = True


class SeasonalityResponse(BaseModel):
    """Resposta da API de sazonalidade de custos"""
    monthlyComparison: float = Field(..., ge=0, le=100, description="% comparação mês atual vs histórico", alias="monthly_comparison")
    weeklyPattern: float = Field(..., ge=0, le=100, description="% aderência ao padrão semanal", alias="weekly_pattern")
    seasonalProgress: float = Field(..., ge=0, le=100, description="% progresso até pico sazonal", alias="seasonal_progress")
    trendVariation: float = Field(..., ge=0, le=100, description="% variação vs tendência", alias="trend_variation")
    status: Literal["normal", "attention", "alert"] = Field(..., description="Status geral das métricas")
    lastUpdated: datetime = Field(..., description="Última atualização dos dados", alias="last_updated")
    metadata: SeasonalityMetadata = Field(..., description="Metadados da análise")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        by_alias = True
        
        json_schema_extra = {
            "example": {
                "monthlyComparison": 78.5,
                "weeklyPattern": 92.1,
                "seasonalProgress": 45.3,
                "trendVariation": 67.8,
                "status": "normal",
                "lastUpdated": "2025-01-15T10:30:00Z",
                "metadata": {
                    "historicalMonths": 12,
                    "dataQuality": "Good",
                    "nextPeakExpected": "2025-03-15",
                    "analysisPeriod": "current_month",
                    "confidenceLevel": 0.85
                }
            }
        }
