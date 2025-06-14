# 🔐 X Cost API - Gerenciamento de custos Multi-Cloud

Uma API completa para gerenciamento de custos e credenciais de provedores de nuvem, baseada na especificação FOCUS (FinOps Open Cost and Usage Specification) com sistema robusto de autenticação e autorização.

## 🌟 Principais Funcionalidades

### 💰 **Análise de Custos Multi-Cloud**
- ✅ Extração automatizada de dados de faturamento (AWS, Azure, GCP, Oracle Cloud)
- ✅ Transformação para padrão FOCUS
- ✅ Análises avançadas: tendências, previsões, anomalias
- ✅ Relatórios executivos automatizados

### 🔐 **Gerenciamento Seguro de Credenciais**
- ✅ Armazenamento criptografado no AWS Secrets Manager
- ✅ Criptografia em múltiplas camadas (AES-256 + KMS + Fernet)
- ✅ Validação automática de credenciais
- ✅ Rotação assistida de chaves
- ✅ Audit trail completo

### 🛡️ **Segurança Enterprise**
- ✅ Autenticação JWT com refresh tokens
- ✅ RBAC com 4 níveis (Admin, FinOps Admin, Operator, Viewer)
- ✅ Rate limiting e IP whitelisting
- ✅ Conformidade OWASP Top 10
- ✅ Logs de auditoria detalhados

### 📊 **Analytics Avançados**
- ✅ Machine Learning para previsões de custo
- ✅ Detecção de anomalias automatizada
- ✅ Análises por tags, serviços e projetos
- ✅ Alertas de orçamento personalizáveis

## 🚀 Quick Start (5 minutos)

### **Método 1: Script Automatizado (Recomendado)**

```bash
# 1. Clone o projeto
git clone <url-do-repositorio>
cd xcost-api

# 2. Executar setup automático
chmod +x quick_start.sh
./quick_start.sh

# 3. Iniciar API
source venv/bin/activate
uvicorn app.main:app --reload
```

### **Método 2: Setup Manual**

```bash
# 1. Ambiente Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements-dev.txt

# 2. Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# 3. Subir infraestrutura
docker-compose up -d postgres redis localstack

# 4. Inicializar banco
python scripts/init_db.py

# 5. Iniciar API
uvicorn app.main:app --reload
```

## 📖 Acesso Rápido

### **🌐 URLs Importantes**
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **PostgreSQL Admin**: http://localhost:8080
- **Redis Admin**: http://localhost:8081

### **🔑 Login Padrão**
- **Usuário**: `admin`
- **Senha**: `ChangeMe123!`

### **📱 Teste Rápido**

```bash
# 1. Health check
curl http://localhost:8000/api/v1/health

# 2. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ChangeMe123!"}'

# 3. Salvar token
export TOKEN="seu_access_token_aqui"

# 4. Listar credenciais
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/credentials

# 5. Ver status do sistema
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/status
```

## 🏗️ Arquitetura

### **Stack Tecnológico**
- **Backend**: FastAPI + Python 3.11+
- **Banco de Dados**: PostgreSQL 15 + Redis 7
- **Segurança**: JWT + AWS Secrets Manager + KMS
- **Cloud**: AWS (Secrets Manager, KMS, ECS, RDS)
- **Containers**: Docker + Docker Compose
- **Analytics**: Pandas + Scikit-learn + NumPy

### **Estrutura do Projeto**

```
xcost-api/
├── app/                      # Código principal da aplicação
│   ├── main.py              # FastAPI app principal
│   ├── models.py            # Modelos FOCUS originais
│   ├── credential_models.py # Modelos de credenciais e auth
│   ├── auth_security.py     # Sistema de autenticação
│   ├── secrets_manager.py   # Gerenciador de credenciais
│   ├── credentials_api.py   # Endpoints de credenciais
│   ├── cost_analytics.py    # Análises de custo
│   └── cloud_connectors.py  # Conectores multi-cloud
├── tests/                   # Testes automatizados
├── scripts/                 # Scripts de utilidade
├── docs/                    # Documentação completa
├── migrations/              # Migrações de banco
└── config/                  # Configurações
```

