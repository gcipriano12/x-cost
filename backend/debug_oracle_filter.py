#!/usr/bin/env python3
"""
Script de debug para investigar o problema do filtro Oracle Cloud no Spend Summary
"""

import sys
import os
import requests
import json
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func, and_, distinct
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date, timedelta

def debug_oracle_cloud_data():
    """Investigar dados da Oracle Cloud no banco"""
    
    print("🔍 DEBUG: Problema do filtro Oracle Cloud")
    print("=" * 60)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 90 dias
        end_date = date.today()
        start_date = end_date - timedelta(days=90)
        
        print(f"📅 Período analisado: {start_date} a {end_date}")
        
        # 1. Verificar todos os providers únicos
        print("\n1️⃣ Verificando providers únicos no banco:")
        providers = db.query(distinct(FocusCostData.provider_name)).all()
        for provider in providers:
            print(f"   - '{provider[0]}'")
        
        # 2. Verificar dados Oracle Cloud específicos
        print("\n2️⃣ Verificando dados Oracle Cloud no período:")
        
        oracle_query = db.query(
            FocusCostData.service_name,
            FocusCostData.provider_name,
            FocusCostData.region,
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.provider_name == 'Oracle Cloud',
                FocusCostData.effective_cost > 0
            )
        ).group_by(
            FocusCostData.service_name,
            FocusCostData.provider_name,
            FocusCostData.region
        ).order_by(func.sum(FocusCostData.effective_cost).desc())
        
        oracle_results = oracle_query.all()
        
        if oracle_results:
            print(f"   ✅ Encontrados {len(oracle_results)} serviços Oracle Cloud:")
            for result in oracle_results:
                print(f"      - {result.service_name} ({result.region}): ${result.total_cost:,.2f} ({result.record_count} registros)")
        else:
            print("   ❌ Nenhum dado Oracle Cloud encontrado no período!")
        
        # 3. Verificar se existe problema com filtro exato
        print("\n3️⃣ Testando diferentes variações do nome Oracle Cloud:")
        
        test_names = [
            'Oracle Cloud',
            'Oracle',
            'oracle cloud',
            'ORACLE CLOUD',
            'OracleCloud',
            'Oracle_Cloud'
        ]
        
        for test_name in test_names:
            count = db.query(func.count(FocusCostData.id)).filter(
                and_(
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date,
                    FocusCostData.provider_name == test_name,
                    FocusCostData.effective_cost > 0
                )
            ).scalar()
            
            if count > 0:
                print(f"   ✅ '{test_name}': {count} registros")
            else:
                print(f"   ❌ '{test_name}': 0 registros")
        
        # 4. Verificar dados sem filtro (All)
        print("\n4️⃣ Verificando dados sem filtro de provider:")
        
        all_query = db.query(
            FocusCostData.service_name,
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.effective_cost > 0
            )
        ).group_by(
            FocusCostData.service_name,
            FocusCostData.provider_name
        ).order_by(func.sum(FocusCostData.effective_cost).desc()).limit(10)
        
        all_results = all_query.all()
        
        print(f"   📊 Top 10 serviços (todos os providers):")
        for i, result in enumerate(all_results, 1):
            print(f"      {i}. {result.service_name} ({result.provider_name}): ${result.total_cost:,.2f}")
        
        # 5. Verificar especificamente Oracle nos top services
        oracle_in_all = [r for r in all_results if 'Oracle' in r.provider_name]
        if oracle_in_all:
            print(f"\n   🎯 Serviços Oracle encontrados no 'All':")
            for result in oracle_in_all:
                print(f"      - {result.service_name} ({result.provider_name}): ${result.total_cost:,.2f}")
        else:
            print(f"\n   ❌ Nenhum serviço Oracle encontrado no top 10 'All'")
        
        # 6. Verificar datas dos registros Oracle Cloud
        print("\n5️⃣ Verificando datas dos registros Oracle Cloud:")
        
        oracle_dates = db.query(
            func.min(FocusCostData.charge_period_start).label('min_date'),
            func.max(FocusCostData.charge_period_start).label('max_date'),
            func.count().label('total_records')
        ).filter(
            FocusCostData.provider_name == 'Oracle Cloud'
        ).first()
        
        if oracle_dates and oracle_dates.total_records > 0:
            print(f"   📅 Período dos dados Oracle Cloud:")
            print(f"      - Data mais antiga: {oracle_dates.min_date}")
            print(f"      - Data mais recente: {oracle_dates.max_date}")
            print(f"      - Total de registros: {oracle_dates.total_records}")
            
            # Verificar se há registros no período específico
            period_records = db.query(func.count(FocusCostData.id)).filter(
                and_(
                    FocusCostData.provider_name == 'Oracle Cloud',
                    FocusCostData.charge_period_start >= start_date,
                    FocusCostData.charge_period_start <= end_date
                )
            ).scalar()
            
            print(f"      - Registros no período {start_date} a {end_date}: {period_records}")
        else:
            print("   ❌ Nenhum registro Oracle Cloud encontrado!")
        
        # 7. Verificar case sensitivity
        print("\n6️⃣ Verificando problemas de case sensitivity:")
        
        oracle_variations = db.query(
            FocusCostData.provider_name,
            func.count().label('count')
        ).filter(
            FocusCostData.provider_name.ilike('%oracle%')
        ).group_by(FocusCostData.provider_name).all()
        
        for variation in oracle_variations:
            print(f"   - '{variation.provider_name}': {variation.count} registros")
        
    except Exception as e:
        print(f"❌ Erro durante investigação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def test_dashboard_summary_api():
    """Testar o endpoint /api/v1/dashboard/summary com filtro Oracle Cloud"""
    
    print("\n" + "=" * 60)
    print("🌐 TESTE API DASHBOARD SUMMARY")
    
    # Token obtido de variável de ambiente
    token = os.environ.get("X_COST_API_TOKEN", "")
    if not token:
        print("⚠️ Configure a variável de ambiente X_COST_API_TOKEN")
        return
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Período de 30 dias (padrão do frontend)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"📅 Testando período: {start_date} a {end_date}")
    
    # Teste 1: Dashboard Summary sem filtro (All)
    print("\n1️⃣ Teste Dashboard Summary - SEM filtro (All):")
    try:
        url = f"{base_url}/api/v1/dashboard/summary"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            total_cost = data.get("cost_summary", {}).get("totals", {}).get("total_cost", 0)
            print(f"   💰 Total Cost (All): ${total_cost:,.2f}")
            
            # Verificar se há Oracle na distribuição
            providers = data.get("provider_distribution", [])
            oracle_provider = [p for p in providers if "Oracle" in p.get("provider_name", "")]
            
            if oracle_provider:
                for p in oracle_provider:
                    print(f"   🎯 Oracle encontrado: {p['provider_name']} - ${p['total_cost']:,.2f} ({p['percentage_of_total']:.1f}%)")
            else:
                print("   ❌ Nenhum provider Oracle encontrado na distribuição")
                
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro no teste All: {e}")
    
    # Teste 2: Dashboard Summary com filtro Oracle Cloud
    print("\n2️⃣ Teste Dashboard Summary - COM filtro 'Oracle Cloud':")
    try:
        url = f"{base_url}/api/v1/dashboard/summary"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "provider_name": "Oracle Cloud"
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            total_cost = data.get("cost_summary", {}).get("totals", {}).get("total_cost", 0)
            record_count = data.get("cost_summary", {}).get("totals", {}).get("record_count", 0)
            
            print(f"   💰 Total Cost (Oracle Cloud): ${total_cost:,.2f}")
            print(f"   📊 Record Count: {record_count}")
            
            # Verificar distribuição
            providers = data.get("provider_distribution", [])
            print(f"   🏢 Providers na distribuição: {len(providers)}")
            
            for p in providers:
                print(f"      - {p['provider_name']}: ${p['total_cost']:,.2f} ({p['percentage_of_total']:.1f}%)")
                
            # ❌ PROBLEMA: Se total_cost for 0, há um bug!
            if total_cost == 0:
                print("   🚨 PROBLEMA ENCONTRADO: Total cost é $0.00 para Oracle Cloud!")
            else:
                print("   ✅ Oracle Cloud retornou dados válidos")
                
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro no teste Oracle Cloud: {e}")

