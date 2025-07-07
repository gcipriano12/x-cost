#!/usr/bin/env python3
"""
Script para verificar dados de provider no banco
"""

import os
import sys
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date, timedelta

def check_provider_data():
    """Verificar dados dos providers no banco"""
    
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Verificar dados dos últimos 30 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f'Período: {start_date} a {end_date}')
        print()
        
        # Query simples por provider
        provider_costs = db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count(FocusCostData.id).label('record_count')
        ).filter(
            FocusCostData.billing_period_start >= start_date,
            FocusCostData.billing_period_start <= end_date
        ).group_by(FocusCostData.provider_name).all()
        
        total_all = sum(p.total_cost for p in provider_costs)
        print('DISTRIBUIÇÃO POR PROVIDER (30 dias):')
        for p in provider_costs:
            pct = (p.total_cost / total_all * 100) if total_all > 0 else 0
            print(f'  {p.provider_name:<15}: ${p.total_cost:>12,.2f} ({pct:>5.1f}%) - {p.record_count:>6} registros')
        
        print(f'  TOTAL: ${total_all:,.2f}')
        
        # Verificar dados únicos de provider_name
        print('\nVALORES ÚNICOS DE PROVIDER_NAME:')
        unique_providers = db.query(
            FocusCostData.provider_name
        ).distinct().all()
        
        for p in unique_providers:
            print(f'  - "{p.provider_name}"')
        
    except Exception as e:
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_provider_data()