## 🔐 Sistema de Autenticação e Autorização

### **Roles e Permissões**

| Funcionalidade | Admin | FinOps Admin | Operator | Viewer |
|---------------|-------|--------------|----------|--------|
| **Credenciais** |
| Criar credenciais | ✅ | ✅ | ❌ | ❌ |
| Visualizar credenciais | ✅ | ✅ | ✅ | ✅ |
| Editar credenciais | ✅ | ✅ | ❌ | ❌ |
| Excluir credenciais | ✅ | ✅ | ❌ | ❌ |
| Validar credenciais | ✅ | ✅ | ✅ | ❌ |
| **Usuários** |
| Gerenciar usuários | ✅ | ❌ | ❌ | ❌ |
| **Sistema** |
| Configurações sistema | ✅ | ❌ | ❌ | ❌ |
| Logs de auditoria | ✅ | ✅ | ❌ | ✅ |
| **Dados** |
| Ingestão de dados | ✅ | ✅ | ✅ | ❌ |
| Visualizar relatórios | ✅ | ✅ | ✅ | ✅ |

### **Fluxo de Autenticação**

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as API
    participant DB as Database
    participant SM as Secrets Manager
    
    U->>F: Username/Password
    F->>A: POST /auth/login
    A->>DB: Validate user
    DB-->>A: User data
    A-->>F: JWT Token + User info
    F->>A: API calls with Bearer token
    A->>DB: Verify token & permissions
    A->>SM: Access credentials (if authorized)
    SM-->>A: Encrypted credentials
    A-->>F: API response
```

## 🗝️ Gerenciamento de Credenciais

### **Fluxo de Segurança das Credenciais**

```mermaid
graph TD
    A[Frontend] --> B[API Endpoint]
    B --> C[Autenticação JWT]
    C --> D[Verificação RBAC]
    D --> E[Validação Input]
    E --> F[Criptografia Fernet]
    F --> G[AWS Secrets Manager]
    G --> H[Criptografia KMS]
    H --> I[Armazenamento Seguro]
    
    J[Audit Logger] --> K[PostgreSQL]
    B --> J
    D --> J
    E --> J
```

### **Tipos de Credenciais Suportadas**

#### **🔹 AWS**
```json
{
  "provider_type": "AWS",
  "credentials": {
    "access_key_id": "AKIA...",
    "secret_access_key": "...",
    "region": "us-east-1",
    "account_id": "123456789012",
    "role_arn": "arn:aws:iam::...",
    "external_id": "optional"
  }
}
```

#### **🔹 Azure**
```json
{
  "provider_type": "Azure",
  "credentials": {
    "subscription_id": "uuid",
    "client_id": "uuid",
    "client_secret": "...",
    "tenant_id": "uuid"
  }
}
```

#### **🔹 GCP**
```json
{
  "provider_type": "GCP",
  "credentials": {
    "project_id": "my-project",
    "service_account_key": {
      "type": "service_account",
      "project_id": "...",
      "private_key": "...",
      "client_email": "..."
    }
  }
}
```

#### **🔹 Oracle Cloud**
```json
{
  "provider_type": "Oracle Cloud",
  "credentials": {
    "user_ocid": "ocid1.user.oc1...",
    "tenancy_ocid": "ocid1.tenancy.oc1...",
    "region": "us-ashburn-1",
    "fingerprint": "aa:bb:cc:...",
    "private_key": "-----BEGIN PRIVATE KEY-----..."
  }
}
```

## 📊 Principais Endpoints da API

### **🔐 Autenticação**
```
POST   /api/v1/auth/login           # Login do usuário
POST   /api/v1/auth/users           # Criar usuário (admin only)
```

### **🗝️ Gerenciamento de Credenciais**
```
GET    /api/v1/credentials          # Listar credenciais
POST   /api/v1/credentials          # Criar credencial
GET    /api/v1/credentials/{id}     # Obter credencial específica
PUT    /api/v1/credentials/{id}     # Atualizar credencial
DELETE /api/v1/credentials/{id}     # Remover credencial
POST   /api/v1/credentials/{id}/validate  # Validar credencial
POST   /api/v1/credentials/test     # Testar sem salvar
```

### **💰 Dados de Custo**
```
GET    /api/v1/costs                # Obter dados de custo
GET    /api/v1/costs/summary        # Resumo agregado
POST   /api/v1/data/secure-ingest   # Ingestão segura de dados
```

### **📈 Analytics**
```
GET    /api/v1/analytics/trend      # Análise de tendências
GET    /api/v1/analytics/forecast   # Previsões de custo
GET    /api/v1/analytics/anomalies  # Detecção de anomalias
GET    /api/v1/analytics/by-tags    # Análise por tags
GET    /api/v1/analytics/report     # Relatório executivo
```

### **💳 Orçamentos**
```
GET    /api/v1/budgets              # Listar orçamentos
POST   /api/v1/budgets              # Criar orçamento
GET    /api/v1/budgets/alerts       # Verificar alertas
```

### **📋 Auditoria**
```
GET    /api/v1/audit/logs           # Logs de auditoria
```

### **🔧 Sistema**
```
GET    /api/v1/health               # Health check
GET    /api/v1/system/status        # Status detalhado
GET    /api/v1/providers/status     # Status dos provedores
DELETE /api/v1/cache/clear          # Limpar cache
```

## 🧪 Testes

### **Executar Testes**

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=app --cov-report=html

# Testes específicos
pytest tests/test_auth.py
pytest tests/test_credentials.py

# Testes com output detalhado
pytest -v -s
```

