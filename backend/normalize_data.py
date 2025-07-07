#!/usr/bin/env python3
"""
Script para normalizar os dados no banco - todos os provedores em todos os meses
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date, datetime, timedelta
import random
from decimal import Decimal

def normalize_database_data():
    """Normalizar dados no banco para todos os provedores em todos os meses"""
    
    print("🔧 NORMALIZAÇÃO DOS DADOS NO BANCO")
    print("=" * 60)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Verificar estado atual
        print("\n1️⃣ ESTADO ATUAL:")
        current_providers = db.query(distinct(FocusCostData.provider_name)).all()
        all_providers = [p[0] for p in current_providers]
        print(f"   Provedores existentes: {sorted(all_providers)}")
        
        min_date = db.query(func.min(FocusCostData.billing_period_start)).scalar()
        max_date = db.query(func.max(FocusCostData.billing_period_start)).scalar()
        print(f"   Range atual: {min_date} a {max_date}")
        
        # 2. Definir período completo desejado
        start_normalize = date(2024, 1, 1)
        end_normalize = date(2025, 7, 31)  # Julho/2025 completo
        
        print(f"\n2️⃣ NORMALIZAÇÃO DESEJADA:")
        print(f"   Período: {start_normalize} a {end_normalize}")
        print(f"   Provedores: {sorted(all_providers)}")
        
        # 3. Identificar gaps por provider
        print(f"\n3️⃣ IDENTIFICANDO GAPS:")
        
        provider_gaps = {}
        for provider in all_providers:
            # Buscar range atual do provider
            provider_min = db.query(func.min(FocusCostData.billing_period_start)).filter(
                FocusCostData.provider_name == provider
            ).scalar()
            provider_max = db.query(func.max(FocusCostData.billing_period_start)).filter(
                FocusCostData.provider_name == provider
            ).scalar()
            
            gaps_before = []
            gaps_after = []
            
            # Gaps antes do início
            if provider_min > start_normalize:
                gaps_before = generate_monthly_dates(start_normalize, provider_min - timedelta(days=1))
            
            # Gaps depois do fim (até julho/2025)
            if provider_max < end_normalize:
                gaps_after = generate_monthly_dates(provider_max + timedelta(days=1), end_normalize)
            
            provider_gaps[provider] = {
                'current_range': f"{provider_min} a {provider_max}",
                'gaps_before': gaps_before,
                'gaps_after': gaps_after,
                'total_gaps': len(gaps_before) + len(gaps_after)
            }
            
            print(f"   {provider:<15}: {provider_gaps[provider]['current_range']} | {provider_gaps[provider]['total_gaps']} meses faltando")
        
        # 4. Confirmar normalização
        total_gaps = sum(gap['total_gaps'] for gap in provider_gaps.values())
        if total_gaps == 0:
            print(f"\n✅ Dados já estão normalizados!")
            return
        
        print(f"\n4️⃣ PLANO DE NORMALIZAÇÃO:")
        print(f"   Total de gaps a preencher: {total_gaps} meses")
        
        response = input(f"\n🤔 Deseja prosseguir com a normalização? (y/N): ")
        if response.lower() != 'y':
            print("❌ Normalização cancelada.")
            return
        
        # 5. Gerar dados sintéticos
        print(f"\n5️⃣ GERANDO DADOS SINTÉTICOS:")
        
        new_records = []
        record_id_counter = db.query(func.max(FocusCostData.id)).scalar() + 1
        
        for provider, gaps in provider_gaps.items():
            # Buscar dados de referência para este provider
            reference_data = db.query(FocusCostData).filter(
                FocusCostData.provider_name == provider
            ).limit(100).all()
            
            if not reference_data:
                print(f"   ⚠️ Sem dados de referência para {provider}, pulando...")
                continue
            
            # Gerar dados para gaps_before
            for gap_date in gaps['gaps_before']:
                monthly_records = generate_monthly_records(
                    provider, gap_date, reference_data, record_id_counter
                )
                new_records.extend(monthly_records)
                record_id_counter += len(monthly_records)
                print(f"   ✅ {provider}: {gap_date.strftime('%b/%Y')} - {len(monthly_records)} registros")
            
            # Gerar dados para gaps_after
            for gap_date in gaps['gaps_after']:
                monthly_records = generate_monthly_records(
                    provider, gap_date, reference_data, record_id_counter
                )
                new_records.extend(monthly_records)
                record_id_counter += len(monthly_records)
                print(f"   ✅ {provider}: {gap_date.strftime('%b/%Y')} - {len(monthly_records)} registros")
        
        # 6. Inserir dados no banco
        print(f"\n6️⃣ INSERINDO NO BANCO:")
        print(f"   Total de novos registros: {len(new_records)}")
        
        if len(new_records) > 0:
            # Inserir em lotes para performance
            batch_size = 1000
            for i in range(0, len(new_records), batch_size):
                batch = new_records[i:i+batch_size]
                db.add_all(batch)
                db.commit()
                print(f"   Inserido lote {i//batch_size + 1}/{(len(new_records)-1)//batch_size + 1}")
        
        # 7. Verificar resultado
        print(f"\n7️⃣ VERIFICAÇÃO PÓS-NORMALIZAÇÃO:")
        
        final_count = db.query(func.count(FocusCostData.id)).scalar()
        final_providers = db.query(
            FocusCostData.provider_name,
            func.count(FocusCostData.id).label('record_count'),
            func.min(FocusCostData.billing_period_start).label('min_date'),
            func.max(FocusCostData.billing_period_start).label('max_date')
        ).group_by(FocusCostData.provider_name).all()
        
        print(f"   Total de registros: {final_count:,}")
        for provider in final_providers:
            print(f"   {provider.provider_name:<15}: {provider.record_count:>6,} registros | {provider.min_date} a {provider.max_date}")
        
        print(f"\n✅ NORMALIZAÇÃO CONCLUÍDA!")
        
    except Exception as e:
        print(f"❌ Erro na normalização: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

def generate_monthly_dates(start_date, end_date):
    """Gerar lista de datas mensais entre start_date e end_date"""
    dates = []
    current = date(start_date.year, start_date.month, 1)
    end = date(end_date.year, end_date.month, 1)
    
    while current <= end:
        dates.append(current)
        # Próximo mês
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    
    return dates

def generate_monthly_records(provider, month_date, reference_data, start_id):
    """Gerar registros sintéticos para um mês específico"""
    
    # Configurações por provider
    provider_configs = {
        'AWS': {
            'services': ['EC2', 'S3', 'RDS', 'Lambda', 'CloudWatch'],
            'regions': ['us-east-1', 'us-west-2', 'eu-west-1'],
            'base_cost': 800000,
            'variance': 0.15
        },
        'Azure': {
            'services': ['Virtual Machines', 'Storage Account', 'SQL Database', 'Functions', 'Monitor'],
            'regions': ['East US', 'West Europe', 'Southeast Asia'],
            'base_cost': 750000,
            'variance': 0.12
        },
        'GCP': {
            'services': ['Compute Engine', 'Cloud Storage', 'Cloud SQL', 'Cloud Functions', 'Cloud Monitoring'],
            'regions': ['us-central1', 'europe-west1', 'asia-southeast1'],
            'base_cost': 770000,
            'variance': 0.14
        },
        'Oracle Cloud': {
            'services': ['Compute', 'Object Storage', 'Database', 'Functions', 'Monitoring'],
            'regions': ['us-ashburn-1', 'eu-frankfurt-1', 'ap-singapore-1'],
            'base_cost': 600000,
            'variance': 0.18
        }
    }
    
    config = provider_configs.get(provider, provider_configs['AWS'])
    
    # Número de registros por mês (baseado nos dados existentes)
    num_records = random.randint(80, 120)
    
    # Custo total do mês com variação
    base_monthly_cost = config['base_cost']
    monthly_variance = random.uniform(1 - config['variance'], 1 + config['variance'])
    total_monthly_cost = base_monthly_cost * monthly_variance
    
    records = []
    current_id = start_id
    
    for i in range(num_records):
        # Distribuir custo pelos registros
        record_cost = total_monthly_cost / num_records * random.uniform(0.1, 3.0)
        
        # Calcular data específica no mês
        days_in_month = 28 if month_date.month == 2 else 30
        record_day = random.randint(1, days_in_month)
        record_date = date(month_date.year, month_date.month, record_day)
        
        record = FocusCostData(
            id=current_id,
            billing_account_id=f"{provider.lower()}-account-{random.randint(1, 5)}",
            billing_account_name=f"{provider} Account {random.randint(1, 5)}",
            billing_currency="USD",
            billing_period_start=record_date,
            billing_period_end=record_date,
            charge_category="Usage",
            charge_description=f"Usage charges for {random.choice(config['services'])}",
            charge_frequency="One-Time",
            charge_period_start=datetime.combine(record_date, datetime.min.time()),
            charge_period_end=datetime.combine(record_date, datetime.max.time()),
            
            billed_cost=Decimal(str(round(record_cost, 4))),
            effective_cost=Decimal(str(round(record_cost, 4))),
            list_cost=Decimal(str(round(record_cost * 1.1, 4))),
            pricing_category="On-Demand",
            pricing_quantity=Decimal(str(round(random.uniform(1, 100), 6))),
            pricing_unit="Hours",
            usage_quantity=Decimal(str(round(random.uniform(1, 100), 6))),
            usage_unit="Hours",
            
            provider_name=provider,
            service_name=random.choice(config['services']),
            service_category="Compute" if "EC2" in config['services'][0] or "Compute" in config['services'][0] else "Storage",
            
            resource_id=f"resource-{random.randint(100000, 999999)}",
            resource_name=f"{random.choice(config['services'])}-{random.randint(1, 100)}",
            resource_type=random.choice(config['services']),
            region=random.choice(config['regions']),
            
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            data_source="synthetic_normalization"
        )
        
        records.append(record)
        current_id += 1
    
    return records

if __name__ == "__main__":
    normalize_database_data()
