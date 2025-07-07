#!/usr/bin/env python3
"""
Script simplificado para corrigir Jan/Fev 2025 usando SQL direto
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, text
from datetime import date
import random

def fix_jan_feb_2025_simple():
    """Corrigir dados usando SQL direto"""
    
    print("🔧 CORREÇÃO SIMPLIFICADA: Janeiro e Fevereiro de 2025")
    print("=" * 60)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    
    try:
        with engine.connect() as conn:
            # Verificar situação atual
            print("\n1️⃣ SITUAÇÃO ATUAL:")
            for month in [1, 2]:
                result = conn.execute(text("""
                    SELECT provider_name, COUNT(*) as count, SUM(effective_cost) as total
                    FROM finops.focus_cost_data 
                    WHERE EXTRACT(year FROM billing_period_start) = 2025 
                    AND EXTRACT(month FROM billing_period_start) = :month
                    GROUP BY provider_name
                    ORDER BY provider_name
                """), {"month": month})
                
                month_name = ['Jan', 'Fev'][month-1]
                print(f"   {month_name}/2025:")
                for row in result:
                    print(f"      {row.provider_name}: {row.count} registros - ${row.total:,.2f}")
            
            # SQL para inserir dados em lote
            insert_sql = """
            INSERT INTO finops.focus_cost_data (
                billing_account_id, billing_account_name, billing_currency,
                billing_period_start, billing_period_end, charge_category,
                charge_description, charge_frequency, charge_period_start,
                charge_period_end, billed_cost, effective_cost, list_cost,
                pricing_category, pricing_quantity, pricing_unit,
                usage_quantity, usage_unit, provider_name, service_category,
                service_name, resource_id, resource_name, resource_type,
                region, tags, data_source
            ) VALUES (
                :billing_account_id, :billing_account_name, 'USD',
                :billing_period_start, :billing_period_end, 'Usage',
                :charge_description, 'Usage-Based', :charge_period_start,
                :charge_period_end, :effective_cost, :effective_cost, :list_cost,
                'On-Demand', :pricing_quantity, 'hours',
                :usage_quantity, 'hours', :provider_name, :service_category,
                :service_name, :resource_id, :resource_name, :resource_type,
                :region, :tags, 'synthetic'
            )
            """
            
            # Dados base para cada provider
            provider_data = {
                'AWS': {
                    'services': ['EC2', 'S3', 'RDS', 'Lambda', 'CloudFront'],
                    'regions': ['us-east-1', 'us-west-2', 'eu-west-1']
                },
                'Azure': {
                    'services': ['Virtual Machines', 'Storage Account', 'SQL Database', 'Functions'],
                    'regions': ['East US', 'West Europe', 'Southeast Asia']
                },
                'GCP': {
                    'services': ['Compute Engine', 'Cloud Storage', 'Cloud SQL', 'Cloud Functions'],
                    'regions': ['us-central1', 'europe-west1', 'asia-southeast1']
                }
            }
            
            # Inserir dados para Jan e Fev 2025
            for month in [1, 2]:
                month_name = ['Jan', 'Fev'][month-1]
                print(f"\n2️⃣ INSERINDO DADOS PARA {month_name.upper()}/2025:")
                
                for provider in ['AWS', 'Azure', 'GCP']:
                    print(f"   Inserindo dados para {provider}...")
                    
                    services = provider_data[provider]['services']
                    regions = provider_data[provider]['regions']
                    
                    # Inserir 500 registros por provider
                    for i in range(500):
                        day = random.randint(1, 28 if month == 2 else 31)
                        billing_date = date(2025, month, day)
                        
                        service = random.choice(services)
                        region = random.choice(regions)
                        cost = round(random.uniform(100, 2000), 2)
                        
                        data = {
                            'billing_account_id': f'{provider.lower()}-account-{random.randint(1000, 9999)}',
                            'billing_account_name': f'{provider} Production Account',
                            'billing_period_start': billing_date,
                            'billing_period_end': billing_date,
                            'charge_description': f'{service} usage charges',
                            'charge_period_start': billing_date,
                            'charge_period_end': billing_date,
                            'effective_cost': cost,
                            'list_cost': cost * 1.1,
                            'pricing_quantity': round(random.uniform(1, 100), 2),
                            'usage_quantity': round(random.uniform(1, 100), 2),
                            'provider_name': provider,
                            'service_category': 'Compute' if 'EC2' in service or 'VM' in service or 'Compute' in service else 'Storage',
                            'service_name': service,
                            'resource_id': f'r-{random.randint(100000, 999999)}',
                            'resource_name': f'{service.lower().replace(" ", "-")}-resource-{i+1}',
                            'resource_type': service,
                            'region': region,
                            'tags': f'{{"Environment": "Production", "Department": "Engineering", "Project": "project-{random.randint(1, 20)}"}}'
                        }
                        
                        conn.execute(text(insert_sql), data)
                        
                        # Commit em lotes
                        if (i + 1) % 100 == 0:
                            conn.commit()
                    
                    print(f"      ✅ 500 registros inseridos para {provider}")
                
                conn.commit()
            
            # Verificar resultado final
            print("\n3️⃣ VERIFICAÇÃO FINAL:")
            for month in [1, 2]:
                result = conn.execute(text("""
                    SELECT provider_name, COUNT(*) as count, SUM(effective_cost) as total
                    FROM finops.focus_cost_data 
                    WHERE EXTRACT(year FROM billing_period_start) = 2025 
                    AND EXTRACT(month FROM billing_period_start) = :month
                    GROUP BY provider_name
                    ORDER BY provider_name
                """), {"month": month})
                
                month_name = ['Jan', 'Fev'][month-1]
                print(f"   {month_name}/2025:")
                
                rows = list(result)
                total_cost = sum(row.total for row in rows)
                
                for row in rows:
                    percentage = (row.total / total_cost * 100) if total_cost > 0 else 0
                    print(f"      {row.provider_name:<15}: {row.count:>4} registros - ${row.total:>12,.2f} ({percentage:>5.1f}%)")
                
                print(f"      {'TOTAL':<15}: {sum(row.count for row in rows):>4} registros - ${total_cost:>12,.2f} (100.0%)")
            
            print("\n✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
    
    except Exception as e:
        print(f"❌ Erro na correção: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_jan_feb_2025_simple()
