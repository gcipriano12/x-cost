#!/usr/bin/env python3
"""
Script para corrigir os dados de Janeiro e Fevereiro de 2025
Adicionar dados para AWS, Azure e GCP que estão faltando
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date, datetime
import random
from decimal import Decimal

def fix_jan_feb_2025_data():
    """Corrigir dados de Jan/Fev 2025 adicionando registros para AWS, Azure e GCP"""
    
    print("🔧 CORREÇÃO: Janeiro e Fevereiro de 2025")
    print("=" * 60)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Verificar situação atual
        print("\n1️⃣ SITUAÇÃO ATUAL:")
        for month in [1, 2]:  # Janeiro e Fevereiro
            providers_in_month = db.query(
                FocusCostData.provider_name,
                func.count(FocusCostData.id).label('count'),
                func.sum(FocusCostData.effective_cost).label('total')
            ).filter(
                func.extract('year', FocusCostData.billing_period_start) == 2025,
                func.extract('month', FocusCostData.billing_period_start) == month
            ).group_by(FocusCostData.provider_name).all()
            
            month_name = ['Jan', 'Fev'][month-1]
            print(f"   {month_name}/2025:")
            for provider in providers_in_month:
                print(f"      {provider.provider_name}: {provider.count} registros - ${provider.total:,.2f}")
        
        # Definir dados base para geração
        missing_providers = ['AWS', 'Azure', 'GCP']
        months_to_fix = [
            {'year': 2025, 'month': 1, 'days': 31},  # Janeiro
            {'year': 2025, 'month': 2, 'days': 28}   # Fevereiro
        ]
        
        # Serviços típicos por provider
        services_by_provider = {
            'AWS': ['EC2', 'S3', 'RDS', 'Lambda', 'CloudFront', 'EBS', 'VPC'],
            'Azure': ['Virtual Machines', 'Storage Account', 'SQL Database', 'App Service', 'CDN', 'Functions'],
            'GCP': ['Compute Engine', 'Cloud Storage', 'Cloud SQL', 'Cloud Functions', 'BigQuery', 'Cloud Run']
        }
        
        regions_by_provider = {
            'AWS': ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1'],
            'Azure': ['East US', 'West Europe', 'Southeast Asia', 'Central US'],
            'GCP': ['us-central1', 'europe-west1', 'asia-southeast1', 'us-east1']
        }
        
        total_added = 0
        
        # Gerar dados para cada mês problemático
        for month_info in months_to_fix:
            year = month_info['year']
            month = month_info['month']
            days = month_info['days']
            month_name = ['Jan', 'Fev'][month-1]
            
            print(f"\n2️⃣ GERANDO DADOS PARA {month_name.upper()}/{year}:")
            
            for provider in missing_providers:
                records_to_add = random.randint(400, 600)  # Quantidade similar ao Oracle
                print(f"   Gerando {records_to_add} registros para {provider}...")
                
                for i in range(records_to_add):
                    # Datas aleatórias do mês
                    day = random.randint(1, days)
                    billing_date = date(year, month, day)
                    charge_datetime = datetime(year, month, day, random.randint(0, 23), random.randint(0, 59))
                    
                    # Serviço e região aleatórios
                    service = random.choice(services_by_provider[provider])
                    region = random.choice(regions_by_provider[provider])
                    
                    # Custo aleatório (similar aos outros meses)
                    base_cost = random.uniform(50, 2000)
                    effective_cost = round(Decimal(str(base_cost)), 4)
                    
                    # Criar registro (sem especificar ID - deixar auto-incremento)
                    new_record = FocusCostData(
                        billing_account_id=f"{provider.lower()}-account-{random.randint(1000, 9999)}",
                        billing_account_name=f"{provider} Production Account",
                        billing_currency="USD",
                        billing_period_start=billing_date,
                        billing_period_end=billing_date,
                        charge_category="Usage",
                        charge_description=f"{service} usage charges",
                        charge_frequency="Usage-Based",
                        charge_period_start=charge_datetime,
                        charge_period_end=charge_datetime,
                        
                        billed_cost=effective_cost,
                        effective_cost=effective_cost,
                        list_cost=effective_cost * Decimal('1.1'),
                        pricing_category="On-Demand",
                        pricing_quantity=Decimal(str(random.uniform(1, 100))),
                        pricing_unit="hours",
                        usage_quantity=Decimal(str(random.uniform(1, 100))),
                        usage_unit="hours",
                        
                        provider_name=provider,
                        service_category="Compute" if "EC2" in service or "VM" in service or "Compute" in service else "Storage",
                        service_name=service,
                        
                        resource_id=f"r-{random.randint(100000, 999999)}",
                        resource_name=f"{service.lower()}-resource-{i+1}",
                        resource_type=service,
                        region=region,
                        
                        tags={"Environment": random.choice(["Production", "Development", "Staging"]),
                              "Department": random.choice(["Engineering", "Marketing", "Sales"]),
                              "Project": f"project-{random.randint(1, 20)}"},
                        data_source="synthetic"
                    )
                    
                    db.add(new_record)
                    total_added += 1
                
                # Commit em lotes menores para evitar problemas
                if total_added % 100 == 0:
                    db.commit()
                    print(f"      ✅ {total_added} registros adicionados...")
        
        # Commit final
        db.commit()
        print(f"\n✅ CORREÇÃO CONCLUÍDA: {total_added} registros adicionados")
        
        # Verificar resultado
        print("\n3️⃣ VERIFICAÇÃO FINAL:")
        for month in [1, 2]:  # Janeiro e Fevereiro
            providers_in_month = db.query(
                FocusCostData.provider_name,
                func.count(FocusCostData.id).label('count'),
                func.sum(FocusCostData.effective_cost).label('total')
            ).filter(
                func.extract('year', FocusCostData.billing_period_start) == 2025,
                func.extract('month', FocusCostData.billing_period_start) == month
            ).group_by(FocusCostData.provider_name).order_by(FocusCostData.provider_name).all()
            
            month_name = ['Jan', 'Fev'][month-1]
            print(f"   {month_name}/2025:")
            total_month_cost = sum(float(p.total) for p in providers_in_month)
            
            for provider in providers_in_month:
                percentage = (float(provider.total) / total_month_cost * 100) if total_month_cost > 0 else 0
                print(f"      {provider.provider_name:<15}: {provider.count:>4} registros - ${provider.total:>12,.2f} ({percentage:>5.1f}%)")
            
            print(f"      {'TOTAL':<15}: {sum(p.count for p in providers_in_month):>4} registros - ${total_month_cost:>12,.2f} (100.0%)")
        
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_jan_feb_2025_data()
