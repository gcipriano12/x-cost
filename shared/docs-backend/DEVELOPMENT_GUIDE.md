# 🚀 Guia de Desenvolvimento Local - X Cost API

Este guia fornece instruções completas para configurar e executar a API FinOps com gerenciamento de credenciais em ambiente local.

## 📋 Pré-requisitos

### Software Necessário
- **Python 3.11+** (testado com 3.12)
- **Docker & Docker Compose** ou **Podman & Podman Compose**
- **Git**
- **PostgreSQL** (ou use Docker/Podman)
- **Redis** (ou use Docker/Podman)

### Conhecimentos Recomendados
- FastAPI
- SQLAlchemy
- JWT/OAuth2
- Docker/Podman
- PostgreSQL
- Pytest (para testes)
- SQLite (para ambiente de testes)

## 🔧 Configuração Inicial

### 1. Clone e Configuração do Projeto

```bash
# Clone o projeto
git clone <url-do-repositorio>
cd xcost-api

# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements-dev.txt
```

### 2. Configuração do Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env
```

**Configurações importantes no .env:**

```bash
# Banco de dados
DATABASE_URL=postgresql://finops_user:finops_password@localhost:5432/finops_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT (gerar chave segura)
FINOPS_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Criptografia adicional
FINOPS_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Desenvolvimento
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
```

### 3. Inicialização Rápida (Automática)

Para iniciar rapidamente com detecção automática de Docker/Podman:

```bash
# Tornar executável
chmod +x quick_start.sh

# Executar script automático
./quick_start.sh

# O script irá:
# ✅ Detectar Docker ou Podman automaticamente
# ✅ Subir serviços de infraestrutura
# ✅ Aguardar inicialização dos serviços
# ✅ Configurar banco de dados
# ✅ Iniciar a API
```

### 4. Inicialização com Docker/Podman (Manual)

```bash
# Para Docker
docker-compose up -d postgres redis localstack

# Para Podman
podman-compose up -d postgres redis localstack
# OU (se configurado compatibilidade)
docker-compose up -d postgres redis localstack

# Aguardar inicialização (30 segundos)
sleep 30

# Verificar status dos serviços
docker-compose ps  # ou podman-compose ps
```

### 5. Inicialização Manual Completa (Alternativa)

Se preferir não usar Docker:

```bash
# Instalar PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Criar banco e usuário
sudo -u postgres psql
CREATE DATABASE finops_db;
CREATE USER finops_user WITH PASSWORD 'finops_password';
GRANT ALL PRIVILEGES ON DATABASE finops_db TO finops_user;
\q

# Instalar Redis
sudo apt-get install redis-server
redis-server
```

## 🗄️ Configuração do Banco de Dados

### 1. Executar Migrações

```bash
# Inicializar Alembic
alembic init migrations

# Criar primeira migração
alembic revision --autogenerate -m "Initial schema"

# Aplicar migrações
alembic upgrade head
```

### 2. Executar Script de Inicialização

```bash
# Executar script de inicialização
python scripts/init_db.py
```

**O script irá:**
- ✅ Criar todas as tabelas necessárias
- ✅ Criar usuário admin padrão
- ✅ Criar usuários de exemplo
- ✅ Configurar dados iniciais

### 3. Verificar Inicialização

```bash
# Conectar ao banco
psql postgresql://finops_user:finops_password@localhost:5432/finops_db

# Verificar tabelas
\dt finops.*

# Verificar usuários criados
SELECT username, role, is_active FROM finops.users;
```

## 🚀 Execução da API

### 1. Desenvolvimento com Auto-reload

```bash
# Executar API em modo desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Ou usando o script direto
python app/main.py
```

### 2. Usando Docker Compose (Completo)

```bash
# Subir todos os serviços
docker-compose up

# Em background
docker-compose up -d

# Ver logs
docker-compose logs -f api
```

### 3. Verificar Funcionamento

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Documentação interativa
open http://localhost:8000/docs

# Redoc
open http://localhost:8000/redoc
```