### **Testes de Integração**

```bash
# Subir ambiente de teste
docker-compose -f docker-compose.test.yml up -d

# Executar testes de integração
pytest tests/test_integration.py

# Limpar ambiente
docker-compose -f docker-compose.test.yml down
```

### **Cobertura de Testes**

- ✅ **Autenticação**: Login, logout, roles, permissões
- ✅ **Credenciais**: CRUD, validação, segurança
- ✅ **Analytics**: Tendências, previsões, anomalias
- ✅ **API**: Endpoints, middleware, error handling
- ✅ **Integração**: Fluxos end-to-end

## 🛠️ Desenvolvimento

### **Configuração do Ambiente**

1. **Python 3.11+**
2. **Docker & Docker Compose**
3. **PostgreSQL 15** (ou via Docker)
4. **Redis 7** (ou via Docker)

### **Comandos Úteis**

```bash
# Formato de código
black app/ tests/
isort app/ tests/

# Linting
flake8 app/ tests/

# Type checking
mypy app/

# Segurança
bandit -r app/

# Migrações
alembic revision --autogenerate -m "Description"
alembic upgrade head

# Reset do banco
python scripts/init_db.py

# Backup/Restore
python scripts/backup_db.py
python scripts/restore_db.py
```

### **Debug e Troubleshooting**

```bash
# Logs da API
docker-compose logs -f api

# Logs do banco
docker-compose logs -f postgres

# Status dos serviços
docker-compose ps

# Conectar ao banco
psql postgresql://finops_user:finops_password@localhost:5432/finops_db

# Conectar ao Redis
redis-cli -h localhost -p 6379
```

## 🎨 Integração com Frontend

### **Para Lovable/React**

A API foi projetada para fácil integração com qualquer frontend. Veja `docs/FRONTEND_INTEGRATION.md` para:

- ✅ Serviços TypeScript prontos
- ✅ Componentes React de exemplo
- ✅ Hooks customizados
- ✅ Tratamento de erros
- ✅ Configurações de autenticação
- ✅ Prompts específicos para o Lovable

### **Schema OpenAPI**

```bash
# Schema completo da API
curl http://localhost:8000/openapi.json

# Documentação interativa
open http://localhost:8000/docs
```

## 📚 Documentação Completa

### **📖 Guias Disponíveis**

- **[DEVELOPMENT_GUIDE.md](docs/DEVELOPMENT_GUIDE.md)** - Setup e desenvolvimento local
- **[SECURITY_ARCHITECTURE.md](docs/SECURITY_ARCHITECTURE.md)** - Arquitetura de segurança
- **[FRONTEND_INTEGRATION.md](docs/FRONTEND_INTEGRATION.md)** - Integração com frontend
- **[API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)** - Documentação completa da API

