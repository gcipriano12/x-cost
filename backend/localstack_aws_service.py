#!/usr/bin/env python3
"""
Extensão do AWSOptimizationService para usar dados mockados com LocalStack
"""

import json
import os
from typing import List, Optional
from app.cloud_native_optimization import AWSOptimizationService, SavingsOpportunity, CloudAnomaly
from app.cloud_native_optimization import RecommendationType, SeverityLevel, AnomalyType
from datetime import datetime

class LocalStackAWSOptimizationService(AWSOptimizationService):
    """Versão do AWSOptimizationService que usa dados mockados do LocalStack"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mock_data_file = "/tmp/localstack_mock_data.json"
        self.use_mock_data = self._should_use_mock_data()
        
        if self.use_mock_data:
            self.logger.info("Usando dados mockados para LocalStack")
        
    def _should_use_mock_data(self) -> bool:
        """Determina se deve usar dados mockados"""
        # Verifica se está configurado para usar LocalStack
        aws_endpoint = os.getenv('AWS_ENDPOINT_URL', '')
        return 'localhost:4566' in aws_endpoint or '127.0.0.1:4566' in aws_endpoint
    
    def _load_mock_data(self) -> dict:
        """Carrega dados mockados do arquivo"""
        try:
            if os.path.exists(self.mock_data_file):
                with open(self.mock_data_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Erro ao carregar dados mock: {e}")
        
        # Fallback para dados padrão
        return self._get_default_mock_data()
    
    def _get_default_mock_data(self) -> dict:
        """Retorna dados mockados padrão se o arquivo não existir"""
        return {
            'rightsizing_recommendations': {
                'RightsizingRecommendations': [
                    {
                        'AccountId': '123456789012',
                        'EstimatedMonthlySavings': {'Amount': '185.75'},
                        'CurrentInstance': {
                            'InstanceName': 'i-localstack001',
                            'InstanceType': 'm5.large',
                            'Region': 'us-east-1'
                        },
                        'ModifyRecommendationDetail': {
                            'TargetInstances': [{'InstanceType': 'm5.medium'}]
                        }
                    }
                ]
            },
            'reservation_recommendations': {
                'Recommendations': [
                    {
                        'AccountId': '123456789012',
                        'RecommendationDetails': {
                            'EstimatedMonthlySavingsAmount': '425.00',
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
            },
            'savings_plans_recommendations': {
                'SavingsPlansRecommendationDetails': [
                    {
                        'AccountId': '123456789012',
                        'EstimatedMonthlySavings': 340.00,
                        'HourlyCommitmentToPurchase': 4.75,
                        'EstimatedSavingsPercentage': 16.8
                    }
                ]
            },
            'anomalies': {
                'Anomalies': [
                    {
                        'AnomalyId': 'localstack-anom-001',
                        'AnomalyStartDate': '2025-06-15',
                        'DimensionKey': 'EC2-Instance',
                        'Impact': {'MaxImpact': 156.80, 'TotalImpact': 156.80},
                        'RootCauses': [
                            {
                                'Service': 'EC2',
                                'UsageType': 'BoxUsage:m5.large',
                                'Region': 'us-east-1'
                            }
                        ]
                    }
                ]
            },
            'ebs_recommendations': {
                'volumeRecommendations': [
                    {
                        'volumeArn': 'arn:aws:ec2:us-east-1:123456789012:volume/vol-localstack001',
                        'finding': 'Overprovisioned',
                        'currentConfiguration': {
                            'volumeType': 'gp2',
                            'volumeSize': 300
                        }
                    }
                ]
            }
        }
    
    async def _get_ec2_rightsizing_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Override para usar dados mockados"""
        if not self.use_mock_data:
            return await super()._get_ec2_rightsizing_opportunities(min_savings)
        
        opportunities = []
        mock_data = self._load_mock_data()
        
        try:
            rightsizing_data = mock_data.get('rightsizing_recommendations', {})
            
            for rec in rightsizing_data.get('RightsizingRecommendations', []):
                estimated_savings = float(rec.get('EstimatedMonthlySavings', {}).get('Amount', 0))
                
                if estimated_savings < min_savings:
                    continue
                
                current_instance = rec.get('CurrentInstance', {})
                instance_name = current_instance.get('InstanceName', 'unknown')
                current_type = current_instance.get('InstanceType', 'unknown')
                
                opportunity = SavingsOpportunity(
                    id=f"localstack_rightsizing_{instance_name}",
                    provider="AWS",
                    service="EC2",
                    region=current_instance.get('Region', 'us-east-1'),
                    opportunity_type=RecommendationType.RIGHTSIZING,
                    estimated_savings=estimated_savings,
                    confidence_level=90.0,
                    implementation_effort="Baixo",
                    description=f"LocalStack Mock: Rightsizing de {current_type} para m5.medium",
                    resources_affected=[instance_name],
                    action_required=f"Alterar tipo de instância de {current_type} para m5.medium",
                    risk_level=SeverityLevel.LOW
                )
                
                opportunities.append(opportunity)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar dados mock de rightsizing: {e}")
        
        return opportunities
    
    async def _get_reserved_instance_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Override para usar dados mockados"""
        if not self.use_mock_data:
            return await super()._get_reserved_instance_opportunities(min_savings)
        
        opportunities = []
        mock_data = self._load_mock_data()
        
        try:
            ri_data = mock_data.get('reservation_recommendations', {})
            
            for rec in ri_data.get('Recommendations', []):
                rec_details = rec.get('RecommendationDetails', {})
                estimated_savings = float(rec_details.get('EstimatedMonthlySavingsAmount', 0))
                
                if estimated_savings < min_savings:
                    continue
                
                instance_details = rec_details.get('InstanceDetails', {})
                ec2_details = instance_details.get('EC2InstanceDetails', {})
                
                opportunity = SavingsOpportunity(
                    id=f"localstack_ri_{rec.get('AccountId', 'unknown')}",
                    provider="AWS",
                    service="EC2",
                    region=ec2_details.get('Region', 'us-east-1'),
                    opportunity_type=RecommendationType.RESERVED_INSTANCES,
                    estimated_savings=estimated_savings,
                    confidence_level=95.0,
                    implementation_effort="Alto",
                    description=f"LocalStack Mock: Reserved Instance para {ec2_details.get('InstanceType', 'unknown')}",
                    resources_affected=[ec2_details.get('Family', 'unknown')],
                    action_required="Comprar Reserved Instance com termo de 1 ou 3 anos",
                    risk_level=SeverityLevel.MEDIUM
                )
                
                opportunities.append(opportunity)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar dados mock de RI: {e}")
        
        return opportunities
    
    async def _get_savings_plans_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Override para usar dados mockados"""
        if not self.use_mock_data:
            return await super()._get_savings_plans_opportunities(min_savings)
        
        opportunities = []
        mock_data = self._load_mock_data()
        
        try:
            sp_data = mock_data.get('savings_plans_recommendations', {})
            
            for rec in sp_data.get('SavingsPlansRecommendationDetails', []):
                estimated_savings = float(rec.get('EstimatedMonthlySavings', 0))
                
                if estimated_savings < min_savings:
                    continue
                
                hourly_commitment = float(rec.get('HourlyCommitmentToPurchase', 0))
                savings_percentage = float(rec.get('EstimatedSavingsPercentage', 0))
                
                opportunity = SavingsOpportunity(
                    id=f"localstack_sp_{rec.get('AccountId', 'unknown')}",
                    provider="AWS",
                    service="Compute",
                    opportunity_type=RecommendationType.RESERVED_INSTANCES,
                    estimated_savings=estimated_savings,
                    confidence_level=90.0,
                    implementation_effort="Alto",
                    description=f"LocalStack Mock: Savings Plan ${hourly_commitment:.2f}/hora com {savings_percentage:.1f}% economia",
                    resources_affected=["Compute workloads"],
                    action_required=f"Comprar Savings Plan com compromisso de ${hourly_commitment:.2f}/hora",
                    risk_level=SeverityLevel.MEDIUM
                )
                
                opportunities.append(opportunity)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar dados mock de Savings Plans: {e}")
        
        return opportunities
    
    async def _get_ebs_optimization_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Override para usar dados mockados"""
        if not self.use_mock_data:
            return await super()._get_ebs_optimization_opportunities(min_savings)
        
        opportunities = []
        mock_data = self._load_mock_data()
        
        try:
            ebs_data = mock_data.get('ebs_recommendations', {})
            
            for rec in ebs_data.get('volumeRecommendations', []):
                finding = rec.get('finding', '')
                current_config = rec.get('currentConfiguration', {})
                volume_arn = rec.get('volumeArn', 'unknown')
                
                # Estimar economia baseada no finding
                estimated_savings = 0
                if finding == 'Overprovisioned':
                    volume_size = current_config.get('volumeSize', 100)
                    estimated_savings = min(volume_size * 0.4, 120)  # 40% de economia estimada
                elif finding == 'NotOptimized':
                    estimated_savings = 85.0
                
                if estimated_savings < min_savings:
                    continue
                
                opportunity = SavingsOpportunity(
                    id=f"localstack_ebs_{volume_arn.split('/')[-1] if '/' in volume_arn else volume_arn}",
                    provider="AWS",
                    service="EBS",
                    opportunity_type=RecommendationType.STORAGE_OPTIMIZATION,
                    estimated_savings=estimated_savings,
                    confidence_level=80.0,
                    implementation_effort="Baixo",
                    description=f"LocalStack Mock: Otimização EBS - {finding}",
                    resources_affected=[volume_arn],
                    action_required=f"Otimizar volume EBS ({finding.lower()})",
                    risk_level=SeverityLevel.LOW
                )
                
                opportunities.append(opportunity)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar dados mock de EBS: {e}")
        
        return opportunities
    
    async def get_aws_anomalies(self, days: int = 30, min_impact: float = 10.0) -> List[CloudAnomaly]:
        """Override para usar dados mockados de anomalias"""
        if not self.use_mock_data:
            return await super().get_aws_anomalies(days, min_impact)
        
        anomalies = []
        mock_data = self._load_mock_data()
        
        try:
            anomalies_data = mock_data.get('anomalies', {})
            
            for anomaly in anomalies_data.get('Anomalies', []):
                impact_data = anomaly.get('Impact', {})
                cost_impact = float(impact_data.get('MaxImpact', 0))
                
                if cost_impact < min_impact:
                    continue
                
                # Classificar severidade
                if cost_impact >= 150:
                    severity = SeverityLevel.HIGH
                elif cost_impact >= 100:
                    severity = SeverityLevel.MEDIUM
                else:
                    severity = SeverityLevel.LOW
                
                cloud_anomaly = CloudAnomaly(
                    id=f"localstack_{anomaly.get('AnomalyId', 'unknown')}",
                    provider="AWS",
                    service=anomaly.get('DimensionKey', 'Unknown'),
                    region="us-east-1",
                    anomaly_type=AnomalyType.COST_INCREASE,
                    severity=severity,
                    detected_at=datetime.utcnow(),
                    cost_impact=cost_impact,
                    currency="USD",
                    description=f"LocalStack Mock: Anomalia detectada com impacto de ${cost_impact:.2f}",
                    root_cause="Simulação LocalStack - aumento de custos",
                    affected_resources=["LocalStack mock resources"]
                )
                
                anomalies.append(cloud_anomaly)
                
        except Exception as e:
            self.logger.error(f"Erro ao processar dados mock de anomalias: {e}")
        
        return anomalies

# Função para registrar o serviço mockado
def create_localstack_aws_service(**kwargs):
    """Cria instância do serviço AWS configurado para LocalStack"""
    return LocalStackAWSOptimizationService(**kwargs)
