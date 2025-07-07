#!/usr/bin/env python3
"""
Script para verificar e garantir que o budget "All" existe
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Budget

def ensure_budget_all():
    """Garantir que o budget 'All' existe"""
    
    print("🔍 Verificando budget 'All'...")
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Verificar todos os budgets
        print("\n💰 TODOS OS BUDGETS:")
        all_budgets = db.query(Budget).all()
        for budget in all_budgets:
            status = "✅ Ativo" if budget.is_active else "❌ Inativo"
            print(f"   {budget.provider_name:<15}: ${budget.budget_amount:>10,.2f} ({status})")
        
        # Procurar budget "All"
        all_budget = db.query(Budget).filter(
            Budget.provider_name == 'All'
        ).first()
        
        if all_budget:
            print(f"\n✅ Budget 'All' encontrado:")
            print(f"   Nome: {all_budget.budget_name}")
            print(f"   Valor: ${all_budget.budget_amount:,.2f}")
            print(f"   Ativo: {all_budget.is_active}")
            
            if not all_budget.is_active:
                print("⚠️ Budget 'All' está inativo. Ativando...")
                all_budget.is_active = True
                db.commit()
                print("✅ Budget 'All' ativado!")
        else:
            print("\n❌ Budget 'All' não encontrado. Criando...")
            
            new_budget = Budget(
                budget_name="Budget Global - All Providers",
                provider_name="All",
                budget_amount=Decimal("5000000.00"),  # 5M mensal
                budget_period="monthly",
                is_active=True
            )
            db.add(new_budget)
            db.commit()
            print("✅ Budget 'All' criado com sucesso!")
            print(f"   Nome: {new_budget.budget_name}")
            print(f"   Valor: ${new_budget.budget_amount:,.2f}")
        
        # Verificar novamente os budgets ativos
        print("\n💰 BUDGETS ATIVOS FINAIS:")
        active_budgets = db.query(Budget).filter(Budget.is_active == True).all()
        for budget in active_budgets:
            print(f"   {budget.provider_name:<15}: ${budget.budget_amount:>10,.2f}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    ensure_budget_all()
