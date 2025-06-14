#!/usr/bin/env python3
"""
Script para popular o banco PostgreSQL com dados de teste realistas
para a aplicação X-Cost FinOps.

Este script cria:
- Usuários com diferentes roles
- Credenciais de cloud providers
- Dados de custo do FOCUS
- Análises de custo
- Budgets
- Dados de auditoria

Uso:
    python scripts/populate_database.py
"""

import os
import sys
import uuid
import random
import json
from datetime import datetime, date, timedelta
from decimal import Decimal
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, CloudProvider, FocusCostData, CostAnalysis, Budget
from app.credential_models import User, CloudCredentialConfig, UserRole, CloudProviderType, CredentialStatus

# Configuração do banco
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://finops_user:finops_password@localhost:5432/finops_db")

def create_database_connection():
    """Cria conexão com o banco de dados"""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal()

def create_users(session):
    """Cria usuários de teste com diferentes roles"""
    # Hash simples para senhas (apenas para testes)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@xfinops.com", 
            "password": "AdminPass123!",
            "role": UserRole.ADMIN,
            "is_active": True
        },
        {
            "username": "finops_manager",
            "email": "manager@xfinops.com",
            "password": "ManagerPass123!",
            "role": UserRole.FINOPS_ADMIN,
            "is_active": True
        },
        {
            "username": "cloud_operator",
            "email": "operator@xfinops.com",
            "password": "OperatorPass123!",
            "role": UserRole.OPERATOR,
            "is_active": True
        },
        {
            "username": "cost_viewer",
            "email": "viewer@xfinops.com",
            "password": "ViewerPass123!",
            "role": UserRole.VIEWER,
            "is_active": True
        },
        {
            "username": "demo_user",
            "email": "demo@xfinops.com",
            "password": "DemoPass123!",
            "role": UserRole.VIEWER,
            "is_active": True
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Verificar se o usuário já existe
        existing_user = session.query(User).filter(User.username == user_data["username"]).first()
        if existing_user:
            print(f"Usuário {user_data['username']} já existe, pulando...")
            created_users.append(existing_user)
            continue
            
        hashed_password = pwd_context.hash(user_data["password"])
        user = User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=hashed_password,
            role=user_data["role"],
            is_active=user_data["is_active"]
        )
        session.add(user)
        created_users.append(user)
        print(f"Criado usuário: {user_data['username']} ({user_data['role']})")
    
    session.commit()
    return created_users

def create_cloud_credentials(session, users):
    """Cria credenciais de cloud providers de teste"""
    credentials_data = [
        {
            "name": "AWS Production Account",
            "provider_type": CloudProviderType.AWS,
            "description": "Conta de produção AWS principal",
            "secret_name": "aws-prod-credentials",
            "secret_arn": "arn:aws:secretsmanager:us-east-1:123456789:secret:aws-prod-creds",
            "account_id": "123456789012",
            "region_preference": "us-east-1",
            "additional_config": {"environment": "production", "team": "platform"}
        },
        {
            "name": "AWS Development Account", 
            "provider_type": CloudProviderType.AWS,
            "description": "Conta de desenvolvimento AWS",
            "secret_name": "aws-dev-credentials",
            "secret_arn": "arn:aws:secretsmanager:us-west-2:123456789:secret:aws-dev-creds",
            "account_id": "123456789013",
            "region_preference": "us-west-2",
            "additional_config": {"environment": "development", "team": "engineering"}
        },
        {
            "name": "Azure Production Subscription",
            "provider_type": CloudProviderType.AZURE,
            "description": "Subscription principal do Azure",
            "secret_name": "azure-prod-credentials",
            "secret_arn": "arn:aws:secretsmanager:us-east-1:123456789:secret:azure-prod-creds",
            "account_id": str(uuid.uuid4()),
            "region_preference": "East US",
            "additional_config": {"environment": "production", "team": "platform"}
        },
        {
            "name": "GCP Production Project",
            "provider_type": CloudProviderType.GCP,
            "description": "Projeto principal do Google Cloud",
            "secret_name": "gcp-prod-credentials",
            "secret_arn": "arn:aws:secretsmanager:us-east-1:123456789:secret:gcp-prod-creds",
            "account_id": "xfinops-prod-" + "".join(random.choices("0123456789", k=6)),
            "region_preference": "us-central1",
            "additional_config": {"environment": "production", "team": "platform"}
        }
    ]
    
    created_credentials = []
    admin_user = next((u for u in users if u.role == UserRole.ADMIN), users[0])
    
    for cred_data in credentials_data:
        # Verificar se a credencial já existe
        existing_cred = session.query(CloudCredentialConfig).filter(CloudCredentialConfig.name == cred_data["name"]).first()
        if existing_cred:
            print(f"Credencial {cred_data['name']} já existe, pulando...")
            created_credentials.append(existing_cred)
            continue
            
        credential = CloudCredentialConfig(
            name=cred_data["name"],
            provider_type=cred_data["provider_type"],
            description=cred_data["description"],
            secret_name=cred_data["secret_name"],
            secret_arn=cred_data["secret_arn"],
            account_id=cred_data["account_id"],
            region_preference=cred_data["region_preference"],
            additional_config=cred_data["additional_config"],
            created_by=admin_user.id,
            status=CredentialStatus.ACTIVE
        )
        session.add(credential)
        created_credentials.append(credential)
        print(f"Criada credencial: {cred_data['name']} ({cred_data['provider_type']})")
    
    session.commit()
    return created_credentials