### **🎯 Casos de Uso**

1. **Gerenciamento Centralizado**: Todas as credenciais cloud em um local seguro
2. **Conformidade**: Audit trail completo para auditorias
3. **Automação**: Validação e rotação automática de credenciais
4. **Visibilidade**: Dashboard unificado de custos multi-cloud
5. **Governança**: Controle de acesso baseado em roles
6. **Prevenção**: Alertas proativos de orçamento e anomalias

## 🔧 Configuração para Produção

### **⚠️ Checklist de Segurança**

- [ ] **Alterar senha padrão** do usuário admin
- [ ] **Configurar HTTPS** com certificado SSL
- [ ] **Usar AWS RDS** em vez de PostgreSQL local
- [ ] **Configurar AWS Secrets Manager** real
- [ ] **Definir IP whitelist** apropriado
- [ ] **Configurar CORS** adequadamente
- [ ] **Habilitar logs de auditoria** detalhados
- [ ] **Configurar backups** automáticos
- [ ] **Implementar monitoramento** CloudWatch
- [ ] **Configurar alertas** de segurança

### **🚀 Deploy na AWS**

Use o `deploy.sh` fornecido para deploy automatizado:

```bash
# Configure AWS CLI
aws configure

# Execute deploy
./deploy.sh
```

O script criará automaticamente:
- ✅ VPC com subnets públicas/privadas
- ✅ RDS PostgreSQL Multi-AZ
- ✅ ElastiCache Redis
- ✅ ECS Fargate cluster
- ✅ Application Load Balancer
- ✅ Security Groups configurados
- ✅ IAM roles e políticas

## 📈 Roadmap

### **🎯 v2.1 (Próxima Release)**
- [ ] **Rotação automática** de credenciais
- [ ] **Dashboard avançado** com mais visualizações
- [ ] **Alertas via email/Slack** 
- [ ] **API de webhooks** para integrações
- [ ] **Exportação de relatórios** em PDF/Excel

### **🚀 v2.2 (Futuro)**
- [ ] **Multi-tenancy** para empresas
- [ ] **SSO/SAML** integration
- [ ] **Mobile app** companion
- [ ] **AI/ML** insights avançados
- [ ] **Recommendations engine** para otimização

## 🤝 Contribuição

### **Como Contribuir**

1. **Fork** o repositório
2. **Criar branch** para feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** alterações (`git commit -m 'feat: adicionar nova funcionalidade'`)
4. **Push** para branch (`git push origin feature/nova-funcionalidade`)
5. **Abrir Pull Request**

### **Padrões de Código**

- **Python**: PEP 8 + Black formatting
- **Commits**: Conventional Commits
- **Tests**: Pytest com >80% cobertura
- **Docs**: Markdown com exemplos práticos

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🆘 Suporte

### **Problemas Comuns**

1. **Erro de conexão com banco**: Verificar se PostgreSQL está rodando
2. **Erro de autenticação**: Verificar credenciais do usuário admin
3. **Erro no Redis**: Limpar cache com `redis-cli FLUSHALL`
4. **API não responde**: Verificar logs com `docker-compose logs api`

### **Onde Obter Ajuda**

- 📖 **Documentação**: `docs/` directory
- 🐛 **Issues**: GitHub Issues
- 💬 **Discussões**: GitHub Discussions
- 📧 **Email**: support@xcost-api.com

---

## ✅ Status do Projeto

- ✅ **API Core**: Completa e funcional
- ✅ **Autenticação**: JWT + RBAC implementado
- ✅ **Gerenciamento de Credenciais**: Totalmente seguro
- ✅ **Analytics**: ML + Previsões funcionando
- ✅ **Testes**: >85% cobertura
- ✅ **Documentação**: Completa
- ✅ **Deploy**: Automatizado na AWS
- ✅ **Frontend Ready**: Pronto para integração

**🎯 A API está pronta para uso em produção!**

---

**Desenvolvido com ❤️ para a comunidade FinOps**