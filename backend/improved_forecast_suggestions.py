# Exemplo de melhoria no algoritmo de forecast
def improved_forecast_algorithm(self, costs: np.ndarray) -> Tuple[List, float]:
    """Algoritmo melhorado de forecast com múltiplas técnicas"""
    
    # 1. Detectar e suavizar outliers
    cleaned_costs = self._remove_outliers(costs)
    
    # 2. Tentar múltiplos modelos
    models = {
        'moving_avg': self._moving_average_forecast(cleaned_costs),
        'linear_trend': self._linear_regression_forecast(cleaned_costs),
        'exponential_smoothing': self._exponential_smoothing_forecast(cleaned_costs)
    }
    
    # 3. Selecionar o melhor modelo baseado na validação
    best_model = self._select_best_model(models, cleaned_costs)
    
    # 4. Usar métrica de acurácia mais robusta
    accuracy = self._calculate_robust_accuracy(cleaned_costs, best_model)
    
    return best_model, accuracy

def _remove_outliers(self, costs: np.ndarray) -> np.ndarray:
    """Remove outliers usando IQR"""
    if len(costs) < 4:
        return costs
    
    q1, q3 = np.percentile(costs, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Suavizar outliers em vez de remover
    cleaned = costs.copy()
    median_val = np.median(costs)
    
    for i in range(len(cleaned)):
        if cleaned[i] < lower_bound or cleaned[i] > upper_bound:
            cleaned[i] = median_val
    
    return cleaned

def _calculate_robust_accuracy(self, actual: np.ndarray, predicted: np.ndarray) -> float:
    """Cálculo de acurácia mais robusto"""
    
    # Usar múltiplas métricas
    mape = np.mean(np.abs((actual - predicted) / np.maximum(actual, np.mean(actual) * 0.1))) * 100
    mae = np.mean(np.abs(actual - predicted))
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    
    # Normalizar RMSE pela média
    nrmse = rmse / np.mean(actual) * 100
    
    # Combinar métricas (menos peso para MAPE se há outliers)
    accuracy = max(0, 100 - (mape * 0.4 + nrmse * 0.6))
    
    return min(accuracy, 95.0)
