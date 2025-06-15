#!/usr/bin/env python3
"""
Cria dados de custo para os últimos 7 dias para testes
"""

from app.database import SessionLocal
from app.models import FocusCostData
import random
from datetime import datetime, date, timedelta
from decimal import Decimal

def create_recent_data():
    """Cria dados dos últimos 7 dias"""
    db = SessionLocal()
    try:
        # Definir serviços e provedores para criar dados
        services = [
            ('EC2', 'AWS'), ('S3', 'AWS'), ('RDS', 'AWS'),
            ('Virtual Machines', 'Azure'), ('Storage Account', 'Azure'),
            ('Compute Engine', 'GCP'), ('Cloud Storage', 'GCP')
        ]
        
        regions = [
            'us-east-1', 'us-west-2', 'eu-west-1',
            'eastus', 'westus', 'southeastasia',
            'us-central1', 'europe-west1'
        ]
        
        # Criar dados para os últimos 7 dias
        today = date.today()
        records_created = 0
        
        for i in range(7):
            current_date = today - timedelta(days=i)
            
            # Criar 10-15 registros por dia
            daily_records = random.randint(10, 15)
            
            for _ in range(daily_records):
                service, provider = random.choice(services)
                region = random.choice(regions)
                
                # Custo aleatório entre 50 e 2000
                cost = round(random.uniform(50, 2000), 4)
                
                record = FocusCostData(
                    provider_name=provider,
                    service_name=service,
                    region=region,
                    billing_period_start=current_date,
                    billing_period_end=current_date,
                    effective_cost=Decimal(str(cost)),
                    usage_quantity=Decimal(str(random.uniform(1, 100))),
                    resource_id=f"resource-{random.randint(1000, 9999)}",
                    tags={"Environment": random.choice(["prod", "dev", "staging"])}
                )
                
                db.add(record)
                records_created += 1
        
        db.commit()
        print(f"✅ Criados {records_created} registros para os últimos 7 dias")
        
        # Verificar os dados criados
        recent_count = db.query(FocusCostData).filter(
            FocusCostData.billing_period_start >= (today - timedelta(days=7))
        ).count()
        
        print(f"📊 Total de registros dos últimos 7 dias: {recent_count}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_recent_data()
