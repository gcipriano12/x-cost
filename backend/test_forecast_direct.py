#!/usr/bin/env python3
"""
Teste direto do ForecastAnalyzer
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from app.forecast_analytics import ForecastAnalyzer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Setup
engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Test forecast
    analyzer = ForecastAnalyzer(db)
    result = analyzer.generate_forecast(months=7)

    print('📊 TESTE DO FORECAST:')
    print(f'Período: {result.period.start_date} a {result.period.end_date}')
    print(f'Total de pontos de previsão: {len(result.forecast_data)}')
    print(f'Acurácia do modelo: {result.metadata.model_accuracy}%')
    print(f'Completude dos dados: {result.metadata.data_completeness}%')
    print(f'Método: {result.metadata.forecast_method}')

    print('\n📈 DADOS DA PREVISÃO:')
    for point in result.forecast_data:
        actual_str = f"${point.actual:,.2f}" if point.actual else "N/A"
        forecast_str = f"${point.forecast:,.2f}" if point.forecast else "N/A"
        print(f'{point.month}: Atual={actual_str} | Previsão={forecast_str}')

    if result.budget_info:
        print(f'\n💰 BUDGET INFO:')
        print(f'Orçamento mensal: ${result.budget_info.monthly_budget:,.2f}')
        print(f'Meses excedendo budget: {result.budget_info.budget_exceeded_months}')
    else:
        print('\n💰 Nenhum orçamento configurado')

except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
