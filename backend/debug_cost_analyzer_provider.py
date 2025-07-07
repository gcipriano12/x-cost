#!/usr/bin/env python3
"""
Script para debugar especificamente o CostAnalyzer.analyze_costs_by_provider
"""

import os
import sys
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.cost_analytics import CostAnalyzer
from datetime import date, timedelta

def debug_cost_analyzer_provider():
    """Debug do método analyze_costs_by_provider do CostAnalyzer"""
    
    print("🔬 DEBUG: CostAnalyzer.analyze_costs_by_provider")
    print("=" * 60)
    
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 30 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"📅 Período: {start_date} a {end_date}")
        
        # Criar analisador
        cost_analyzer = CostAnalyzer(db)
        
        # Executar método com debug
        print("\n🔍 Executando analyze_costs_by_provider com debug...")
        result = cost_analyzer.analyze_costs_by_provider(
            start_date=start_date,
            end_date=end_date,
            limit=10,
            provider_name=None
        )
        
        print(f"\n📊 RESULTADO FINAL:")
        print(f"  Total cost: ${result.get('total_cost', 0):,.2f}")
        print(f"  Providers count: {result.get('providers_count', 0)}")
        
        if 'providers' in result:
            for p in result['providers']:
                print(f"  {p['provider_name']:<15}: ${p['total_cost']:>12,.2f} ({p['percentage_of_total']:>5.1f}%)")
        
        # Verificar se o total_cost está sendo calculado corretamente
        print(f"\n🧮 VERIFICAÇÃO DE CÁLCULO:")
        if 'providers' in result:
            manual_total = sum(p['total_cost'] for p in result['providers'])
            reported_total = result.get('total_cost', 0)
            print(f"  Soma manual dos providers: ${manual_total:,.2f}")
            print(f"  Total reportado: ${reported_total:,.2f}")
            print(f"  Diferença: ${abs(manual_total - reported_total):,.2f}")
            
            # Recalcular percentuais
            print(f"\n🔢 PERCENTUAIS RECALCULADOS:")
            for p in result['providers']:
                cost = p['total_cost']
                correct_percentage = (cost / manual_total * 100) if manual_total > 0 else 0
                reported_percentage = p['percentage_of_total']
                print(f"  {p['provider_name']:<15}: {reported_percentage:>5.1f}% → {correct_percentage:>5.1f}% (diferença: {abs(reported_percentage - correct_percentage):>5.1f}%)")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_cost_analyzer_provider()