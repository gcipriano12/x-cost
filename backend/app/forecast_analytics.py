"""
Forecast Analytics Module

Implementa algoritmos de previsão de gastos em nuvem
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from app.models import FocusCostData, Budget
from app.forecast_models import (
    ForecastMethod, ConfidenceInterval, ForecastDataPoint, 
    ForecastMetadata, BudgetInfo, ForecastPeriod, ForecastResponse
)
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


from app.forecast_models import (
    ForecastMethod, ConfidenceInterval, ForecastDataPoint, 
    ForecastMetadata, BudgetInfo, ForecastPeriod, ForecastResponse
)


class ForecastAnalyzer:
    """Analisador de previsão de gastos"""
    
    def __init__(self, db: Session):
        self.db = db
        self.min_historical_months = 3
        self.default_confidence_level = 90
        self.default_confidence_margin = 0.15  # ±15%

    def generate_forecast(
        self,
        credential_id: Optional[str] = None,
        provider_name: Optional[str] = None,
        months: int = 7,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        method: ForecastMethod = ForecastMethod.WEIGHTED_MOVING_AVERAGE
    ) -> ForecastResponse:
        """
        Gera previsão de gastos baseada em dados históricos
        
        Args:
            credential_id: ID da credencial específica
            provider_name: Nome do provedor (AWS, Azure, GCP)
            months: Número de meses para previsão
            start_date: Data inicial para análise histórica
            end_date: Data final para análise histórica
            method: Método de previsão a ser usado
            
        Returns:
            ForecastResponse com dados da previsão
        """
        logger.info(f"Generating forecast for {months} months using {method}")
        
        # Definir período de análise se não especificado
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)  # 12 meses históricos
            
        # Obter dados históricos
        historical_data = self._get_historical_data(
            credential_id, provider_name, start_date, end_date
        )
        
        # Validar se há dados suficientes
        if len(historical_data) < self.min_historical_months:
            raise ValueError(f"Insufficient historical data. Minimum {self.min_historical_months} months required.")
        
        # Preparar dados para análise
        df = self._prepare_data(historical_data)
        
        # Calcular métricas de qualidade dos dados
        data_completeness = self._calculate_data_completeness(df)
        
        # Gerar previsão baseada no método escolhido
        forecast_data, model_accuracy = self._generate_forecast_data(
            df, months, method
        )
        
        # Obter informações de orçamento
        budget_info = self._get_budget_info(
            credential_id, provider_name, forecast_data
        )
        
        # Criar resposta
        return ForecastResponse(
            period=ForecastPeriod(
                start_date=start_date.isoformat(),
                end_date=(end_date + timedelta(days=months * 30)).isoformat(),
                forecast_months=months
            ),
            generated_at=datetime.utcnow().isoformat() + "Z",
            forecast_data=forecast_data,
            metadata=ForecastMetadata(
                model_accuracy=model_accuracy,
                confidence_level=self.default_confidence_level,
                data_completeness=data_completeness,
                forecast_method=method.value
            ),
            budget_info=budget_info
        )

    def _get_historical_data(
        self,
        credential_id: Optional[str],
        provider_name: Optional[str],
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        """Obtém dados históricos de custo"""
        
        query = self.db.query(
            extract('year', FocusCostData.billing_period_start).label('year'),
            extract('month', FocusCostData.billing_period_start).label('month'),
            func.sum(FocusCostData.billed_cost).label('total_cost')
        )
        
        # Aplicar filtros
        filters = [
            FocusCostData.billing_period_start >= start_date,
            FocusCostData.billing_period_start <= end_date
        ]
        
        if credential_id:
            # Assumindo que há uma relação com credencial via provider
            filters.append(FocusCostData.provider_name == provider_name)
            
        if provider_name:
            filters.append(FocusCostData.provider_name == provider_name)
            
        query = query.filter(and_(*filters))
        query = query.group_by(
            extract('year', FocusCostData.billing_period_start),
            extract('month', FocusCostData.billing_period_start)
        )
        query = query.order_by('year', 'month')
        
        results = query.all()
        
        return [
            {
                'year': int(row.year),
                'month': int(row.month),
                'total_cost': float(row.total_cost or 0)
            }
            for row in results
        ]

    def _prepare_data(self, historical_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Prepara dados para análise"""
        
        df = pd.DataFrame(historical_data)
        if df.empty:
            return df
            
        # Criar coluna de data
        df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))
        
        # Ordenar por data
        df = df.sort_values('date')
        
        # Preencher meses ausentes com zero
        df = df.set_index('date')
        full_range = pd.date_range(
            start=df.index.min(),
            end=df.index.max(),
            freq='MS'  # Month start
        )
        df = df.reindex(full_range, fill_value=0)
        df['total_cost'] = df['total_cost'].fillna(0)
        
        return df

    def _generate_forecast_data(
        self,
        df: pd.DataFrame,
        months: int,
        method: ForecastMethod
    ) -> Tuple[List[ForecastDataPoint], float]:
        """Gera dados de previsão"""
        
        if method == ForecastMethod.WEIGHTED_MOVING_AVERAGE:
            return self._weighted_moving_average_forecast(df, months)
        elif method == ForecastMethod.LINEAR_REGRESSION:
            return self._linear_regression_forecast(df, months)
        else:
            # Fallback para média móvel ponderada
            return self._weighted_moving_average_forecast(df, months)

    def _weighted_moving_average_forecast(
        self,
        df: pd.DataFrame,
        months: int
    ) -> Tuple[List[ForecastDataPoint], float]:
        """Previsão usando média móvel ponderada"""
        
        forecast_data = []
        costs = df['total_cost'].values
        dates = df.index
        
        # Calcular accuracy usando validação cruzada
        accuracy = self._calculate_model_accuracy(costs)
        
        # Processar dados históricos
        for i, (date_val, cost) in enumerate(zip(dates, costs)):
            month_name = date_val.strftime('%b')
            forecast_data.append(ForecastDataPoint(
                month=month_name,
                actual=float(cost)
            ))
        
        # Gerar previsões futuras
        window_size = min(6, len(costs))  # Usar últimos 6 meses ou menos
        weights = np.exp(np.linspace(-1, 0, window_size))  # Pesos exponenciais
        weights = weights / weights.sum()
        
        for i in range(months):
            # Usar janela deslizante dos últimos valores
            recent_costs = costs[-window_size:] if len(costs) >= window_size else costs
            
            # Calcular previsão ponderada
            if len(recent_costs) > 0:
                forecast_value = np.average(recent_costs, weights=weights[:len(recent_costs)])
                
                # Adicionar tendência de crescimento
                if len(costs) >= 2:
                    growth_rate = (costs[-1] - costs[-2]) / max(costs[-2], 1)
                    growth_rate = np.clip(growth_rate, -0.1, 0.1)  # Limitar crescimento
                    forecast_value *= (1 + growth_rate)
                
                # Calcular intervalo de confiança
                std_dev = np.std(recent_costs) if len(recent_costs) > 1 else forecast_value * 0.1
                margin = std_dev * self.default_confidence_margin
                
                confidence_interval = ConfidenceInterval(
                    lower=max(0, forecast_value - margin),
                    upper=forecast_value + margin
                )
            else:
                forecast_value = 0
                confidence_interval = ConfidenceInterval(lower=0, upper=0)
            
            # Adicionar à lista de dados históricos para próxima iteração
            costs = np.append(costs, forecast_value)
            
            # Criar ponto de dados
            future_date = dates[-1] + timedelta(days=30 * (i + 1))
            month_name = future_date.strftime('%b')
            
            forecast_data.append(ForecastDataPoint(
                month=month_name,
                forecast=float(forecast_value),
                confidence_interval=confidence_interval
            ))
        
        return forecast_data, accuracy

    def _linear_regression_forecast(
        self,
        df: pd.DataFrame,
        months: int
    ) -> Tuple[List[ForecastDataPoint], float]:
        """Previsão usando regressão linear"""
        
        costs = df['total_cost'].values
        dates = df.index
        
        if len(costs) < 2:
            return self._weighted_moving_average_forecast(df, months)
        
        # Preparar dados para regressão
        X = np.arange(len(costs)).reshape(-1, 1)
        y = costs
        
        # Treinar modelo
        model = LinearRegression()
        model.fit(X, y)
        
        # Calcular accuracy
        y_pred = model.predict(X)
        accuracy = max(0, r2_score(y, y_pred) * 100)
        
        forecast_data = []
        
        # Processar dados históricos
        for i, (date_val, cost) in enumerate(zip(dates, costs)):
            month_name = date_val.strftime('%b')
            forecast_data.append(ForecastDataPoint(
                month=month_name,
                actual=float(cost)
            ))
        
        # Gerar previsões futuras
        for i in range(months):
            X_future = np.array([[len(costs) + i]])
            forecast_value = model.predict(X_future)[0]
            forecast_value = max(0, forecast_value)  # Não permitir valores negativos
            
            # Calcular intervalo de confiança baseado no erro do modelo
            residuals = y - y_pred
            std_error = np.std(residuals) if len(residuals) > 1 else forecast_value * 0.1
            margin = std_error * self.default_confidence_margin
            
            confidence_interval = ConfidenceInterval(
                lower=max(0, forecast_value - margin),
                upper=forecast_value + margin
            )
            
            future_date = dates[-1] + timedelta(days=30 * (i + 1))
            month_name = future_date.strftime('%b')
            
            forecast_data.append(ForecastDataPoint(
                month=month_name,
                forecast=float(forecast_value),
                confidence_interval=confidence_interval
            ))
        
        return forecast_data, accuracy

    def _calculate_model_accuracy(self, costs: np.ndarray) -> float:
        """Calcula accuracy do modelo usando validação cruzada simples"""
        
        if len(costs) < 4:
            return 70.0  # Accuracy padrão para poucos dados
        
        # Usar últimos 30% dos dados para validação
        split_point = int(len(costs) * 0.7)
        train_costs = costs[:split_point]
        test_costs = costs[split_point:]
        
        if len(test_costs) == 0:
            return 70.0
        
        # Simular previsão usando média móvel
        predictions = []
        for i in range(len(test_costs)):
            if len(train_costs) >= 3:
                pred = np.mean(train_costs[-3:])  # Média dos últimos 3 meses
            else:
                pred = np.mean(train_costs)
            predictions.append(pred)
            train_costs = np.append(train_costs, test_costs[i])
        
        # Calcular MAPE (Mean Absolute Percentage Error)
        mape = np.mean(np.abs((test_costs - predictions) / np.maximum(test_costs, 1))) * 100
        accuracy = max(0, 100 - mape)
        
        return min(accuracy, 95.0)  # Máximo de 95% de accuracy

    def _calculate_data_completeness(self, df: pd.DataFrame) -> float:
        """Calcula completude dos dados"""
        
        if df.empty:
            return 0.0
        
        # Contar meses com dados > 0
        months_with_data = (df['total_cost'] > 0).sum()
        total_months = len(df)
        
        completeness = (months_with_data / total_months) * 100 if total_months > 0 else 0
        return min(completeness, 100.0)

    def _get_budget_info(
        self,
        credential_id: Optional[str],
        provider_name: Optional[str],
        forecast_data: List[ForecastDataPoint]
    ) -> Optional[BudgetInfo]:
        """
        Obtém informações de orçamento com lógica de priorização
        
        Lógica de busca:
        1. Se provider_name fornecido: Buscar budget específico para esse provider
        2. Se não encontrar budget específico: Buscar budget com provider "All"
        3. Se provider_name não fornecido: Buscar budget com provider "All"
        4. Se nenhum encontrado: Retornar None
        """
        
        try:
            budget = None
            
            # 1. Tentar buscar budget específico para o provider
            if provider_name:
                budget = self.db.query(Budget).filter(
                    Budget.is_active == True,
                    Budget.provider_name == provider_name
                ).first()
                
                if budget:
                    logger.info(f"Found specific budget for provider {provider_name}")
            
            # 2. Se não encontrou budget específico, buscar budget "All"
            if not budget:
                budget = self.db.query(Budget).filter(
                    Budget.is_active == True,
                    Budget.provider_name == 'All'
                ).first()
                
                if budget:
                    if provider_name:
                        logger.info(f"Using fallback budget 'All' for provider {provider_name}")
                    else:
                        logger.info("Using budget 'All' (no specific provider requested)")
            
            if not budget:
                logger.info("No active budget found (neither specific nor 'All')")
                return None
            
            monthly_budget = float(budget.budget_amount)
            
            # Calcular meses onde previsão excede orçamento
            budget_exceeded_months = []
            for point in forecast_data:
                if point.forecast and point.forecast > monthly_budget:
                    budget_exceeded_months.append(point.month)
            
            # Estimar orçamento total baseado no período
            forecast_months = len([p for p in forecast_data if p.forecast])
            total_budget = monthly_budget * max(12, forecast_months)  # Mínimo anual
            
            logger.info(f"Budget info: monthly=${monthly_budget:,.2f}, exceeded_months={len(budget_exceeded_months)}")
            
            return BudgetInfo(
                total_budget=total_budget,
                monthly_budget=monthly_budget,
                budget_exceeded_months=budget_exceeded_months
            )
            
        except Exception as e:
            logger.warning(f"Error getting budget info: {e}")
            return None
