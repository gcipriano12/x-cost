# Cloud Native Optimization Service

## Visão Geral

O **Cloud Native Optimization Service** é um módulo abrangente que implementa otimização de custos em tempo real para múltiplos provedores de nuvem. Ele oferece detecção de anomalias, identificação de oportunidades de economia e recomendações unificadas de otimização.

## Funcionalidades Principais

### 🔍 Detecção de Anomalias
- Detecção automática de picos de custo anômalos
- Identificação de padrões de uso incomuns
- Análise de deriva de custos
- Alertas baseados em severidade

### 💰 Oportunidades de Economia
- Recomendações de rightsizing
- Sugestões de Reserved Instances
- Identificação de recursos ociosos
- Otimização de armazenamento

### 📊 Recomendações Unificadas
- Consolidação de recomendações de múltiplos provedores
- Priorização baseada em impacto financeiro
- Passos detalhados de implementação
- Estimativas de tempo e esforço

### ⚡ Cache Inteligente
- TTL diferenciado por tipo de dados
- Cache distribuído com Redis
- Invalidação automática
- Otimização de performance

## Provedores Suportados

### ✅ AWS (Amazon Web Services)
- **APIs utilizadas**: Cost Explorer, Compute Optimizer, CloudWatch
- **Funcionalidades**:
  - Cost Anomaly Detection
  - Right Sizing Recommendations
  - Reserved Instance Recommendations
  - EC2 Instance Optimization

### ✅ Microsoft Azure
- **APIs utilizadas**: Azure Advisor API, Resource Management
- **Funcionalidades**:
  - Azure Advisor Recommendations
  - Cost Management Integration
  - Resource Optimization
  - VM Right Sizing

### ✅ Google Cloud Platform (GCP)
- **APIs utilizadas**: Cloud Recommender API
- **Funcionalidades**:
  - Machine Type Recommendations
  - Idle Resource Detection
  - Storage Optimization
  - IAM Recommendations

### 🚧 Oracle Cloud Infrastructure (OCI)
- **Status**: Placeholder implementado
- **Implementação**: Aguardando disponibilidade de SDK oficial

## Instalação e Configuração

### 1. Dependências

```bash
# Instalar dependências básicas
pip install redis pydantic python-dateutil

# Instalar SDKs dos provedores (opcionais)
pip install boto3  # AWS
pip install azure-mgmt-advisor azure-identity  # Azure
pip install google-cloud-recommender  # GCP
```

### 2. Configuração de Ambiente

Copie o arquivo de exemplo:
```bash
cp .env.cloud_optimization.example .env
```

Configure as credenciais necessárias:

```bash
# AWS
AWS_OPTIMIZATION_ENABLED=true
AWS_ACCESS_KEY_ID=sua_chave_de_acesso
AWS_SECRET_ACCESS_KEY=sua_chave_secreta
AWS_DEFAULT_REGION=us-east-1

# Azure
AZURE_OPTIMIZATION_ENABLED=true
AZURE_SUBSCRIPTION_ID=seu_subscription_id
AZURE_TENANT_ID=seu_tenant_id
AZURE_CLIENT_ID=seu_client_id
AZURE_CLIENT_SECRET=seu_client_secret

# GCP
GCP_OPTIMIZATION_ENABLED=true
GCP_PROJECT_ID=seu_project_id
GOOGLE_APPLICATION_CREDENTIALS=/caminho/para/service-account.json

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 3. Configuração do Redis

```bash
# Instalar Redis (Ubuntu/Debian)
sudo apt-get install redis-server

# Ou usar Docker
docker run -d -p 6379:6379 redis:alpine
```

## Uso Básico

### Inicialização do Serviço

```python
import redis
from app.cloud_native_optimization import (
    CloudNativeOptimizationService,
    load_config_from_env
)

# Carregar configuração
config = load_config_from_env()

# Conectar ao Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Criar serviço
optimization_service = CloudNativeOptimizationService(redis_client, config)
```

### Obter Anomalias

```python
# Anomalias de todos os provedores
anomalies = await optimization_service.get_anomalies_by_provider()

