"""
Cloud Native Optimization Service

Este módulo implementa otimização de custos em tempo real para diferentes provedores de nuvem,
incluindo detecção de anomalias, oportunidades de economia e recomendações unificadas.

Provedores suportados:
- AWS (Cost Explorer + Compute Optimizer)
- Azure (Azure Advisor API)
- GCP (Cloud Recommender API)
- Oracle Cloud (placeholder para implementação futura)
"""

import asyncio
import json
import logging
import os
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from dataclasses import dataclass
from functools import wraps

import redis
from pydantic import BaseModel, Field, validator
from fastapi import HTTPException

# AWS imports
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, PartialCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False

# Azure imports
try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.advisor import AdvisorManagementClient
    from azure.mgmt.resource import ResourceManagementClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

# GCP imports
try:
    from google.cloud import recommender_v1
    from google.oauth2 import service_account
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False

# Configurações e logging
logger = logging.getLogger(__name__)

# ============================================================================
# Utilitários para retry e tratamento de erros
# ============================================================================

def retry_with_exponential_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Decorator para retry com exponential backoff
    
    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Delay inicial em segundos
        max_delay: Delay máximo em segundos
        exponential_base: Base para exponential backoff
        jitter: Adicionar jitter para evitar thundering herd
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except (ClientError, BotoCoreError) as e:
                    last_exception = e
                    
                    # Não fazer retry para alguns tipos de erro
                    if isinstance(e, ClientError):
                        error_code = e.response.get('Error', {}).get('Code', '')
                        
                        # Erros que não devem ser retentados
                        if error_code in [
                            'AccessDenied', 'InvalidUserID.NotFound', 'Forbidden',
                            'UnauthorizedOperation', 'NoCredentialsError', 'InvalidParameterValue'
                        ]:
                            raise e
                    
                    if attempt == max_retries:
                        break
                    
                    # Calcular delay com exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Adicionar jitter se solicitado
                    if jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    # Log do retry
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f"AWS API call failed (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {delay:.2f}s. Error: {str(e)}"
                    )
                    
                    await asyncio.sleep(delay)
                except Exception as e:
                    # Para outras exceções, não fazer retry
                    raise e
            
            # Se chegou aqui, todas as tentativas falharam
            raise last_exception
        
        return wrapper
    return decorator


# ============================================================================
# Modelos Pydantic para resposta unificada
# ============================================================================

class AnomalyType(str, Enum):
    """Tipos de anomalias de custo"""
    SPIKE = "spike"
    DRIFT = "drift"
    UNUSUAL_PATTERN = "unusual_pattern"
    COST_INCREASE = "cost_increase"

