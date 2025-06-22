#!/usr/bin/env python3
"""
Análise dos dados disponíveis para cálculos de desperdício e economias
"""

from app.database import get_database
from app.models import FocusCostData
from sqlalchemy import func, and_
import datetime

def analyze_available_data():
    db = next(get_database())
    
    print("=== ANÁLISE DE DADOS PARA CÁLCULOS DE OTIMIZAÇÃO ===\n")
    
    # 1. Verificar campos disponíveis para análise de desperdício
    print("1. ANÁLISE DE CAMPOS PARA DESPERDÍCIO")
    
    # Verificar tipos de serviços (potencial para identificar subutilizados)
    services = db.query(FocusCostData.service_name).distinct().limit(10).all()
    print(f"   Exemplos de serviços: {[s[0] for s in services if s[0]]}")
    
    # Verificar resource_ids (para identificar recursos órfãos/não utilizados)
    resource_count = db.query(FocusCostData.resource_id).distinct().count()
    print(f"   Total de recursos únicos: {resource_count}")
    
    # Verificar billing_account_names (para análise por conta)
    accounts = db.query(FocusCostData.billing_account_name).distinct().all()
    print(f"   Contas de billing: {[a[0] for a in accounts if a[0]]}")
    
    # 2. Recursos com custo muito baixo (potencial desperdício)
    print("\n2. ANÁLISE DE RECURSOS COM BAIXO CUSTO (Potencial Desperdício)")
    low_cost_resources = db.query(
        FocusCostData.provider_name,
        func.count(FocusCostData.resource_id)
    ).filter(
        FocusCostData.effective_cost < 1.0,
        FocusCostData.effective_cost > 0
    ).group_by(FocusCostData.provider_name).all()
    
    for provider, count in low_cost_resources:
        print(f"   {provider}: {count} recursos com custo < $1")
    
    # 3. Análise de variabilidade de custos (potencial para economias)
    print("\n3. ANÁLISE DE VARIABILIDADE DE CUSTOS")
    cost_stats = db.query(
        FocusCostData.provider_name,
        func.count(FocusCostData.id).label('count'),
        func.avg(FocusCostData.effective_cost).label('avg_cost'),
        func.min(FocusCostData.effective_cost).label('min_cost'),
        func.max(FocusCostData.effective_cost).label('max_cost')
    ).filter(FocusCostData.effective_cost > 0).group_by(FocusCostData.provider_name).all()
    
    for stat in cost_stats:
        print(f"   {stat.provider_name}:")
        print(f"     Registros: {stat.count}")
        print(f"     Custo médio: ${stat.avg_cost:.2f}")
        print(f"     Custo mín: ${stat.min_cost:.2f}")
        print(f"     Custo máx: ${stat.max_cost:.2f}")
    
    # 4. Análise temporal para identificar padrões
    print("\n4. ANÁLISE TEMPORAL (Últimos 30 dias)")
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=30)
    
    recent_data = db.query(
        FocusCostData.provider_name,
        func.sum(FocusCostData.effective_cost).label('total_cost'),
        func.count(FocusCostData.id).label('record_count')
    ).filter(
        FocusCostData.billing_period_start >= start_date,
        FocusCostData.billing_period_end <= end_date
    ).group_by(FocusCostData.provider_name).all()
    
    for data in recent_data:
        print(f"   {data.provider_name}: ${data.total_cost:.2f} ({data.record_count} registros)")
    
    # 5. Identificar serviços mais caros (candidatos a otimização)
    print("\n5. SERVIÇOS MAIS CAROS (Candidatos a Otimização)")
    expensive_services = db.query(
        FocusCostData.service_name,
        func.sum(FocusCostData.effective_cost).label('total_cost')
    ).filter(
        FocusCostData.effective_cost > 0,
        FocusCostData.service_name.isnot(None)
    ).group_by(FocusCostData.service_name).order_by(
        func.sum(FocusCostData.effective_cost).desc()
    ).limit(10).all()
    
    for service in expensive_services:
        print(f"   {service.service_name}: ${service.total_cost:.2f}")

if __name__ == "__main__":
    analyze_available_data()
