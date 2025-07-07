#!/usr/bin/env python3

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

print("Iniciando script...")

try:
    from app.forecast_analytics import ForecastAnalyzer
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from datetime import date, timedelta
    print("Imports OK")
    
    # Inicializar componentes
    engine = create_engine(os.environ.get('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    print("DB connection OK")
    
    forecast_analyzer = ForecastAnalyzer(db)
    print("ForecastAnalyzer created")
    
    # Primeiro verificar quais dados existem
    print("\n📊 VERIFICANDO DADOS DISPONÍVEIS:")
    from app.models import FocusCostData
    from sqlalchemy import func
    
    # Contar registros totais
    total_records = db.query(func.count(FocusCostData.id)).scalar()
    print(f"Total de registros: {total_records}")
    
    if total_records == 0:
        print("❌ Nenhum dado encontrado no banco!")
        sys.exit(1)
    
    # Contar registros por provider
    providers_query = db.query(
        FocusCostData.provider_name,
        func.count(FocusCostData.id).label('count'),
        func.min(FocusCostData.billing_period_start).label('min_date'),
        func.max(FocusCostData.billing_period_start).label('max_date')
    ).group_by(FocusCostData.provider_name).all()
    
    print(f"Providers disponíveis:")
    for p in providers_query:
        print(f"  {p.provider_name}: {p.count:,} registros ({p.min_date} a {p.max_date})")
    
    # Tentar forecast com todos os dados
    end_date = date.today()
    start_date = end_date - timedelta(days=365)
    
    print(f"\n🚀 TESTANDO FORECAST:")
    print(f"Período: {start_date} a {end_date}")
    
    try:
        result = forecast_analyzer.generate_forecast(
            provider_name=None,
            start_date=start_date,
            end_date=end_date
        )
        
        print(f"✅ Forecast gerado com sucesso!")
        print(f"Total de pontos: {len(result.forecast_data)}")
        print(f"Acurácia: {result.metadata.model_accuracy:.2f}%")
        
        print(f"\n📅 SEQUÊNCIA DE MESES:")
        for i, point in enumerate(result.forecast_data):
            data_type = "ACTUAL" if point.actual is not None else "FORECAST"
            value = point.actual if point.actual is not None else point.forecast
            print(f"  {i+1:2d}. {point.month} - {data_type}: ${value:,.0f}")
            
    except Exception as e:
        print(f"❌ Erro no forecast: {e}")
        
        # Tentar com provider específico
        if providers_query:
            first_provider = providers_query[0].provider_name
            print(f"\n🔄 Tentando com provider específico: {first_provider}")
            try:
                result = forecast_analyzer.generate_forecast(
                    provider_name=first_provider,
                    start_date=start_date,
                    end_date=end_date
                )
                
                print(f"✅ Forecast gerado com {first_provider}!")
                print(f"Total de pontos: {len(result.forecast_data)}")
                print(f"Acurácia: {result.metadata.model_accuracy:.2f}%")
                
            except Exception as e2:
                print(f"❌ Erro com provider específico: {e2}")
    
    db.close()
    
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()

print("\nScript concluído.")
