# Endpoint de Forecast de Gastos - Documentação

## Endpoint Implementado

**URL**: `/api/v1/analytics/forecast`  
**Método**: `GET`  
**Autenticação**: Bearer Token obrigatório

## Parâmetros de Query

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `credential_id` | string | Não | ID da credencial específica |
| `provider_name` | string | Não | Filtro por provedor (AWS, Azure, GCP, Oracle Cloud) |
| `months` | integer | Não | Número de meses para previsão (1-24, default: 7) |
| `start_date` | string | Não | Data inicial para análise histórica (YYYY-MM-DD) |
| `end_date` | string | Não | Data final para análise histórica (YYYY-MM-DD) |
| `method` | string | Não | Método de previsão (default: weighted_moving_average) |

### Métodos de Previsão Disponíveis
- `weighted_moving_average` - Média móvel ponderada (padrão)
- `linear_regression` - Regressão linear
- `seasonal_decomposition` - Decomposição sazonal (futuro)
- `exponential_smoothing` - Suavização exponencial (futuro)

## Lógica de Budget com Fallback

O endpoint implementa uma **lógica de priorização inteligente** para orçamentos:

### Priorização de Budget
1. **Provider específico**: Busca primeiro um budget ativo para o provider solicitado
2. **Fallback para "All"**: Se não encontrar budget específico, usa budget com provider "All"
3. **Provider vazio**: Quando `provider_name` não especificado, usa diretamente budget "All"
4. **Sem budget**: Retorna forecast sem informações de orçamento se nenhum budget for encontrado

### Exemplos de Cenários
```
Provider "AWS" → Budget AWS específico ($1M/mês)
Provider "Digital Ocean" → Budget "All" ($5M/mês) [fallback]
Provider vazio → Budget "All" ($5M/mês) [direto]
```

### Budget "All" - Global
- Representa o orçamento total para todos os provedores
- Usado como fallback quando não há budget específico
- Útil para organizações com orçamento consolidado

## Exemplo de Request

```bash
curl -X GET "http://localhost:8000/api/v1/analytics/forecast" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -G \
  -d "provider_name=AWS" \
  -d "months=6" \
  -d "method=weighted_moving_average"
```

## Estrutura de Resposta

```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2024-01-01",
      "end_date": "2024-12-31", 
      "forecast_months": 6
    },
    "generated_at": "2024-07-06T14:30:00Z",
    "forecast_data": [
      {
        "month": "Jan",
        "actual": 280000,
        "forecast": null,
        "budget": null,
        "variance": null,
        "confidence_interval": null
      },
      {
        "month": "Jul",
        "actual": null,
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
      "budget_exceeded_months": ["Jul"]
    }
  },
  "message": "Forecast generated for 6 months using weighted_moving_average"
}
```

## Campos da Resposta

### `period`
- `start_date`: Data de início da análise (ISO format)
- `end_date`: Data de fim da previsão (ISO format)  
- `forecast_months`: Número de meses de previsão

### `forecast_data[]`
- `month`: Nome do mês (Jan, Feb, etc.)
- `actual`: Valor real dos gastos (dados históricos)
- `forecast`: Valor previsto dos gastos (dados futuros)
- `budget`: Valor do orçamento configurado
- `variance`: Diferença entre previsão e orçamento
- `confidence_interval`: Intervalo de confiança da previsão
  - `lower`: Limite inferior
  - `upper`: Limite superior

### `metadata`
- `model_accuracy`: Acurácia do modelo (0-100%)
- `confidence_level`: Nível de confiança (ex: 90%)
- `data_completeness`: Completude dos dados (0-100%)
- `forecast_method`: Método de previsão utilizado

### `budget_info` (opcional)
- `total_budget`: Orçamento total do período
- `monthly_budget`: Orçamento mensal
- `budget_exceeded_months`: Meses onde a previsão excede o orçamento

## Códigos de Status

- `200`: Sucesso - Previsão gerada
- `400`: Erro de validação (datas inválidas, dados insuficientes)
- `401`: Não autenticado
- `500`: Erro interno do servidor

## Erros Comuns

### Dados Insuficientes
```json
{
  "error": true,
  "detail": "Insufficient historical data. Minimum 3 months required.",
  "status_code": 400
}
```

### Data Inválida
```json
{
  "error": true,
  "detail": "Invalid start_date format. Use YYYY-MM-DD",
  "status_code": 400
}
```

### Range de Datas Inválido
```json
{
  "error": true,
  "detail": "start_date must be before end_date",
  "status_code": 400
}
```

## Algoritmos Implementados

### 1. Weighted Moving Average (Padrão)
- Usa os últimos 6 meses de dados
- Aplica pesos exponenciais (mais recente = maior peso)
- Adiciona tendência de crescimento baseada no último mês
- Calcula intervalo de confiança baseado no desvio padrão

### 2. Linear Regression
- Treina modelo de regressão linear com dados históricos
- Projeta tendência linear para o futuro
- Calcula acurácia usando R² score
- Intervalo de confiança baseado no erro residual

## Performance e Limites

- **Dados Mínimos**: 3 meses de dados históricos
- **Máximo de Meses**: 24 meses de previsão
- **Timeout**: ~30 segundos para grandes volumes
- **Cache**: Resultados são calculados em tempo real

## Integração com Frontend

O endpoint está pronto para integração com:
- `SpendingForecastCard.tsx`
- `useForecast.ts` hook
- Método `getForecastData` do cliente API

## Testes

Execute os testes com:
```bash
# Teste unitário
python -m pytest tests/test_forecast_endpoint.py -v

# Teste manual
python test_forecast_manual.py
```
