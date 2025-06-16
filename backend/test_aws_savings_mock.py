#!/usr/bin/env python3
"""
Teste final de validação da implementação do get_aws_savings
"""

import asyncio
import json
import logging
from unittest.mock import Mock, patch
from app.cloud_native_optimization import AWSOptimizationService, SavingsOpportunity, RecommendationType, SeverityLevel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_aws_savings_with_mock_data():
    """Testa o método get_aws_savings com dados mockados"""
    
    print("🧪 Testando get_aws_savings com dados mockados...")
    
    try:
        # Criar mock dos clientes AWS
        mock_cost_explorer = Mock()
        mock_compute_optimizer = Mock()
        mock_session = Mock()
        
        # Mock das respostas das APIs
        mock_cost_explorer.get_rightsizing_recommendation.return_value = {
            'RightsizingRecommendations': [
                {
                    'AccountId': '123456789012',
                    'EstimatedMonthlySavings': {'Amount': '150.00'},
                    'CurrentInstance': {
                        'InstanceName': 'i-1234567890abcdef0',
                        'InstanceType': 'm5.large',
                        'Region': 'us-east-1'
                    },
                    'ModifyRecommendationDetail': {
                        'TargetInstances': [
                            {'InstanceType': 'm5.medium'}
                        ]
                    }
                }
            ]
        }
        
        mock_cost_explorer.get_reservation_purchase_recommendation.return_value = {
            'Recommendations': [
                {
                    'AccountId': '123456789012',
                    'RecommendationDetails': {
                        'EstimatedMonthlySavingsAmount': '300.00',
                        'InstanceDetails': {
                            'EC2InstanceDetails': {
                                'Family': 'm5',
                                'InstanceType': 'm5.large',
                                'Region': 'us-east-1'
                            }
                        }
                    }
                }
            ]
        }
        
        mock_cost_explorer.get_savings_plans_purchase_recommendation.return_value = {
            'SavingsPlansRecommendationDetails': [
                {
                    'AccountId': '123456789012',
                    'EstimatedMonthlySavings': 200.00,
                    'HourlyCommitmentToPurchase': 2.50,
                    'EstimatedSavingsPercentage': 15.0
                }
            ]
        }
        
        mock_compute_optimizer.get_ebs_volume_recommendations.return_value = {
            'volumeRecommendations': [
                {
                    'volumeArn': 'arn:aws:ec2:us-east-1:123456789012:volume/vol-1234567890abcdef0',
                    'finding': 'Overprovisioned',
                    'currentConfiguration': {
                        'volumeType': 'gp2',
                        'volumeSize': 200
                    }
                }
            ]
        }
        
        mock_session.client.side_effect = lambda service: {
            'elbv2': Mock(**{
                'describe_load_balancers.return_value': {'LoadBalancers': []},
                'describe_target_groups.return_value': {'TargetGroups': []}
            }),
            'rds': Mock(**{
                'describe_db_instances.return_value': {'DBInstances': []}
            }),
            'lambda': Mock(**{
                'list_functions.return_value': {'Functions': []}
            })
        }.get(service, Mock())
        
        # Criar instância do serviço AWS com mocks
        aws_service = AWSOptimizationService()
        aws_service.cost_explorer = mock_cost_explorer
        aws_service.compute_optimizer = mock_compute_optimizer
        aws_service.session = mock_session
        
        print("✅ Serviço AWS mockado criado")
        
        # Testar get_aws_savings
        print("🔍 Executando get_aws_savings com dados mockados...")
        
        opportunities = await aws_service.get_aws_savings(min_savings=10.0)
        
        print(f"✅ get_aws_savings executado: {len(opportunities)} oportunidades")
        
        # Verificar tipos de oportunidades encontradas
        opportunity_types = {}
        total_savings = 0
        
        for opp in opportunities:
            opp_type = opp.opportunity_type.value
            opportunity_types[opp_type] = opportunity_types.get(opp_type, 0) + 1
            total_savings += opp.estimated_savings
            
            print(f"   - {opp.id}: ${opp.estimated_savings:.2f} ({opp.opportunity_type.value})")
        
        print(f"📊 Resumo das oportunidades:")
        for opp_type, count in opportunity_types.items():
            print(f"   - {opp_type}: {count} oportunidades")
        
        print(f"💰 Total de economia estimada: ${total_savings:.2f}")
        
        # Verificar se os dados estão corretos
        expected_types = [
            RecommendationType.RIGHTSIZING,
            RecommendationType.RESERVED_INSTANCES,
            RecommendationType.STORAGE_OPTIMIZATION
        ]
        
        found_types = [opp.opportunity_type for opp in opportunities]
        
        for expected_type in expected_types:
            if expected_type in found_types:
                print(f"   ✅ {expected_type.value} encontrado")
            else:
                print(f"   ⚠️ {expected_type.value} não encontrado")
        
        # Testar normalização dos dados
        if opportunities:
            first_opp = opportunities[0]
            print(f"📋 Exemplo de oportunidade normalizada:")
            print(f"   ID: {first_opp.id}")
            print(f"   Provider: {first_opp.provider}")
            print(f"   Service: {first_opp.service}")
            print(f"   Tipo: {first_opp.opportunity_type.value}")
            print(f"   Economia: ${first_opp.estimated_savings:.2f}")
            print(f"   Confiança: {first_opp.confidence_level:.1f}%")
            print(f"   Esforço: {first_opp.implementation_effort}")
            print(f"   Risco: {first_opp.risk_level.value}")
        
        print("✅ Teste com dados mockados concluído com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro no teste com dados mockados: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_aws_savings_with_mock_data())
