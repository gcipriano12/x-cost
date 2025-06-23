#!/usr/bin/env python3
"""
Script de debug para testar highlights isoladamente
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from datetime import date
from app.database import SessionLocal
from app.cost_analytics.dashboard.dashboard_analyzer import DashboardAnalyzer

def test_highlights():
    print("🔍 Testando highlights isoladamente...")
    
    try:
        # Obter conexão com banco
        db = SessionLocal()
        print("✅ Conexão com banco estabelecida")
        
        # Criar analyzer
        analyzer = DashboardAnalyzer(db)
        print("✅ DashboardAnalyzer criado")
        
        # Testar cada método isoladamente
        start_date = date(2025, 5, 24)
        end_date = date(2025, 6, 22)
        providers = None
        
        print(f"📅 Período: {start_date} a {end_date}")
        
        # 1. Testar _get_total_cost
        print("\n1️⃣ Testando _get_total_cost...")
        total_cost = analyzer._get_total_cost(start_date, end_date, providers)
        print(f"💰 Total cost: ${total_cost:,.2f}")
        
        # 2. Testar _calculate_estimated_waste
        print("\n2️⃣ Testando _calculate_estimated_waste...")
        waste = analyzer._calculate_estimated_waste(total_cost, providers)
        print(f"🗑️ Waste: {waste}")
        
        # 3. Testar _calculate_savings_achieved
        print("\n3️⃣ Testando _calculate_savings_achieved...")
        savings = analyzer._calculate_savings_achieved(total_cost, providers)
        print(f"💎 Savings: {savings}")
        
        # 4. Testar _calculate_next_month_forecast
        print("\n4️⃣ Testando _calculate_next_month_forecast...")
        period_days = (end_date - start_date).days + 1
        forecast = analyzer._calculate_next_month_forecast(total_cost, period_days, providers)
        print(f"🔮 Forecast: {forecast}")
        
        # 5. Testar método completo
        print("\n5️⃣ Testando _calculate_highlights completo...")
        highlights = analyzer._calculate_highlights(start_date, end_date, providers)
        print(f"✨ Highlights completos: {highlights}")
        
        print("\n✅ Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        print(f"🔍 Traceback completo:")
        traceback.print_exc()
    finally:
        # Fechar conexão com banco
        db.close()
        print("🔒 Conexão com banco fechada")

if __name__ == "__main__":
    test_highlights()