# Anomalias de um provedor específico
aws_anomalies = await optimization_service.get_anomalies_by_provider("AWS")

# Processar resultados
for anomaly in anomalies:
    print(f"Anomalia: {anomaly.description}")
    print(f"Impacto: ${anomaly.cost_impact}")
    print(f"Severidade: {anomaly.severity}")
```

### Obter Oportunidades de Economia

```python
# Oportunidades de todos os provedores
opportunities = await optimization_service.get_savings_opportunities_by_provider()

# Oportunidades do Azure
azure_opportunities = await optimization_service.get_savings_opportunities_by_provider("Azure")

for opportunity in opportunities:
    print(f"Oportunidade: {opportunity.description}")
    print(f"Economia Estimada: ${opportunity.estimated_savings}/mês")
    print(f"Confiança: {opportunity.confidence_level}%")
```

### Obter Recomendações

```python
# Recomendações unificadas
recommendations = await optimization_service.get_unified_recommendations()

for rec in recommendations:
    print(f"Recomendação: {rec.title}")
    print(f"Economia Potencial: ${rec.potential_savings}")
    print(f"Prioridade: {rec.priority}")
    print(f"Passos: {', '.join(rec.steps)}")
```

### Relatório Completo

```python
# Gerar relatório completo
report = await optimization_service.get_full_optimization_report("AWS")

print("=== Estatísticas Resumidas ===")
stats = report["statistics"]["summary"]
print(f"Total de Anomalias: {stats['total_anomalies']}")
print(f"Impacto Total: ${stats['total_anomaly_impact']}")
print(f"Economia Potencial: ${stats['total_potential_savings']}")

print("\n=== Por Provedor ===")
for provider, data in report["statistics"]["provider_statistics"].items():
    print(f"{provider}: {data['opportunities_count']} oportunidades")
```

## Modelos de Dados

### CloudAnomaly

```python
class CloudAnomaly(BaseModel):
    id: str
    provider: str  # AWS, Azure, GCP, Oracle
    service: str   # EC2, VM, Compute Engine, etc.
    anomaly_type: AnomalyType  # spike, drift, unusual_pattern, cost_increase
    severity: SeverityLevel    # low, medium, high, critical
    detected_at: datetime
    cost_impact: float
    description: str
    root_cause: Optional[str]
    affected_resources: List[str]
```

### SavingsOpportunity

```python
class SavingsOpportunity(BaseModel):
    id: str
    provider: str
    service: str
    opportunity_type: RecommendationType  # rightsizing, reserved_instances, etc.
    estimated_savings: float              # Economia mensal estimada
    confidence_level: float               # 0-100%
    implementation_effort: str            # Low, Medium, High
    description: str
    action_required: str
    risk_level: SeverityLevel
```

### OptimizationRecommendation

```python
class OptimizationRecommendation(BaseModel):
    id: str
    provider: str
    category: RecommendationType
    title: str
    description: str
    potential_savings: float
    priority: SeverityLevel
    implementation_time: str
    prerequisites: List[str]
    steps: List[str]
    resources: List[str]
```

## Cache e Performance

### Configuração de TTL

- **Anomalias**: 1 hora (dados críticos, atualizações frequentes)
- **Oportunidades**: 4 horas (análises complexas, menor volatilidade)
- **Recomendações**: 6 horas (dados estáveis, menor frequência de mudança)

### Padrões de Cache

```python
# Chaves do Redis seguem o padrão:
# cloud_optimization:{category}:{provider}

# Exemplos:
# cloud_optimization:anomalies:AWS
# cloud_optimization:savings:Azure
# cloud_optimization:recommendations:GCP
# cloud_optimization:anomalies  (todos os provedores)
```

### Estratégias de Invalidação

- **Automática**: TTL expira automaticamente
- **Manual**: Invalidação forçada via API
- **Inteligente**: Invalidação baseada em eventos críticos

## Integração com APIs

### FastAPI Endpoints

```python
from fastapi import FastAPI, Depends
from app.cloud_native_optimization import CloudNativeOptimizationService

app = FastAPI()

