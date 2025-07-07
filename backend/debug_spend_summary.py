#!/usr/bin/env python3
"""
Script de debug para investigar problema com filtro Oracle Cloud no Spend Summary
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func, and_, distinct
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date, timedelta
import requests
import json

def debug_spend_summary_oracle():
    """Investigar dados Oracle Cloud no Spend Summary"""
    
    print("🔍 DEBUG: Problema Oracle Cloud no Spend Summary")
    print("=" * 70)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 30 dias (padrão do dashboard)
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"📅 Período analisado: {start_date} a {end_date}")
        
        # 1. Verificar dados Oracle Cloud brutos no período
        print("\n1️⃣ Verificando dados Oracle Cloud brutos:")
        
        oracle_summary = db.query(
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.provider_name == 'Oracle Cloud',
                FocusCostData.effective_cost > 0
            )
        ).first()
        
        if oracle_summary and oracle_summary.total_cost:
            print(f"   ✅ Oracle Cloud encontrado:")
            print(f"      - Total Cost: ${oracle_summary.total_cost:,.2f}")
            print(f"      - Record Count: {oracle_summary.record_count}")
        else:
            print("   ❌ Nenhum dado Oracle Cloud encontrado no período!")
            
            # Verificar se há dados Oracle com outros nomes
            print("\n   🔍 Verificando variações do nome Oracle:")
            oracle_variations = db.query(
                FocusCostData.provider_name,
                func.sum(FocusCostData.effective_cost).label('total_cost'),
                func.count().label('record_count')
            ).filter(
                and_(
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date,
                    FocusCostData.provider_name.ilike('%oracle%'),
                    FocusCostData.effective_cost > 0
                )
            ).group_by(FocusCostData.provider_name).all()
            
            for variation in oracle_variations:
                print(f"      - '{variation.provider_name}': ${variation.total_cost:,.2f} ({variation.record_count} registros)")
        
        # 2. Verificar todos os providers no período
        print("\n2️⃣ Verificando todos os providers no período:")
        
        all_providers = db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.effective_cost > 0
            )
        ).group_by(FocusCostData.provider_name).order_by(
            func.sum(FocusCostData.effective_cost).desc()
        ).all()
        
        print(f"   📊 Providers encontrados ({len(all_providers)}):")
        for provider in all_providers:
            print(f"      - '{provider.provider_name}': ${provider.total_cost:,.2f} ({provider.record_count} registros)")
        
        # 3. Verificar summary sem filtro
        print("\n3️⃣ Verificando summary total (sem filtro):")
        
        total_summary = db.query(
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.effective_cost > 0
            )
        ).first()
        
        if total_summary:
            print(f"   📊 Total geral:")
            print(f"      - Total Cost: ${total_summary.total_cost:,.2f}")
            print(f"      - Record Count: {total_summary.record_count}")
        
        # 4. Simular query do dashboard summary para Oracle Cloud
        print("\n4️⃣ Simulando query do dashboard summary com filtro Oracle Cloud:")
        
        # Esta é a query que o dashboard summary deveria executar
        dashboard_oracle = db.query(
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.provider_name == 'Oracle Cloud'  # Filtro exato
            )
        ).first()
        
        if dashboard_oracle and dashboard_oracle.total_cost:
            print(f"   ✅ Query do dashboard funcionaria:")
            print(f"      - Total Cost: ${dashboard_oracle.total_cost:,.2f}")
            print(f"      - Record Count: {dashboard_oracle.record_count}")
        else:
            print("   ❌ Query do dashboard retornaria $0.00!")
        
        # 5. Verificar distribuição por provider
        print("\n5️⃣ Verificando distribuição por provider (Oracle Cloud):")
        
        oracle_distribution = db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.provider_name == 'Oracle Cloud'
            )
        ).group_by(FocusCostData.provider_name).all()
        
        if oracle_distribution:
            for dist in oracle_distribution:
                percentage = (dist.total_cost / total_summary.total_cost * 100) if total_summary.total_cost else 0
                print(f"   ✅ Distribution Oracle Cloud:")
                print(f"      - Provider: '{dist.provider_name}'")
                print(f"      - Total: ${dist.total_cost:,.2f}")
                print(f"      - Percentage: {percentage:.2f}%")
        else:
            print("   ❌ Nenhuma distribuição Oracle Cloud encontrada!")
        
    except Exception as e:
        print(f"❌ Erro durante investigação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_api_endpoints():
    """Testar endpoints da API diretamente"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTE DOS ENDPOINTS DA API")
    
    base_url = "http://localhost:8000"
    
    # Headers para autenticação (se necessário)
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    # Período de 30 dias
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"\n📅 Testando período: {start_date} a {end_date}")
    
    # 1. Testar dashboard summary sem filtro
    print("\n1️⃣ Testando /api/v1/dashboard/summary (sem filtro):")
    try:
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        response = requests.get(f"{base_url}/api/v1/dashboard/summary", params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get("cost_summary", {}).get("totals", {}).get("total_cost", 0)
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total Cost: ${total_cost:,.2f}")
            
            # Verificar se há Oracle na distribuição
            providers = data.get("provider_distribution", [])
            oracle_in_dist = [p for p in providers if 'Oracle' in p.get("provider_name", "")]
            if oracle_in_dist:
                print(f"   🎯 Oracle encontrado na distribuição:")
                for oracle in oracle_in_dist:
                    print(f"      - {oracle['provider_name']}: ${oracle['total_cost']:,.2f}")
            else:
                print(f"   ❌ Oracle não encontrado na distribuição")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   ❌ Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")
    
    # 2. Testar dashboard summary com filtro Oracle Cloud
    print("\n2️⃣ Testando /api/v1/dashboard/summary (Oracle Cloud):")
    try:
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "provider_name": "Oracle Cloud"
        }
        
        response = requests.get(f"{base_url}/api/v1/dashboard/summary", params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            total_cost = data.get("cost_summary", {}).get("totals", {}).get("total_cost", 0)
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Total Cost: ${total_cost:,.2f}")
            
            if total_cost == 0:
                print(f"   ❌ PROBLEMA ENCONTRADO: Total Cost = $0.00!")
            else:
                print(f"   ✅ Total Cost > 0: Filtro funcionando!")
            
            # Verificar distribuição
            providers = data.get("provider_distribution", [])
            print(f"   📊 Provider Distribution ({len(providers)} items):")
            for provider in providers:
                print(f"      - {provider['provider_name']}: ${provider['total_cost']:,.2f}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   ❌ Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")
    
    # 3. Testar analytics by-provider
    print("\n3️⃣ Testando /api/v1/analytics/by-provider (Oracle Cloud):")
    try:
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "provider_name": "Oracle Cloud"
        }
        
        response = requests.get(f"{base_url}/api/v1/analytics/by-provider", params=params, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📊 Analytics data: {json.dumps(data, indent=2)[:300]}...")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   ❌ Error: {response.text}")
    
    except Exception as e:
        print(f"   ❌ Erro ao testar endpoint: {e}")

