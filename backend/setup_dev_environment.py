#!/usr/bin/env python3
"""
Script para configurar ambiente de desenvolvimento com dados mockados
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Configurar caminho para imports
sys.path.append(str(Path(__file__).parent))

async def setup_mock_optimization_service():
    """Configura o serviço de otimização com dados mockados"""
    
    # Definir variáveis de ambiente do LocalStack
    os.environ['AWS_ENDPOINT_URL'] = 'http://localhost:4566'
    os.environ['AWS_ACCESS_KEY_ID'] = 'test'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
    os.environ['AWS_REGION'] = 'us-east-1'
    os.environ['USE_LOCALSTACK'] = 'true'
    
    from app.cloud_native_optimization import AWSOptimizationService
    
    print("🚀 Configurando serviço AWS com dados mockados...")
    
    # Criar serviço AWS
    aws_service = AWSOptimizationService()
    
    # Testar anomalias
    print("🔍 Testando anomalias...")
    try:
        anomalies = await aws_service.get_aws_anomalies(days=30, min_impact=10.0)
        print(f"   ✅ {len(anomalies)} anomalias encontradas")
        
        for anomaly in anomalies[:3]:
            print(f"   - {anomaly.service}: ${anomaly.cost_impact:.2f} ({anomaly.severity})")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Testar oportunidades de economia
    print("💰 Testando oportunidades de economia...")
    try:
        opportunities = await aws_service.get_aws_savings(min_savings=50.0)
        print(f"   ✅ {len(opportunities)} oportunidades encontradas")
        
        total_savings = sum(opp.estimated_savings for opp in opportunities)
        print(f"   💰 Total de economia: ${total_savings:.2f}")
        
        for opp in opportunities[:3]:
            print(f"   - {opp.opportunity_type.value}: ${opp.estimated_savings:.2f}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")

def create_mock_data_json():
    """Cria arquivo JSON com dados mockados para teste do frontend"""
    
    mock_data = {
        "anomalies": [
            {
                "id": "aws_anomaly_001",
                "provider": "AWS",
                "service": "EC2",
                "region": "us-east-1",
                "anomaly_type": "cost_increase",
                "severity": "high",
                "detected_at": "2025-06-16T12:00:00Z",
                "cost_impact": 2340.50,
                "currency": "USD",
                "description": "Unusual EC2 cost spike detected in us-east-1",
                "root_cause": "New instance types launched",
                "affected_resources": ["i-1234567890abcdef0", "i-0987654321fedcba0"]
            },
            {
                "id": "aws_anomaly_002", 
                "provider": "Azure",
                "service": "Storage",
                "region": "eastus",
                "anomaly_type": "unusual_pattern",
                "severity": "medium",
                "detected_at": "2025-06-16T10:30:00Z",
                "cost_impact": 890.25,
                "currency": "USD",
                "description": "Unexpected storage cost pattern in Azure",
                "root_cause": "Increased data transfer",
                "affected_resources": ["storage-account-001"]
            },
            {
                "id": "gcp_anomaly_001",
                "provider": "GCP", 
                "service": "Compute Engine",
                "region": "us-central1",
                "anomaly_type": "spike",
                "severity": "medium",
                "detected_at": "2025-06-16T09:15:00Z",
                "cost_impact": 567.80,
                "currency": "USD",
                "description": "Compute Engine cost spike in us-central1",
                "root_cause": "Auto-scaling triggered",
                "affected_resources": ["instance-group-001"]
            }
        ],
        "savings_opportunities": [
            {
                "id": "aws_ri_001",
                "provider": "AWS",
                "service": "EC2",
                "region": "us-east-1",
                "opportunity_type": "reserved_instances",
                "estimated_savings": 6780.00,
                "currency": "USD",
                "confidence_level": 95.0,
                "implementation_effort": "Alto",
                "description": "Reserved Instance opportunity for m5.large instances",
                "resources_affected": ["m5.large instances"],
                "action_required": "Purchase 1-year RI commitment",
                "risk_level": "medium",
                "created_at": "2025-06-16T08:00:00Z"
            },
            {
                "id": "aws_rightsizing_001",
                "provider": "AWS",
                "service": "EC2", 
                "region": "us-west-2",
                "opportunity_type": "rightsizing",
                "estimated_savings": 4520.00,
                "currency": "USD",
                "confidence_level": 88.0,
                "implementation_effort": "Baixo",
                "description": "Right-size over-provisioned instances",
                "resources_affected": ["i-abcdef1234567890"],
                "action_required": "Downsize from m5.xlarge to m5.large",
                "risk_level": "low",
                "created_at": "2025-06-16T07:30:00Z"
            },
            {
                "id": "aws_unused_001",
                "provider": "AWS",
                "service": "EBS",
                "region": "us-east-1", 
                "opportunity_type": "idle_resources",
                "estimated_savings": 3950.00,
                "currency": "USD",
                "confidence_level": 92.0,
                "implementation_effort": "Baixo",
                "description": "Remove unused EBS volumes",
                "resources_affected": ["vol-1234567890abcdef0"],
                "action_required": "Delete unattached volumes",
                "risk_level": "low",
                "created_at": "2025-06-16T07:00:00Z"
            }
        ],
        "optimization_summary": {
            "total_anomalies": 7,
            "total_opportunities": 15,
            "total_recommendations": 23,
            "total_estimated_savings": 152570.00,
            "optimization_score": 67,
            "health_status": "needs_attention",
            "currency": "USD",
            "last_updated": "2025-06-16T15:00:00Z",
            "providers_summary": {
                "AWS": {
                    "anomalies_count": 4,
                    "opportunities_count": 12,
                    "estimated_savings": 89340.0,
                    "optimization_score": 71
                },
                "Azure": {
                    "anomalies_count": 2,
                    "opportunities_count": 2,
                    "estimated_savings": 34520.0,
                    "optimization_score": 65
                },
                "GCP": {
                    "anomalies_count": 1,
                    "opportunities_count": 1,
                    "estimated_savings": 28710.0,
                    "optimization_score": 58
                }
            }
        }
    }
    
    # Salvar dados mockados
    mock_file = Path(__file__).parent / "mock_optimization_data.json"
    with open(mock_file, 'w') as f:
        json.dump(mock_data, f, indent=2)
    
    print(f"✅ Dados mockados salvos em: {mock_file}")
    
    return mock_data

def print_api_endpoints():
    """Mostra os endpoints corretos para o frontend"""
    
    endpoints_info = """
