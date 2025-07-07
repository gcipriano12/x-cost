#!/usr/bin/env python3
"""
Script para debugar o problema específico do provider distribution
"""

import os
import sys
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from app.cost_analytics import DashboardAnalyzer, CostAnalyzer
from app.cost_analytics.dashboard.dashboard_analyzer import DashboardAnalyzer as NewDashboardAnalyzer
from datetime import date, timedelta

def debug_provider_issue():
    """Debug do problema específico de provider distribution"""
    
    print("🐛 DEBUG: Provider Distribution Issue")
    print("=" * 60)
    
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 30 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"📅 Período: {start_date} a {end_date}")
        
        # 1. Query direta no banco
        print("\n1️⃣ QUERY DIRETA NO BANCO:")
        direct_query = db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).filter(
            and_(
                FocusCostData.billing_period_start >= start_date,
                FocusCostData.billing_period_start <= end_date
            )
        ).group_by(
            FocusCostData.provider_name
        ).order_by(
            func.sum(FocusCostData.effective_cost).desc()
        ).all()
        
        total_direct = sum(float(r.total_cost or 0) for r in direct_query)
        for result in direct_query:
            cost = float(result.total_cost or 0)
            percentage = (cost / total_direct * 100) if total_direct > 0 else 0
            print(f"  {result.provider_name:<15}: ${cost:>12,.2f} ({percentage:>5.1f}%)")
        
        # 2. Testar DashboardAnalyzer antigo
        print("\n2️⃣ DASHBOARD ANALYZER ANTIGO:")
        old_analyzer = DashboardAnalyzer(db)
        if hasattr(old_analyzer, '_calculate_provider_distribution'):
            old_distribution = old_analyzer._calculate_provider_distribution(start_date, end_date, None)
            print(f"  Resultado: {len(old_distribution)} providers")
            for p in old_distribution:
                print(f"  {p['provider_name']:<15}: ${p['total_cost']:>12,.2f} ({p['percentage']:>5.1f}%)")
        else:
            print("  Método _calculate_provider_distribution não encontrado")
        
        # 3. Testar DashboardAnalyzer novo
        print("\n3️⃣ DASHBOARD ANALYZER NOVO:")
        try:
            new_analyzer = NewDashboardAnalyzer(db)
            new_summary = new_analyzer.get_dashboard_summary(
                start_date=start_date,
                end_date=end_date,
                providers=None
            )
            
            if 'provider_distribution' in new_summary:
                provider_dist = new_summary['provider_distribution']
                if provider_dist:
                    print(f"  Resultado: {len(provider_dist)} providers")
                    for p in provider_dist:
                        print(f"  {p['provider_name']:<15}: ${p['total_cost']:>12,.2f} ({p.get('percentage', 0):>5.1f}%)")
                else:
                    print("  provider_distribution está vazio")
            else:
                print("  provider_distribution não encontrado na resposta")
                print(f"  Chaves disponíveis: {list(new_summary.keys())}")
        except Exception as e:
            print(f"  Erro com novo analyzer: {e}")
        
        # 4. Testar CostAnalyzer.analyze_costs_by_provider
        print("\n4️⃣ COST ANALYZER BY PROVIDER:")
        cost_analyzer = CostAnalyzer(db)
        provider_analysis = cost_analyzer.analyze_costs_by_provider(
            start_date=start_date,
            end_date=end_date,
            limit=10,
            provider_name=None
        )
        
        if 'error' in provider_analysis:
            print(f"  Erro: {provider_analysis['error']}")
        elif 'providers' in provider_analysis:
            providers = provider_analysis['providers']
            print(f"  Resultado: {len(providers)} providers")
            for p in providers:
                print(f"  {p['provider_name']:<15}: ${p['total_cost']:>12,.2f} ({p['percentage_of_total']:>5.1f}%)")
        else:
            print(f"  Estrutura inesperada: {provider_analysis}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_provider_issue()