## 🔐 Primeiros Passos com Autenticação

### 1. Login como Admin

```bash
# Fazer login (usuário padrão: admin / ChangeMe123!)
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "ChangeMe123!"
  }'

# Resposta esperada:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "username": "admin",
    "role": "admin"
  }
}
```

### 2. Salvar Token

```bash
# Salvar token em variável
export TOKEN="seu_token_aqui"

# Ou criar script
echo 'export TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '"'"'{"username":"admin","password":"ChangeMe123!"}'"'"' | \
  jq -r ".access_token")' > get_token.sh

chmod +x get_token.sh
source get_token.sh
```

### 3. Testar Endpoints Protegidos

```bash
# Listar credenciais (deve retornar lista vazia)
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/credentials

# Obter status do sistema
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/system/status
```

## 🔧 Configuração de Credenciais

### 1. Simulação com LocalStack

Para desenvolvimento, use LocalStack para simular AWS Services:

```bash
# LocalStack já está no podman-compose.yml
# Verificar se está rodando
curl http://localhost:4566/health

# Configurar AWS CLI para LocalStack
aws configure set aws_access_key_id test
aws configure set aws_secret_access_key test
aws configure set region us-east-1

# Testar Secrets Manager local
aws --endpoint-url=http://localhost:4566 secretsmanager list-secrets
```

### 2. Primeira Credencial de Teste

```bash
# Criar credencial AWS de teste
curl -X POST "http://localhost:8000/api/v1/credentials" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test-aws-local",
    "description": "Credencial AWS para testes locais",
    "provider_type": "AWS",
    "credentials": {
      "access_key_id": "AKIAIOSFODNN7EXAMPLE",
      "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
      "region": "us-east-1",
      "account_id": "123456789012"
    }
  }'
```

### 3. Testar Validação

```bash
# Obter ID da credencial criada
CRED_ID=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/credentials" | \
  jq -r '.[0].id')

# Validar credencial
curl -X POST "http://localhost:8000/api/v1/credentials/$CRED_ID/validate" \
  -H "Authorization: Bearer $TOKEN"
```

## 🧪 Executar Testes

### 1. Configuração de Testes

```bash
# Instalar dependências de teste
pip install -r requirements-dev.txt

# Configurar pytest
cp pytest.ini.example pytest.ini
```

### 2. Executar Testes

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

### 3. Testes de Integração

```bash
# Subir ambiente de teste
docker-compose -f docker-compose.test.yml up -d

# Executar testes de integração
pytest tests/test_integration.py

# Limpar ambiente de teste
docker-compose -f docker-compose.test.yml down
```

## 🧪 Sistema de Testes

### 1. Arquitetura de Testes

A API utiliza um sistema dual de bancos:
- **PostgreSQL com schema "finops"** para produção
- **SQLite sem schema** para testes (compatibilidade máxima)

### 2. Executar Testes

```bash
# Executar todos os testes
pytest tests/ -v

# Executar testes específicos
pytest tests/test_credentials.py -v

# Executar testes com cobertura
pytest tests/ --cov=app --cov-report=html

# Executar testes de performance
pytest tests/stress_test_finops_api.py -v
```

### 3. Estrutura de Testes

```
tests/
├── conftest.py                # Configurações globais de teste
├── test_config.py             # Configuração de ambiente de teste
├── test_models.py             # Modelos SQLite sem schema
├── test_auth_security.py      # SecurityManager para testes
├── test_credentials_api.py    # API endpoints para testes
├── test_credentials.py        # Testes principais de credenciais
├── test_auth.py               # Testes de autenticação
└── stress_test_finops_api.py  # Testes de carga
```

### 4. Fixtures Disponíveis

```python
# Usuários de teste
admin_user, finops_admin_user, viewer_auth_headers

# Credenciais de exemplo
sample_aws_credentials, sample_azure_credentials

# Mocks
mock_secrets_manager

# Clientes de teste
client, db_session
```

