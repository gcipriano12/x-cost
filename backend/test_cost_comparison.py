#!/usr/bin/env python3
"""
Script para comparar os diferentes métodos de cálculo de custo
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from datetime import date
from app.database import SessionLocal
from app.cost_analytics.dashboard.dashboard_analyzer import DashboardAnalyzer
from app.cost_analytics.analytics.cost_analyzer import CostAnalyzer

def compare_cost_methods():
    print("🔍 Comparando métodos de cálculo de custo...")
    
    try:
        # Obter conexão com banco
        db = SessionLocal()
        print("✅ Conexão com banco estabelecida")
        
        # Período de teste (mesmo da API)
        start_date = date(2025, 5, 24)
        end_date = date(2025, 6, 22)
        providers = None
        
        print(f"📅 Período: {start_date} a {end_date}")
        
        # Método 1: DashboardAnalyzer._get_total_cost (usado no teste isolado)
        print("\n1️⃣ Testando DashboardAnalyzer._get_total_cost...")
        dashboard_analyzer = DashboardAnalyzer(db)
        total_cost_1 = dashboard_analyzer._get_total_cost(start_date, end_date, providers)
        print(f"💰 DashboardAnalyzer: ${total_cost_1:,.2f}")
        
        # Método 2: CostAnalyzer.get_cost_summary (usado na API)
        print("\n2️⃣ Testando CostAnalyzer.get_cost_summary...")
        cost_analyzer = CostAnalyzer(db)
        cost_summary = cost_analyzer.get_cost_summary(
            start_date=start_date,
            end_date=end_date,
            provider_name=None
        )
        total_cost_2 = cost_summary['totals']['total_cost']
        print(f"💰 CostAnalyzer: ${total_cost_2:,.2f}")
        
        # Comparação
        print(f"\n📊 COMPARAÇÃO:")
        print(f"DashboardAnalyzer: ${total_cost_1:,.2f}")
        print(f"CostAnalyzer:      ${total_cost_2:,.2f}")
        print(f"Diferença:         ${abs(total_cost_2 - total_cost_1):,.2f}")
        print(f"Ratio:             {total_cost_2 / total_cost_1:.2f}x")
        
        if abs(total_cost_2 - total_cost_1) > 1:
            print("❌ PROBLEMA: Os métodos retornam valores diferentes!")
        else:
            print("✅ OK: Os métodos retornam valores iguais")
        
        print("\n✅ Comparação concluída!")
        
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
    compare_cost_methods()
