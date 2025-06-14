# Scripts de Configuração do Banco de Dados - X-Cost FinOps

Este diretório contém scripts para configurar e popular o banco de dados PostgreSQL com dados de teste para a aplicação X-Cost FinOps.

## 📋 Scripts Disponíveis

### 1. `setup_postgres.py`
Configura o ambiente PostgreSQL básico:
- ✅ Verifica conexão com PostgreSQL
- ✅ Cria banco de dados se não existir
- ✅ Cria schema `finops`
- ✅ Cria todas as tabelas necessárias
- ✅ Insere provedores de nuvem padrão
- ✅ Verifica integridade da estrutura

### 2. `populate_database.py`
Popula o banco com dados de teste realistas:
- 👥 **5 usuários** com diferentes roles (admin, finops_admin, operator, viewer)
- 🔐 **4 credenciais** de cloud providers (AWS, Azure, GCP)
- 💰 **3.000+ registros de custo** FOCUS (últimos 90 dias)
- 📊 **30 análises de custo** (trends, deltas, forecasts)
- 💼 **5 budgets** de exemplo
- 📝 Logs de auditoria (desabilitado temporariamente)

### 3. `setup_database.sh`
Script bash que executa todo o processo automaticamente:
- 🔍 Verifica dependências
- 🐘 Verifica PostgreSQL
- ⚙️ Executa setup
- 📊 Popula dados
- ✅ Verifica resultado final

## 🚀 Como Usar

### Método 1: Script Automático (Recomendado)
```bash
# Do diretório backend/
./scripts/setup_database.sh
```

### Método 2: Execução Manual
```bash
# 1. Iniciar PostgreSQL (usando podman-compose)
podman-compose up -d postgres

# 2. Configurar estrutura do banco
python scripts/setup_postgres.py

# 3. Popular com dados de teste
python scripts/populate_database.py
```

## 🐘 Configuração do PostgreSQL

### Usando Podman/Docker Compose
```bash
# O projeto já tem um podman-compose.yml configurado
podman-compose up -d postgres
```

### Configuração Manual (Docker)
```bash
docker run -d --name postgres-finops \
  -e POSTGRES_USER=finops_user \
  -e POSTGRES_PASSWORD=finops_password \
  -e POSTGRES_DB=finops_db \
  -p 5432:5432 \
  postgres:15
```

### Instalação Local (Ubuntu/Debian)
```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres createuser finops_user
sudo -u postgres createdb finops_db
```

## 🔧 Configuração de Ambiente

### Variáveis de Ambiente Suportadas
```bash
# Configuração do PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=finops_user
export POSTGRES_PASSWORD=finops_password
export POSTGRES_DB=finops_db

# URL completa (alternativa)
export DATABASE_URL="postgresql://finops_user:finops_password@localhost:5432/finops_db"
```

## 👥 Usuários de Teste Criados

| Username | Password | Role | Descrição |
|----------|----------|------|-----------|
| `admin` | `AdminPass123!` | `admin` | Administrador do sistema |
| `finops_manager` | `ManagerPass123!` | `finops_admin` | Gerente FinOps |
| `cloud_operator` | `OperatorPass123!` | `operator` | Operador de nuvem |
| `cost_viewer` | `ViewerPass123!` | `viewer` | Visualizador de custos |
| `demo_user` | `DemoPass123!` | `viewer` | Usuário demo |

## 🔐 Credenciais de Cloud Providers

O script cria credenciais de exemplo para:
- **AWS Production Account** (us-east-1)
- **AWS Development Account** (us-west-2)  
- **Azure Production Subscription**
- **GCP Production Project**

> ⚠️ **Nota**: As credenciais são fictícias e armazenadas como referências no AWS Secrets Manager.

## 💰 Dados de Custo FOCUS

O script gera dados realistas seguindo o padrão FOCUS:
- **Período**: Últimos 90 dias
- **Registros**: ~3.000 por execução
- **Provedores**: AWS, Azure, GCP
- **Serviços**: EC2, S3, RDS, Virtual Machines, Storage, etc.
- **Regiões**: Múltiplas regiões por provider
- **Custos**: Entre $1-500 por registro
- **Tags**: Environment, Team, Project, Owner

## 📊 Análises e Budgets

### Análises de Custo
- **30 análises** com tipos: trend, delta, forecast
- Métricas calculadas: custo total, média diária, tendências
- Confidence levels e versioning

### Budgets
- **AWS Production Monthly**: $50.000
- **Azure Development Quarterly**: $15.000  
- **AWS EC2 Monthly**: $20.000
- **GCP Storage Annual**: $12.000
- **Multi-Cloud AI/ML Annual**: $100.000

## 🔍 Verificação dos Dados

Após executar os scripts, você pode verificar os dados:

```sql
-- Conectar ao PostgreSQL
psql -h localhost -U finops_user -d finops_db

-- Verificar usuários
SELECT username, role, email, is_active FROM finops.users;

-- Verificar credenciais
SELECT name, provider_type, status, account_id FROM finops.cloud_credential_configs;

-- Verificar dados de custo
SELECT 
    provider_name, 
    service_name, 
    COUNT(*) as records,
    SUM(effective_cost) as total_cost
FROM finops.focus_cost_data 
GROUP BY provider_name, service_name
ORDER BY total_cost DESC;

-- Verificar budgets
SELECT budget_name, budget_amount, budget_period, alert_threshold 
FROM finops.budgets;
```

## 📚 Estrutura do Banco

### Schema: `finops`
- `users` - Usuários do sistema
- `cloud_credential_configs` - Configurações de credenciais
- `cloud_providers` - Provedores de nuvem disponíveis
- `focus_cost_data` - Dados de custo FOCUS
- `cost_analysis` - Análises de custo calculadas
- `budgets` - Budgets configurados
- `credential_audit_logs` - Logs de auditoria

## 🐛 Troubleshooting

### Erro de Conexão PostgreSQL
```bash
# Verificar se PostgreSQL está rodando
podman ps | grep postgres

# Verificar logs
podman logs finops_postgres

# Reiniciar container
podman-compose restart postgres
```

### Erro de Dependências Python
```bash
# Instalar dependências
pip install -r requirements-dev.txt

# Especificamente para PostgreSQL
pip install psycopg2-binary
```

### Tabelas já Existem
Os scripts verificam a existência de dados antes de criar:
- Usuários existentes são pulados
- Credenciais existentes são puladas  
- Dados de custo são sempre regenerados
- Para limpar tudo: `DROP SCHEMA finops CASCADE;`

## 🔄 Regeneração de Dados

Para regenerar apenas os dados de custo:
```bash
# Limpar dados de custo existentes
psql -h localhost -U finops_user -d finops_db -c "DELETE FROM finops.focus_cost_data;"

# Executar apenas a população de custos
python -c "
from scripts.populate_database import *
engine, session = create_database_connection()
create_focus_cost_data(session)
session.close()
"
```

## 🌐 Próximos Passos

Após popular o banco:

1. **Iniciar o Backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Acessar Documentação da API**:
   http://localhost:8000/docs

3. **Iniciar o Frontend** (se disponível):
   ```bash
   cd ../frontend
   npm run dev
   ```

4. **Testar Login**:
   Use qualquer um dos usuários criados para fazer login na aplicação.

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique os logs do PostgreSQL
2. Confirme as variáveis de ambiente
3. Execute os scripts individuais para isolar o problema
4. Verifique se todas as dependências estão instaladas