def investigate_backend_code():
    """Investigar o código do backend para encontrar possíveis problemas"""
    
    print("\n" + "=" * 70)
    print("🔍 INVESTIGAÇÃO DO CÓDIGO BACKEND")
    
    # Vamos verificar onde o dashboard summary é implementado
    print("\n📁 Arquivos para investigar:")
    print("   - app/routers/dashboard_api.py (ou similar)")
    print("   - app/cost_analytics.py")
    print("   - app/main.py")
    print("   - Qualquer arquivo relacionado a dashboard summary")

def main():
    """Função principal"""
    print("🚨 INVESTIGAÇÃO: Oracle Cloud Spend Summary retornando $0.00")
    print("=" * 70)
    
    debug_spend_summary_oracle()
    test_api_endpoints()
    investigate_backend_code()
    
    print("\n" + "=" * 70)
    print("🎯 RESUMO DA INVESTIGAÇÃO:")
    print("1. Verificar se dados Oracle Cloud existem no banco (período 30 dias)")
    print("2. Confirmar se endpoint /api/v1/dashboard/summary está aplicando filtro corretamente")
    print("3. Validar se nomenclatura 'Oracle Cloud' está consistente")
    print("4. Comparar comportamento com outros providers (AWS, Azure)")
    print("5. Verificar se há problema similar ao Top Services (LIMIT antes de GROUP BY)")
    print("\n💡 PRÓXIMOS PASSOS:")
    print("- Se dados existem no banco mas API retorna $0, problema está no código do endpoint")
    print("- Se dados não existem no banco, problema está na fonte de dados")
    print("- Se nomenclatura está inconsistente, precisa padronizar no backend")

if __name__ == "__main__":
    main()