class SeverityLevel(str, Enum):
    """Níveis de severidade"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecommendationType(str, Enum):
    """Tipos de recomendações"""
    RIGHTSIZING = "rightsizing"
    RESERVED_INSTANCES = "reserved_instances"
    SPOT_INSTANCES = "spot_instances"
    STORAGE_OPTIMIZATION = "storage_optimization"
    NETWORK_OPTIMIZATION = "network_optimization"
    IDLE_RESOURCES = "idle_resources"
    SCHEDULING = "scheduling"

class CloudAnomaly(BaseModel):
    """Modelo para anomalias de custo detectadas"""
    id: str = Field(..., description="ID único da anomalia")
    provider: str = Field(..., description="Provedor de nuvem")
    service: str = Field(..., description="Serviço afetado")
    region: Optional[str] = Field(None, description="Região onde ocorreu")
    anomaly_type: AnomalyType = Field(..., description="Tipo da anomalia")
    severity: SeverityLevel = Field(..., description="Nível de severidade")
    detected_at: datetime = Field(..., description="Data/hora de detecção")
    cost_impact: float = Field(..., description="Impacto financeiro estimado")
    currency: str = Field(default="USD", description="Moeda")
    description: str = Field(..., description="Descrição da anomalia")
    root_cause: Optional[str] = Field(None, description="Causa raiz identificada")
    affected_resources: List[str] = Field(default=[], description="Recursos afetados")
    
    @validator('cost_impact')
    def validate_cost_impact(cls, v):
        if v < 0:
            raise ValueError('cost_impact deve ser não-negativo')
        return v

class SavingsOpportunity(BaseModel):
    """Modelo para oportunidades de economia"""
    id: str = Field(..., description="ID único da oportunidade")
    provider: str = Field(..., description="Provedor de nuvem")
    service: str = Field(..., description="Serviço com oportunidade")
    region: Optional[str] = Field(None, description="Região")
    opportunity_type: RecommendationType = Field(..., description="Tipo de oportunidade")
    estimated_savings: float = Field(..., description="Economia estimada mensal")
    currency: str = Field(default="USD", description="Moeda")
    confidence_level: float = Field(..., ge=0, le=100, description="Nível de confiança (%)")
    implementation_effort: str = Field(..., description="Esforço de implementação")
    description: str = Field(..., description="Descrição da oportunidade")
    resources_affected: List[str] = Field(default=[], description="Recursos afetados")
    action_required: str = Field(..., description="Ação necessária")
    risk_level: SeverityLevel = Field(default=SeverityLevel.LOW, description="Nível de risco")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OptimizationRecommendation(BaseModel):
    """Modelo para recomendações de otimização"""
    id: str = Field(..., description="ID único da recomendação")
    provider: str = Field(..., description="Provedor de nuvem")
    category: RecommendationType = Field(..., description="Categoria da recomendação")
    title: str = Field(..., description="Título da recomendação")
    description: str = Field(..., description="Descrição detalhada")
    potential_savings: float = Field(..., description="Economia potencial")
    currency: str = Field(default="USD", description="Moeda")
    priority: SeverityLevel = Field(..., description="Prioridade")
    implementation_time: str = Field(..., description="Tempo estimado de implementação")
    prerequisites: List[str] = Field(default=[], description="Pré-requisitos")
    steps: List[str] = Field(..., description="Passos para implementação")
    impact_areas: List[str] = Field(default=[], description="Áreas de impacto")
    resources: List[str] = Field(default=[], description="Recursos relacionados")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")

# ============================================================================
# Configuração do Redis Cache
# ============================================================================

@dataclass
class CacheConfig:
    """Configuração do cache Redis"""
    ANOMALIES_TTL: int = 3600  # 1 hora
    SAVINGS_TTL: int = 14400   # 4 horas
    RECOMMENDATIONS_TTL: int = 21600  # 6 horas
    KEY_PREFIX: str = "cloud_optimization:"

class RedisCache:
    """Gerenciador de cache Redis para otimização"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.config = CacheConfig()
    
    def _get_key(self, category: str, provider: Optional[str] = None) -> str:
        """Gera chave do cache"""
        base_key = f"{self.config.KEY_PREFIX}{category}"
        if provider:
            base_key += f":{provider}"
        return base_key
    
    async def get_anomalies(self, provider: Optional[str] = None) -> Optional[List[CloudAnomaly]]:
        """Recupera anomalias do cache"""
        try:
            key = self._get_key("anomalies", provider)
            data = self.redis.get(key)
            if data:
                anomalies_data = json.loads(data)
                return [CloudAnomaly(**item) for item in anomalies_data]
        except Exception as e:
            logger.error(f"Erro ao recuperar anomalias do cache: {e}")
        return None
    
    async def set_anomalies(self, anomalies: List[CloudAnomaly], provider: Optional[str] = None):
        """Armazena anomalias no cache"""
        try:
            key = self._get_key("anomalies", provider)
            data = [anomaly.dict() for anomaly in anomalies]
            self.redis.setex(key, self.config.ANOMALIES_TTL, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Erro ao armazenar anomalias no cache: {e}")
    
    async def get_savings(self, provider: Optional[str] = None) -> Optional[List[SavingsOpportunity]]:
        """Recupera oportunidades do cache"""
        try:
            key = self._get_key("savings", provider)
            data = self.redis.get(key)
            if data:
                savings_data = json.loads(data)
                return [SavingsOpportunity(**item) for item in savings_data]
        except Exception as e:
            logger.error(f"Erro ao recuperar savings do cache: {e}")
        return None
    
    async def set_savings(self, savings: List[SavingsOpportunity], provider: Optional[str] = None):
        """Armazena oportunidades no cache"""
        try:
            key = self._get_key("savings", provider)
            data = [saving.dict() for saving in savings]
            self.redis.setex(key, self.config.SAVINGS_TTL, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Erro ao armazenar savings no cache: {e}")
    
    async def get_recommendations(self, provider: Optional[str] = None) -> Optional[List[OptimizationRecommendation]]:
        """Recupera recomendações do cache"""
        try:
            key = self._get_key("recommendations", provider)
            data = self.redis.get(key)
            if data:
                rec_data = json.loads(data)
                return [OptimizationRecommendation(**item) for item in rec_data]
        except Exception as e:
            logger.error(f"Erro ao recuperar recommendations do cache: {e}")
        return None
    
    async def set_recommendations(self, recommendations: List[OptimizationRecommendation], provider: Optional[str] = None):
        """Armazena recomendações no cache"""
        try:
            key = self._get_key("recommendations", provider)
            data = [rec.dict() for rec in recommendations]
            self.redis.setex(key, self.config.RECOMMENDATIONS_TTL, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Erro ao armazenar recommendations no cache: {e}")

# ============================================================================
# Serviços específicos por provedor
# ============================================================================

class BaseOptimizationService:
    """Classe base para serviços de otimização"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.logger = logging.getLogger(f"{__name__}.{provider_name}")
    
    async def get_anomalies(self) -> List[CloudAnomaly]:
        """Método base para obter anomalias - deve ser sobrescrito"""
        raise NotImplementedError
    
    async def get_savings_opportunities(self) -> List[SavingsOpportunity]:
        """Método base para obter oportunidades - deve ser sobrescrito"""
        raise NotImplementedError
    
    async def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Método base para obter recomendações - deve ser sobrescrito"""
        raise NotImplementedError

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
                        risk_level=SeverityLevel.LOW
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
                        risk_level=SeverityLevel.MEDIUM
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
                        risk_level=SeverityLevel.MEDIUM
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
                            risk_level=SeverityLevel.LOW
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
            risk_level=SeverityLevel.LOW
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
                                risk_level=SeverityLevel.LOW
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
                                risk_level=SeverityLevel.MEDIUM
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
                            risk_level=SeverityLevel.LOW
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

class AzureOptimizationService(BaseOptimizationService):
    """Serviço de otimização para Azure usando Azure Advisor API"""
    
    def __init__(self, subscription_id: str, tenant_id: str = None, client_id: str = None, client_secret: str = None):
        super().__init__("Azure")
        
        if not AZURE_AVAILABLE:
            raise ImportError("Azure SDK não está disponível. Instale com: pip install azure-mgmt-advisor azure-identity")
        
        self.subscription_id = subscription_id
        
        # Configurar autenticação
        if client_id and client_secret and tenant_id:
            from azure.identity import ClientSecretCredential
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            self.credential = DefaultAzureCredential()
        
        self.advisor_client = AdvisorManagementClient(self.credential, subscription_id)
        self.resource_client = ResourceManagementClient(self.credential, subscription_id)
    
    @retry_with_exponential_backoff()
    async def get_anomalies(self) -> List[CloudAnomaly]:
        """Obtém anomalias de custo do Azure (simulado - Azure não tem API nativa)"""
        anomalies = []
        
        try:
            # Azure não tem API nativa de anomalias, então simulamos baseado em recomendações críticas
            recommendations = self.advisor_client.recommendations.list()
            
            for rec in recommendations:
                if rec.impact == "High" and "cost" in rec.category.lower():
                    anomalies.append(CloudAnomaly(
                        id=rec.name,
                        provider="Azure",
                        service=rec.impacted_field or "Unknown",
                        anomaly_type=AnomalyType.COST_INCREASE,
                        severity=SeverityLevel.HIGH,
                        detected_at=datetime.utcnow(),
                        cost_impact=500.0,  # Estimado
                        description=rec.short_description.get("problem", "Anomalia detectada"),
                        root_cause="Alto consumo detectado via Advisor"
                    ))
                    
        except Exception as e:
            self.logger.error(f"Erro ao obter anomalias Azure: {e}")
            
        return anomalies
    
    @retry_with_exponential_backoff()
    async def get_savings_opportunities(self) -> List[SavingsOpportunity]:
        """Obtém oportunidades de economia do Azure"""
        opportunities = []
        
        try:
            recommendations = self.advisor_client.recommendations.list(filter="Category eq 'Cost'")
            
            for rec in recommendations:
                # Mapear categoria do Azure para nosso enum
                opportunity_type = RecommendationType.RIGHTSIZING
                if "reserved" in rec.short_description.get("problem", "").lower():
                    opportunity_type = RecommendationType.RESERVED_INSTANCES
                elif "storage" in rec.short_description.get("problem", "").lower():
                    opportunity_type = RecommendationType.STORAGE_OPTIMIZATION
                
                # Estimar economia baseada no impacto
                estimated_savings = 100.0
                if rec.impact == "High":
                    estimated_savings = 500.0
                elif rec.impact == "Medium":
                    estimated_savings = 250.0
                
                opportunities.append(SavingsOpportunity(
                    id=rec.name,
                    provider="Azure",
                    service=rec.impacted_field or "Unknown",
                    opportunity_type=opportunity_type,
                    estimated_savings=estimated_savings,
                    confidence_level=80.0,
                    implementation_effort="Médio",
                    description=rec.short_description.get("problem", "Oportunidade de economia"),
                    action_required=rec.short_description.get("solution", "Seguir recomendação do Advisor")
                ))
                
        except Exception as e:
            self.logger.error(f"Erro ao obter oportunidades Azure: {e}")
            
        return opportunities
    
    @retry_with_exponential_backoff()
    async def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Obtém recomendações de otimização do Azure"""
        recommendations = []
        
        try:
            advisor_recs = self.advisor_client.recommendations.list()
            
            for rec in advisor_recs:
                if rec.category == "Cost":
                    # Mapear impacto para prioridade
                    priority = SeverityLevel.LOW
                    if rec.impact == "High":
                        priority = SeverityLevel.HIGH
                    elif rec.impact == "Medium":
                        priority = SeverityLevel.MEDIUM
                    
                    recommendations.append(OptimizationRecommendation(
                        id=rec.name,
                        provider="Azure",
                        category=RecommendationType.RIGHTSIZING,
                        title=rec.short_description.get("problem", "Recomendação do Azure Advisor"),
                        description=rec.extended_properties.get("displayQueriesAndResults", rec.short_description.get("solution", "")),
                        potential_savings=200.0,  # Estimado
                        priority=priority,
                        implementation_time="1 hora",
                        steps=[
                            "Revisar recomendação no Azure Portal",
                            "Analisar impacto nos recursos",
                            "Implementar alteração sugerida",
                            "Monitorar resultados"
                        ],
                        resources=[rec.resource_metadata.get("resourceId", "unknown")]
                    ))
                    
        except Exception as e:
            self.logger.error(f"Erro ao obter recomendações Azure: {e}")
            
        return recommendations

class GCPOptimizationService(BaseOptimizationService):
    """Serviço de otimização para GCP usando Cloud Recommender API"""
    
    def __init__(self, project_id: str, credentials_path: str = None):
        super().__init__("GCP")
        
        if not GCP_AVAILABLE:
            raise ImportError("Google Cloud SDK não está disponível. Instale com: pip install google-cloud-recommender")
        
        self.project_id = project_id
        
        # Configurar autenticação
        if credentials_path:
            self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        else:
            self.credentials = None
        
        self.recommender_client = recommender_v1.RecommenderClient(credentials=self.credentials)
    
    @retry_with_exponential_backoff()
    async def get_anomalies(self) -> List[CloudAnomaly]:
        """Obtém anomalias de custo do GCP (simulado - baseado em recomendações críticas)"""
        anomalies = []
        
        try:
            # GCP não tem API específica de anomalias, simulamos baseado em recomendações críticas
            parent = f"projects/{self.project_id}/locations/global/recommenders/google.compute.instance.MachineTypeRecommender"
            
            try:
                recommendations = self.recommender_client.list_recommendations(parent=parent)
                
                for rec in recommendations:
                    if rec.priority == recommender_v1.Recommendation.Priority.P1:  # Alta prioridade
                        anomalies.append(CloudAnomaly(
                            id=rec.name,
                            provider="GCP",
                            service="Compute Engine",
                            anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                            severity=SeverityLevel.HIGH,
                            detected_at=datetime.utcnow(),
                            cost_impact=300.0,  # Estimado
                            description=rec.description,
                            root_cause="Padrão de uso ineficiente detectado"
                        ))
                        
            except Exception as e:
                self.logger.warning(f"Não foi possível acessar recomendações GCP: {e}")
                
        except Exception as e:
            self.logger.error(f"Erro ao obter anomalias GCP: {e}")
            
        return anomalies
    
    @retry_with_exponential_backoff()
    async def get_savings_opportunities(self) -> List[SavingsOpportunity]:
        """Obtém oportunidades de economia do GCP"""
        opportunities = []
        
        try:
            # Listar recomendadores disponíveis
            recommenders = [
                "google.compute.instance.MachineTypeRecommender",
                "google.compute.disk.IdleResourceRecommender",
                "google.iam.policy.Recommender"
            ]
            
            for recommender in recommenders:
                try:
                    parent = f"projects/{self.project_id}/locations/global/recommenders/{recommender}"
                    recommendations = self.recommender_client.list_recommendations(parent=parent)
                    
                    for rec in recommendations:
                        # Mapear tipo de recomendador para nosso enum
                        opportunity_type = RecommendationType.RIGHTSIZING
                        if "disk" in recommender.lower():
                            opportunity_type = RecommendationType.STORAGE_OPTIMIZATION
                        elif "idle" in recommender.lower():
                            opportunity_type = RecommendationType.IDLE_RESOURCES
                        
                        # Estimar economia baseada na prioridade
                        estimated_savings = 50.0
                        if rec.priority == recommender_v1.Recommendation.Priority.P1:
                            estimated_savings = 300.0
                        elif rec.priority == recommender_v1.Recommendation.Priority.P2:
                            estimated_savings = 150.0
                        
                        opportunities.append(SavingsOpportunity(
                            id=rec.name,
                            provider="GCP",
                            service="Compute Engine",
                            opportunity_type=opportunity_type,
                            estimated_savings=estimated_savings,
                            confidence_level=75.0,
                            implementation_effort="Baixo",
                            description=rec.description,
                            action_required="Seguir recomendação do Cloud Recommender"
                        ))
                        
                except Exception as e:
                    self.logger.warning(f"Erro ao acessar recomendador {recommender}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Erro ao obter oportunidades GCP: {e}")
            
        return opportunities
    
    @retry_with_exponential_backoff()
    async def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Obtém recomendações de otimização do GCP"""
        recommendations = []
        
        try:
            parent = f"projects/{self.project_id}/locations/global/recommenders/google.compute.instance.MachineTypeRecommender"
            
            try:
                gcp_recommendations = self.recommender_client.list_recommendations(parent=parent)
                
                for rec in gcp_recommendations:
                    # Mapear prioridade para nossa enum
                    priority = SeverityLevel.LOW
                    if rec.priority == recommender_v1.Recommendation.Priority.P1:
                        priority = SeverityLevel.HIGH
                    elif rec.priority == recommender_v1.Recommendation.Priority.P2:
                        priority = SeverityLevel.MEDIUM
                    
                    recommendations.append(OptimizationRecommendation(
                        id=rec.name,
                        provider="GCP",
                        category=RecommendationType.RIGHTSIZING,
                        title="Otimização de Machine Type",
                        description=rec.description,
                        potential_savings=200.0,  # Estimado
                        priority=priority,
                        implementation_time="45 minutos",
                        steps=[
                            "Analisar métricas de utilização no Cloud Monitoring",
                            "Verificar compatibilidade do novo machine type",
                            "Agendar janela de manutenção",
                            "Aplicar mudança via Cloud Console ou gcloud"
                        ],
                        resources=[rec.name]
                    ))
                    
            except Exception as e:
                self.logger.warning(f"Não foi possível acessar recomendações GCP: {e}")
                
        except Exception as e:
            self.logger.error(f"Erro ao obter recomendações GCP: {e}")
            
        return recommendations

class OracleOptimizationService(BaseOptimizationService):
    """Serviço de otimização para Oracle Cloud (placeholder para implementação futura)"""
    
    def __init__(self, config_file_path: str = None):
        super().__init__("Oracle")
        self.config_file_path = config_file_path
        
        # TODO: Implementar quando Oracle Cloud SDK estiver disponível
        self.logger.info("Oracle Cloud Optimization Service inicializado (placeholder)")
    
    async def get_anomalies(self) -> List[CloudAnomaly]:
        """Placeholder para anomalias Oracle"""
        # TODO: Implementar quando API estiver disponível
        return [
            CloudAnomaly(
                id="oracle-placeholder-001",
                provider="Oracle",
                service="Compute",
                anomaly_type=AnomalyType.SPIKE,
                severity=SeverityLevel.MEDIUM,
                detected_at=datetime.utcnow(),
                cost_impact=150.0,
                description="Placeholder: Implementação futura para Oracle Cloud",
                root_cause="API não implementada"
            )
        ]
    
    async def get_savings_opportunities(self) -> List[SavingsOpportunity]:
        """Placeholder para oportunidades Oracle"""
        # TODO: Implementar quando API estiver disponível
        return [
            SavingsOpportunity(
                id="oracle-placeholder-savings-001",
                provider="Oracle",
                service="Compute",
                opportunity_type=RecommendationType.RIGHTSIZING,
                estimated_savings=100.0,
                confidence_level=50.0,
                implementation_effort="A ser determinado",
                description="Placeholder: Implementação futura para Oracle Cloud",
                action_required="Aguardar implementação da API"
            )
        ]
    
    async def get_recommendations(self) -> List[OptimizationRecommendation]:
        """Placeholder para recomendações Oracle"""
        # TODO: Implementar quando API estiver disponível
        return [
            OptimizationRecommendation(
                id="oracle-placeholder-rec-001",
                provider="Oracle",
                category=RecommendationType.RIGHTSIZING,
                title="Placeholder Oracle Recommendation",
                description="Implementação futura para Oracle Cloud",
                potential_savings=75.0,
                priority=SeverityLevel.LOW,
                implementation_time="TBD",
                steps=["Aguardar implementação da API Oracle Cloud"]
            )
        ]

# ============================================================================
# Serviço Principal de Otimização Cloud Native
# ============================================================================

class CloudNativeOptimizationService:
    """Serviço principal que orquestra otimização para todos os provedores"""
    
    def __init__(self, redis_client: redis.Redis, config: Dict[str, Any]):
        self.cache = RedisCache(redis_client)
        self.config = config
        self.providers = {}
        self.logger = logging.getLogger(__name__)
        
        # Inicializar serviços por provedor
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Inicializa serviços específicos por provedor"""
        try:
            # AWS
            if self.config.get('aws', {}).get('enabled', False):
                self.providers['AWS'] = AWSOptimizationService(
                    access_key=self.config['aws'].get('access_key'),
                    secret_key=self.config['aws'].get('secret_key'),
                    region=self.config['aws'].get('region', 'us-east-1')
                )
                self.logger.info("AWS Optimization Service inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar AWS service: {e}")
        
        try:
            # Azure
            if self.config.get('azure', {}).get('enabled', False):
                self.providers['Azure'] = AzureOptimizationService(
                    subscription_id=self.config['azure']['subscription_id'],
                    tenant_id=self.config['azure'].get('tenant_id'),
                    client_id=self.config['azure'].get('client_id'),
                    client_secret=self.config['azure'].get('client_secret')
                )
                self.logger.info("Azure Optimization Service inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Azure service: {e}")
        
        try:
            # GCP
            if self.config.get('gcp', {}).get('enabled', False):
                self.providers['GCP'] = GCPOptimizationService(
                    project_id=self.config['gcp']['project_id'],
                    credentials_path=self.config['gcp'].get('credentials_path')
                )
                self.logger.info("GCP Optimization Service inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar GCP service: {e}")
        
        try:
            # Oracle
            if self.config.get('oracle', {}).get('enabled', False):
                self.providers['Oracle'] = OracleOptimizationService(
                    config_file_path=self.config['oracle'].get('config_file_path')
                )
                self.logger.info("Oracle Optimization Service inicializado")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar Oracle service: {e}")
    
    async def get_anomalies_by_provider(self, provider_name: Optional[str] = None) -> List[CloudAnomaly]:
        """
        Obtém anomalias de custo por provedor
        
        Args:
            provider_name: Nome do provedor (AWS, Azure, GCP, Oracle) ou None para todos
            
        Returns:
            Lista de anomalias de custo
        """
        # Verificar cache primeiro
        cached_anomalies = await self.cache.get_anomalies(provider_name)
        if cached_anomalies:
            self.logger.info(f"Anomalias recuperadas do cache para {provider_name or 'todos os provedores'}")
            return cached_anomalies
        
        anomalies = []
        
        # Determinar quais provedores consultar
        providers_to_query = []
        if provider_name:
            if provider_name in self.providers:
                providers_to_query = [provider_name]
            else:
                raise HTTPException(status_code=404, detail=f"Provedor {provider_name} não encontrado")
        else:
            providers_to_query = list(self.providers.keys())
        
        # Consultar provedores em paralelo
        tasks = []
        for provider in providers_to_query:
            if provider in self.providers:
                tasks.append(self.providers[provider].get_anomalies())
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Erro ao obter anomalias: {result}")
                else:
                    anomalies.extend(result)
        
        # Ordenar por impacto financeiro (maior primeiro)
        anomalies.sort(key=lambda x: x.cost_impact, reverse=True)
        
        # Armazenar no cache
        await self.cache.set_anomalies(anomalies, provider_name)
        
        self.logger.info(f"Encontradas {len(anomalies)} anomalias para {provider_name or 'todos os provedores'}")
        return anomalies
    
    async def get_savings_opportunities_by_provider(self, provider_name: Optional[str] = None) -> List[SavingsOpportunity]:
        """
        Obtém oportunidades de economia por provedor
        
        Args:
            provider_name: Nome do provedor ou None para todos
            
        Returns:
            Lista de oportunidades de economia
        """
        # Verificar cache primeiro
        cached_savings = await self.cache.get_savings(provider_name)
        if cached_savings:
            self.logger.info(f"Oportunidades recuperadas do cache para {provider_name or 'todos os provedores'}")
            return cached_savings
        
        opportunities = []
        
        # Determinar provedores
        providers_to_query = []
        if provider_name:
            if provider_name in self.providers:
                providers_to_query = [provider_name]
            else:
                raise HTTPException(status_code=404, detail=f"Provedor {provider_name} não encontrado")
        else:
            providers_to_query = list(self.providers.keys())
        
        # Consultar em paralelo
        tasks = []
        for provider in providers_to_query:
            if provider in self.providers:
                tasks.append(self.providers[provider].get_savings_opportunities())
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Erro ao obter oportunidades: {result}")
                else:
                    opportunities.extend(result)
        
        # Ordenar por economia estimada (maior primeiro)
        opportunities.sort(key=lambda x: x.estimated_savings, reverse=True)
        
        # Armazenar no cache
        await self.cache.set_savings(opportunities, provider_name)
        
        self.logger.info(f"Encontradas {len(opportunities)} oportunidades para {provider_name or 'todos os provedores'}")
        return opportunities
    
    async def get_unified_recommendations(self, provider_name: Optional[str] = None) -> List[OptimizationRecommendation]:
        """
        Obtém recomendações unificadas de otimização
        
        Args:
            provider_name: Nome do provedor ou None para todos
            
        Returns:
            Lista de recomendações unificadas
        """
        # Verificar cache primeiro
        cached_recommendations = await self.cache.get_recommendations(provider_name)
        if cached_recommendations:
            self.logger.info(f"Recomendações recuperadas do cache para {provider_name or 'todos os provedores'}")
            return cached_recommendations
        
        recommendations = []
        
        # Determinar provedores
        providers_to_query = []
        if provider_name:
            if provider_name in self.providers:
                providers_to_query = [provider_name]
            else:
                raise HTTPException(status_code=404, detail=f"Provedor {provider_name} não encontrado")
        else:
            providers_to_query = list(self.providers.keys())
        
        # Consultar em paralelo
        tasks = []
        for provider in providers_to_query:
            if provider in self.providers:
                tasks.append(self.providers[provider].get_recommendations())
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error(f"Erro ao obter recomendações: {result}")
                else:
                    recommendations.extend(result)
        
        # Ordenar por economia potencial e prioridade
        recommendations.sort(key=lambda x: (
            x.priority == SeverityLevel.CRITICAL,
            x.priority == SeverityLevel.HIGH,
            x.potential_savings
        ), reverse=True)
        
        # Armazenar no cache
        await self.cache.set_recommendations(recommendations, provider_name)
        
        self.logger.info(f"Encontradas {len(recommendations)} recomendações para {provider_name or 'todos os provedores'}")
        return recommendations
    
    def get_summary_statistics(self, 
                              anomalies: List[CloudAnomaly], 
                              opportunities: List[SavingsOpportunity], 
                              recommendations: List[OptimizationRecommendation]) -> Dict[str, Any]:
        """Gera estatísticas resumidas"""
        
        total_anomaly_impact = sum(a.cost_impact for a in anomalies)
        total_savings_potential = sum(o.estimated_savings for o in opportunities)
        total_recommendation_savings = sum(r.potential_savings for r in recommendations)
        
        # Contar por severidade/prioridade
        anomaly_severity_count = {}
        for severity in SeverityLevel:
            anomaly_severity_count[severity.value] = len([a for a in anomalies if a.severity == severity])
        
        recommendation_priority_count = {}
        for priority in SeverityLevel:
            recommendation_priority_count[priority.value] = len([r for r in recommendations if r.priority == priority])
        
        # Contar por provedor
        provider_stats = {}
        all_providers = set([a.provider for a in anomalies] + 
                           [o.provider for o in opportunities] + 
                           [r.provider for r in recommendations])
        
        for provider in all_providers:
            provider_anomalies = [a for a in anomalies if a.provider == provider]
            provider_opportunities = [o for o in opportunities if o.provider == provider]
            provider_recommendations = [r for r in recommendations if r.provider == provider]
            
            provider_stats[provider] = {
                "anomalies_count": len(provider_anomalies),
                "anomalies_impact": sum(a.cost_impact for a in provider_anomalies),
                "opportunities_count": len(provider_opportunities),
                "opportunities_savings": sum(o.estimated_savings for o in provider_opportunities),
                "recommendations_count": len(provider_recommendations),
                "recommendations_savings": sum(r.potential_savings for r in provider_recommendations)
            }
        
        return {
            "summary": {
                "total_anomalies": len(anomalies),
                "total_anomaly_impact": total_anomaly_impact,
                "total_opportunities": len(opportunities),
                "total_savings_potential": total_savings_potential,
                "total_recommendations": len(recommendations),
                "total_recommendation_savings": total_recommendation_savings,
                "total_potential_savings": total_savings_potential + total_recommendation_savings
            },
            "anomaly_severity_distribution": anomaly_severity_count,
            "recommendation_priority_distribution": recommendation_priority_count,
            "provider_statistics": provider_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def get_full_optimization_report(self, provider_name: Optional[str] = None) -> Dict[str, Any]:
        """Gera relatório completo de otimização"""
        
        # Obter todos os dados em paralelo
        anomalies_task = self.get_anomalies_by_provider(provider_name)
        opportunities_task = self.get_savings_opportunities_by_provider(provider_name)
        recommendations_task = self.get_unified_recommendations(provider_name)
        
        anomalies, opportunities, recommendations = await asyncio.gather(
            anomalies_task, opportunities_task, recommendations_task
        )
        
        # Gerar estatísticas
        statistics = self.get_summary_statistics(anomalies, opportunities, recommendations)
        
        return {
            "anomalies": [anomaly.dict() for anomaly in anomalies],
            "savings_opportunities": [opportunity.dict() for opportunity in opportunities],
            "recommendations": [recommendation.dict() for recommendation in recommendations],
            "statistics": statistics
        }

# ============================================================================
# Funções utilitárias para integração
# ============================================================================

def create_optimization_service(redis_client: redis.Redis = None, config: Dict[str, Any] = None) -> CloudNativeOptimizationService:
    """Factory function para criar o serviço de otimização"""
    if redis_client is None:
        # Criar cliente Redis padrão se não fornecido
        try:
            redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
            redis_client.ping()  # Testar conexão
        except Exception:
            # Se Redis não estiver disponível, usar um mock
            redis_client = None
    
    if config is None:
        config = load_config_from_env()
    
    # Verificar se estamos usando LocalStack
    aws_endpoint = os.getenv('AWS_ENDPOINT_URL', '')
    use_localstack = 'localhost:4566' in aws_endpoint or '127.0.0.1:4566' in aws_endpoint
    
    if use_localstack:
        logger.info("Detectado LocalStack - usando serviço AWS mockado")
        # Importar e usar o serviço LocalStack
        try:
            from localstack_aws_service import create_localstack_aws_service
            
            # Modificar config para usar o serviço mockado
            modified_config = config.copy()
            modified_config['aws']['enabled'] = True  # Forçar habilitação para teste
            modified_config['_use_localstack_aws'] = True
            
            service = CloudNativeOptimizationService(redis_client, modified_config)
            
            # Substituir o serviço AWS pelo mockado
            if 'AWS' in service.providers:
                aws_service = create_localstack_aws_service(
                    access_key=config['aws'].get('access_key'),
                    secret_key=config['aws'].get('secret_key'),
                    region=config['aws'].get('region', 'us-east-1')
                )
                service.providers['AWS'] = aws_service
                logger.info("Serviço AWS substituído pelo LocalStack mockado")
            
            return service
            
        except ImportError as e:
            logger.warning(f"Não foi possível importar serviço LocalStack: {e}")
            # Fallback para serviço normal
    
    return CloudNativeOptimizationService(redis_client, config)

def load_config_from_env() -> Dict[str, Any]:
    """Carrega configuração das variáveis de ambiente"""
    import os
    
    config = {
        'aws': {
            'enabled': os.getenv('AWS_OPTIMIZATION_ENABLED', 'false').lower() == 'true',
            'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'region': os.getenv('AWS_DEFAULT_REGION', 'us-east-1')
        },
        'azure': {
            'enabled': os.getenv('AZURE_OPTIMIZATION_ENABLED', 'false').lower() == 'true',
            'subscription_id': os.getenv('AZURE_SUBSCRIPTION_ID'),
            'tenant_id': os.getenv('AZURE_TENANT_ID'),
            'client_id': os.getenv('AZURE_CLIENT_ID'),
            'client_secret': os.getenv('AZURE_CLIENT_SECRET')
        },
        'gcp': {
            'enabled': os.getenv('GCP_OPTIMIZATION_ENABLED', 'false').lower() == 'true',
            'project_id': os.getenv('GCP_PROJECT_ID'),
            'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        },
        'oracle': {
            'enabled': os.getenv('ORACLE_OPTIMIZATION_ENABLED', 'false').lower() == 'true',
            'config_file_path': os.getenv('OCI_CONFIG_FILE')
        }
    }
    
    return config

# Exemplo de uso
if __name__ == "__main__":
    # Configuração de exemplo
    config = load_config_from_env()
    
    # Criar cliente Redis (exemplo)
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    
    # Criar serviço
    optimization_service = create_optimization_service(redis_client, config)
    
    print("Serviço de Otimização Cloud Native inicializado com sucesso!")
