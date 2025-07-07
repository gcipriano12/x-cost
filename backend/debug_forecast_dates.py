#!/usr/bin/env python3
"""
Debug script para investigar bugs de datas no forecast.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from app.cost_analytics import CostAnalyzer
from app.forecast_analytics import ForecastAnalyzer
from datetime import datetime, date, timedelta
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_forecast_dates():
    """Debugar problemas de datas no forecast"""
    print("\n=== DEBUG FORECAST DATES ===")
    
    db = next(get_db())
    try:
        # Testar ForecastAnalyzer diretamente
        forecast_analyzer = ForecastAnalyzer(db)
        
        # Obter forecast para os últimos 12 meses
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        print(f"Período: {start_date} a {end_date}")
        
        result = forecast_analyzer.generate_forecast(
            provider_name=None,
            service_name=None,
            start_date=start_date,
            end_date=end_date
        )
        
        if 'error' in result:
            print(f"Erro no forecast: {result['error']}")
            return
        
        # Debugar dados históricos
        print(f"\n--- Dados Históricos ({len(result.get('historical_data', []))}) ---")
        for i, item in enumerate(result.get('historical_data', [])[:5]):  # Primeiros 5
            print(f"{i+1}. {item}")
        
        if len(result.get('historical_data', [])) > 5:
            print("...")
            for i, item in enumerate(result.get('historical_data', [])[-5:]):  # Últimos 5
                print(f"{len(result.get('historical_data', []))-4+i}. {item}")
        
        # Debugar dados de forecast
        print(f"\n--- Dados de Forecast ({len(result.get('forecast_data', []))}) ---")
        for i, item in enumerate(result.get('forecast_data', [])):
            print(f"{i+1}. {item}")
        
        # Debugar metadata
        print(f"\n--- Metadata ---")
        metadata = result.get('metadata', {})
        for key, value in metadata.items():
            print(f"{key}: {value}")
        
        # Debugar ordem cronológica
        print(f"\n--- Verificação de Ordem Cronológica ---")
        all_data = result.get('historical_data', []) + result.get('forecast_data', [])
        
        print(f"Total de pontos de dados: {len(all_data)}")
        
        for i, item in enumerate(all_data):
            month = item.get('month', 'N/A')
            period_start = item.get('period_start', 'N/A')
            cost = item.get('cost', 0)
            
            print(f"{i+1:2d}. Month: {month:8s} | Period: {period_start} | Cost: ${cost:,.2f}")
            
            if i > 0:
                prev_period = all_data[i-1].get('period_start', '')
                curr_period = item.get('period_start', '')
                
                if prev_period and curr_period:
                    try:
                        prev_date = datetime.strptime(prev_period, '%Y-%m-%d').date()
                        curr_date = datetime.strptime(curr_period, '%Y-%m-%d').date()
                        
                        if curr_date < prev_date:
                            print(f"     ⚠️  PROBLEMA: Data {curr_date} é anterior a {prev_date}")
                        elif curr_date == prev_date:
                            print(f"     ⚠️  ATENÇÃO: Data {curr_date} repetida")
                    except Exception as e:
                        print(f"     ❌ Erro ao comparar datas: {e}")
        
    finally:
        db.close()

def debug_cost_data():
    """Debugar dados de custo disponíveis usando CostAnalyzer"""
    print("\n=== DEBUG COST DATA ===")
    
    db = next(get_db())
    try:
        cost_analyzer = CostAnalyzer(db)
        
        # Obter tendência de custos dos últimos 30 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"Buscando dados de {start_date} a {end_date}")
        
        trend_data = cost_analyzer.calculate_cost_trend(
            start_date=start_date,
            end_date=end_date,
            period="daily"
        )
        
        print(f"Dados diários disponíveis: {len(trend_data)}")
        
        if trend_data:
            print("\nPrimeiros 5 registros:")
            for i, cost in enumerate(trend_data[:5]):
                print(f"{i+1}. {cost}")
            
            if len(trend_data) > 5:
                print("\nÚltimos 5 registros:")
                for i, cost in enumerate(trend_data[-5:]):
                    print(f"{len(trend_data)-4+i}. {cost}")
        
        # Obter tendência mensal para comparar
        trend_monthly = cost_analyzer.calculate_cost_trend(
            start_date=start_date - timedelta(days=335),  # ~12 meses
            end_date=end_date,
            period="monthly"
        )
        
        print(f"\nDados mensais disponíveis: {len(trend_monthly)}")
        if trend_monthly:
            print("\nDados mensais:")
            for i, cost in enumerate(trend_monthly):
                print(f"{i+1}. {cost}")
        
    finally:
        db.close()

def main():
    print("🔍 Iniciando debug de datas do forecast...")
    
    debug_forecast_dates()
    debug_cost_data()
    
    print("\n✅ Debug concluído!")

if __name__ == "__main__":
    main()