def create_focus_cost_data(session):
    """Cria dados de custo FOCUS realistas"""
    providers = ["AWS", "Azure", "GCP"]
    services = {
        "AWS": ["EC2", "S3", "RDS", "Lambda", "CloudFront", "ELB", "VPC", "CloudWatch"],
        "Azure": ["Virtual Machines", "Storage Account", "SQL Database", "Functions", "CDN", "Load Balancer", "Virtual Network", "Monitor"],
        "GCP": ["Compute Engine", "Cloud Storage", "Cloud SQL", "Cloud Functions", "Cloud CDN", "Load Balancing", "VPC", "Monitoring"]
    }
    
    regions = {
        "AWS": ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"],
        "Azure": ["East US", "West US 2", "West Europe", "Southeast Asia"],
        "GCP": ["us-central1", "us-west1", "europe-west1", "asia-southeast1"]
    }
    
    resource_types = {
        "EC2": ["t3.micro", "t3.small", "t3.medium", "m5.large", "c5.xlarge"],
        "Virtual Machines": ["Standard_B1s", "Standard_B2s", "Standard_D2s_v3", "Standard_E4s_v3"],
        "Compute Engine": ["n1-standard-1", "n1-standard-2", "n1-standard-4", "e2-medium"]
    }
    
    # Gerar dados para os últimos 90 dias, com mais concentração nos últimos 30 dias
    start_date = date(2025, 3, 15)  # Começar em 15/03/2025 para ter dados até hoje (14/06/2025)
    end_date = date(2025, 6, 14)    # Até hoje
    
    cost_records = []
    current_date = start_date
    
    while current_date <= end_date:
        # Mais registros nos últimos 30 dias
        days_from_today = (end_date - current_date).days
        if days_from_today <= 30:
            daily_records = random.randint(50, 100)  # Mais dados recentes
        elif days_from_today <= 60:
            daily_records = random.randint(30, 60)
        else:
            daily_records = random.randint(15, 30)
        
        for _ in range(daily_records):
            provider = random.choice(providers)
            service = random.choice(services[provider])
            region = random.choice(regions[provider])
            
            # Gerar custos realistas com tendência crescente para dados mais recentes
            base_multiplier = 1.0 + (90 - days_from_today) * 0.01  # Crescimento gradual
            base_cost = random.uniform(5.0, 1500.0) * base_multiplier
            usage_quantity = random.uniform(1.0, 200.0)
            
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
                effective_cost=Decimal(str(round(base_cost * 0.95, 4))),  # Com desconto
                list_cost=Decimal(str(round(base_cost * 1.1, 4))),  # Preço de lista maior
                list_unit_price=Decimal(str(round(base_cost / usage_quantity, 6))),
                pricing_category=random.choice(["On-Demand", "Reserved", "Spot"]),
                pricing_quantity=Decimal(str(round(usage_quantity, 6))),
                pricing_unit="hours",
                usage_quantity=Decimal(str(round(usage_quantity, 6))),
                usage_unit="hours",
                
                provider_name=provider,
                publisher_name=provider,
                service_category="Compute" if service in ["EC2", "Virtual Machines", "Compute Engine"] else "Storage",
                service_name=service,
                
                resource_id=f"i-{uuid.uuid4().hex[:17]}" if provider == "AWS" else f"vm-{uuid.uuid4().hex[:17]}",
                resource_name=f"{service.lower()}-{random.randint(1000, 9999)}",
                resource_type=random.choice(resource_types.get(service, ["standard"])),
                availability_zone=f"{region}{'a' if provider == 'AWS' else '-1'}",
                region=region,
                
                invoice_issuer_name=provider,
                tags={
                    "Environment": random.choice(["production", "staging", "development"]),
                    "Team": random.choice(["platform", "engineering", "data", "ml"]),
                    "Project": random.choice(["webapp", "api", "analytics", "ml-training"]),
                    "Owner": random.choice(["team-a", "team-b", "team-c"])
                },
                data_source="billing_api"
            )
            cost_records.append(cost_record)
        
        current_date += timedelta(days=1)  # Incrementar a data
    
    print(f"Criando {len(cost_records)} registros de custo FOCUS...")
    session.add_all(cost_records)
    session.commit()
    print(f"✅ Criados {len(cost_records)} registros de custo")
    
    return cost_records