## 🛠️ Ferramentas de Desenvolvimento

### 1. Interfaces Web Úteis

```bash
# API Documentation (Swagger)
open http://localhost:8000/docs

# Alternative Documentation (Redoc)
open http://localhost:8000/redoc

# PostgreSQL Admin (Adminer)
open http://localhost:8080

# Redis Admin (Redis Commander)
open http://localhost:8081
```

### 2. Logs e Debug

```bash
# Ver logs da API
docker-compose logs -f api

# Ver logs do PostgreSQL
docker-compose logs -f postgres

# Ver logs do Redis
docker-compose logs -f redis

# Debug com breakpoints
# Adicionar no código: import pdb; pdb.set_trace()
```

### 3. Scripts Úteis

```bash
# Resetar banco de dados
python scripts/reset_db.py

# Criar usuário de teste
python scripts/create_test_user.py

# Backup do banco
python scripts/backup_db.py

# Restore do banco
python scripts/restore_db.py
```

## 📊 Desenvolvimento de Features

### 1. Estrutura de Arquivos

```
app/
├── main.py                 # API principal
├── models.py              # Modelos FOCUS originais
├── credential_models.py   # Modelos de credenciais
├── database.py            # Configuração DB
├── auth_security.py       # Autenticação/autorização
├── secrets_manager.py     # Gerenciamento de secrets
├── credentials_api.py     # Endpoints de credenciais
├── cloud_connectors.py    # Conectores cloud
├── cost_analytics.py      # Analytics de custos
└── data_ingestion.py      # Ingestão de dados
```

### 2. Adicionando Novos Endpoints

```python
# Em credentials_api.py ou novo arquivo
from fastapi import APIRouter, Depends
from auth_security import get_current_active_user

router = APIRouter(prefix="/api/v1/nova-feature")

@router.get("/")
async def nova_funcionalidade(
    current_user: User = Depends(get_current_active_user)
):
    # Implementar lógica
    pass

# Registrar no main.py
app.include_router(router)
```

### 3. Adicionando Novos Modelos

```python
# Em credential_models.py
class NovoModelo(Base):
    __tablename__ = "novo_modelo"
    __table_args__ = {"schema": "finops"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # ... outros campos

# Pydantic model correspondente
class NovoModeloResponse(BaseModel):
    id: str
    # ... outros campos
    
    class Config:
        from_attributes = True
```

### 4. Migrações de Banco

```bash
# Criar nova migração
alembic revision --autogenerate -m "Adicionar novo modelo"

# Revisar arquivo de migração gerado
vim migrations/versions/xxx_adicionar_novo_modelo.py

# Aplicar migração
alembic upgrade head

# Rollback se necessário
alembic downgrade -1
```

## 🔍 Debug e Troubleshooting

### 1. Problemas Comuns

**Erro de Conexão com Banco:**
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps postgres

# Verificar logs
docker-compose logs postgres

# Testar conexão manual
psql postgresql://finops_user:finops_password@localhost:5432/finops_db
```

**Erro de Autenticação:**
```bash
# Verificar se usuário admin existe
psql -c "SELECT * FROM finops.users WHERE role='admin';" $DATABASE_URL

# Recriar usuário admin
python scripts/create_admin_user.py
```

**Erro no Redis:**
```bash
# Verificar Redis
redis-cli ping

# Limpar cache
redis-cli FLUSHALL
```

### 2. Logs Detalhados

```python
# Adicionar logging detalhado
import logging
logging.basicConfig(level=logging.DEBUG)

# Em qualquer módulo
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### 3. Debug com VS Code

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI Debug",
            "type": "python",
            "request": "launch",
            "program": "app/main.py",
            "console": "integratedTerminal",
            "env": {
                "ENVIRONMENT": "development",
                "DEBUG": "true"
            }
        }
    ]
}
```

## 🧪 Testando Funcionalidades

### 1. Testes Manuais com curl

```bash
# Script de testes completo
cat > test_api.sh << 'EOF'
#!/bin/bash