def test_analytics_by_provider_api():
    """Testar o endpoint /api/v1/analytics/by-provider com filtro Oracle Cloud"""
    
    print("\n" + "=" * 60)
    print("🔍 TESTE API ANALYTICS BY PROVIDER")
    
    # Token obtido de variável de ambiente
    token = os.environ.get("X_COST_API_TOKEN", "")
    if not token:
        print("⚠️ Configure a variável de ambiente X_COST_API_TOKEN")
        return
    
    base_url = "http://localhost:8000"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Período de 30 dias
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    print(f"📅 Testando período: {start_date} a {end_date}")
    
    # Teste analytics by provider
    print("\n1️⃣ Teste Analytics By Provider - COM filtro 'Oracle Cloud':")
    try:
        url = f"{base_url}/api/v1/analytics/by-provider"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "provider_name": "Oracle Cloud"
        }
        
        response = requests.get(url, headers=headers, params=params)
        print(f"   📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list):
                print(f"   📊 Providers encontrados: {len(data)}")
                for provider in data:
                    name = provider.get("provider_name", "Unknown")
                    cost = provider.get("total_cost", 0)
                    percentage = provider.get("percentage_of_total", 0)
                    print(f"      - {name}: ${cost:,.2f} ({percentage:.1f}%)")
            else:
                print(f"   📊 Resposta: {data}")
                
        else:
            print(f"   ❌ Erro: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Erro no teste Analytics: {e}")

def debug_database_queries():
    """Debug direto das queries do banco para Oracle Cloud"""
    
    print("\n" + "=" * 60)
    print("🔍 DEBUG QUERIES BANCO DE DADOS")
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Período de 30 dias (igual ao frontend)
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        print(f"📅 Período analisado: {start_date} a {end_date}")
        
        # 1. Query simples para Oracle Cloud (igual ao que o backend deveria fazer)
        print("\n1️⃣ Query simples Oracle Cloud:")
        
        oracle_total = db.query(
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.provider_name == 'Oracle Cloud'
            )
        ).first()
        
        print(f"   💰 Total Oracle Cloud: ${oracle_total.total_cost or 0:,.2f}")
        print(f"   📊 Registros Oracle Cloud: {oracle_total.record_count}")
        
        # 2. Query para todos os providers (igual ao "All")
        print("\n2️⃣ Query todos os providers:")
        
        all_total = db.query(
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date
            )
        ).first()
        
        print(f"   💰 Total Geral: ${all_total.total_cost or 0:,.2f}")
        print(f"   📊 Registros Totais: {all_total.record_count}")
        
        # 3. Distribuição por provider
        print("\n3️⃣ Distribuição por provider:")
        
        provider_distribution = db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.count().label('record_count')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date
            )
        ).group_by(FocusCostData.provider_name).order_by(
            func.sum(FocusCostData.effective_cost).desc()
        ).all()
        
        for provider in provider_distribution:
            percentage = (provider.total_cost / all_total.total_cost * 100) if all_total.total_cost > 0 else 0
            print(f"   - {provider.provider_name}: ${provider.total_cost:,.2f} ({percentage:.1f}%) - {provider.record_count} registros")
        
        # 4. Verificar se há dados Oracle com nomenclatura diferente
        print("\n4️⃣ Verificando variações Oracle:")
        
        oracle_variations = db.query(
            FocusCostData.provider_name,
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).filter(
            and_(
                FocusCostData.charge_period_start >= start_date,
                FocusCostData.charge_period_start <= end_date,
                FocusCostData.provider_name.ilike('%oracle%')
            )
        ).group_by(FocusCostData.provider_name).all()
        
        for variation in oracle_variations:
            print(f"   - '{variation.provider_name}': ${variation.total_cost:,.2f}")
        
    except Exception as e:
        print(f"❌ Erro durante debug: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def main():
    """Função principal"""
    print("🔍 DEBUG: Problema do filtro Oracle Cloud no Spend Summary")
    print("=" * 80)
    
    # 1. Debug básico do banco
    debug_oracle_cloud_data()
    
    # 2. Debug queries diretas
    debug_database_queries()
    
    # 3. Teste APIs
    test_dashboard_summary_api()
    test_analytics_by_provider_api()
    
    print("\n" + "=" * 80)
    print("🎯 PRÓXIMOS PASSOS:")
    print("1. Se APIs retornam $0.00 para Oracle Cloud, há bug no backend")
    print("2. Verificar se filtro provider_name está sendo aplicado corretamente")
    print("3. Comparar com funcionamento do endpoint Top Services (que está correto)")
    print("4. Investigar diferenças na implementação entre endpoints")

if __name__ == "__main__":
    main()
