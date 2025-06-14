#!/usr/bin/env python3
"""
Script para criar dados de teste na tabela budgets
"""
import sys
sys.path.append('/Users/gcipriano/Repositories/xcost-api')

from app.database import get_database, db_manager
from app.models import Budget
from decimal import Decimal
from datetime import datetime

def create_test_budgets():
    """Criar orçamentos de teste"""
    print("📊 Criando dados de teste para budgets...")
    
    # Conectar ao banco
    db = next(get_database())
    
    try:
        # Limpar budgets existentes para teste limpo
        db.query(Budget).delete()
        
        # Budget 1: AWS Monthly
        aws_budget = Budget(
            budget_name="AWS Monthly Budget",
            provider_name="AWS",
            budget_amount=Decimal('25000.00'),
            budget_period="monthly",
            alert_threshold=Decimal('80.0'),
            is_active=True,
            tags={"department": "Engineering", "env": "production"}
        )
        
        # Budget 2: Azure Monthly  
        azure_budget = Budget(
            budget_name="Azure Monthly Budget",
            provider_name="Azure",
            budget_amount=Decimal('20000.00'),
            budget_period="monthly", 
            alert_threshold=Decimal('75.0'),
            is_active=True,
            tags={"department": "Data", "env": "production"}
        )
        
        # Budget 3: GCP Monthly
        gcp_budget = Budget(
            budget_name="GCP Monthly Budget",
            provider_name="GCP",
            budget_amount=Decimal('15000.00'),
            budget_period="monthly",
            alert_threshold=Decimal('85.0'),
            is_active=True,
            tags={"department": "ML", "env": "production"}
        )
        
        # Budget 4: Oracle Cloud Monthly
        oracle_budget = Budget(
            budget_name="Oracle Cloud Monthly Budget",
            provider_name="Oracle Cloud",
            budget_amount=Decimal('18000.00'),
            budget_period="monthly",
            alert_threshold=Decimal('90.0'),
            is_active=True,
            tags={"department": "Database", "env": "production"}
        )
        
        # Budget 5: General Annual Budget
        annual_budget = Budget(
            budget_name="Annual Cloud Budget",
            provider_name=None,  # Geral para todos
            budget_amount=Decimal('1200000.00'),  # R$ 1.2M por ano
            budget_period="annual",
            alert_threshold=Decimal('80.0'),
            is_active=True,
            tags={"type": "general", "scope": "company"}
        )
        
        # Budget 6: Budget inativo para teste
        inactive_budget = Budget(
            budget_name="Old AWS Budget",
            provider_name="AWS", 
            budget_amount=Decimal('10000.00'),
            budget_period="monthly",
            alert_threshold=Decimal('70.0'),
            is_active=False,  # Inativo
            tags={"status": "deprecated"}
        )
        
        # Adicionar todos
        budgets = [aws_budget, azure_budget, gcp_budget, oracle_budget, annual_budget, inactive_budget]
        
        for budget in budgets:
            db.add(budget)
        
        db.commit()
        
        print("✅ Budgets criados com sucesso!")
        
        # Exibir resumo
        active_budgets = db.query(Budget).filter(Budget.is_active == True).all()
        total_monthly = sum(float(b.budget_amount) for b in active_budgets if b.budget_period == 'monthly')
        total_annual = sum(float(b.budget_amount) for b in active_budgets if b.budget_period == 'annual')
        
        print(f"\n📋 Resumo dos orçamentos ativos:")
        print(f"  • Orçamentos mensais: R$ {total_monthly:,.2f}")
        print(f"  • Orçamentos anuais: R$ {total_annual:,.2f}")
        print(f"  • Total de budgets ativos: {len(active_budgets)}")
        
        print(f"\n📝 Detalhes dos budgets:")
        for budget in active_budgets:
            status = "🟢 Ativo" if budget.is_active else "🔴 Inativo"
            print(f"  • {budget.budget_name}: R$ {float(budget.budget_amount):,.2f} ({budget.budget_period}) {status}")
        
    except Exception as e:
        print(f"❌ Erro ao criar budgets: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_budgets()
