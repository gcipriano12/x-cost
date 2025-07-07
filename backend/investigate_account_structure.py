#!/usr/bin/env python3
"""
Script para investigar estrutura de dados de contas no banco
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date, timedelta

def investigate_account_structure():
    """Investigar como os dados de conta estão estruturados"""
    
    print("🔍 INVESTIGANDO ESTRUTURA DE CONTAS")
    print("=" * 60)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 30 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"📅 Período analisado: {start_date} a {end_date}")
        
        # 1. Verificar colunas disponíveis relacionadas a contas
        print("\n1️⃣ Campos disponíveis no modelo FocusCostData:")
        model_fields = FocusCostData.__table__.columns.keys()
        account_fields = [field for field in model_fields if 'account' in field.lower() or 'billing' in field.lower()]
        print(f"   Campos relacionados a conta: {account_fields}")
        
        # 2. Verificar dados únicos de conta para Oracle Cloud
        print("\n2️⃣ Verificando dados únicos de conta Oracle Cloud:")
        
        # Tentar diferentes campos que podem conter dados de conta
        potential_account_fields = [
            'billing_account_id',
            'billing_account_name', 
            'account_id',
            'account_name',
            'sub_account_id',
            'sub_account_name'
        ]
        
        for field_name in potential_account_fields:
            if hasattr(FocusCostData, field_name):
                field = getattr(FocusCostData, field_name)
                unique_accounts = db.query(distinct(field)).filter(
                    FocusCostData.provider_name == 'Oracle Cloud'
                ).all()
                
                print(f"   {field_name}:")
                for account in unique_accounts[:10]:  # Limitar a 10 para não poluir
                    print(f"      - {account[0]}")
        
        # 3. Verificar distribuição Oracle Cloud por conta
        print("\n3️⃣ Distribuição Oracle Cloud por conta (30 dias):")
        
        # Usar billing_account_name como campo principal
        if hasattr(FocusCostData, 'billing_account_name'):
            account_distribution = db.query(
                FocusCostData.billing_account_name,
                FocusCostData.billing_account_id,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.count().label('record_count')
            ).filter(
                FocusCostData.provider_name == 'Oracle Cloud',
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date
            ).group_by(
                FocusCostData.billing_account_name,
                FocusCostData.billing_account_id
            ).order_by(
                func.sum(FocusCostData.effective_cost).desc()
            ).all()
            
            total_oracle_cost = sum(acc.total_cost for acc in account_distribution if acc.total_cost)
            
            print(f"   Total Oracle Cloud: ${total_oracle_cost:,.2f}")
            print(f"   Número de contas: {len(account_distribution)}")
            
            for account in account_distribution:
                percentage = (account.total_cost / total_oracle_cost * 100) if total_oracle_cost > 0 else 0
                print(f"   - ID: {account.billing_account_id}")
                print(f"     Nome: {account.billing_account_name}")
                print(f"     Custo: ${account.total_cost:,.2f} ({percentage:.1f}%)")
                print(f"     Registros: {account.record_count}")
                print()
        
        # 4. Verificar outros provedores para comparação
        print("\n4️⃣ Verificando estrutura de outros provedores:")
        
        for provider in ['AWS', 'Azure', 'GCP']:
            if hasattr(FocusCostData, 'billing_account_name'):
                provider_accounts = db.query(
                    distinct(FocusCostData.billing_account_name)
                ).filter(
                    FocusCostData.provider_name == provider
                ).limit(3).all()
                
                print(f"   {provider} (sample):")
                for account in provider_accounts:
                    print(f"      - {account[0]}")
        
    except Exception as e:
        print(f"❌ Erro durante investigação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    investigate_account_structure()
