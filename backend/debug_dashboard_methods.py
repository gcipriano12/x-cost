#!/usr/bin/env python3
"""
Script para debugar diretamente os métodos do DashboardAnalyzer
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.cost_analytics import DashboardAnalyzer, CostAnalyzer
from datetime import date, timedelta

def debug_dashboard_methods():
    """Debug direto dos métodos do DashboardAnalyzer"""
    
    print("🔍 DEBUG: Métodos DashboardAnalyzer")
    print("=" * 50)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 90 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=89)  # 90 dias incluindo hoje
        
        print(f"📅 Período: {start_date} a {end_date}")
        
        # Inicializar analisadores
        dashboard_analyzer = DashboardAnalyzer(db)
        cost_analyzer = CostAnalyzer(db)
        
        # 1. Testar _calculate_provider_distribution diretamente
        print("\n1️⃣ TESTANDO _calculate_provider_distribution:")
        provider_dist = dashboard_analyzer._calculate_provider_distribution(start_date, end_date, None)
        print(f"   Resultado: {len(provider_dist)} providers")
        for p in provider_dist:
            print(f"      {p['provider_name']}: ${p['total_cost']:,.2f} ({p['percentage']:.1f}%)")
        
        # 2. Testar analyze_costs_by_provider diretamente
        print("\n2️⃣ TESTANDO analyze_costs_by_provider:")
        provider_analysis = cost_analyzer.analyze_costs_by_provider(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )
        if 'providers' in provider_analysis:
            print(f"   Resultado: {len(provider_analysis['providers'])} providers")
            for p in provider_analysis['providers']:
                print(f"      {p['provider_name']}: ${p['total_cost']:,.2f} ({p['percentage_of_total']:.1f}%)")
        else:
            print(f"   Erro: {provider_analysis}")
        
        # 3. Testar get_dashboard_summary completo
        print("\n3️⃣ TESTANDO get_dashboard_summary:")
        summary = dashboard_analyzer.get_dashboard_summary(
            start_date=start_date,
            end_date=end_date,
            providers=None
        )
        
        if 'error' in summary:
            print(f"   Erro: {summary['error']}")
        else:
            print(f"   Cost Summary: ${summary.get('cost_summary', {}).get('totals', {}).get('total_cost', 0):,.2f}")
            provider_dist = summary.get('provider_distribution', [])
            print(f"   Provider Distribution: {len(provider_dist)} providers")
            for p in provider_dist:
                print(f"      {p['provider_name']}: ${p['total_cost']:,.2f} ({p['percentage']:.1f}%)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_dashboard_methods()