@app.get("/optimization/anomalies")
async def get_anomalies(
    provider: Optional[str] = None,
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    return await service.get_anomalies_by_provider(provider)

@app.get("/optimization/savings")
async def get_savings_opportunities(
    provider: Optional[str] = None,
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    return await service.get_savings_opportunities_by_provider(provider)

@app.get("/optimization/recommendations")
async def get_recommendations(
    provider: Optional[str] = None,
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    return await service.get_unified_recommendations(provider)

@app.get("/optimization/report")
async def get_full_report(
    provider: Optional[str] = None,
    service: CloudNativeOptimizationService = Depends(get_optimization_service)
):
    return await service.get_full_optimization_report(provider)
```

## Monitoramento e Logging

### Configuração de Logs

```python
import logging

# Configurar logging para o módulo
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('cloud_native_optimization')
```

### Métricas Importantes

- **Taxa de Cache Hit**: Percentual de consultas atendidas pelo cache
- **Tempo de Resposta**: Latência das APIs dos provedores
- **Anomalias Detectadas**: Número e severidade das anomalias
- **Economia Identificada**: Total de oportunidades encontradas

## Testes

### Executar Testes

```bash
# Todos os testes
python -m pytest tests/test_cloud_native_optimization.py -v

# Testes específicos
python -m pytest tests/test_cloud_native_optimization.py::TestPydanticModels -v

# Com cobertura
python -m pytest tests/test_cloud_native_optimization.py --cov=app.cloud_native_optimization
```

### Testes de Integração

```bash
# Configurar ambiente de teste
export AWS_OPTIMIZATION_ENABLED=true
export AWS_ACCESS_KEY_ID=test_key
export AWS_SECRET_ACCESS_KEY=test_secret

# Executar testes de integração
python -m pytest tests/test_cloud_native_optimization.py::TestIntegration -v
```

## Troubleshooting

### Problemas Comuns

#### 1. Erro de Autenticação AWS

```
Erro: botocore.exceptions.NoCredentialsError
Solução: Verificar AWS_ACCESS_KEY_ID e AWS_SECRET_ACCESS_KEY
```

#### 2. Erro de Conexão Redis

```
Erro: redis.exceptions.ConnectionError
Solução: Verificar se Redis está rodando e acessível
```

#### 3. Timeout na API do Azure

```
Erro: azure.core.exceptions.ServiceRequestTimeoutError
Solução: Verificar conectividade e credenciais do Azure
```

### Debug Mode

```python
# Habilitar logs detalhados
import logging
logging.getLogger('cloud_native_optimization').setLevel(logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.DEBUG)
logging.getLogger('azure').setLevel(logging.DEBUG)
```

## Roadmap

### Versão Atual (v1.0)
- ✅ Suporte AWS, Azure, GCP
- ✅ Cache Redis com TTL
- ✅ Modelos Pydantic unificados
- ✅ Testes automatizados

### Próximas Versões

#### v1.1
- 🔄 Implementação completa Oracle Cloud
- 🔄 WebHooks para notificações
- 🔄 Dashboard em tempo real

#### v1.2
- 🔄 Machine Learning para predição de anomalias
- 🔄 Recomendações inteligentes baseadas em histórico
- 🔄 Integração com ferramentas de CI/CD

#### v1.3
- 🔄 Suporte a Alibaba Cloud
- 🔄 Suporte a IBM Cloud
- 🔄 API GraphQL

## Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Clone** sua cópia local
3. **Crie** uma branch para sua feature
4. **Implemente** sua funcionalidade
5. **Teste** suas alterações
6. **Submit** um Pull Request

### Padrões de Código

- Seguir PEP 8
- Documentar funções com docstrings
- Incluir testes para novas funcionalidades
- Atualizar documentação conforme necessário

## Licença

Este módulo está licenciado sob [MIT License](LICENSE).

## Suporte

Para suporte técnico ou dúvidas:

- 📧 Email: suporte@x-cost.com
- 📱 Slack: #cloud-optimization
- 📖 Wiki: [Documentação Técnica](docs/wiki)
- 🐛 Issues: [GitHub Issues](issues)

---

**Desenvolvido com ❤️ pela equipe X-Cost/MegaBill**
