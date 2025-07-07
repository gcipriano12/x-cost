#!/usr/bin/env python3
"""
Script para verificar o range de datas disponível no banco de dados
"""

import sys
import os
sys.path.append('/Users/gcipriano/Repositories/x-cost/backend')

from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import sessionmaker
from app.models import FocusCostData
from datetime import date

def check_data_range():
    """Verificar range de datas no banco de dados"""
    
    print("📅 VERIFICAÇÃO DO RANGE DE DATAS NO BANCO")
    print("=" * 60)
    
    # Conectar ao banco
    engine = create_engine(os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_password@localhost:5432/finops_db'))
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # 1. Range geral de datas
        print("\n1️⃣ RANGE GERAL DE DATAS:")
        min_max_dates = db.query(
            func.min(FocusCostData.billing_period_start).label('min_date'),
            func.max(FocusCostData.billing_period_start).label('max_date'),
            func.count(FocusCostData.id).label('total_records')
        ).first()
        
        print(f"   Data mais antiga: {min_max_dates.min_date}")
        print(f"   Data mais recente: {min_max_dates.max_date}")
        print(f"   Total de registros: {min_max_dates.total_records:,}")
        
        # 2. Datas únicas disponíveis (ordenadas)
        print("\n2️⃣ DATAS ÚNICAS DISPONÍVEIS (por billing_period_start):")
        unique_dates = db.query(
            distinct(FocusCostData.billing_period_start)
        ).order_by(FocusCostData.billing_period_start).all()
        
        print(f"   Total de datas únicas: {len(unique_dates)}")
        for i, date_row in enumerate(unique_dates):
            if i < 10:  # Primeiras 10
                print(f"   {date_row[0]}")
            elif i == 10:
                print(f"   ... ({len(unique_dates) - 20} datas no meio) ...")
            elif i >= len(unique_dates) - 10:  # Últimas 10
                print(f"   {date_row[0]}")
        
        # 3. Distribuição por mês/ano
        print("\n3️⃣ DISTRIBUIÇÃO POR MÊS/ANO:")
        monthly_distribution = db.query(
            func.extract('year', FocusCostData.billing_period_start).label('year'),
            func.extract('month', FocusCostData.billing_period_start).label('month'),
            func.count(FocusCostData.id).label('record_count'),
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).group_by(
            func.extract('year', FocusCostData.billing_period_start),
            func.extract('month', FocusCostData.billing_period_start)
        ).order_by(
            func.extract('year', FocusCostData.billing_period_start),
            func.extract('month', FocusCostData.billing_period_start)
        ).all()
        
        for row in monthly_distribution:
            year = int(row.year)
            month = int(row.month)
            month_name = [
                'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
            ][month-1]
            print(f"   {month_name}/{year}: {row.record_count:>6,} registros - ${row.total_cost:>12,.2f}")
        
        # 4. Distribuição por provider no período mais recente
        print("\n4️⃣ DISTRIBUIÇÃO POR PROVIDER (último mês com dados):")
        latest_month = db.query(
            func.max(FocusCostData.billing_period_start)
        ).scalar()
        
        if latest_month:
            latest_year = latest_month.year
            latest_month_num = latest_month.month
            
            provider_distribution = db.query(
                FocusCostData.provider_name,
                func.count(FocusCostData.id).label('record_count'),
                func.sum(FocusCostData.effective_cost).label('total_cost')
            ).filter(
                func.extract('year', FocusCostData.billing_period_start) == latest_year,
                func.extract('month', FocusCostData.billing_period_start) == latest_month_num
            ).group_by(FocusCostData.provider_name).all()
            
            print(f"   Mês: {latest_month_num:02d}/{latest_year}")
            for provider in provider_distribution:
                print(f"   {provider.provider_name:<15}: {provider.record_count:>6,} registros - ${provider.total_cost:>12,.2f}")
        
        # 5. Data atual vs dados disponíveis
        print("\n5️⃣ CONTEXTO TEMPORAL:")
        today = date.today()
        print(f"   Data atual: {today}")
        if min_max_dates.max_date:
            days_diff = (today - min_max_dates.max_date).days
            print(f"   Diferença até dados mais recentes: {days_diff} dias")
            if days_diff > 30:
                print(f"   ⚠️  ATENÇÃO: Dados estão {days_diff} dias defasados!")
            else:
                print(f"   ✅ Dados estão atualizados (menos de 30 dias)")
        
        # 6. Análise detalhada: Providers por mês
        print("\n6️⃣ ANÁLISE DETALHADA: PROVIDERS POR MÊS/ANO:")
        provider_monthly = db.query(
            func.extract('year', FocusCostData.billing_period_start).label('year'),
            func.extract('month', FocusCostData.billing_period_start).label('month'),
            FocusCostData.provider_name,
            func.count(FocusCostData.id).label('record_count'),
            func.sum(FocusCostData.effective_cost).label('total_cost')
        ).group_by(
            func.extract('year', FocusCostData.billing_period_start),
            func.extract('month', FocusCostData.billing_period_start),
            FocusCostData.provider_name
        ).order_by(
            func.extract('year', FocusCostData.billing_period_start),
            func.extract('month', FocusCostData.billing_period_start),
            FocusCostData.provider_name
        ).all()
        
        # Organizar dados por mês/ano
        months_data = {}
        all_providers = set()
        
        for row in provider_monthly:
            year = int(row.year)
            month = int(row.month)
            month_key = f"{year}-{month:02d}"
            provider = row.provider_name
            
            if month_key not in months_data:
                months_data[month_key] = {}
            
            months_data[month_key][provider] = {
                'records': row.record_count,
                'cost': float(row.total_cost)
            }
            all_providers.add(provider)
        
        print(f"   Provedores encontrados: {sorted(all_providers)}")
        print(f"   Total de meses com dados: {len(months_data)}")
        
        # Verificar completude por mês
        print("\n   📊 COMPLETUDE POR MÊS:")
        incomplete_months = []
        
        for month_key in sorted(months_data.keys()):
            year, month = month_key.split('-')
            month_name = [
                'Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun',
                'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'
            ][int(month)-1]
            
            providers_in_month = set(months_data[month_key].keys())
            missing_providers = all_providers - providers_in_month
            
            if missing_providers:
                incomplete_months.append({
                    'month': f"{month_name}/{year}",
                    'missing': missing_providers,
                    'present': providers_in_month
                })
                print(f"   ❌ {month_name}/{year}: FALTAM {sorted(missing_providers)} (têm: {sorted(providers_in_month)})")
            else:
                print(f"   ✅ {month_name}/{year}: Todos os {len(all_providers)} provedores presentes")
        
        # Resumo de completude
        print(f"\n   📈 RESUMO DE COMPLETUDE:")
        complete_months = len(months_data) - len(incomplete_months)
        print(f"   Meses completos (todos os providers): {complete_months}/{len(months_data)} ({complete_months/len(months_data)*100:.1f}%)")
        print(f"   Meses incompletos: {len(incomplete_months)}/{len(months_data)} ({len(incomplete_months)/len(months_data)*100:.1f}%)")
        
        # 7. Análise dos últimos 90 dias (período usado pelo frontend)
        print("\n7️⃣ ANÁLISE DOS ÚLTIMOS 90 DIAS (período do frontend):")
        from datetime import timedelta
        
        today = date.today()
        start_90_days = today - timedelta(days=89)  # 90 dias incluindo hoje
        
        print(f"   Período analisado: {start_90_days} a {today}")
        
        provider_90_days = db.query(
            FocusCostData.provider_name,
            func.count(FocusCostData.id).label('record_count'),
            func.sum(FocusCostData.effective_cost).label('total_cost'),
            func.min(FocusCostData.billing_period_start).label('min_date'),
            func.max(FocusCostData.billing_period_start).label('max_date')
        ).filter(
            FocusCostData.billing_period_start >= start_90_days,
            FocusCostData.billing_period_start <= today
        ).group_by(FocusCostData.provider_name).all()
        
        print(f"   Provedores com dados nos últimos 90 dias: {len(provider_90_days)}")
        total_cost_90_days = sum(float(row.total_cost) for row in provider_90_days)
        
        for row in provider_90_days:
            percentage = (float(row.total_cost) / total_cost_90_days * 100) if total_cost_90_days > 0 else 0
            print(f"   {row.provider_name:<15}: {row.record_count:>6,} registros | ${row.total_cost:>12,.2f} ({percentage:>5.1f}%) | {row.min_date} a {row.max_date}")
        
        print(f"   TOTAL (90 dias): ${total_cost_90_days:>12,.2f}")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_data_range()
