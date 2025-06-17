"""
AWS Optimization Service

Serviço de otimização para AWS usando Cost Explorer e Compute Optimizer
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from fastapi import HTTPException

from ..decorators import retry_with_exponential_backoff
from ..models import (
    CloudAnomaly, 
    SavingsOpportunity, 
    OptimizationRecommendation,
    AnomalyType,
    SeverityLevel,
    RecommendationType
)
from .base import BaseOptimizationService

# AWS imports
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False


class AWSOptimizationService(BaseOptimizationService):
    """Serviço de otimização para AWS usando Cost Explorer e Compute Optimizer"""
    
    def __init__(self, access_key: str = None, secret_key: str = None, region: str = "us-east-1"):
        super().__init__("AWS")
        
        if not AWS_AVAILABLE:
            raise ImportError("boto3 não está disponível. Instale com: pip install boto3")
        
        # Configuração detalhada de logging
        self.logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [AWS] %(message)s'
        )
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        
        # Configurar clientes AWS com tratamento de erro
        try:
            session_kwargs = {"region_name": region}
            if access_key and secret_key:
                session_kwargs.update({
                    "aws_access_key_id": access_key,
                    "aws_secret_access_key": secret_key
                })
            
            self.session = boto3.Session(**session_kwargs)
            self.cost_explorer = self.session.client('ce')
            self.compute_optimizer = self.session.client('compute-optimizer')
            self.cloudwatch = self.session.client('cloudwatch')
            self.region = region
            
            self.logger.info(f"AWS clients inicializados com sucesso na região {region}")
            
        except (NoCredentialsError, PartialCredentialsError) as e:
            self.logger.error(f"Erro de credenciais AWS: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao inicializar clientes AWS: {e}")
            raise
    
    @retry_with_exponential_backoff()
    async def get_anomalies(self) -> List[CloudAnomaly]:
        """Método compatível com interface base - usa get_aws_anomalies"""
        return await self.get_aws_anomalies()
    
    @retry_with_exponential_backoff()
    async def get_savings_opportunities(self) -> List[SavingsOpportunity]:
        """Método compatível com interface base - usa get_aws_savings"""
        return await self.get_aws_savings()
    
    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    async def get_aws_savings(self, min_savings: float = 50.0, include_categories: List[str] = None) -> List[SavingsOpportunity]:
        """
        Obtém oportunidades de economia da AWS de múltiplas fontes
        
        Args:
            min_savings: Economia mínima em USD para incluir (padrão: $50)
            include_categories: Categorias a incluir (compute, storage, network, database, reserved_instances)
            
        Returns:
            Lista de SavingsOpportunity normalizadas e priorizadas
        """
        opportunities = []
        
        try:
            self.logger.info(f"Iniciando busca de oportunidades de economia AWS - economia mínima ${min_savings}")
            
            # Definir categorias padrão se não especificadas
            if include_categories is None:
                include_categories = ['compute', 'storage', 'network', 'database', 'reserved_instances']
            
            # 1. Right Sizing Recommendations para EC2
            if 'compute' in include_categories:
                opportunities.extend(await self._get_ec2_rightsizing_opportunities(min_savings))
            
            # 2. Reserved Instance Recommendations
            if 'reserved_instances' in include_categories:
                opportunities.extend(await self._get_reserved_instance_opportunities(min_savings))
            
            # 3. Savings Plans Recommendations
            if 'reserved_instances' in include_categories:
                opportunities.extend(await self._get_savings_plans_opportunities(min_savings))
            
            # 4. EBS Volume Optimization
            if 'storage' in include_categories:
                opportunities.extend(await self._get_ebs_optimization_opportunities(min_savings))
            
            # 5. Load Balancer Optimization
            if 'network' in include_categories:
                opportunities.extend(await self._get_load_balancer_opportunities(min_savings))
            
            # 6. RDS Optimization
            if 'database' in include_categories:
                opportunities.extend(await self._get_rds_optimization_opportunities(min_savings))
            
            # 7. Lambda Optimization
            if 'compute' in include_categories:
                opportunities.extend(await self._get_lambda_optimization_opportunities(min_savings))
            
            # Filtrar por economia mínima
            opportunities = [opp for opp in opportunities if opp.estimated_savings >= min_savings]
            
            # Calcular ROI e priorizar
            self._calculate_roi_and_prioritize(opportunities)
            
            # Ordenar por economia estimada (maior primeiro)
            opportunities.sort(key=lambda x: x.estimated_savings, reverse=True)
            
            self.logger.info(f"Processamento concluído: {len(opportunities)} oportunidades de economia encontradas")
            
            return opportunities
            
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar oportunidades AWS: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao buscar oportunidades de economia AWS"
            )
    
    @retry_with_exponential_backoff()
    async def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Obtém recomendações de otimização da AWS"""
        recommendations = []
        
        try:
            # Compute Optimizer Recommendations
            try:
                ec2_recs = self.compute_optimizer.get_ec2_instance_recommendations()
                
                for rec in ec2_recs.get('instanceRecommendations', []):
                    potential_savings = 0
                    
                    # Calcular economia baseada nas opções de recomendação
                    for option in rec.get('recommendationOptions', []):
                        if option.get('estimatedMonthlySavings'):
                            potential_savings += float(option['estimatedMonthlySavings'].get('value', 0))
                    
                    recommendations.append(OptimizationRecommendation(
                        id=f"aws-compute-{rec.get('instanceArn', 'unknown')}",
                        provider="AWS",
                        category=RecommendationType.RIGHTSIZING,
                        title="Otimização de Instância EC2",
                        description=f"Recomendação de otimização para {rec.get('instanceName', 'instância')}",
                        potential_savings=potential_savings,
                        priority=SeverityLevel.MEDIUM,
                        implementation_time="30 minutos",
                        steps=[
                            "Analisar métricas de utilização",
                            "Selecionar novo tipo de instância",
                            "Agendar janela de manutenção",
                            "Aplicar alteração"
                        ],
                        resources=[rec.get('instanceArn', 'unknown')]
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Compute Optimizer não disponível: {e}")
                
        except Exception as e:
            self.logger.error(f"Erro ao obter recomendações AWS: {e}")
            
        return recommendations

    @retry_with_exponential_backoff(max_retries=3, initial_delay=1.0)
    async def get_aws_anomalies(self, days: int = 30, min_impact: float = 10.0) -> List[CloudAnomaly]:
        """
        Obtém anomalias de custo da AWS usando Cost Explorer
        
        Args:
            days: Número de dias para buscar anomalias (padrão: 30)
            min_impact: Impacto mínimo em USD para incluir anomalia (padrão: $10)
            
        Returns:
            Lista de CloudAnomaly normalizadas
        """
        anomalies = []
        
        try:
            self.logger.info(f"Iniciando busca de anomalias AWS - últimos {days} dias, impacto mínimo ${min_impact}")
            
            # Calcular datas
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            self.logger.debug(f"Período de busca: {start_date_str} a {end_date_str}")
            
            # Buscar detectores de anomalia primeiro
            detectors_response = self.cost_explorer.get_anomaly_detectors()
            active_detectors = [
                d for d in detectors_response.get('AnomalyDetectors', [])
                if d.get('DetectorState') == 'ACTIVE'
            ]
            
            self.logger.info(f"Encontrados {len(active_detectors)} detectores ativos")
            
            # Buscar anomalias detectadas
            anomalies_response = self.cost_explorer.get_anomalies(
                DateInterval={
                    'StartDate': start_date_str,
                    'EndDate': end_date_str
                },
                MaxResults=100,  # Limite da API
                TotalImpactAbsolute={
                    'NumericOperator': 'GREATER_THAN_OR_EQUAL',
                    'Values': [str(min_impact)]
                }
            )
            
            aws_anomalies = anomalies_response.get('Anomalies', [])
            self.logger.info(f"API retornou {len(aws_anomalies)} anomalias")
            
            # Processar e normalizar cada anomalia
            for idx, anomaly in enumerate(aws_anomalies):
                try:
                    normalized_anomaly = self._normalize_aws_anomaly(anomaly)
                    if normalized_anomaly:
                        anomalies.append(normalized_anomaly)
                        self.logger.debug(f"Anomalia {idx + 1} processada: {normalized_anomaly.id}")
                
                except Exception as e:
                    self.logger.warning(f"Erro ao processar anomalia {idx + 1}: {e}")
                    continue
            
            # Ordenar por impacto (maior primeiro)
            anomalies.sort(key=lambda x: x.cost_impact, reverse=True)
            
            self.logger.info(f"Processamento concluído: {len(anomalies)} anomalias válidas")
            
            return anomalies
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_message = e.response.get('Error', {}).get('Message', str(e))
            
            self.logger.error(f"Erro da API AWS Cost Explorer: {error_code} - {error_message}")
            
            # Mapear erros comuns
            if error_code == 'AccessDenied':
                raise HTTPException(
                    status_code=403,
                    detail="Acesso negado ao AWS Cost Explorer. Verifique as permissões IAM."
                )
            elif error_code == 'ThrottlingException':
                raise HTTPException(
                    status_code=429,
                    detail="Limite de taxa da API AWS excedido. Tente novamente em alguns momentos."
                )
            elif error_code == 'DataUnavailableException':
                self.logger.warning("Dados de anomalia não disponíveis para o período solicitado")
                return []
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro na API AWS: {error_message}"
                )
                
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar anomalias AWS: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erro interno ao buscar anomalias AWS"
            )
    
    def _normalize_aws_anomaly(self, aws_anomaly: dict) -> Optional[CloudAnomaly]:
        """
        Normaliza anomalia AWS para formato CloudAnomaly
        
        Args:
            aws_anomaly: Dados brutos da anomalia da AWS
            
        Returns:
            CloudAnomaly normalizada ou None se inválida
        """
        try:
            # Extrair informações básicas
            anomaly_id = aws_anomaly.get('AnomalyId', '')
            if not anomaly_id:
                self.logger.warning("Anomalia sem ID - pulando")
                return None
            
            # Impacto financeiro
            impact_data = aws_anomaly.get('Impact', {})
            max_impact = float(impact_data.get('MaxImpact', 0))
            total_impact = float(impact_data.get('TotalImpact', 0))
            cost_impact = max(max_impact, total_impact)
            
            # Classificar severidade baseada no impacto
            if cost_impact >= 1000:
                severity = SeverityLevel.CRITICAL
            elif cost_impact >= 500:
                severity = SeverityLevel.HIGH
            elif cost_impact >= 100:
                severity = SeverityLevel.MEDIUM
            else:
                severity = SeverityLevel.LOW
            
            # Data de detecção
            try:
                detected_date = datetime.fromisoformat(
                    aws_anomaly['AnomalyStartDate'].replace('Z', '+00:00')
                )
            except (KeyError, ValueError):
                detected_date = datetime.utcnow()
                self.logger.warning(f"Data de detecção inválida para anomalia {anomaly_id}")
            
            # Serviço e dimensões
            dimension_key = aws_anomaly.get('DimensionKey', 'Unknown')
            service_name = self._extract_service_name(dimension_key, aws_anomaly)
            
            # Recursos afetados
            affected_resources = self._extract_affected_resources(aws_anomaly)
            
            # Causa raiz
            root_cause = self._extract_root_cause(aws_anomaly)
            
            # Descrição detalhada
            description = self._build_anomaly_description(aws_anomaly, cost_impact, service_name)
            
            # Criar CloudAnomaly normalizada
            return CloudAnomaly(
                id=f"aws_anomaly_{anomaly_id}",
                provider="AWS",
                service=service_name,
                region=self.region,
                anomaly_type=AnomalyType.COST_INCREASE,
                severity=severity,
                detected_at=detected_date,
                cost_impact=cost_impact,
                currency="USD",
                description=description,
                root_cause=root_cause,
                affected_resources=affected_resources
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao normalizar anomalia AWS: {e}")
            return None
    
    def _extract_service_name(self, dimension_key: str, aws_anomaly: dict) -> str:
        """Extrai o nome do serviço da anomalia"""
        # Tentar extrair do dimension key
        if dimension_key and dimension_key != 'Unknown':
            return dimension_key
        
        # Tentar extrair das causas raiz
        root_causes = aws_anomaly.get('RootCauses', [])
        if root_causes:
            service = root_causes[0].get('Service')
            if service:
                return service
        
        # Fallback
        return "AWS Service"
    
    def _extract_affected_resources(self, aws_anomaly: dict) -> List[str]:
        """Extrai recursos afetados da anomalia"""
        resources = []
        
        # Recursos das causas raiz
        root_causes = aws_anomaly.get('RootCauses', [])
        for cause in root_causes:
            usage_type = cause.get('UsageType')
            if usage_type:
                resources.append(usage_type)
        
        # ARNs se disponíveis
        monitor_arn = aws_anomaly.get('MonitorArn')
        if monitor_arn:
            resources.append(monitor_arn)
        
        return list(set(resources))  # Remove duplicatas
    
    def _extract_root_cause(self, aws_anomaly: dict) -> Optional[str]:
        """Extrai a causa raiz da anomalia"""
        root_causes = aws_anomaly.get('RootCauses', [])
        if not root_causes:
            return None
        
        cause_descriptions = []
        for cause in root_causes:
            service = cause.get('Service', '')
            usage_type = cause.get('UsageType', '')
            region = cause.get('Region', '')
            
            parts = [p for p in [service, usage_type, region] if p]
            if parts:
                cause_descriptions.append(' - '.join(parts))
        
        return '; '.join(cause_descriptions[:3])  # Limite de 3 causas
    
    def _build_anomaly_description(self, aws_anomaly: dict, cost_impact: float, service_name: str) -> str:
        """Constrói descrição detalhada da anomalia"""
        impact_data = aws_anomaly.get('Impact', {})
        
        description_parts = [
            f"Anomalia de custo detectada em {service_name}",
            f"Impacto financeiro: ${cost_impact:.2f} USD"
        ]
        
        # Adicionar informações de impacto se disponíveis
        if 'TotalImpact' in impact_data:
            total_impact = float(impact_data['TotalImpact'])
            description_parts.append(f"Impacto total: ${total_impact:.2f}")
        
        # Adicionar informações de período
        start_date = aws_anomaly.get('AnomalyStartDate')
        end_date = aws_anomaly.get('AnomalyEndDate')
        if start_date:
            period_info = f"Período: {start_date}"
            if end_date:
                period_info += f" a {end_date}"
            description_parts.append(period_info)
        
        return ". ".join(description_parts)
    
    async def _get_ec2_rightsizing_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Obtém oportunidades de rightsizing para EC2"""
        opportunities = []
        
        try:
            self.logger.debug("Buscando oportunidades de rightsizing EC2...")
            
            # Right Sizing Recommendations para EC2
            rightsizing_response = self.cost_explorer.get_rightsizing_recommendation(
                Service='EC2-Instance',
                Configuration={
                    'RecommendationTarget': 'CROSS_INSTANCE_FAMILY',
                    'BenefitsConsidered': True
                }
            )
            
            for rec in rightsizing_response.get('RightsizingRecommendations', []):
                try:
                    estimated_savings = float(rec.get('EstimatedMonthlySavings', {}).get('Amount', 0))
                    
                    if estimated_savings < min_savings:
                        continue
                    
                    current_instance = rec.get('CurrentInstance', {})
                    modify_recommendation = rec.get('ModifyRecommendationDetail', {})
                    
                    instance_name = current_instance.get('InstanceName', 'unknown')
                    current_type = current_instance.get('InstanceType', 'unknown')
                    
                    # Extrair tipo recomendado
                    recommended_type = 'optimized'
                    if modify_recommendation:
                        target_instances = modify_recommendation.get('TargetInstances', [])
                        if target_instances:
                            recommended_type = target_instances[0].get('InstanceType', 'optimized')
                    
                    # Calcular confidence baseado nos dados disponíveis
                    confidence = 85.0
                    utilization_data = current_instance.get('UtilizationMetrics', [])
                    if utilization_data:
                        confidence = 90.0
                    
                    opportunity = SavingsOpportunity(
                        id=f"aws_rightsizing_{rec.get('AccountId', 'unknown')}_{instance_name}",
                        provider="AWS",
                        service="EC2",
                        region=current_instance.get('Region'),
                        opportunity_type=RecommendationType.RIGHTSIZING,
                        estimated_savings=estimated_savings,
                        confidence_level=confidence,
                        implementation_effort="Baixo" if estimated_savings < 200 else "Médio",
                        description=f"Rightsizing de {current_type} para {recommended_type} na instância {instance_name}",
                        resources_affected=[instance_name],
                        action_required=f"Alterar tipo de instância de {current_type} para {recommended_type}",
                        risk_level=SeverityLevel.LOW,
                        title="Rightsizing EC2",
                        category="compute"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao processar recomendação de rightsizing: {e}")
                    continue
            
            self.logger.debug(f"Encontradas {len(opportunities)} oportunidades de rightsizing EC2")
            
        except ClientError as e:
            self.logger.warning(f"Erro ao buscar rightsizing recommendations: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado em rightsizing: {e}")
        
        return opportunities
    
    async def _get_reserved_instance_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Obtém oportunidades de Reserved Instances"""
        opportunities = []
        
        try:
            self.logger.debug("Buscando oportunidades de Reserved Instances...")
            
            # EC2 Reserved Instances
            ri_response = self.cost_explorer.get_reservation_purchase_recommendation(
                Service='EC2-Instance',
                LookbackPeriodInDays='SIXTY_DAYS'
            )
            
            for rec in ri_response.get('Recommendations', []):
                try:
                    rec_details = rec.get('RecommendationDetails', {})
                    estimated_savings = float(rec_details.get('EstimatedMonthlySavingsAmount', 0))
                    
                    if estimated_savings < min_savings:
                        continue
                    
                    instance_details = rec_details.get('InstanceDetails', {})
                    ec2_details = instance_details.get('EC2InstanceDetails', {})
                    
                    family = ec2_details.get('Family', 'unknown')
                    instance_type = ec2_details.get('InstanceType', 'unknown')
                    region = ec2_details.get('Region', 'unknown')
                    
                    opportunity = SavingsOpportunity(
                        id=f"aws_ri_{rec.get('AccountId', 'unknown')}_{family}_{region}",
                        provider="AWS",
                        service="EC2",
                        region=region,
                        opportunity_type=RecommendationType.RESERVED_INSTANCES,
                        estimated_savings=estimated_savings,
                        confidence_level=95.0,
                        implementation_effort="Alto",
                        description=f"Reserved Instance para {instance_type} na região {region}",
                        resources_affected=[f"{family}-{instance_type}"],
                        action_required="Comprar Reserved Instance com termo de 1 ou 3 anos",
                        risk_level=SeverityLevel.MEDIUM,
                        title="Reserved Instance",
                        category="compute"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao processar recomendação RI: {e}")
                    continue
            
            self.logger.debug(f"Encontradas {len(opportunities)} oportunidades de Reserved Instances")
            
        except ClientError as e:
            self.logger.warning(f"Erro ao buscar RI recommendations: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado em RI: {e}")
        
        return opportunities
    
    async def _get_savings_plans_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Obtém oportunidades de Savings Plans"""
        opportunities = []
        
        try:
            self.logger.debug("Buscando oportunidades de Savings Plans...")
            
            # Compute Savings Plans
            sp_response = self.cost_explorer.get_savings_plans_purchase_recommendation(
                SavingsPlansType='COMPUTE_SP',
                TermInYears='ONE_YEAR',
                PaymentOption='NO_UPFRONT',
                LookbackPeriodInDays='SIXTY_DAYS'
            )
            
            for rec in sp_response.get('SavingsPlansRecommendationDetails', []):
                try:
                    estimated_savings = float(rec.get('EstimatedMonthlySavings', 0))
                    
                    if estimated_savings < min_savings:
                        continue
                    
                    hourly_commitment = float(rec.get('HourlyCommitmentToPurchase', 0))
                    savings_percentage = float(rec.get('EstimatedSavingsPercentage', 0))
                    
                    opportunity = SavingsOpportunity(
                        id=f"aws_sp_{rec.get('AccountId', 'unknown')}_{int(hourly_commitment * 100)}",
                        provider="AWS",
                        service="Compute",
                        opportunity_type=RecommendationType.RESERVED_INSTANCES,  # Usando enum existente
                        estimated_savings=estimated_savings,
                        confidence_level=90.0,
                        implementation_effort="Alto",
                        description=f"Savings Plan de ${hourly_commitment:.2f}/hora com {savings_percentage:.1f}% de economia",
                        resources_affected=["Compute workloads"],
                        action_required=f"Comprar Savings Plan com compromisso de ${hourly_commitment:.2f}/hora",
                        risk_level=SeverityLevel.MEDIUM,
                        title="Savings Plan",
                        category="compute"
                    )
                    
                    opportunities.append(opportunity)
                    
                except Exception as e:
                    self.logger.warning(f"Erro ao processar recomendação Savings Plan: {e}")
                    continue
            
            self.logger.debug(f"Encontradas {len(opportunities)} oportunidades de Savings Plans")
            
        except ClientError as e:
            self.logger.warning(f"Erro ao buscar Savings Plans recommendations: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado em Savings Plans: {e}")
        
        return opportunities
    
    async def _get_ebs_optimization_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Obtém oportunidades de otimização de volumes EBS"""
        opportunities = []
        
        try:
            self.logger.debug("Buscando oportunidades de otimização EBS...")
            
            # Usar Compute Optimizer para EBS se disponível
            try:
                ebs_response = self.compute_optimizer.get_ebs_volume_recommendations()
                
                for rec in ebs_response.get('volumeRecommendations', []):
                    try:
                        current_config = rec.get('currentConfiguration', {})
                        finding = rec.get('finding', '')
                        
                        # Estimar economia baseada no tipo de finding
                        estimated_savings = 0
                        if finding == 'Underprovisioned':
                            estimated_savings = 20  # Economia menor para underprovisioned
                        elif finding == 'Overprovisioned':
                            volume_size = current_config.get('volumeSize', 100)
                            # Estimar economia baseada no tamanho do volume
                            estimated_savings = min(volume_size * 0.5, 500)  # Max $500/mês
                        elif finding == 'NotOptimized':
                            estimated_savings = 100  # Economia média
                        
                        if estimated_savings < min_savings:
                            continue
                        
                        volume_arn = rec.get('volumeArn', 'unknown')
                        volume_type = current_config.get('volumeType', 'unknown')
                        
                        opportunity = SavingsOpportunity(
                            id=f"aws_ebs_{volume_arn.split('/')[-1] if '/' in volume_arn else volume_arn}",
                            provider="AWS",
                            service="EBS",
                            opportunity_type=RecommendationType.STORAGE_OPTIMIZATION,
                            estimated_savings=estimated_savings,
                            confidence_level=80.0,
                            implementation_effort="Baixo",
                            description=f"Otimização de volume EBS {volume_type} - {finding}",
                            resources_affected=[volume_arn],
                            action_required=f"Otimizar configuração do volume EBS ({finding.lower()})",
                            risk_level=SeverityLevel.LOW,
                            title="EBS Optimization",
                            category="storage"
                        )
                        
                        opportunities.append(opportunity)
                        
                    except Exception as e:
                        self.logger.warning(f"Erro ao processar recomendação EBS: {e}")
                        continue
                
            except ClientError as e:
                if e.response.get('Error', {}).get('Code') != 'OptInRequiredException':
                    self.logger.warning(f"Compute Optimizer não disponível para EBS: {e}")
                
                # Fallback: criar oportunidades genéricas baseadas em métricas
                await self._create_generic_ebs_opportunities(opportunities, min_savings)
            
            self.logger.debug(f"Encontradas {len(opportunities)} oportunidades de otimização EBS")
            
        except Exception as e:
            self.logger.error(f"Erro inesperado em EBS optimization: {e}")
        
        return opportunities
    
    async def _create_generic_ebs_opportunities(self, opportunities: List[SavingsOpportunity], min_savings: float):
        """Cria oportunidades genéricas de EBS quando Compute Optimizer não está disponível"""
        # Oportunidade genérica de migração para GP3
        gp3_opportunity = SavingsOpportunity(
            id="aws_ebs_gp3_migration",
            provider="AWS",
            service="EBS",
            opportunity_type=RecommendationType.STORAGE_OPTIMIZATION,
            estimated_savings=150.0,  # Estimativa conservadora
            confidence_level=70.0,
            implementation_effort="Baixo",
            description="Migração de volumes GP2 para GP3 para melhor custo-benefício",
            resources_affected=["Volumes GP2"],
            action_required="Migrar volumes GP2 para GP3",
            risk_level=SeverityLevel.LOW,
            title="GP3 Migration",
            category="storage"
        )
        
        if gp3_opportunity.estimated_savings >= min_savings:
            opportunities.append(gp3_opportunity)
    
    async def _get_load_balancer_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Obtém oportunidades de otimização de Load Balancers"""
        opportunities = []
        
        try:
            self.logger.debug("Buscando oportunidades de otimização de Load Balancers...")
            
            # Criar cliente ELB
            elb_client = self.session.client('elbv2')
            
            # Listar Application Load Balancers
            alb_response = elb_client.describe_load_balancers()
            
            for lb in alb_response.get('LoadBalancers', []):
                try:
                    lb_arn = lb.get('LoadBalancerArn', '')
                    lb_name = lb.get('LoadBalancerName', 'unknown')
                    
                    # Verificar se há targets saudáveis
                    target_groups = elb_client.describe_target_groups(
                        LoadBalancerArn=lb_arn
                    ).get('TargetGroups', [])
                    
                    has_healthy_targets = False
                    for tg in target_groups:
                        tg_arn = tg.get('TargetGroupArn', '')
                        try:
                            targets = elb_client.describe_target_health(
                                TargetGroupArn=tg_arn
                            ).get('TargetHealthDescriptions', [])
                            
                            if any(t.get('TargetHealth', {}).get('State') == 'healthy' for t in targets):
                                has_healthy_targets = True
                                break
                        except:
                            continue
                    
                    # Se não há targets saudáveis, é uma oportunidade de economia
                    if not has_healthy_targets:
                        estimated_savings = 25.0  # ~$25/mês por ALB idle
                        
                        if estimated_savings >= min_savings:
                            opportunity = SavingsOpportunity(
                                id=f"aws_alb_idle_{lb_name}",
                                provider="AWS",
                                service="ELB",
                                opportunity_type=RecommendationType.IDLE_RESOURCES,
                                estimated_savings=estimated_savings,
                                confidence_level=85.0,
                                implementation_effort="Baixo",
                                description=f"Application Load Balancer sem targets saudáveis: {lb_name}",
                                resources_affected=[lb_arn],
                                action_required="Remover ou consolidar Load Balancer não utilizado",
                                risk_level=SeverityLevel.LOW,
                                title="Idle Load Balancer",
                                category="network"
                            )
                            
                            opportunities.append(opportunity)
                
                except Exception as e:
                    self.logger.warning(f"Erro ao analisar Load Balancer {lb.get('LoadBalancerName', 'unknown')}: {e}")
                    continue
            
            self.logger.debug(f"Encontradas {len(opportunities)} oportunidades de Load Balancer")
            
        except ClientError as e:
            self.logger.warning(f"Erro ao buscar Load Balancers: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado em Load Balancer optimization: {e}")
        
        return opportunities
    
    async def _get_rds_optimization_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Obtém oportunidades de otimização de RDS"""
        opportunities = []
        
        try:
            self.logger.debug("Buscando oportunidades de otimização RDS...")
            
            # Criar cliente RDS
            rds_client = self.session.client('rds')
            
            # Listar instâncias RDS
            rds_response = rds_client.describe_db_instances()
            
            for db in rds_response.get('DBInstances', []):
                try:
                    db_identifier = db.get('DBInstanceIdentifier', 'unknown')
                    db_class = db.get('DBInstanceClass', 'unknown')
                    engine = db.get('Engine', 'unknown')
                    
                    # Verificar se a instância está idle (simulação baseada em status)
                    db_status = db.get('DBInstanceStatus', 'unknown')
                    
                    if db_status == 'available':
                        # Verificar métricas via CloudWatch para determinar utilização
                        # Por simplicidade, criar oportunidade baseada no tipo de instância
                        
                        if 'micro' in db_class or 'small' in db_class:
                            continue  # Pular instâncias já pequenas
                        
                        # Estimar economia baseada no downsize
                        estimated_savings = 50.0  # Estimativa conservadora
                        if 'large' in db_class:
                            estimated_savings = 200.0
                        elif 'xlarge' in db_class:
                            estimated_savings = 500.0
                        elif '2xlarge' in db_class or '4xlarge' in db_class:
                            estimated_savings = 1000.0
                        
                        if estimated_savings >= min_savings:
                            opportunity = SavingsOpportunity(
                                id=f"aws_rds_rightsizing_{db_identifier}",
                                provider="AWS",
                                service="RDS",
                                opportunity_type=RecommendationType.RIGHTSIZING,
                                estimated_savings=estimated_savings,
                                confidence_level=70.0,
                                implementation_effort="Médio",
                                description=f"Possível rightsizing para instância RDS {engine} {db_class}",
                                resources_affected=[db_identifier],
                                action_required="Analisar métricas e considerar downsize da instância RDS",
                                risk_level=SeverityLevel.MEDIUM,
                                title="RDS Rightsizing",
                                category="database"
                            )
                            
                            opportunities.append(opportunity)
                
                except Exception as e:
                    self.logger.warning(f"Erro ao analisar instância RDS {db.get('DBInstanceIdentifier', 'unknown')}: {e}")
                    continue
            
            self.logger.debug(f"Encontradas {len(opportunities)} oportunidades de RDS")
            
        except ClientError as e:
            self.logger.warning(f"Erro ao buscar instâncias RDS: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado em RDS optimization: {e}")
        
        return opportunities
    
    async def _get_lambda_optimization_opportunities(self, min_savings: float) -> List[SavingsOpportunity]:
        """Obtém oportunidades de otimização de Lambda"""
        opportunities = []
        
        try:
            self.logger.debug("Buscando oportunidades de otimização Lambda...")
            
            # Criar cliente Lambda
            lambda_client = self.session.client('lambda')
            
            # Listar funções Lambda
            lambda_response = lambda_client.list_functions()
            
            for func in lambda_response.get('Functions', []):
                try:
                    func_name = func.get('FunctionName', 'unknown')
                    memory_size = func.get('MemorySize', 128)
                    timeout = func.get('Timeout', 3)
                    
                    # Identificar oportunidades baseadas em configuração
                    estimated_savings = 0
                    opportunity_desc = ""
                    
                    # Funções com muito timeout podem estar sobre-provisionadas
                    if timeout > 300:  # 5 minutos
                        estimated_savings += 20
                        opportunity_desc = f"Timeout alto ({timeout}s) pode indicar sobre-provisionamento"
                    
                    # Funções com muita memória podem estar sobre-provisionadas
                    if memory_size > 1024:  # > 1GB
                        estimated_savings += min(memory_size / 50, 100)  # Máximo $100
                        if opportunity_desc:
                            opportunity_desc += " e "
                        opportunity_desc += f"Memória alta ({memory_size}MB) pode ser otimizada"
                    
                    if estimated_savings >= min_savings:
                        opportunity = SavingsOpportunity(
                            id=f"aws_lambda_optimization_{func_name}",
                            provider="AWS",
                            service="Lambda",
                            opportunity_type=RecommendationType.RIGHTSIZING,
                            estimated_savings=estimated_savings,
                            confidence_level=60.0,
                            implementation_effort="Baixo",
                            description=f"Otimização de função Lambda: {opportunity_desc}",
                            resources_affected=[func_name],
                            action_required="Analisar métricas e ajustar configuração da função Lambda",
                            risk_level=SeverityLevel.LOW,
                            title="Lambda Optimization",
                            category="compute"
                        )
                        
                        opportunities.append(opportunity)
                
                except Exception as e:
                    self.logger.warning(f"Erro ao analisar função Lambda {func.get('FunctionName', 'unknown')}: {e}")
                    continue
            
            self.logger.debug(f"Encontradas {len(opportunities)} oportunidades de Lambda")
            
        except ClientError as e:
            self.logger.warning(f"Erro ao buscar funções Lambda: {e}")
        except Exception as e:
            self.logger.error(f"Erro inesperado em Lambda optimization: {e}")
        
        return opportunities
    
    def _calculate_roi_and_prioritize(self, opportunities: List[SavingsOpportunity]):
        """Calcula ROI e prioriza oportunidades baseado em impacto vs esforço"""
        for opportunity in opportunities:
            # Mapear esforço para valor numérico
            effort_scores = {
                "Baixo": 1,
                "Médio": 2, 
                "Alto": 3
            }
            
            effort_score = effort_scores.get(opportunity.implementation_effort, 2)
            
            # Calcular score de prioridade (savings / effort)
            priority_score = opportunity.estimated_savings / effort_score
            
            # Ajustar confidence level baseado no score
            if priority_score > 500:
                opportunity.confidence_level = min(opportunity.confidence_level + 10, 100)
            elif priority_score < 50:
                opportunity.confidence_level = max(opportunity.confidence_level - 10, 50)
            
            # Ajustar risk level baseado no tipo e valor
            if opportunity.estimated_savings > 1000 and opportunity.opportunity_type == RecommendationType.RESERVED_INSTANCES:
                opportunity.risk_level = SeverityLevel.MEDIUM
            elif opportunity.estimated_savings < 100:
                opportunity.risk_level = SeverityLevel.LOW