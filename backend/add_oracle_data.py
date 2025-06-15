#!/usr/bin/env python3
"""
Script para adicionar dados da Oracle Cloud Infrastructure (OCI) ao banco de dados
"""
import random
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.database import get_database
from app.models import CloudProvider, FocusCostData

def add_oracle_provider(db):
    """Adiciona Oracle como provedor se não existir"""
    oracle_provider = db.query(CloudProvider).filter(CloudProvider.provider_name == 'Oracle').first()
    
    if not oracle_provider:
        print("📝 Adicionando Oracle como provedor...")
        oracle_provider = CloudProvider(
            provider_name="Oracle",
            api_endpoint="https://cloud.oracle.com",
            is_active=True
        )
        db.add(oracle_provider)
        db.commit()
        print("✅ Oracle provider adicionado com sucesso!")
    else:
        print("ℹ️ Oracle provider já existe")

def generate_oracle_cost_data(db):
    """Gera dados de custo para Oracle Cloud"""
    print("💰 Gerando dados de custo para Oracle Cloud...")
    
    # Serviços Oracle Cloud típicos
    oracle_services = [
        "Compute", "Block Storage", "Object Storage", "Load Balancer",
        "Networking", "Database", "Autonomous Database", "Functions",
        "Container Engine", "API Gateway", "Logging", "Monitoring",
        "Identity", "Security", "Integration"
    ]
    
    # Regiões Oracle Cloud
    oracle_regions = [
        "us-ashburn-1", "us-phoenix-1", "eu-frankfurt-1", "eu-amsterdam-1",
        "ap-tokyo-1", "ap-sydney-1", "ca-toronto-1", "uk-london-1",
        "ap-mumbai-1", "sa-saopaulo-1"
    ]
    
    # Categorias de recursos
    resource_types = ["standard", "premium", "high-performance", "basic"]
    
    # Gerar dados para os últimos 90 dias
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    
    records_added = 0
    
    # Gerar dados para cada dia nos últimos 90 dias
    current_date = start_date
    while current_date <= end_date:
        # Gerar entre 20-50 registros por dia
        daily_records = random.randint(20, 50)
        
        for _ in range(daily_records):
            service = random.choice(oracle_services)
            region = random.choice(oracle_regions)
            resource_type = random.choice(resource_types)
            
            # Gerar custos realistas baseados no serviço
            base_cost = {
                "Compute": random.uniform(50, 2000),
                "Block Storage": random.uniform(10, 500),
                "Object Storage": random.uniform(5, 300),
                "Load Balancer": random.uniform(20, 100),
                "Networking": random.uniform(10, 200),
                "Database": random.uniform(100, 5000),
                "Autonomous Database": random.uniform(200, 8000),
                "Functions": random.uniform(1, 50),
                "Container Engine": random.uniform(30, 500),
                "API Gateway": random.uniform(5, 100),
                "Logging": random.uniform(1, 20),
                "Monitoring": random.uniform(5, 50),
                "Identity": random.uniform(1, 10),
                "Security": random.uniform(10, 100),
                "Integration": random.uniform(20, 300)
            }.get(service, random.uniform(10, 100))
            
            # Adicionar variação aleatória
            cost = base_cost * random.uniform(0.5, 2.0)
            
            # Criar registro
            cost_record = FocusCostData(
                billing_account_id=f"oracle-{random.randint(1000, 9999)}",
                billing_account_name="Oracle Cloud Account",
                billing_currency="USD",
                billing_period_start=current_date,
                billing_period_end=current_date,
                charge_category="Usage",
                charge_description=f"{service} usage in {region}",
                charge_frequency="Daily",
                charge_period_start=datetime.combine(current_date, datetime.min.time()),
                charge_period_end=datetime.combine(current_date, datetime.max.time()),
                
                # Custos
                billed_cost=Decimal(str(round(cost, 4))),
                effective_cost=Decimal(str(round(cost * 0.95, 4))),  # 5% desconto
                list_cost=Decimal(str(round(cost * 1.1, 4))),  # 10% markup
                list_unit_price=Decimal(str(round(cost / random.uniform(1, 100), 4))),
                pricing_category="On-Demand",
                pricing_quantity=Decimal(str(round(random.uniform(1, 100), 2))),
                pricing_unit="hour",
                usage_quantity=Decimal(str(round(random.uniform(1, 1000), 2))),
                usage_unit="GB-hour" if "Storage" in service else "vCPU-hour",
                
                # Informações do provedor
                provider_name="Oracle",
                publisher_name="Oracle Corporation",
                service_category="Cloud Computing",
                service_name=service,
                
                # Recursos
                region=region,
                resource_id=f"ocid1.{service.lower()}.{region}.{random.randint(100000, 999999)}",
                resource_name=f"{service}-{random.randint(100, 999)}",
                resource_type=resource_type,
                
                # Invoice Information
                invoice_issuer_name="Oracle Corporation",
                
                # Tags (JSON)
                tags={
                    "environment": random.choice(["production", "staging", "development"]),
                    "team": random.choice(["backend", "frontend", "data", "ml"]),
                    "project": random.choice(["x-cost", "analytics", "portal"]),
                    "cost-center": f"CC-{random.randint(1000, 9999)}"
                },
                
                # Metadados
                data_source="simulation"
            )
            
            db.add(cost_record)
            records_added += 1
            
            # Commit a cada 100 registros para performance
            if records_added % 100 == 0:
                db.commit()
                print(f"   💾 {records_added} registros adicionados...")
        
        current_date += timedelta(days=1)
    
    # Commit final
    db.commit()
    print(f"✅ {records_added} registros Oracle adicionados com sucesso!")

def main():
    """Função principal"""
    print("🚀 Iniciando adição de dados Oracle Cloud...")
    
    db = next(get_database())
    
    try:
        # 1. Adicionar Oracle como provedor
        add_oracle_provider(db)
        
        # 2. Gerar dados de custo
        generate_oracle_cost_data(db)
        
        print("\n✅ Dados Oracle Cloud adicionados com sucesso!")
        
        # 3. Verificar dados adicionados
        oracle_count = db.query(FocusCostData).filter(FocusCostData.provider_name == 'Oracle').count()
        total_cost = db.query(FocusCostData.effective_cost).filter(FocusCostData.provider_name == 'Oracle').all()
        total_oracle_cost = sum(float(cost[0]) for cost in total_cost if cost[0])
        
        print(f"\n📊 Resumo dos dados Oracle:")
        print(f"   • Total de registros: {oracle_count:,}")
        print(f"   • Custo total: ${total_oracle_cost:,.2f}")
        
    except Exception as e:
        print(f"❌ Erro ao adicionar dados Oracle: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
