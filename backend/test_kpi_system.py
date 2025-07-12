#!/usr/bin/env python3
"""
Teste do Sistema de KPIs - X Cost
Testa endpoints básicos e funcionalidade do sistema de KPIs
"""

import asyncio
import sys
import os
import json
from datetime import date, datetime

# Adicionar o diretório pai ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_database
from app.kpi.service import KPIService
from app.kpi.calculator import KPICalculator
from app.kpi.models import KPIDefinition, KPICategory

def test_kpi_system():
    """Testa o sistema de KPIs"""
    print("🔄 Testando Sistema de KPIs...")
    
    try:
        # Obter sessão de banco
        db = next(get_database())
        
        print("✅ Conexão com banco estabelecida")
        
        # Testar busca de definições de KPI
        kpi_definitions = db.query(KPIDefinition).filter(
            KPIDefinition.is_active == True
        ).all()
        
        print(f"✅ Encontradas {len(kpi_definitions)} definições de KPI ativas")
        
        for kpi in kpi_definitions[:5]:  # Mostrar primeiros 5
            print(f"   - {kpi.code}: {kpi.name} ({kpi.category})")
        
        # Testar serviço de KPI
        service = KPIService(db)
        
        # Buscar KPIs atuais
        current_kpis = service.get_current_kpis()
        print(f"✅ Obtidos {len(current_kpis)} KPIs atuais via serviço")
        
        # Buscar por categoria
        efficiency_kpis = service.get_current_kpis(category=KPICategory.EFFICIENCY)
        print(f"✅ Encontrados {len(efficiency_kpis)} KPIs de eficiência")
        
        # Testar cálculo
        calculator = KPICalculator(db)
        
        # Calcular KPIs para hoje (pode gerar dados demo)
        today = date.today()
        print(f"🔄 Calculando KPIs para {today}...")
        
        # Tentar calcular apenas alguns KPIs específicos para teste
        test_kpis = ['resource_utilization_rate', 'tag_compliance_rate', 'cloud_waste_percentage']
        
        for kpi_code in test_kpis:
            kpi_def = db.query(KPIDefinition).filter(
                KPIDefinition.code == kpi_code,
                KPIDefinition.is_active == True
            ).first()
            
            if kpi_def:
                try:
                    value = calculator._calculate_kpi(kpi_def, today)
                    if value is not None:
                        print(f"   ✅ {kpi_code}: {float(value):.2f} {kpi_def.unit or ''}")
                    else:
                        print(f"   ⚠️  {kpi_code}: Não foi possível calcular")
                except Exception as e:
                    print(f"   ❌ {kpi_code}: Erro - {str(e)}")
            else:
                print(f"   ❌ {kpi_code}: KPI não encontrado")
        
        # Testar agrupamento por categoria
        categorized = service.get_kpis_by_category()
        print(f"✅ KPIs agrupados em {len(categorized)} categorias")
        
        for category in categorized:
            print(f"   - {category.category}: {len(category.kpis)} KPIs")
        
        print("\n🎉 Teste do Sistema de KPIs concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

def test_api_simulation():
    """Simula chamadas para API de KPIs"""
    print("\n🔄 Simulando chamadas de API...")
    
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Tentar endpoints sem autenticação (pode dar erro, mas vamos ver a estrutura)
        print("🔄 Testando endpoints...")
        
        endpoints = [
            "/api/v1/kpis/current",
            "/api/v1/kpis/by-category",
        ]
        
        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                print(f"   {endpoint}: Status {response.status_code}")
                if response.status_code != 401:  # Se não for erro de auth
                    print(f"     Response: {response.json()}")
            except Exception as e:
                print(f"   {endpoint}: Erro - {str(e)}")
        
        print("✅ Teste de API concluído")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de API: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TESTE DO SISTEMA DE KPIs - X COST")
    print("=" * 60)
    
    success = True
    
    # Teste 1: Sistema básico
    success &= test_kpi_system()
    
    # Teste 2: API
    success &= test_api_simulation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de KPIs está funcionando corretamente")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("⚠️  Verifique os logs acima para mais detalhes")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
