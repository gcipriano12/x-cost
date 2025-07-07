#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from app.forecast_analytics import ForecastAnalyzer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

def debug_forecast_dates():
    print("🔍 DEBUG: Investigando problema das datas no eixo X")
    print("=" * 60)
    
    # Inicializar componentes
    engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    forecast_analyzer = ForecastAnalyzer(db)
    
    # Parâmetros do teste - usar período de 12 meses como no frontend
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    print(f"📅 Período: {start_date} a {end_date}")
    print(f"🏢 Provider: oracle")
    print()
    
    try:
        # Chamar método de forecast diretamente usando generate_forecast
        result = forecast_analyzer.generate_forecast(
            provider_name="oracle",
            start_date=start_date,
            end_date=end_date
        )
        
        print("📊 DADOS DO FORECAST:")
        print(f"   Total de pontos: {len(result.forecast_data)}")
        print(f"   Período: {result.period.start_date} a {result.period.end_date}")
        print(f"   Acurácia: {result.metadata.model_accuracy:.2f}%")
        print()
        
        print("📅 SEQUÊNCIA DE MESES RETORNADA PELA API:")
        for i, point in enumerate(result.forecast_data):
            data_type = "ACTUAL" if point.actual is not None else "FORECAST"
            value = point.actual if point.actual is not None else point.forecast
            budget = f" (Budget: ${point.budget:,.0f})" if point.budget else ""
            print(f"   {i+1:2d}. {point.month} - {data_type}: ${value:,.0f}{budget}")
        
        print()
        print("🚨 ANÁLISE DO PROBLEMA:")
        
        # Analisar a sequência de meses
        months = [point.month for point in result.forecast_data]
        print(f"   Meses na ordem: {' → '.join(months)}")
        
        # Verificar se há repetições problemáticas
        month_counts = {}
        for month in months:
            month_counts[month] = month_counts.get(month, 0) + 1
        
        repeated_months = {k: v for k, v in month_counts.items() if v > 1}
        if repeated_months:
            print(f"   ⚠️  Meses repetidos: {repeated_months}")
        
        # Verificar a lógica atual de formatação (simulada)
        print()
        print("🔧 SIMULAÇÃO DA FORMATAÇÃO ATUAL:")
        for i, point in enumerate(result.forecast_data):
            month = point.month
            has_actual = point.actual is not None
            has_forecast = point.forecast is not None
            
            # Simular lógica atual (problemática)
            if has_actual and month in ['Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                year_suffix = "24"  # 2024
            elif has_actual:
                year_suffix = "25"  # 2025
            elif has_forecast and month in ['Jan', 'Feb', 'Mar', 'Apr', 'May']:
                year_suffix = "26"  # 2026 (PROBLEMA!)
            else:
                year_suffix = "25"  # 2025
                
            formatted = f"{month}/{year_suffix}"
            print(f"   {i+1:2d}. {month} → {formatted} ({'actual' if has_actual else 'forecast'})")
        
        print()
        print("✅ SOLUÇÃO PROPOSTA:")
        print("   1. Usar índice sequencial para determinar o ano correto")
        print("   2. Calcular ano baseado na data atual e posição na sequência")
        print("   3. Assumir que dados estão em ordem cronológica")
        
        # Demonstrar solução proposta
        print()
        print("🔧 FORMATAÇÃO CORRIGIDA (PROPOSTA):")
        current_date = date.today()
        
        for i, point in enumerate(result.forecast_data):
            month = point.month
            
            # Calcular ano baseado na posição sequencial
            # Assumindo que começamos 12 meses atrás
            months_from_start = i
            target_date = current_date.replace(day=1) - timedelta(days=365) + timedelta(days=30 * months_from_start)
            year_suffix = str(target_date.year)[-2:]
            
            formatted_correct = f"{month}/{year_suffix}"
            data_type = "actual" if point.actual is not None else "forecast"
            print(f"   {i+1:2d}. {month} → {formatted_correct} ({data_type})")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_forecast_dates()