BASE_URL="http://localhost:8000"

# 1. Health check
echo "=== Health Check ==="
curl -s "$BASE_URL/api/v1/health" | jq

# 2. Login
echo "=== Login ==="
TOKEN=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ChangeMe123!"}' | \
  jq -r '.access_token')

echo "Token: $TOKEN"

# 3. Listar credenciais
echo "=== Credenciais ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/credentials" | jq

# 4. Status do sistema
echo "=== Status ==="
curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/api/v1/system/status" | jq

EOF

chmod +x test_api.sh
./test_api.sh
```

### 2. Testes Automatizados

```bash
# Executar suite de testes
pytest -v

# Testes com cobertura
pytest --cov=app tests/

# Testes específicos
pytest tests/test_auth.py::test_login_success -v

# Testes com output
pytest -s tests/test_credentials.py
```

### 3. Testes de Performance

```bash
# Instalar ferramentas
pip install locust

# Criar arquivo de teste
cat > locustfile.py << 'EOF'
from locust import HttpUser, task, between

class FinOpsUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "ChangeMe123!"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task
    def health_check(self):
        self.client.get("/api/v1/health")
    
    @task
    def list_credentials(self):
        self.client.get("/api/v1/credentials", headers=self.headers)
EOF

# Executar teste de carga
locust -f locustfile.py --host=http://localhost:8000
```

## 🔄 Workflow de Desenvolvimento

### 1. Feature Development

```bash
# 1. Criar branch
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver
# ... fazer alterações

# 3. Executar testes
pytest

# 4. Verificar qualidade
black app/
isort app/
flake8 app/

# 5. Commit
git add .
git commit -m "feat: adicionar nova funcionalidade"

# 6. Push
git push origin feature/nova-funcionalidade
```

### 2. Code Quality

```bash
# Formatação automática
black app/ tests/

# Organizar imports
isort app/ tests/

# Linting
flake8 app/ tests/

# Type checking
mypy app/

# Security check
bandit -r app/
```

### 3. Pre-commit Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.11.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
EOF

# Instalar hooks
pre-commit install
```

## 📚 Recursos e Documentação

### 1. Documentação Técnica

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/
- **JWT**: https://pyjwt.readthedocs.io/

### 2. Referências da API

```bash
# Documentação interativa
http://localhost:8000/docs

# Schema OpenAPI
http://localhost:8000/openapi.json

# Redoc
http://localhost:8000/redoc
```

### 3. Arquivos de Referência

- `docs/SECURITY_ARCHITECTURE.md` - Arquitetura de segurança
- `docs/API_DOCUMENTATION.md` - Documentação da API
- `docs/FRONTEND_INTEGRATION.md` - Integração com frontend

## 🚨 Importante para Produção

### ⚠️ Configurações que DEVEM ser alteradas:

1. **Senhas Padrão**:
   ```bash
   # Alterar senha do admin
   # Alterar FINOPS_SECRET_KEY
   # Alterar senhas do banco
   ```

2. **Configurações de Segurança**:
   ```bash
   # Habilitar HTTPS
   # Configurar CORS adequadamente
   # Configurar IP whitelist
   # Usar AWS Secrets Manager real
   ```

3. **Banco de Dados**:
   ```bash
   # Usar RDS em produção
   # Configurar backups
   # Configurar SSL
   ```

4. **Monitoramento**:
   ```bash
   # Configurar CloudWatch
   # Configurar alertas
   # Configurar métricas
   ```

---

## ✅ Checklist de Desenvolvimento

- [ ] Ambiente local configurado
- [ ] Banco de dados inicializado
- [ ] Usuário admin criado
- [ ] Primeira credencial testada
- [ ] Testes automatizados passando
- [ ] Documentação lida
- [ ] Scripts de desenvolvimento testados
- [ ] Debug configurado
- [ ] Code quality verificado

**🎯 Agora você está pronto para desenvolver na API FinOps com total segurança e funcionalidade!**