#!/usr/bin/env python3
"""
Script para criar dados históricos de 2024 para testar o filtro "Ano anterior"
"""

import os
import sys
import random
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, FocusCostData

# Configuração do banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finops_user:finops_password@localhost:5432/finops_db")

def create_database_connection():
    """Cria conexão com o banco de dados"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal()

def create_2024_historical_data(session):
    """Criar dados históricos de 2024 para testar o filtro 'Ano anterior'"""
    print("📅 Criando dados históricos de 2024...")
    
    providers = ["AWS", "Azure", "GCP"]
    
    services = {
        "AWS": ["EC2", "S3", "RDS", "Lambda", "CloudWatch", "ELB", "VPC", "Route53"],
        "Azure": ["Virtual Machines", "Storage", "SQL Database", "App Service", "Logic Apps"],
        "GCP": ["Compute Engine", "Cloud Storage", "BigQuery", "Cloud Functions", "Cloud SQL"]
    }
    
    regions = {
        "AWS": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
        "Azure": ["eastus", "westus2", "westeurope", "southeastasia"],
        "GCP": ["us-central1", "us-west1", "europe-west1", "asia-southeast1"]
    }
    
    # Gerar dados para todo o ano de 2024
    start_date = date(2024, 1, 1)
    end_date = date(2024, 12, 31)
    
    cost_records = []
    current_date = start_date
    
    while current_date <= end_date:
        # Gerar entre 20-50 registros por dia em 2024
        daily_records = random.randint(20, 50)
        
        for _ in range(daily_records):
            provider = random.choice(providers)
            service = random.choice(services[provider])
            region = random.choice(regions[provider])
            
            # Custos de 2024 um pouco menores que 2025
            base_cost = random.uniform(10.0, 2000.0) * 0.9  # 10% menor que 2025
            usage_quantity = random.uniform(1.0, 150.0)
            
            cost_record = FocusCostData(
                billing_account_id=f"123456789{random.randint(100, 999)}",
                billing_account_name=f"{provider} Production Account",
                billing_currency="USD",
                billing_period_start=current_date.replace(day=1),
                billing_period_end=(current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1),
                charge_category=random.choice(["Usage", "Purchase", "Tax"]),
                charge_description=f"{service} usage in {region}",
                charge_frequency="Usage-Based",
                charge_period_start=datetime.combine(current_date, datetime.min.time()),
                charge_period_end=datetime.combine(current_date + timedelta(days=1), datetime.min.time()),
                
                billed_cost=Decimal(str(round(base_cost, 4))),
                effective_cost=Decimal(str(round(base_cost * 0.95, 4))),
                list_cost=Decimal(str(round(base_cost * 1.1, 4))),
                
                provider_name=provider,
                publisher_name=provider,
                service_category="Compute" if "EC2" in service or "Virtual" in service or "Compute" in service else "Storage",
                service_name=service,
                
                resource_id=f"i-{random.randint(100000000000000000, 999999999999999999):017x}",
                resource_name=f"{service.lower()}-{region}-{random.randint(1000, 9999)}",
                resource_type=service,
                
                usage_unit="Hours" if "EC2" in service or "Virtual" in service else "GB",
                usage_quantity=Decimal(str(round(usage_quantity, 2))),
                
                region=region,
                availability_zone=f"{region}{'abc'[random.randint(0, 2)]}",
                
                tags={
                    "Environment": random.choice(["Production", "Development", "Staging"]),
                    "Team": random.choice(["Engineering", "Data", "Marketing", "Finance"]),
                    "Project": f"project-{random.randint(1, 10)}",
                    "Owner": random.choice(["team-a", "team-b", "team-c"])
                }
            )
            
            cost_records.append(cost_record)
        
        # Mostrar progresso
        if current_date.day == 1:
            print(f"📊 Processando {current_date.strftime('%B %Y')}...")
        
        current_date += timedelta(days=1)
    
    # Inserir dados em lotes
    print(f"💾 Inserindo {len(cost_records)} registros de custo de 2024...")
    
    batch_size = 1000
    for i in range(0, len(cost_records), batch_size):
        batch = cost_records[i:i+batch_size]
        session.add_all(batch)
        session.commit()
        print(f"✅ Inseridos {min(i+batch_size, len(cost_records))}/{len(cost_records)} registros")
    
    print("✅ Dados históricos de 2024 criados com sucesso!")
    
    # Estatísticas
    total_cost_2024 = sum(float(record.effective_cost) for record in cost_records)
    print(f"📈 Total de custos de 2024: ${total_cost_2024:,.2f}")
    print(f"📊 Registros por mês: ~{len(cost_records)/12:.0f}")

def main():
    """Função principal"""
    print("🚀 Iniciando criação de dados históricos de 2024...")
    
    try:
        engine, session = create_database_connection()
        
        # Verificar se já existem dados de 2024
        existing_2024 = session.query(FocusCostData).filter(
            FocusCostData.charge_period_start >= datetime(2024, 1, 1),
            FocusCostData.charge_period_start < datetime(2025, 1, 1)
        ).count()
        
        if existing_2024 > 0:
            print(f"⚠️  Já existem {existing_2024} registros de 2024 no banco.")
            response = input("Deseja continuar e adicionar mais dados? (y/N): ")
            if response.lower() != 'y':
                print("❌ Operação cancelada.")
                return
        
        create_2024_historical_data(session)
        
        print("🎉 Script executado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao executar script: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()
