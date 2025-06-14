# GITHUB COPILOT - Instruções para Backend (X-Cost)

## Visão Geral
Este é um projeto monorepo X-Cost com backend em FastAPI/Python e frontend em React/TypeScript. Como Copilot, você é responsável exclusivamente pelo **backend** e deve seguir rigorosamente estas diretrizes.

## Responsabilidades
- ✅ Desenvolvimento e manutenção do backend (`/backend`)
- ✅ Documentação backend (`/shared/docs-backend`)
- ✅ APIs e endpoints
- ✅ Banco de dados e migrations
- ✅ Autenticação e segurança
- ❌ **NUNCA** modificar arquivos do frontend (`/frontend`)
- ❌ **NUNCA** modificar configurações do frontend

## Stack Tecnológica Backend
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn
- **Database**: PostgreSQL + SQLAlchemy 2.0
- **Cache**: Redis + aioredis
- **Auth**: JWT + passlib
- **Cloud SDKs**: boto3 (AWS), azure-*, google-cloud-*, oci
- **Analytics**: pandas, numpy, scikit-learn
- **Background Tasks**: Celery
- **Container**: Podman + podman-compose

## Comandos Disponíveis
```bash
cd backend
# Ambiente virtual
source venv/bin/activate

# Dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Desenvolvimento
python app/main.py
# ou
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testes
pytest
python -m pytest tests/

# Database
python scripts/init_db.py
alembic upgrade head

# Containers
podman-compose up -d
```

## Regras de Desenvolvimento

### 1. Preservação de Funcionalidades
- **CRÍTICO**: Novas implementações NÃO podem quebrar funcionalidades existentes
- Sempre executar testes antes de finalizar
- Manter compatibilidade com APIs consumidas pelo frontend

### 2. Estrutura do Projeto
```
backend/
├── app/
│   ├── main.py              # FastAPI app principal
│   ├── database.py          # Configuração DB
│   ├── models.py            # Modelos SQLAlchemy
│   ├── credentials_api.py   # API de credenciais
│   ├── cost_analytics.py    # Analytics de custos
│   ├── auth_security.py     # Autenticação
│   └── cloud_connectors.py  # Conectores cloud
├── tests/                   # Testes automatizados
├── scripts/                 # Scripts utilitários
├── migrations/              # Migrations Alembic
└── docs/                    # Documentação específica
```

### 3. APIs e Endpoints
- **Base URL**: `http://localhost:8000`
- Seguir padrões REST
- Documentação automática: `/docs` (Swagger)
- Versionamento de API quando necessário
- **Manter compatibilidade** com frontend existente

### 4. Banco de Dados
- PostgreSQL como principal
- SQLAlchemy 2.0 (async)
- Migrations com Alembic
- Testes com SQLite (`test.db`)

### 5. Autenticação
- JWT tokens
- Hash de senhas com bcrypt
- Middleware de autenticação
- Gestão de sessões

### 6. Cloud Providers
Suporte configurado para:
- **AWS**: boto3, Cost Explorer, Billing API
- **Azure**: azure-mgmt-consumption
- **Google Cloud**: google-cloud-billing, BigQuery
- **Oracle Cloud**: oci SDK

### 7. Testes
- pytest como framework
- Cobertura em `tests/`
- Testes de API, auth, modelos
- **Executar sempre**: `pytest` antes de finalizar

## Configurações Importantes
- `settings.local.json` - Configurações locais
- `podman-compose.yml` - Container orchestration
- `requirements.txt` - Dependências produção
- `requirements-dev.txt` - Dependências desenvolvimento

## Segurança
- Nunca commitar credentials
- Usar environment variables
- Secrets em `secrets_manager.py`
- Validação rigorosa de inputs

## Performance
- Cache Redis para dados frequentes
- Background tasks com Celery
- Otimização de queries SQL
- Paginação em endpoints

## Documentação Compartilhada
- Documentar APIs em `/shared/docs-backend/`
- Guias de desenvolvimento e integração
- Consultar `/shared/docs-frontend/` para entender necessidades

## Colaboração com Claude
- Claude trabalha exclusivamente no frontend
- Comunicação via documentação em `/shared/`
- Manter APIs estáveis para o frontend
- Documentar mudanças de contratos

## Fluxo de Trabalho
1. Analisar requisitos (incluindo prompts de integração do Claude)
2. Verificar testes existentes
3. Implementar sem quebrar APIs existentes
4. Executar suite de testes
5. Atualizar documentação se necessário
6. Verificar compatibilidade com frontend
7. **GERAR PROMPT DE INTEGRAÇÃO** para o usuário quando necessário

## Sistema de Prompts de Integração

### OBRIGATÓRIO: Processar prompts do Claude e gerar prompts de resposta

Quando você receber um prompt de integração do Claude (via usuário), você DEVE:

1. **Implementar** as necessidades do backend conforme especificado
2. **Testar** a implementação
3. **Gerar prompt de resposta** para o Claude quando necessário

### Formato do Prompt de Resposta para Claude:

```
=== PROMPT PARA CLAUDE (FRONTEND) ===

**Tarefa Completada**: [Descrição do que foi implementado no backend]

**Endpoint Implementado**:
- URL: `/api/exemplo`
- Método: [GET/POST/PUT/DELETE]
- Autenticação: [Bearer token/None]

**Request Body** (se aplicável):
```json
{
  "field1": "string",
  "field2": 123
}
```

**Response Body**:
```json
{
  "data": {
    "field1": "string",
    "field2": 123
  },
  "status": "success"
}
```

**Códigos de Status**:
- 200: Sucesso
- 400: Erro de validação
- 401: Não autorizado
- 404: Não encontrado
- 500: Erro interno

**Headers Necessários**:
- Content-Type: application/json
- Authorization: Bearer {token} (se aplicável)

**Validações Implementadas**:
- [Lista de validações ativas]

**Casos de Erro**:
- [Estrutura de resposta de erro]

**Testes Disponíveis**:
- [Endpoints de teste disponíveis]

**Arquivos Modificados**:
- [Lista de arquivos do backend modificados]

**Próximos Passos para Frontend**:
1. [Atualizar client HTTP se necessário]
2. [Atualizar tipos TypeScript]
3. [Implementar chamadas da API]
4. [Atualizar hooks se necessário]

===================================
```

### Situações que Requerem Prompt de Resposta:

1. **Implementação de nova API** solicitada pelo frontend
2. **Modificação de estrutura** de dados existente
3. **Mudança de autenticação** ou segurança
4. **Adição de validações** que afetam o frontend
5. **Alteração de endpoints** existentes

### Processamento de Prompts do Claude:

Quando receber um prompt do Claude:
1. **Analisar** todas as necessidades listadas
2. **Implementar** endpoints e lógica necessária
3. **Criar/atualizar** modelos de dados
4. **Adicionar** validações especificadas
5. **Escrever** testes para a funcionalidade
6. **Executar** todos os testes
7. **Gerar** prompt de resposta se necessário

## Debugging
- Logs estruturados com structlog
- Debug dashboard: `debug_dashboard.py`
- Monitoramento: prometheus-client
- Environment validation: `tests/validate_environment.py`