def create_cost_analysis(session):
    """Cria análises de custo"""
    providers = ["AWS", "Azure", "GCP"]
    services = ["EC2", "S3", "RDS", "Virtual Machines", "Storage Account", "Compute Engine"]
    
    analyses = []
    for i in range(50):  # 50 análises (mais análises)
        # Períodos variados, com foco nos últimos dias
        period_days = random.choice([7, 14, 30, 60])
        end_date = date(2025, 6, 14)  # Hoje
        start_date = end_date - timedelta(days=period_days)
        
        analysis = CostAnalysis(
            analysis_type=random.choice(["trend", "delta", "forecast"]),
            provider_name=random.choice(providers),
            service_name=random.choice(services),
            resource_type=random.choice(["compute", "storage", "network"]),
            period_start=start_date,
            period_end=end_date,
            total_cost=Decimal(str(round(random.uniform(5000, 80000), 2))),  # Custos maiores
            average_daily_cost=Decimal(str(round(random.uniform(100, 3000), 2))),
            cost_trend=Decimal(str(round(random.uniform(-15, 25), 2))),  # -15% a +25%
            cost_delta=Decimal(str(round(random.uniform(-8000, 15000), 2))),
            forecasted_cost=Decimal(str(round(random.uniform(6000, 100000), 2))),
            tags={
                "analysis_version": "v1.0",
                "confidence": random.choice(["high", "medium", "low"]),
                "generated_at": "2025-06-14"
            }
        )
        analyses.append(analysis)
    
    session.add_all(analyses)
    session.commit()
    print(f"✅ Criadas {len(analyses)} análises de custo")
    
    return analyses

