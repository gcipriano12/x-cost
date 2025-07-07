#!/usr/bin/env python3
"""
Script para testar o endpoint de forecast especificamente com Oracle Cloud
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.forecast_analytics import ForecastAnalyzer
from app.forecast_models import ForecastMethod
from datetime import date
import json

def test_oracle_cloud_forecast():
    """Testar forecast especificamente para Oracle Cloud"""
    
    print("🔮 Testando Forecast para Oracle Cloud...")
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Criar analyzer
        analyzer = ForecastAnalyzer(db)
        
        # Teste 1: Forecast para Oracle Cloud específico
        print("\n1️⃣ Testando forecast para Oracle Cloud...")
        result = analyzer.generate_forecast(
            provider_name="Oracle Cloud",
            months=6,
            method=ForecastMethod.WEIGHTED_MOVING_AVERAGE
        )
        
        print(f"✅ Forecast gerado:")
        print(f"   📅 Período: {result.period.start_date} a {result.period.end_date}")
        print(f"   📊 Meses previstos: {len([p for p in result.forecast_data if p.forecast])}")
        print(f"   🎯 Acurácia: {result.metadata.model_accuracy:.1f}%")
        print(f"   📈 Método: {result.metadata.forecast_method}")
        
        if result.budget_info:
            print(f"   💰 Budget mensal: ${result.budget_info.monthly_budget:,.2f}")
            print(f"   💸 Total anual: ${result.budget_info.total_budget:,.2f}")
            print(f"   ⚠️ Meses excedidos: {len(result.budget_info.budget_exceeded_months)}")
        else:
            print("   ❌ Nenhum budget encontrado")
        
        print(f"\n📊 Dados de previsão:")
        for point in result.forecast_data[-6:]:  # Últimos 6 pontos
            if point.forecast:
                print(f"   {point.month}: ${point.forecast:,.2f}")
            else:
                print(f"   {point.month}: ${point.actual:,.2f} (atual)")
        
        # Teste 2: Comparar com provider inexistente (deve usar fallback)
        print("\n2️⃣ Testando com provider inexistente (fallback para 'All')...")
        result_fallback = analyzer.generate_forecast(
            provider_name="Provider Inexistente",
            months=6,
            method=ForecastMethod.WEIGHTED_MOVING_AVERAGE
        )
        
        if result_fallback.budget_info:
            print(f"   ✅ Budget fallback encontrado: ${result_fallback.budget_info.monthly_budget:,.2f}")
        else:
            print("   ❌ Nenhum budget fallback encontrado")
        
        # Teste 3: Sem provider (deve usar "All")
        print("\n3️⃣ Testando sem provider específico (deve usar 'All')...")
        result_all = analyzer.generate_forecast(
            provider_name=None,
            months=6,
            method=ForecastMethod.WEIGHTED_MOVING_AVERAGE
        )
        
        if result_all.budget_info:
            print(f"   ✅ Budget 'All' encontrado: ${result_all.budget_info.monthly_budget:,.2f}")
        else:
            print("   ❌ Nenhum budget 'All' encontrado")
        
        # Comparação de budgets
        print("\n📋 Comparação de budgets:")
        budgets = [
            ("Oracle Cloud", result.budget_info),
            ("Provider Inexistente", result_fallback.budget_info),
            ("Sem provider", result_all.budget_info)
        ]
        
        for name, budget_info in budgets:
            if budget_info:
                print(f"   {name:<20}: ${budget_info.monthly_budget:,.2f}")
            else:
                print(f"   {name:<20}: Nenhum budget")
        
        print("\n🎉 Teste Oracle Cloud concluído!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_oracle_cloud_forecast()
