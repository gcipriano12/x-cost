#!/usr/bin/env python3
"""
Script para simular exatamente o que a API faz e encontrar a diferença
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from datetime import date, timedelta
from app.database import SessionLocal
from app.cost_analytics.dashboard.dashboard_analyzer import DashboardAnalyzer

def simulate_api_call():
    print("🔍 Simulando exatamente o que a API /dashboard/summary faz...")
    
    try:
        # Obter conexão com banco (igual à API)
        db = SessionLocal()
        print("✅ Conexão com banco estabelecida")
        
        # SIMULAR EXATAMENTE O QUE A API FAZ
        
        # 1. Parâmetros da API
        period_days = 30
        provider_name = None
        providers = None
        
        # 2. Determinar período (igual à API)
        end_date = date.today()
        start_date = end_date - timedelta(days=period_days - 1)
        print(f"📅 Período calculado pela API: {start_date} a {end_date}")
        
        # 3. Processar lista de provedores (igual à API)
        provider_list = None
        if provider_name:
            provider_list = [provider_name]
        elif providers:
            provider_list = [p.strip() for p in providers.split(',') if p.strip()]
        print(f"🔧 Provider list: {provider_list}")
        
        # 4. Criar DashboardAnalyzer (igual à API)
        dashboard_analyzer = DashboardAnalyzer(db)
        print("✅ DashboardAnalyzer criado")
        
        # 5. Chamar get_dashboard_summary (igual à API)
        print("\n🚀 Chamando get_dashboard_summary (igual à API)...")
        summary = dashboard_analyzer.get_dashboard_summary(
            start_date=start_date,
            end_date=end_date,
            providers=provider_list
        )
        
        # 6. Verificar resultado
        print(f"\n📊 RESULTADO:")
        print(f"Keys no summary: {list(summary.keys())}")
        print(f"Highlights present: {'highlights' in summary}")
        if 'highlights' in summary:
            print(f"Highlights value: {summary['highlights']}")
            print(f"Highlights type: {type(summary['highlights'])}")
        else:
            print("❌ Highlights NOT in summary!")
        
        if 'error' in summary:
            print(f"❌ Error in summary: {summary['error']}")
        
        # 7. Verificar cost_summary para comparação
        if 'cost_summary' in summary:
            total_cost = summary['cost_summary']['totals']['total_cost']
            print(f"💰 Total cost from cost_summary: ${total_cost:,.2f}")
        
        print("\n✅ Simulação da API concluída!")
        
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
    simulate_api_call()
