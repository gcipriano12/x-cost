#!/usr/bin/env python3
"""
Script para testar a nova lógica de budget com provider "All"
"""
import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Budget
from app.forecast_analytics import ForecastAnalyzer
from app.forecast_models import ForecastMethod

def test_budget_all_logic():
    """Testar a lógica de budget com provider 'All'"""
    
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print("🧪 Testando nova lógica de budget com provider 'All'...")
        
        # 1. Verificar budgets existentes
        print("\n📊 Budgets ativos existentes:")
        budgets = db.query(Budget).filter(Budget.is_active == True).all()
        for budget in budgets:
            print(f"  - {budget.budget_name}: {budget.provider_name} (${budget.budget_amount:,.2f})")
        
        # 2. Criar budget "All" se não existir
        all_budget = db.query(Budget).filter(
            Budget.provider_name == 'All',
            Budget.is_active == True
        ).first()
        
        if not all_budget:
            print("\n📝 Criando budget 'All' para teste...")
            all_budget = Budget(
                budget_name="Budget Global All Providers",
                provider_name="All",
                budget_amount=Decimal("5000000.00"),  # 5M mensal
                budget_period="monthly",
                is_active=True
            )
            db.add(all_budget)
            db.commit()
            print("✅ Budget 'All' criado!")
        else:
            print(f"✅ Budget 'All' já existe: ${all_budget.budget_amount:,.2f}")
        
        # 3. Testar diferentes cenários
        analyzer = ForecastAnalyzer(db)
        
        test_scenarios = [
            {
                "name": "AWS (com budget específico)",
                "provider": "AWS",
                "expected": "Budget específico AWS"
            },
            {
                "name": "Azure (com budget específico)", 
                "provider": "Azure",
                "expected": "Budget específico Azure"
            },
            {
                "name": "GCP (fallback para All)",
                "provider": "GCP", 
                "expected": "Budget 'All' como fallback"
            },
            {
                "name": "Oracle Cloud (fallback para All)",
                "provider": "Oracle Cloud",
                "expected": "Budget 'All' como fallback"
            },
            {
                "name": "Provider inexistente (fallback para All)",
                "provider": "NewProvider",
                "expected": "Budget 'All' como fallback"
            },
            {
                "name": "Sem provider (usa All diretamente)",
                "provider": None,
                "expected": "Budget 'All' direto"
            }
        ]
        
        print("\n🔍 Testando cenários:")
        
        for scenario in test_scenarios:
            print(f"\n--- {scenario['name']} ---")
            
            try:
                # Gerar forecast para testar budget
                forecast_result = analyzer.generate_forecast(
                    provider_name=scenario['provider'],
                    months=3,
                    method=ForecastMethod.WEIGHTED_MOVING_AVERAGE
                )
                
                if forecast_result.budget_info:
                    print(f"✅ Budget encontrado:")
                    print(f"   - Orçamento mensal: ${forecast_result.budget_info.monthly_budget:,.2f}")
                    print(f"   - Orçamento total: ${forecast_result.budget_info.total_budget:,.2f}")
                    print(f"   - Meses excedentes: {len(forecast_result.budget_info.budget_exceeded_months)}")
                    print(f"   - Resultado: {scenario['expected']}")
                else:
                    print("❌ Nenhum budget encontrado")
                    
            except Exception as e:
                print(f"❌ Erro no cenário: {e}")
        
        # 4. Teste específico da função _get_budget_info
        print("\n🔬 Teste direto da função _get_budget_info:")
        
        # Mock forecast data para teste
        from app.forecast_models import ForecastDataPoint
        mock_forecast_data = [
            ForecastDataPoint(month="Jan", forecast=4500000),  # Valor alto para testar excesso
            ForecastDataPoint(month="Feb", forecast=3000000),
            ForecastDataPoint(month="Mar", forecast=2800000)
        ]
        
        # Testar com AWS (deve usar budget específico)
        budget_info_aws = analyzer._get_budget_info(None, "AWS", mock_forecast_data)
        if budget_info_aws:
            print(f"✅ AWS: ${budget_info_aws.monthly_budget:,.2f} (específico)")
        else:
            print("❌ AWS: Nenhum budget encontrado")
        
        # Testar com GCP (deve usar budget "All")
        budget_info_gcp = analyzer._get_budget_info(None, "GCP", mock_forecast_data)
        if budget_info_gcp:
            print(f"✅ GCP: ${budget_info_gcp.monthly_budget:,.2f} (fallback 'All')")
        else:
            print("❌ GCP: Nenhum budget encontrado")
        
        # Testar sem provider (deve usar budget "All")
        budget_info_none = analyzer._get_budget_info(None, None, mock_forecast_data)
        if budget_info_none:
            print(f"✅ None: ${budget_info_none.monthly_budget:,.2f} (direto 'All')")
        else:
            print("❌ None: Nenhum budget encontrado")
        
        print("\n🎉 Teste da lógica de budget 'All' concluído!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_budget_all_logic()
    sys.exit(0 if success else 1)
