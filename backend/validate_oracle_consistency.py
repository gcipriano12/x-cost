#!/usr/bin/env python3
"""
Script para validar a consistência dos dados Oracle Cloud
"""
import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import CloudProvider, FocusCostData, Budget

def validate_oracle_consistency():
    """Validar consistência dos dados Oracle Cloud"""
    
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print("🔍 Validando consistência dos dados Oracle Cloud...")
        
        # 1. Verificar provedores na tabela cloud_providers
        print("\n📋 Provedores registrados:")
        providers = db.query(CloudProvider).all()
        oracle_providers = []
        
        for provider in providers:
            print(f"  - ID: {provider.id}, Nome: {provider.provider_name}")
            if 'oracle' in provider.provider_name.lower():
                oracle_providers.append(provider)
        
        # 2. Verificar se existe apenas "Oracle Cloud"
        if len(oracle_providers) == 1 and oracle_providers[0].provider_name == "Oracle Cloud":
            print("✅ Provedor Oracle Cloud único e correto!")
        else:
            print("❌ Problema encontrado com provedores Oracle!")
            for p in oracle_providers:
                print(f"    - {p.provider_name}")
        
        # 3. Verificar dados de custo
        print("\n💰 Dados de custo por provedor:")
        cost_providers = db.query(FocusCostData.provider_name).distinct().all()
        oracle_cost_data = []
        
        for provider in cost_providers:
            count = db.query(FocusCostData).filter(FocusCostData.provider_name == provider[0]).count()
            print(f"  - {provider[0]}: {count:,} registros")
            
            if 'oracle' in provider[0].lower():
                oracle_cost_data.append((provider[0], count))
        
        # 4. Validar que só existe "Oracle Cloud" nos dados de custo
        if len(oracle_cost_data) == 1 and oracle_cost_data[0][0] == "Oracle Cloud":
            print("✅ Dados de custo Oracle Cloud consistentes!")
        else:
            print("❌ Problema encontrado nos dados de custo Oracle!")
            for name, count in oracle_cost_data:
                print(f"    - {name}: {count}")
        
        # 5. Verificar orçamentos
        print("\n📊 Orçamentos Oracle:")
        oracle_budgets = db.query(Budget).filter(
            Budget.provider_name.ilike('%oracle%')
        ).all()
        
        for budget in oracle_budgets:
            print(f"  - {budget.budget_name}: {budget.provider_name}")
        
        if all(b.provider_name == "Oracle Cloud" for b in oracle_budgets):
            print("✅ Orçamentos Oracle Cloud consistentes!")
        elif len(oracle_budgets) == 0:
            print("ℹ️ Nenhum orçamento Oracle encontrado (normal)")
        else:
            print("❌ Problema encontrado nos orçamentos Oracle!")
        
        # 6. Verificar se há referências antigas no código
        print("\n🔍 Resumo da validação:")
        total_oracle_records = sum(count for _, count in oracle_cost_data)
        
        print(f"  - Provedores Oracle únicos: {len(oracle_providers)}")
        print(f"  - Tipos de dados Oracle nos custos: {len(oracle_cost_data)}")  
        print(f"  - Total de registros Oracle: {total_oracle_records:,}")
        print(f"  - Orçamentos Oracle: {len(oracle_budgets)}")
        
        # Verificação final
        is_consistent = (
            len(oracle_providers) == 1 and 
            oracle_providers[0].provider_name == "Oracle Cloud" and
            len(oracle_cost_data) == 1 and
            oracle_cost_data[0][0] == "Oracle Cloud" and
            all(b.provider_name == "Oracle Cloud" for b in oracle_budgets)
        )
        
        if is_consistent:
            print("\n🎉 VALIDAÇÃO COMPLETA: Todos os dados Oracle Cloud estão consistentes!")
            return True
        else:
            print("\n⚠️ ATENÇÃO: Foram encontradas inconsistências nos dados Oracle!")
            return False
            
    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = validate_oracle_consistency()
    sys.exit(0 if success else 1)
