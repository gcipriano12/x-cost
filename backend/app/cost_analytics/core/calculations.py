"""
Statistical Calculations Module

Módulo para cálculos estatísticos e matemáticos reutilizáveis
"""

import math
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Optional, Tuple, Union
from datetime import date, datetime, timedelta


class StatisticalCalculations:
    """
    Classe com métodos estáticos para cálculos estatísticos
    """
    
    @staticmethod
    def calculate_percentage_change(
        current_value: float, 
        previous_value: float,
        precision: int = 2
    ) -> Optional[float]:
        """
        Calcula mudança percentual entre dois valores
        
        Args:
            current_value: Valor atual
            previous_value: Valor anterior
            precision: Precisão decimal
            
        Returns:
            Percentual de mudança ou None se previous_value é 0
        """
        if previous_value == 0:
            return None if current_value == 0 else float('inf')
        
        change = ((current_value - previous_value) / previous_value) * 100
        return round(change, precision)
    
    @staticmethod
    def calculate_growth_rate(
        values: List[float],
        periods: int = None
    ) -> Optional[float]:
        """
        Calcula taxa de crescimento médio
        
        Args:
            values: Lista de valores temporais
            periods: Número de períodos (padrão: len(values) - 1)
            
        Returns:
            Taxa de crescimento médio
        """
        if len(values) < 2:
            return None
        
        if periods is None:
            periods = len(values) - 1
        
        initial_value = values[0]
        final_value = values[-1]
        
        if initial_value == 0:
            return None
        
        growth_rate = (pow(final_value / initial_value, 1 / periods) - 1) * 100
        return round(growth_rate, 2)
    
    @staticmethod
    def calculate_variance(values: List[float]) -> float:
        """Calcula variância"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance
    
    @staticmethod
    def calculate_standard_deviation(values: List[float]) -> float:
        """Calcula desvio padrão"""
        variance = StatisticalCalculations.calculate_variance(values)
        return math.sqrt(variance)
    
    @staticmethod
    def calculate_moving_average(
        values: List[float], 
        window: int = 7
    ) -> List[float]:
        """
        Calcula média móvel
        
        Args:
            values: Lista de valores
            window: Tamanho da janela
            
        Returns:
            Lista com médias móveis
        """
        if len(values) < window:
            return values
        
        moving_averages = []
        for i in range(len(values) - window + 1):
            window_values = values[i:i + window]
            avg = sum(window_values) / len(window_values)
            moving_averages.append(round(avg, 2))
        
        return moving_averages
    
    @staticmethod
    def detect_outliers(
        values: List[float],
        method: str = "iqr",
        threshold: float = 1.5
    ) -> Tuple[List[int], List[float]]:
        """
        Detecta outliers usando IQR ou desvio padrão
        
        Args:
            values: Lista de valores
            method: Método (iqr ou std)
            threshold: Threshold para detecção
            
        Returns:
            Tupla com (índices dos outliers, valores outliers)
        """
        if len(values) < 4:
            return [], []
        
        if method == "iqr":
            return StatisticalCalculations._detect_outliers_iqr(values, threshold)
        elif method == "std":
            return StatisticalCalculations._detect_outliers_std(values, threshold)
        else:
            raise ValueError("Method must be 'iqr' or 'std'")
    
    @staticmethod
    def _detect_outliers_iqr(
        values: List[float], 
        threshold: float = 1.5
    ) -> Tuple[List[int], List[float]]:
        """Detecta outliers usando método IQR"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        # Calcular quartis
        q1_idx = n // 4
        q3_idx = 3 * n // 4
        
        q1 = sorted_values[q1_idx]
        q3 = sorted_values[q3_idx]
        iqr = q3 - q1
        
        # Calcular limites
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        # Encontrar outliers
        outlier_indices = []
        outlier_values = []
        
        for i, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                outlier_indices.append(i)
                outlier_values.append(value)
        
        return outlier_indices, outlier_values
    
    @staticmethod
    def _detect_outliers_std(
        values: List[float],
        threshold: float = 2.0
    ) -> Tuple[List[int], List[float]]:
        """Detecta outliers usando desvio padrão"""
        mean = sum(values) / len(values)
        std_dev = StatisticalCalculations.calculate_standard_deviation(values)
        
        outlier_indices = []
        outlier_values = []
        
        for i, value in enumerate(values):
            z_score = abs(value - mean) / std_dev if std_dev > 0 else 0
            if z_score > threshold:
                outlier_indices.append(i)
                outlier_values.append(value)
        
        return outlier_indices, outlier_values
    
    @staticmethod
    def calculate_trend_direction(values: List[float]) -> str:
        """
        Determina direção da tendência
        
        Args:
            values: Lista de valores temporais
            
        Returns:
            'increasing', 'decreasing', 'stable'
        """
        if len(values) < 2:
            return 'stable'
        
        # Calcular coeficiente de correlação com índices
        indices = list(range(len(values)))
        
        # Correlação de Pearson simples
        n = len(values)
        sum_x = sum(indices)
        sum_y = sum(values)
        sum_xy = sum(i * v for i, v in zip(indices, values))
        sum_x2 = sum(i * i for i in indices)
        sum_y2 = sum(v * v for v in values)
        
        denominator = math.sqrt((n * sum_x2 - sum_x ** 2) * (n * sum_y2 - sum_y ** 2))
        
        if denominator == 0:
            return 'stable'
        
        correlation = (n * sum_xy - sum_x * sum_y) / denominator
        
        if correlation > 0.1:
            return 'increasing'
        elif correlation < -0.1:
            return 'decreasing'
        else:
            return 'stable'


