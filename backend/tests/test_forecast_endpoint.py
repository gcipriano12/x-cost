"""
Testes para o endpoint de forecast de gastos
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import FocusCostData, Budget
from app.forecast_analytics import ForecastAnalyzer, ForecastMethod


def test_forecast_endpoint_basic(client: TestClient, auth_headers: dict, db_session: Session):
    """Teste básico do endpoint de forecast"""
    
    # Criar dados de custo históricos
    end_date = date.today()
    start_date = end_date - timedelta(days=180)  # 6 meses
    
    # Criar dados mensais simulados
    monthly_costs = [45000, 47000, 52000, 48000, 51000, 49000]  # 6 meses
    
    for i, cost in enumerate(monthly_costs):
        cost_date = start_date + timedelta(days=30 * i)
        cost_data = FocusCostData(
            billing_period_start=cost_date,
            billing_period_end=cost_date + timedelta(days=29),
            provider_name="AWS",
            service_name="EC2-Instance",
            billed_cost=Decimal(str(cost)),
            effective_cost=Decimal(str(cost)),
            billing_currency="USD"
        )
        db_session.add(cost_data)
    
    # Criar orçamento
    budget = Budget(
        budget_name="AWS Monthly Budget",
        provider_name="AWS",
        budget_amount=Decimal("50000.00"),
        budget_period="monthly",
        is_active=True
    )
    db_session.add(budget)
    db_session.commit()
    
    # Testar endpoint
    response = client.get(
        "/api/v1/analytics/forecast",
        headers=auth_headers,
        params={
            "provider_name": "AWS",
            "months": 6,
            "method": "weighted_moving_average"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verificar estrutura da resposta
    assert "success" in data
    assert data["success"] is True
    assert "data" in data
    
    forecast_data = data["data"]
    assert "period" in forecast_data
    assert "generated_at" in forecast_data
    assert "forecast_data" in forecast_data
    assert "metadata" in forecast_data
    assert "budget_info" in forecast_data
    
    # Verificar dados do período
    period = forecast_data["period"]
    assert "start_date" in period
    assert "end_date" in period
    assert "forecast_months" in period
    assert period["forecast_months"] == 6
    
    # Verificar metadados
    metadata = forecast_data["metadata"]
    assert "model_accuracy" in metadata
    assert "confidence_level" in metadata
    assert "data_completeness" in metadata
    assert "forecast_method" in metadata
    assert metadata["forecast_method"] == "weighted_moving_average"
    
    # Verificar dados de forecast
    forecast_points = forecast_data["forecast_data"]
    assert len(forecast_points) > 0
    
    # Deve ter pontos históricos e de previsão
    historical_points = [p for p in forecast_points if p.get("actual") is not None]
    prediction_points = [p for p in forecast_points if p.get("forecast") is not None]
    
    assert len(historical_points) >= 3  # Dados históricos
    assert len(prediction_points) == 6  # 6 meses de previsão
    
    # Verificar informações de orçamento
    budget_info = forecast_data["budget_info"]
    assert budget_info is not None
    assert "total_budget" in budget_info
    assert "monthly_budget" in budget_info
    assert "budget_exceeded_months" in budget_info
    assert budget_info["monthly_budget"] == 50000.0


def test_forecast_endpoint_insufficient_data(client: TestClient, auth_headers: dict, db_session: Session):
    """Teste com dados insuficientes"""
    
    # Criar apenas 1 mês de dados (insuficiente)
    cost_data = FocusCostData(
        billing_period_start=date.today() - timedelta(days=30),
        billing_period_end=date.today(),
        provider_name="AWS",
        service_name="EC2-Instance",
        billed_cost=Decimal("45000"),
        effective_cost=Decimal("45000"),
        billing_currency="USD"
    )
    db_session.add(cost_data)
    db_session.commit()
    
    response = client.get(
        "/api/v1/analytics/forecast",
        headers=auth_headers,
        params={
            "provider_name": "AWS",
            "months": 6
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Insufficient historical data" in data["detail"]


def test_forecast_endpoint_invalid_dates(client: TestClient, auth_headers: dict):
    """Teste com datas inválidas"""
    
    # Data inválida
    response = client.get(
        "/api/v1/analytics/forecast",
        headers=auth_headers,
        params={
            "start_date": "invalid-date",
            "months": 6
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Invalid start_date format" in data["detail"]
    
    # Range de datas inválido
    response = client.get(
        "/api/v1/analytics/forecast",
        headers=auth_headers,
        params={
            "start_date": "2024-12-01",
            "end_date": "2024-01-01",
            "months": 6
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "start_date must be before end_date" in data["detail"]


def test_forecast_endpoint_different_methods(client: TestClient, auth_headers: dict, db_session: Session):
    """Teste com diferentes métodos de previsão"""
    
    # Criar dados históricos suficientes
    end_date = date.today()
    start_date = end_date - timedelta(days=180)
    
    monthly_costs = [45000, 47000, 52000, 48000, 51000, 49000]
    
    for i, cost in enumerate(monthly_costs):
        cost_date = start_date + timedelta(days=30 * i)
        cost_data = FocusCostData(
            billing_period_start=cost_date,
            billing_period_end=cost_date + timedelta(days=29),
            provider_name="AWS",
            service_name="EC2-Instance",
            billed_cost=Decimal(str(cost)),
            effective_cost=Decimal(str(cost)),
            billing_currency="USD"
        )
        db_session.add(cost_data)
    
    db_session.commit()
    
    # Testar diferentes métodos
    methods = ["weighted_moving_average", "linear_regression"]
    
    for method in methods:
        response = client.get(
            "/api/v1/analytics/forecast",
            headers=auth_headers,
            params={
                "provider_name": "AWS",
                "months": 3,
                "method": method
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        forecast_data = data["data"]
        assert forecast_data["metadata"]["forecast_method"] == method


def test_forecast_analyzer_unit():
    """Teste unitário do ForecastAnalyzer"""
    
    # Mock de sessão de banco (seria necessário um mock mais elaborado)
    # Por enquanto, teste básico de inicialização
    
    analyzer = ForecastAnalyzer(None)
    assert analyzer.min_historical_months == 3
    assert analyzer.default_confidence_level == 90
    assert analyzer.default_confidence_margin == 0.15


def test_forecast_method_enum():
    """Teste do enum ForecastMethod"""
    
    assert ForecastMethod.WEIGHTED_MOVING_AVERAGE == "weighted_moving_average"
    assert ForecastMethod.LINEAR_REGRESSION == "linear_regression"
    assert ForecastMethod.SEASONAL_DECOMPOSITION == "seasonal_decomposition"
    assert ForecastMethod.EXPONENTIAL_SMOOTHING == "exponential_smoothing"


def test_forecast_endpoint_parameters(client: TestClient, auth_headers: dict, db_session: Session):
    """Teste dos parâmetros do endpoint"""
    
    # Criar dados mínimos
    for i in range(4):  # 4 meses
        cost_date = date.today() - timedelta(days=30 * (4-i))
        cost_data = FocusCostData(
            billing_period_start=cost_date,
            billing_period_end=cost_date + timedelta(days=29),
            provider_name="Azure",
            service_name="Virtual Machines",
            billed_cost=Decimal("30000"),
            effective_cost=Decimal("30000"),
            billing_currency="USD"
        )
        db_session.add(cost_data)
    
    db_session.commit()
    
    # Teste com todos os parâmetros
    response = client.get(
        "/api/v1/analytics/forecast",
        headers=auth_headers,
        params={
            "provider_name": "Azure",
            "months": 12,
            "start_date": "2024-01-01",
            "end_date": "2024-06-01",
            "method": "linear_regression"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    forecast_data = data["data"]
    assert forecast_data["period"]["forecast_months"] == 12
    assert forecast_data["metadata"]["forecast_method"] == "linear_regression"


def test_forecast_endpoint_no_budget(client: TestClient, auth_headers: dict, db_session: Session):
    """Teste sem dados de orçamento"""
    
    # Criar dados históricos sem orçamento
    for i in range(4):
        cost_date = date.today() - timedelta(days=30 * (4-i))
        cost_data = FocusCostData(
            billing_period_start=cost_date,
            billing_period_end=cost_date + timedelta(days=29),
            provider_name="GCP",
            service_name="Compute Engine",
            billed_cost=Decimal("25000"),
            effective_cost=Decimal("25000"),
            billing_currency="USD"
        )
        db_session.add(cost_data)
    
    db_session.commit()
    
    response = client.get(
        "/api/v1/analytics/forecast",
        headers=auth_headers,
        params={
            "provider_name": "GCP",
            "months": 6
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    forecast_data = data["data"]
    # budget_info pode ser None se não há orçamento configurado
    assert "budget_info" in forecast_data
