#!/usr/bin/env python3
"""
Script para investigar o problema do PieChart mostrando apenas Oracle Cloud quando filtro está em "All"
"""

import sys
import os
import requests
import json
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date, timedelta

def investigate_provider_distribution():
    """Investigar distribuição de provedores no banco vs API"""
    
    print("🔍 INVESTIGAÇÃO: PieChart mostrando apenas Oracle Cloud")
    print("=" * 60)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 90 dias (padrão do frontend)
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        print(f"📅 Período analisado: {start_date} a {end_date}")
        
        # 1. Verificar dados brutos no banco por provider
        print("\n1️⃣ DADOS BRUTOS NO BANCO (últimos 90 dias):")
        provider_costs = db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count(FocusCostData.id).label('record_count')
        ).filter(
            FocusCostData.billing_period_start >= start_date,
            FocusCostData.billing_period_start <= end_date
        ).group_by(FocusCostData.provider_name).all()
        
        total_all_providers = sum(cost.total_cost for cost in provider_costs)
        
        for provider in provider_costs:
            percentage = (provider.total_cost / total_all_providers * 100) if total_all_providers > 0 else 0
            print(f"   {provider.provider_name:<15}: ${provider.total_cost:>12,.2f} ({percentage:>5.1f}%) - {provider.record_count:>6} registros")
        
        print(f"   {'TOTAL':<15}: ${total_all_providers:>12,.2f} (100.0%)")
        
        # 2. Testar API /dashboard/summary sem filtro (All)
        print("\n2️⃣ TESTE API - Dashboard Summary (All):")
        token = os.environ.get("X_COST_API_TOKEN", "")
        if not token:
            print("⚠️ Configure a variável de ambiente X_COST_API_TOKEN")
            return
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Teste sem filtro de provider (All)
        response = requests.get(
            "http://localhost:8000/api/v1/dashboard/summary",
            headers=headers,
            params={"time_filter": "90d"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {response.status_code}")
            print(f"   Total Cost: ${data.get('cost_summary', {}).get('totals', {}).get('total_cost', 0):,.2f}")
            
            provider_dist = data.get('provider_distribution', [])
            print(f"   Provider Distribution ({len(provider_dist)} providers):")
            for provider in provider_dist:
                print(f"      {provider['provider_name']:<15}: ${provider['total_cost']:>12,.2f} ({provider['percentage_of_total']:>5.1f}%)")
        else:
            print(f"   ❌ Erro API: {response.status_code} - {response.text}")
        
        # 3. Testar API /analytics/by-provider sem filtro
        print("\n3️⃣ TESTE API - Analytics By Provider (All):")
        response = requests.get(
            "http://localhost:8000/api/v1/analytics/by-provider",
            headers=headers,
            params={"time_filter": "90d"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {response.status_code}")
            
            # Verificar estrutura da resposta
            if 'data' in data and 'provider_breakdown' in data['data']:
                providers = data['data']['provider_breakdown']
                print(f"   Providers retornados: {len(providers)}")
                for provider in providers:
                    print(f"      {provider['provider_name']:<15}: ${provider['total_cost']:>12,.2f} ({provider['percentage_of_total']:>5.1f}%)")
            else:
                print(f"   📄 Resposta completa: {json.dumps(data, indent=2)}")
        else:
            print(f"   ❌ Erro API: {response.status_code} - {response.text}")
        
        # 4. Análise de discrepância
        print("\n4️⃣ ANÁLISE DE DISCREPÂNCIA:")
        if len(provider_costs) > 1:
            print(f"   📊 Banco de dados: {len(provider_costs)} provedores com dados")
            if response.status_code == 200:
                if 'data' in data and 'provider_breakdown' in data['data']:
                    api_providers = len(data['data']['provider_breakdown'])
                    print(f"   🔌 API retorna: {api_providers} provedores")
                    if api_providers == 1 and len(provider_costs) > 1:
                        print("   🚨 PROBLEMA IDENTIFICADO: API retorna apenas 1 provider, mas banco tem múltiplos!")
                    elif api_providers == len(provider_costs):
                        print("   ✅ API e banco consistentes em número de providers")
                    else:
                        print(f"   ⚠️  Inconsistência: Banco={len(provider_costs)}, API={api_providers}")
        
    except Exception as e:
        print(f"❌ Erro na investigação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    investigate_provider_distribution()
