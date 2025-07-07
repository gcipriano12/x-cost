"""
Modelos Pydantic para o endpoint de forecast
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class ForecastMethod(str, Enum):
    """Métodos de previsão disponíveis"""
    WEIGHTED_MOVING_AVERAGE = "weighted_moving_average"
    LINEAR_REGRESSION = "linear_regression"
    SEASONAL_DECOMPOSITION = "seasonal_decomposition"
    EXPONENTIAL_SMOOTHING = "exponential_smoothing"


class ConfidenceInterval(BaseModel):
    """Intervalo de confiança para previsões"""
    lower: float = Field(..., description="Limite inferior do intervalo de confiança")
    upper: float = Field(..., description="Limite superior do intervalo de confiança")


class ForecastDataPoint(BaseModel):
    """Ponto de dados do forecast"""
    month: str = Field(..., description="Nome do mês (ex: Jan, Feb)")
    actual: Optional[float] = Field(None, description="Valor real dos gastos")
    forecast: Optional[float] = Field(None, description="Valor previsto dos gastos")
    budget: Optional[float] = Field(None, description="Valor do orçamento")
    variance: Optional[float] = Field(None, description="Variação entre previsto e orçamento")
    confidence_interval: Optional[ConfidenceInterval] = Field(None, description="Intervalo de confiança")


class ForecastMetadata(BaseModel):
    """Metadados do modelo de previsão"""
    model_accuracy: float = Field(..., description="Acurácia do modelo (0-100%)")
    confidence_level: float = Field(..., description="Nível de confiança (ex: 90%)")
    data_completeness: float = Field(..., description="Completude dos dados (0-100%)")
    forecast_method: str = Field(..., description="Método de previsão utilizado")


class BudgetInfo(BaseModel):
    """Informações de orçamento"""
    total_budget: float = Field(..., description="Orçamento total do período")
    monthly_budget: float = Field(..., description="Orçamento mensal")
    budget_exceeded_months: List[str] = Field(..., description="Meses onde a previsão excede o orçamento")


class ForecastPeriod(BaseModel):
    """Período do forecast"""
    start_date: str = Field(..., description="Data de início da análise (ISO format)")
    end_date: str = Field(..., description="Data de fim da previsão (ISO format)")
    forecast_months: int = Field(..., description="Número de meses de previsão")


class ForecastResponse(BaseModel):
    """Resposta completa do forecast"""
    period: ForecastPeriod = Field(..., description="Informações do período analisado")
    generated_at: str = Field(..., description="Timestamp de quando a previsão foi gerada")
    forecast_data: List[ForecastDataPoint] = Field(..., description="Dados históricos e previsões")
    metadata: ForecastMetadata = Field(..., description="Metadados da qualidade do modelo")
    budget_info: Optional[BudgetInfo] = Field(None, description="Informações de orçamento se disponível")

    class Config:
        json_schema_extra = {
            "example": {
                "period": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "forecast_months": 7
                },
                "generated_at": "2024-07-06T14:30:00Z",
                "forecast_data": [
                    {
                        "month": "Jan",
                        "actual": 280000,
                        "budget": 350000
                    },
                    {
                        "month": "Jul",
                        "forecast": 360000,
                        "budget": 350000,
                        "variance": 10000,
                        "confidence_interval": {
                            "lower": 340000,
                            "upper": 380000
                        }
                    }
                ],
                "metadata": {
                    "model_accuracy": 85.5,
                    "confidence_level": 90,
                    "data_completeness": 95.2,
                    "forecast_method": "weighted_moving_average"
                },
                "budget_info": {
                    "total_budget": 4200000,
                    "monthly_budget": 350000,
                    "budget_exceeded_months": ["Jun", "Jul"]
                }
            }
        }


class ForecastRequest(BaseModel):
    """Request model para parâmetros do forecast"""
    credential_id: Optional[str] = Field(None, description="ID da credencial específica")
    provider_name: Optional[str] = Field(None, description="Filtro por provedor (AWS, Azure, GCP)")
    months: int = Field(7, ge=1, le=24, description="Número de meses para previsão (1-24)")
    start_date: Optional[str] = Field(None, description="Data inicial para análise histórica (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Data final para análise histórica (YYYY-MM-DD)")
    method: ForecastMethod = Field(ForecastMethod.WEIGHTED_MOVING_AVERAGE, description="Método de previsão")

    class Config:
        json_schema_extra = {
            "example": {
                "credential_id": "123e4567-e89b-12d3-a456-426614174000",
                "provider_name": "AWS",
                "months": 6,
                "start_date": "2024-01-01",
                "end_date": "2024-06-30",
                "method": "weighted_moving_average"
            }
        }


# Modelo de erro para documentação
class ForecastError(BaseModel):
    """Modelo de erro do forecast"""
    error: bool = Field(True, description="Indica que houve erro")
    message: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes do erro")
    status_code: int = Field(..., description="Código de status HTTP")

    class Config:
        json_schema_extra = {
            "example": {
                "error": True,
                "message": "Insufficient historical data",
                "detail": "Minimum 3 months of historical data required for forecast generation",
                "status_code": 400
            }
        }
