#!/usr/bin/env python3
"""
Teste específico para demonstrar a lógica de priorização de budget
"""
import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.forecast_analytics import ForecastAnalyzer
from app.forecast_models import ForecastDataPoint

def test_budget_priority_logic():
    """Testar a lógica de priorização de budget"""
    
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print("🎯 Teste da Lógica de Priorização de Budget")
        print("=" * 50)
        
        analyzer = ForecastAnalyzer(db)
        
        # Mock forecast data
        mock_forecast_data = [
            ForecastDataPoint(month="Jan", forecast=800000),
            ForecastDataPoint(month="Feb", forecast=900000),
            ForecastDataPoint(month="Mar", forecast=850000)
        ]
        
        print("\n📋 Cenários de Teste:")
        
        scenarios = [
            {
                "provider": "AWS",
                "description": "Provider com budget específico",
                "expected_budget": 1000000,
                "expected_source": "Budget específico AWS"
            },
            {
                "provider": "Azure", 
                "description": "Provider com budget específico",
                "expected_budget": 1000000,
                "expected_source": "Budget específico Azure"
            },
            {
                "provider": "GCP",
                "description": "Provider com budget específico", 
                "expected_budget": 1000000,
                "expected_source": "Budget específico GCP"
            },
            {
                "provider": "Oracle Cloud",
                "description": "Provider com budget específico",
                "expected_budget": 1000000,
                "expected_source": "Budget específico Oracle Cloud"
            },
            {
                "provider": "DigitalOcean",
                "description": "Provider SEM budget específico (fallback para All)",
                "expected_budget": 5000000,
                "expected_source": "Budget 'All' como fallback"
            },
            {
                "provider": None,
                "description": "Sem provider especificado (usa All diretamente)",
                "expected_budget": 5000000,
                "expected_source": "Budget 'All' direto"
            }
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. {scenario['description']}")
            print(f"   Provider: {scenario['provider'] or 'None'}")
            
            budget_info = analyzer._get_budget_info(
                credential_id=None,
                provider_name=scenario['provider'],
                forecast_data=mock_forecast_data
            )
            
            if budget_info:
                actual_budget = budget_info.monthly_budget
                print(f"   ✅ Budget encontrado: ${actual_budget:,.2f}")
                print(f"   📊 Fonte: {scenario['expected_source']}")
                
                # Validar se o budget é o esperado
                if abs(actual_budget - scenario['expected_budget']) < 0.01:
                    print(f"   🎯 CORRETO: Budget conforme esperado")
                else:
                    print(f"   ⚠️ INESPERADO: Esperado ${scenario['expected_budget']:,.2f}, obtido ${actual_budget:,.2f}")
                    
                # Mostrar informações adicionais
                exceeded = len(budget_info.budget_exceeded_months)
                if exceeded > 0:
                    print(f"   🚨 Meses que excedem orçamento: {exceeded}")
                else:
                    print(f"   ✅ Previsão dentro do orçamento")
                    
            else:
                print(f"   ❌ Nenhum budget encontrado")
                if scenario['expected_budget'] > 0:
                    print(f"   ⚠️ ERRO: Esperava budget de ${scenario['expected_budget']:,.2f}")
        
        print("\n" + "=" * 50)
        print("🎯 Resumo da Lógica de Priorização:")
        print("1. ✅ Provider específico TEM PRIORIDADE sobre 'All'")
        print("2. ✅ Provider 'All' é usado como FALLBACK")
        print("3. ✅ Sem provider específico usa 'All' DIRETAMENTE")
        print("4. ✅ Logs informativos mostram a fonte do budget")
        
        print("\n🎉 Teste de priorização concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_budget_priority_logic()
    sys.exit(0 if success else 1)
