#!/usr/bin/env python3
"""
Script para testar manualmente o endpoint de forecast
"""
import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

import json
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import FocusCostData, Budget
from app.forecast_analytics import ForecastAnalyzer
from app.forecast_models import ForecastMethod

def test_forecast_manually():
    """Teste manual do ForecastAnalyzer"""
    
    # Configurar banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        print("🧪 Testando ForecastAnalyzer...")
        
        # Criar dados de teste se não existirem
        print("📊 Verificando dados históricos...")
        
        end_date = date.today()
        start_date = end_date - timedelta(days=180)  # 6 meses
        
        existing_data = db.query(FocusCostData).filter(
            FocusCostData.provider_name == "AWS",
            FocusCostData.billing_period_start >= start_date
        ).count()
        
        if existing_data < 3:
            print("📝 Criando dados de teste...")
            monthly_costs = [45000, 47000, 52000, 48000, 51000, 49000]
            
            for i, cost in enumerate(monthly_costs):
                cost_date = start_date + timedelta(days=30 * i)
                cost_data = FocusCostData(
                    billing_period_start=cost_date,
                    billing_period_end=cost_date + timedelta(days=29),
                    provider_name="AWS",
                    service_name="EC2-Instance",
                    billed_cost=Decimal(str(cost)),
                    effective_cost=Decimal(str(cost)),
                    billing_currency="USD"
                )
                db.add(cost_data)
            
            # Criar orçamento de teste
            existing_budget = db.query(Budget).filter(
                Budget.provider_name == "AWS"
            ).first()
            
            if not existing_budget:
                budget = Budget(
                    budget_name="AWS Test Budget",
                    provider_name="AWS",
                    budget_amount=Decimal("50000.00"),
                    budget_period="monthly",
                    is_active=True
                )
                db.add(budget)
            
            db.commit()
            print("✅ Dados de teste criados!")
        else:
            print(f"✅ Encontrados {existing_data} registros de dados históricos")
        
        # Testar o analisador
        print("🔮 Gerando previsão...")
        
        analyzer = ForecastAnalyzer(db)
        
        # Testar com média móvel ponderada
        forecast_result = analyzer.generate_forecast(
            provider_name="AWS",
            months=6,
            method=ForecastMethod.WEIGHTED_MOVING_AVERAGE
        )
        
        print("📈 Resultado da Previsão:")
        print(f"  - Período: {forecast_result.period.start_date} a {forecast_result.period.end_date}")
        print(f"  - Meses de previsão: {forecast_result.period.forecast_months}")
        print(f"  - Acurácia do modelo: {forecast_result.metadata.model_accuracy:.1f}%")
        print(f"  - Completude dos dados: {forecast_result.metadata.data_completeness:.1f}%")
        print(f"  - Método: {forecast_result.metadata.forecast_method}")
        
        if forecast_result.budget_info:
            print(f"  - Orçamento mensal: ${forecast_result.budget_info.monthly_budget:,.2f}")
            print(f"  - Meses que excedem orçamento: {len(forecast_result.budget_info.budget_exceeded_months)}")
        
        print("\n📊 Dados de Previsão:")
        for i, point in enumerate(forecast_result.forecast_data):
            if i < 5:  # Mostrar apenas os primeiros 5
                actual_str = f"${point.actual:,.0f}" if point.actual else "N/A"
                forecast_str = f"${point.forecast:,.0f}" if point.forecast else "N/A"
                print(f"  {point.month}: Atual={actual_str}, Previsão={forecast_str}")
            elif i == 5:
                print("  ...")
        
        # Testar com regressão linear
        print("\n🔬 Testando com Regressão Linear...")
        
        forecast_linear = analyzer.generate_forecast(
            provider_name="AWS",
            months=3,
            method=ForecastMethod.LINEAR_REGRESSION
        )
        
        print(f"  - Acurácia (Regressão): {forecast_linear.metadata.model_accuracy:.1f}%")
        print(f"  - Método: {forecast_linear.metadata.forecast_method}")
        
        print("\n✅ Teste concluído com sucesso!")
        
        # Salvar resultado em JSON para debug
        with open('/tmp/forecast_test_result.json', 'w') as f:
            json.dump(forecast_result.model_dump(), f, indent=2, default=str)
        print("📄 Resultado salvo em /tmp/forecast_test_result.json")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        db.close()

if __name__ == "__main__":
    success = test_forecast_manually()
    sys.exit(0 if success else 1)