def create_budgets(session):
    """Cria budgets de exemplo"""
    budgets_data = [
        {
            "budget_name": "AWS Production Monthly",
            "provider_name": "AWS",
            "service_name": None,
            "budget_amount": Decimal("50000.00"),
            "budget_period": "monthly",
            "alert_threshold": Decimal("80.0"),
            "tags": {"environment": "production", "criticality": "high"}
        },
        {
            "budget_name": "Azure Development Quarterly", 
            "provider_name": "Azure",
            "service_name": None,
            "budget_amount": Decimal("15000.00"),
            "budget_period": "quarterly",
            "alert_threshold": Decimal("70.0"),
            "tags": {"environment": "development", "criticality": "medium"}
        },
        {
            "budget_name": "AWS EC2 Monthly",
            "provider_name": "AWS",
            "service_name": "EC2",
            "budget_amount": Decimal("20000.00"),
            "budget_period": "monthly", 
            "alert_threshold": Decimal("85.0"),
            "tags": {"service": "compute", "criticality": "high"}
        },
        {
            "budget_name": "GCP Storage Annual",
            "provider_name": "GCP",
            "service_name": "Cloud Storage",
            "budget_amount": Decimal("12000.00"),
            "budget_period": "annual",
            "alert_threshold": Decimal("75.0"),
            "tags": {"service": "storage", "criticality": "medium"}
        },
        {
            "budget_name": "Multi-Cloud AI/ML",
            "provider_name": None,
            "service_name": None,
            "budget_amount": Decimal("100000.00"),
            "budget_period": "annual",
            "alert_threshold": Decimal("90.0"),
            "tags": {"category": "ai-ml", "criticality": "high"}
        }
    ]
    
    budgets = []
    for budget_data in budgets_data:
        # Verificar se o budget já existe
        existing_budget = session.query(Budget).filter(Budget.budget_name == budget_data["budget_name"]).first()
        if existing_budget:
            print(f"Budget {budget_data['budget_name']} já existe, pulando...")
            continue
            
        budget = Budget(**budget_data)
        budgets.append(budget)
        session.add(budget)
    
    session.commit()
    print(f"✅ Criados {len(budgets)} budgets")
    
    return budgets

def create_audit_logs(session, users, credentials):
    """Cria logs de auditoria - Desabilitado temporariamente"""
    print("⚠️  Logs de auditoria desabilitados (módulo AuditLog não disponível)")
    return []

def print_summary(users, credentials, cost_records, analyses, budgets, audit_logs):
    """Imprime resumo dos dados criados"""
    print("\n" + "="*60)
    print("🎉 RESUMO DOS DADOS CRIADOS")
    print("="*60)
    print(f"👥 Usuários: {len(users)}")
    print(f"🔐 Credenciais: {len(credentials)}")
    print(f"💰 Registros de custo: {len(cost_records)}")
    print(f"📊 Análises: {len(analyses)}")
    print(f"💼 Budgets: {len(budgets)}")
    print(f"📝 Logs de auditoria: {len(audit_logs)}")
    print("="*60)
    
    print("\n📋 USUÁRIOS CRIADOS:")
    for user in users:
        print(f"  • {user.username} ({user.role}) - {user.email}")
    
    print("\n🔐 CREDENCIAIS CRIADAS:")
    for cred in credentials:
        print(f"  • {cred.name} ({cred.provider_type}) - {cred.status}")
    
    print("\n💼 BUDGETS CRIADOS:")
    for budget in budgets:
        print(f"  • {budget.budget_name} - ${budget.budget_amount:,.2f} ({budget.budget_period})")
    
    print("\n🔑 CREDENCIAIS DE ACESSO PARA TESTE:")
    print("  • Admin: admin / AdminPass123!")
    print("  • FinOps Manager: finops_manager / ManagerPass123!")
    print("  • Operator: cloud_operator / OperatorPass123!")
    print("  • Viewer: cost_viewer / ViewerPass123!")
    print("  • Demo: demo_user / DemoPass123!")
    
    print("\n🌐 URL da aplicação (quando rodando):")
    print("  • Frontend: http://localhost:3000")
    print("  • Backend API: http://localhost:8000")
    print("  • Documentação API: http://localhost:8000/docs")

def main():
    """Função principal"""
    print("🚀 Iniciando população do banco de dados...")
    
    try:
        # Conectar ao banco
        engine, session = create_database_connection()
        print("✅ Conexão com banco estabelecida")
        
        # Criar dados
        print("\n📊 Criando usuários...")
        users = create_users(session)
        
        print("\n🔐 Criando credenciais...")
        credentials = create_cloud_credentials(session, users)
        
        print("\n💰 Criando dados de custo FOCUS...")
        cost_records = create_focus_cost_data(session)
        
        print("\n📊 Criando análises de custo...")
        analyses = create_cost_analysis(session)
        
        print("\n💼 Criando budgets...")
        budgets = create_budgets(session)
        
        print("\n📝 Criando logs de auditoria...")
        audit_logs = create_audit_logs(session, users, credentials)
        
        # Resumo final
        print_summary(users, credentials, cost_records, analyses, budgets, audit_logs)
        
    except Exception as e:
        print(f"❌ Erro durante a população do banco: {e}")
        raise
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    main()
