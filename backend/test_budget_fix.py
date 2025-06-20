#!/usr/bin/env python3
"""
Script de teste para verificar se as correções do Budget estão funcionando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Budget
from app.cost_analytics.budget.budget_analyzer import BudgetAnalyzer
from decimal import Decimal
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_budget_model():
    """Testa se o modelo Budget está funcionando corretamente"""
    print("🔍 Testando modelo Budget...")
    
    db: Session = SessionLocal()
    try:
        # Tentar buscar todos os budgets
        budgets = db.query(Budget).all()
        print(f"✅ Encontrados {len(budgets)} budgets no banco")
        
        if budgets:
            budget = budgets[0]
            print(f"✅ Budget exemplo:")
            print(f"   - ID: {budget.id}")
            print(f"   - Nome: {budget.budget_name}")  # Campo correto
            print(f"   - Valor: {budget.budget_amount}")  # Campo correto
            print(f"   - Provider: {budget.provider_name}")
            print(f"   - Período: {budget.budget_period}")
            print(f"   - Ativo: {budget.is_active}")
            
            # Verificar se campos antigos não existem mais
            try:
                _ = budget.amount  # Campo incorreto
                print("❌ ERRO: Campo 'amount' ainda existe!")
                return False
            except AttributeError:
                print("✅ Campo 'amount' removido corretamente")
            
            try:
                _ = budget.name  # Campo incorreto
                print("❌ ERRO: Campo 'name' ainda existe!")
                return False
            except AttributeError:
                print("✅ Campo 'name' removido corretamente")
                
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar modelo Budget: {e}")
        return False
    finally:
        db.close()

def test_budget_analyzer():
    """Testa se o BudgetAnalyzer está funcionando corretamente"""
    print("\n🔍 Testando BudgetAnalyzer...")
    
    db: Session = SessionLocal()
    try:
        analyzer = BudgetAnalyzer(db)
        
        # Testar resumo dos budgets
        summary = analyzer.get_budget_summary()
        
        if 'error' in summary:
            print(f"❌ Erro no BudgetAnalyzer: {summary['error']}")
            return False
        
        print(f"✅ Resumo dos budgets:")
        print(f"   - Total de budgets: {summary['total_budgets']}")
        print(f"   - Budgets ativos: {summary['active_budgets']}")
        print(f"   - Valor total: {summary['total_budget_amount']}")
        
        # Se há budgets, testar utilização
        if summary['budgets']:
            budget_id = summary['budgets'][0]['id']
            utilization = analyzer.calculate_budget_utilization(budget_id)
            
            if 'error' in utilization:
                print(f"❌ Erro ao calcular utilização: {utilization['error']}")
                return False
            
            print(f"✅ Utilização do budget {budget_id}:")
            print(f"   - Valor do budget: {utilization['budget_amount']}")
            print(f"   - Período: {utilization['period']}")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar BudgetAnalyzer: {e}")
        return False
    finally:
        db.close()

def create_test_budget():
    """Cria um budget de teste para verificar se a API está funcionando"""
    print("\n🔍 Criando budget de teste...")
    
    db: Session = SessionLocal()
    try:
        # Criar um budget de teste
        test_budget = Budget(
            budget_name="Budget de Teste",
            provider_name="AWS", 
            service_name="EC2",
            budget_amount=Decimal("1000.00"),
            budget_period="monthly",
            alert_threshold=Decimal("80.0"),
            is_active=True,
            tags={"test": True}
        )
        
        db.add(test_budget)
        db.commit()
        db.refresh(test_budget)
        
        print(f"✅ Budget de teste criado com ID: {test_budget.id}")
        print(f"   - Nome: {test_budget.budget_name}")
        print(f"   - Valor: {test_budget.budget_amount}")
        
        return test_budget.id
        
    except Exception as e:
        print(f"❌ Erro ao criar budget de teste: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def cleanup_test_budget(budget_id):
    """Remove o budget de teste"""
    if not budget_id:
        return
        
    print(f"\n🧹 Removendo budget de teste {budget_id}...")
    
    db: Session = SessionLocal()
    try:
        budget = db.query(Budget).filter(Budget.id == budget_id).first()
        if budget:
            db.delete(budget)
            db.commit()
            print("✅ Budget de teste removido")
        
    except Exception as e:
        print(f"❌ Erro ao remover budget de teste: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Executa todos os testes"""
    print("🚀 Iniciando testes do sistema Budget corrigido\n")
    
    success = True
    test_budget_id = None
    
    try:
        # Teste 1: Verificar modelo Budget
        if not test_budget_model():
            success = False
        
        # Teste 2: Criar budget de teste
        test_budget_id = create_test_budget()
        if not test_budget_id:
            success = False
        
        # Teste 3: Verificar BudgetAnalyzer
        if not test_budget_analyzer():
            success = False
        
        if success:
            print("\n🎉 Todos os testes passaram! Sistema Budget corrigido com sucesso!")
            print("\n✅ Correções aplicadas:")
            print("   - budget.amount → budget.budget_amount")
            print("   - budget.name → budget.budget_name")
            print("   - Removidos campos inexistentes (start_date, end_date)")
            print("   - BudgetAnalyzer funcionando corretamente")
        else:
            print("\n❌ Alguns testes falharam. Verifique os erros acima.")
            return 1
            
    finally:
        # Limpeza
        cleanup_test_budget(test_budget_id)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