class CostCalculations:
    """
    Cálculos específicos para análise de custos
    """
    
    @staticmethod
    def calculate_cost_per_unit(
        total_cost: float,
        usage_amount: float,
        usage_unit: str = "hours"
    ) -> Dict[str, Union[float, str]]:
        """
        Calcula custo por unidade de uso
        
        Args:
            total_cost: Custo total
            usage_amount: Quantidade de uso
            usage_unit: Unidade de uso
            
        Returns:
            Dicionário com cálculos
        """
        if usage_amount == 0:
            return {
                "cost_per_unit": 0.0,
                "unit": usage_unit,
                "efficiency": "N/A"
            }
        
        cost_per_unit = total_cost / usage_amount
        
        # Determinar eficiência relativa
        if cost_per_unit < 0.1:
            efficiency = "High"
        elif cost_per_unit < 1.0:
            efficiency = "Medium"
        else:
            efficiency = "Low"
        
        return {
            "cost_per_unit": round(cost_per_unit, 4),
            "unit": usage_unit,
            "efficiency": efficiency
        }
    
    @staticmethod
    def calculate_budget_utilization(
        spent_amount: float,
        budget_amount: float
    ) -> Dict[str, Union[float, str]]:
        """
        Calcula utilização de orçamento
        
        Args:
            spent_amount: Valor gasto
            budget_amount: Valor do orçamento
            
        Returns:
            Dicionário com cálculos de utilização
        """
        if budget_amount == 0:
            return {
                "utilization_percentage": 0.0,
                "remaining_amount": 0.0,
                "status": "No Budget"
            }
        
        utilization = (spent_amount / budget_amount) * 100
        remaining = budget_amount - spent_amount
        
        # Determinar status
        if utilization <= 50:
            status = "On Track"
        elif utilization <= 80:
            status = "Monitor"
        elif utilization <= 100:
            status = "Warning"
        else:
            status = "Over Budget"
        
        return {
            "utilization_percentage": round(utilization, 2),
            "remaining_amount": round(remaining, 2),
            "status": status,
            "over_budget": utilization > 100
        }
    
    @staticmethod
    def calculate_cost_forecast(
        historical_costs: List[float],
        periods_ahead: int = 3,
        method: str = "linear"
    ) -> Dict[str, Union[List[float], str]]:
        """
        Calcula previsão de custos
        
        Args:
            historical_costs: Custos históricos
            periods_ahead: Períodos para prever
            method: Método de previsão (linear, exponential)
            
        Returns:
            Dicionário com previsões
        """
        if len(historical_costs) < 2:
            return {
                "forecast": [0.0] * periods_ahead,
                "confidence": "Low",
                "method": method
            }
        
        if method == "linear":
            return CostCalculations._linear_forecast(historical_costs, periods_ahead)
        elif method == "exponential":
            return CostCalculations._exponential_forecast(historical_costs, periods_ahead)
        else:
            raise ValueError("Method must be 'linear' or 'exponential'")
    
    @staticmethod
    def _linear_forecast(
        costs: List[float], 
        periods: int
    ) -> Dict[str, Union[List[float], str]]:
        """Previsão linear simples"""
        # Calcular tendência linear
        n = len(costs)
        x_values = list(range(n))
        
        # Regressão linear simples
        sum_x = sum(x_values)
        sum_y = sum(costs)
        sum_xy = sum(x * y for x, y in zip(x_values, costs))
        sum_x2 = sum(x * x for x in x_values)
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n
        
        # Gerar previsões
        forecast = []
        for i in range(periods):
            future_x = n + i
            predicted_cost = slope * future_x + intercept
            forecast.append(max(0.0, round(predicted_cost, 2)))
        
        # Determinar confiança baseada em R²
        r_squared = CostCalculations._calculate_r_squared(costs, slope, intercept)
        
        if r_squared > 0.8:
            confidence = "High"
        elif r_squared > 0.5:
            confidence = "Medium"
        else:
            confidence = "Low"
        
        return {
            "forecast": forecast,
            "confidence": confidence,
            "method": "linear",
            "r_squared": round(r_squared, 3)
        }
    
    @staticmethod
    def _exponential_forecast(
        costs: List[float], 
        periods: int
    ) -> Dict[str, Union[List[float], str]]:
        """Previsão exponencial baseada em taxa de crescimento"""
        growth_rate = StatisticalCalculations.calculate_growth_rate(costs)
        
        if growth_rate is None:
            return {
                "forecast": costs[-1:] * periods,
                "confidence": "Low",
                "method": "exponential"
            }
        
        last_cost = costs[-1]
        monthly_multiplier = 1 + (growth_rate / 100)
        
        forecast = []
        for i in range(periods):
            predicted_cost = last_cost * (monthly_multiplier ** (i + 1))
            forecast.append(round(predicted_cost, 2))
        
        return {
            "forecast": forecast,
            "confidence": "Medium",
            "method": "exponential",
            "growth_rate": growth_rate
        }
    
    @staticmethod
    def _calculate_r_squared(
        actual_values: List[float],
        slope: float,
        intercept: float
    ) -> float:
        """Calcula R² para regressão linear"""
        n = len(actual_values)
        x_values = list(range(n))
        
        # Valores preditos
        predicted = [slope * x + intercept for x in x_values]
        
        # Média dos valores reais
        mean_actual = sum(actual_values) / n
        
        # Soma dos quadrados
        ss_res = sum((actual - pred) ** 2 for actual, pred in zip(actual_values, predicted))
        ss_tot = sum((actual - mean_actual) ** 2 for actual in actual_values)
        
        if ss_tot == 0:
            return 1.0
        
        r_squared = 1 - (ss_res / ss_tot)
        return max(0.0, r_squared)