🌐 ENDPOINTS CORRETOS PARA O FRONTEND:

1. Anomalias:
   GET http://localhost:8000/api/v1/anomalies
   Query params: provider_name, days, severity, page, per_page

2. Oportunidades de Economia:
   GET http://localhost:8000/api/v1/savings-opportunities  
   Query params: provider_name, min_savings, category, page, per_page

3. Summary de Otimização:
   GET http://localhost:8000/api/v1/optimization/summary
   Query params: provider_name

4. Recomendações:
   GET http://localhost:8000/api/v1/optimization/recommendations
   Query params: provider_name, page, per_page

🔑 TOKEN JWT PARA TESTES:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTc1MDEwMjA3NCwiaWF0IjoxNzUwMDk4NDc0LCJ0eXBlIjoiYWNjZXNzX3Rva2VuIn0.8fsMHVJnIdFUew4cVpWQUuNnP5z4dmQzxHoZzzkrAqk

📝 PRÓXIMOS PASSOS:
1. O serviço de otimização precisa ser inicializado no backend
2. Configurar LocalStack no backend (USE_LOCALSTACK=true)
3. Reiniciar o backend com as variáveis de ambiente corretas
4. Testar os endpoints com curl
5. Verificar se o token JWT está sendo enviado pelo frontend
    """
    
    print(endpoints_info)

async def main():
    """Função principal"""
    print("🛠️ Configurando ambiente de desenvolvimento...")
    
    # 1. Configurar serviço de otimização
    await setup_mock_optimization_service()
    
    # 2. Criar dados mockados
    mock_data = create_mock_data_json()
    
    # 3. Mostrar informações importantes
    print_api_endpoints()
    
    print("\n✅ Configuração concluída!")

if __name__ == "__main__":
    asyncio.run(main())
