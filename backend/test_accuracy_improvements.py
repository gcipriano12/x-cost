#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

import numpy as np
from app.forecast_analytics import ForecastAnalyzer

def test_improved_accuracy():
    print("🚀 TESTANDO MELHORIAS DE ACURÁCIA")
    print("=" * 50)
    
    # Simular dados similares aos reais (com alta variabilidade)
    # Baseado nos dados do gráfico: Jul->Dec 2024, Jan->Jul 2025
    real_monthly_costs = np.array([
        749839,    # Jul 2024
        1802709,   # Aug 2024  
        2002619,   # Sep 2024
        2026369,   # Oct 2024
        1848599,   # Nov 2024
        1908035,   # Dec 2024
        2514113,   # Jan 2025
        2584073,   # Feb 2025
        1843097,   # Mar 2025
        2396557,   # Apr 2025
        3661701,   # May 2025
        6610504,   # Jun 2025 (OUTLIER!)
        2013557    # Jul 2025
    ])
    
    print(f"📊 Dados de teste: {len(real_monthly_costs)} meses")
    print(f"💰 Valores: ${real_monthly_costs.min():,.0f} - ${real_monthly_costs.max():,.0f}")
    print(f"📈 Média: ${real_monthly_costs.mean():,.0f}")
    print(f"📊 Coef. Variação: {(real_monthly_costs.std() / real_monthly_costs.mean()) * 100:.1f}%")
    print()
    
    # Detectar outliers
    q1, q3 = np.percentile(real_monthly_costs, [25, 75])
    iqr = q3 - q1
    upper_bound = q3 + 1.5 * iqr
    outliers = real_monthly_costs > upper_bound
    print(f"🚨 Outliers detectados: {np.sum(outliers)} ({real_monthly_costs[outliers]})")
    print()
    
    # Inicializar analisador com conexão de banco simulada
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    forecast_analyzer = ForecastAnalyzer(db)
    
    # Testar accuracy ANTES das melhorias (simulando método antigo)
    print("📉 MÉTODO ANTIGO (simulação):")
    old_accuracy = simulate_old_method(real_monthly_costs)
    print(f"   Acurácia estimada: {old_accuracy:.2f}%")
    print()
    
    # Testar accuracy DEPOIS das melhorias
    print("📈 MÉTODO MELHORADO:")
    new_accuracy = forecast_analyzer._calculate_model_accuracy(real_monthly_costs)
    print(f"   Acurácia calculada: {new_accuracy:.2f}%")
    print()
    
    # Comparar melhorias
    improvement = new_accuracy - old_accuracy
    print("🎯 COMPARAÇÃO:")
    print(f"   Método antigo:     {old_accuracy:.2f}%")
    print(f"   Método melhorado:  {new_accuracy:.2f}%")
    print(f"   Melhoria:          +{improvement:.2f} pontos percentuais")
    print()
    
    if improvement > 10:
        print("✅ EXCELENTE! Melhoria significativa na acurácia")
    elif improvement > 5:
        print("✅ BOM! Melhoria considerável na acurácia")
    elif improvement > 0:
        print("✅ POSITIVO! Pequena melhoria na acurácia")
    else:
        print("❌ SEM MELHORIA: Acurácia manteve-se igual ou piorou")
    
    # Testar suavização de outliers
    print()
    print("🔧 TESTE DE SUAVIZAÇÃO DE OUTLIERS:")
    smoothed_costs = forecast_analyzer._smooth_outliers(real_monthly_costs)
    
    print(f"   Original máximo:   ${real_monthly_costs.max():,.0f}")
    print(f"   Suavizado máximo:  ${smoothed_costs.max():,.0f}")
    print(f"   Redução outlier:   {((real_monthly_costs.max() - smoothed_costs.max()) / real_monthly_costs.max()) * 100:.1f}%")
    
    # Verificar se o outlier de junho foi suavizado
    june_index = np.argmax(real_monthly_costs)  # Junho (índice do maior valor)
    print(f"   Junho original:    ${real_monthly_costs[june_index]:,.0f}")
    print(f"   Junho suavizado:   ${smoothed_costs[june_index]:,.0f}")

def simulate_old_method(costs):
    """Simula o método antigo para comparação"""
    if len(costs) < 4:
        return 70.0
    
    # Método antigo: janela de 3 meses, sem suavização, só MAPE
    split_point = int(len(costs) * 0.7)
    train_costs = costs[:split_point]
    test_costs = costs[split_point:]
    
    if len(test_costs) == 0:
        return 70.0
    
    predictions = []
    for i in range(len(test_costs)):
        if len(train_costs) >= 3:
            pred = np.mean(train_costs[-3:])  # Só 3 meses
        else:
            pred = np.mean(train_costs)
        predictions.append(pred)
        train_costs = np.append(train_costs, test_costs[i])
    
    # Só MAPE, sem suavização
    mape = np.mean(np.abs((test_costs - predictions) / np.maximum(test_costs, 1))) * 100
    accuracy = max(0, 100 - mape)
    
    return min(accuracy, 95.0)

if __name__ == "__main__":
    test_improved_accuracy()
