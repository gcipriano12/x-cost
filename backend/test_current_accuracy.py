#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from app.forecast_analytics import ForecastAnalyzer
from app.cost_analytics import CostAnalyzer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
import numpy as np

def test_current_accuracy():
    print("🔍 TESTANDO ACURÁCIA ATUAL EM PRODUÇÃO")
    print("=" * 50)
    
    # Inicializar componentes
    engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    cost_analyzer = CostAnalyzer(db)
    forecast_analyzer = ForecastAnalyzer(db)
    
    # Parâmetros do teste
    credential_id = "1"
    provider_name = "oracle"
    start_date = "2024-07-07"
    end_date = "2025-07-07"
    
    try:
        # Testar via API do forecast_analyzer como em produção
        result = forecast_analyzer.generate_forecast(
            credential_id=credential_id,
            provider_name=provider_name,
            start_date=start_date,
            end_date=end_date,
            months=7
        )
        
        print(f"📊 RESULTADOS DA API DE FORECAST:")
        print(f"   Pontos de dados: {len(result.data)}")
        print(f"   Acurácia do modelo: {result.metadata.model_accuracy:.2f}%")
        print(f"   Completude dos dados: {result.metadata.data_completeness:.1f}%")
        print(f"   Método usado: {result.metadata.forecast_method}")
        print()
        
        # Verificar se a melhoria foi aplicada
        if result.metadata.model_accuracy > 70:
            print("✅ MELHORIAS APLICADAS! Acurácia alta detectada")
            print(f"   Acurácia: {result.metadata.model_accuracy:.2f}% (esperado: ~80-90%)")
        elif result.metadata.model_accuracy > 50:
            print("🟡 MELHORIA PARCIAL: Acurácia média detectada")
            print(f"   Acurácia: {result.metadata.model_accuracy:.2f}% (anterior: ~47%)")
        else:
            print("❌ MELHORIAS NÃO APLICADAS: Acurácia ainda baixa")
            print(f"   Acurácia: {result.metadata.model_accuracy:.2f}% (sem melhoria)")
        
        print()
        print("🔍 MÉTODOS DISPONÍVEIS NO FORECAST_ANALYZER:")
        methods = [method for method in dir(forecast_analyzer) if 'smooth' in method.lower() or 'accuracy' in method.lower()]
        if methods:
            print(f"   Métodos encontrados: {methods}")
        else:
            print("   ⚠️  Métodos de suavização não encontrados")
        
        # Verificar se tem método _smooth_outliers
        if hasattr(forecast_analyzer, '_smooth_outliers'):
            print("   ✅ Método _smooth_outliers encontrado")
        else:
            print("   ❌ Método _smooth_outliers NÃO encontrado")
            
        if hasattr(forecast_analyzer, '_calculate_model_accuracy'):
            print("   ✅ Método _calculate_model_accuracy encontrado")
        else:
            print("   ❌ Método _calculate_model_accuracy NÃO encontrado")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_accuracy()
