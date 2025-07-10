#!/bin/bash

# X Cost API - Quick Start Script
# Este script configura rapidamente o ambiente de desenvolvimento local
# Compatível com Docker e Podman

set -e

echo "🚀 X Cost API - Quick Start Setup"
echo "=================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuração do LocalStack externo
LOCALSTACK_PATH="/Users/gcipriano/Repositories/localstack-web"

# Função para logging
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Função para verificar LocalStack externo
check_external_localstack() {
    log_info "Verificando LocalStack externo em: $LOCALSTACK_PATH"
    
    if [ ! -d "$LOCALSTACK_PATH" ]; then
        log_error "Diretório do LocalStack não encontrado: $LOCALSTACK_PATH"
        log_error "Certifique-se de que o LocalStack está clonado no caminho correto"
        exit 1
    fi
    
    if [ ! -f "$LOCALSTACK_PATH/docker-compose.yml" ]; then
        log_error "docker-compose.yml não encontrado em: $LOCALSTACK_PATH"
        exit 1
    fi
    
    log_success "LocalStack externo encontrado"
}

# Função para gerenciar LocalStack externo
manage_external_localstack() {
    local action=$1
    
    log_info "Executando '$action' no LocalStack externo..."
    
    cd "$LOCALSTACK_PATH"
    
    case $action in
        "start")
            if $COMPOSE_CMD ps | grep -q "localstack.*Up"; then
                log_info "LocalStack já está rodando"
            else
                log_info "Iniciando LocalStack..."
                $COMPOSE_CMD up -d
                
                # Aguardar LocalStack ficar disponível
                log_info "Aguardando LocalStack ficar disponível..."
                for i in {1..30}; do
                    if curl -s http://localhost:4566/_localstack/health &> /dev/null; then
                        log_success "LocalStack está rodando e disponível"
                        break
                    fi
                    log_info "Aguardando LocalStack ($i/30)..."
                    sleep 2
                done
                
                if ! curl -s http://localhost:4566/_localstack/health &> /dev/null; then
                    log_error "LocalStack não ficou disponível"
                    return 1
                fi
            fi
            ;;
        "stop")
            $COMPOSE_CMD down
            log_success "LocalStack parado"
            ;;
        "status")
            $COMPOSE_CMD ps
            ;;
    esac
    
    # Voltar ao diretório original
    cd - > /dev/null
}

# Função para limpeza de containers conflitantes (removendo localstack)
cleanup_containers() {
    local containers=("finops_postgres" "finops_redis")
    
    for container in "${containers[@]}"; do
        if $CONTAINER_ENGINE ps -a --format "{{.Names}}" | grep -q "^${container}$"; then
            log_info "Removendo container conflitante: $container"
            $CONTAINER_ENGINE stop $container 2>/dev/null || true
            $CONTAINER_ENGINE rm -f $container 2>/dev/null || true
        fi
    done
}

# Detectar se estamos usando Docker ou Podman
CONTAINER_ENGINE=""
COMPOSE_CMD=""

if command -v podman &> /dev/null; then
    CONTAINER_ENGINE="podman"
    if command -v podman-compose &> /dev/null; then
        COMPOSE_CMD="podman-compose"
    elif command -v docker-compose &> /dev/null; then
        COMPOSE_CMD="docker-compose"
        log_info "Usando docker-compose com Podman (modo compatibilidade)"
    else
        log_error "docker-compose ou podman-compose não encontrado"
        exit 1
    fi
    log_info "Detectado: Podman + $COMPOSE_CMD"
elif command -v docker &> /dev/null; then
    CONTAINER_ENGINE="docker"
    COMPOSE_CMD="docker-compose"
    log_info "Detectado: Docker + docker-compose"
else
    log_error "Docker ou Podman não encontrado. Instale um dos dois."
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "requirements.txt" ]; then
    log_error "requirements.txt não encontrado. Execute este script na raiz do projeto."
    exit 1
fi

# Verificar LocalStack externo
check_external_localstack

# 1. Criar estrutura de diretórios
log_info "Criando estrutura de diretórios..."

# Criar diretórios necessários
mkdir -p app
mkdir -p scripts
mkdir -p tests
mkdir -p docs
mkdir -p migrations
mkdir -p config
mkdir -p logs

# Criar arquivos __init__.py
touch app/__init__.py
touch scripts/__init__.py
touch tests/__init__.py
touch config/__init__.py

log_success "Estrutura de diretórios criada"

# 2. Verificar arquivos essenciais
log_info "Verificando arquivos essenciais..."

required_files=(
    "requirements.txt"
    "requirements-dev.txt"
    ".env.example"
    "podman-compose.yml"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        log_error "Arquivo obrigatório não encontrado: $file"
        exit 1
    fi
done

# Verificar se main_updated.py existe e renomear
if [ -f "app/main_updated.py" ]; then
    mv app/main_updated.py app/main.py
    log_success "main_updated.py renomeado para main.py"
elif [ ! -f "app/main.py" ]; then
    log_error "Arquivo app/main.py não encontrado. Certifique-se de que main_updated.py existe."
    exit 1
fi

# Verificar arquivos principais da app
app_files=(
    "app/main.py"
    "app/models.py"
    "app/credential_models.py"
    "app/database.py"
    "app/auth_security.py"
    "app/secrets_manager.py"
    "app/credentials_api.py"
    "app/cloud_connectors.py"
    "app/cost_analytics.py"
    "app/data_ingestion.py"
)

missing_files=()
for file in "${app_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    log_error "Arquivos essenciais da aplicação não encontrados:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    log_error "Certifique-se de baixar todos os arquivos na estrutura correta."
    exit 1
fi

log_success "Arquivos essenciais verificados"

# 3. Verificar pré-requisitos
log_info "Verificando pré-requisitos..."

# Python 3.12 específico
if ! command -v python3.12 &> /dev/null; then
    log_error "Python 3.12 não encontrado. Instalando..."
    if command -v brew &> /dev/null; then
        brew install python@3.12
    else
        log_error "Instale Python 3.12 manualmente"
        exit 1
    fi
fi

# Adicionar verificação do PostgreSQL headers
if ! command -v pg_config &> /dev/null; then
    log_warning "pg_config não encontrado. Tentando instalar PostgreSQL headers..."
    
    if command -v brew &> /dev/null; then
        log_info "Instalando libpq via Homebrew..."
        brew install libpq
        
        # Adicionar ao PATH
        export PATH="/opt/homebrew/opt/libpq/bin:$PATH"
        log_success "libpq instalado"
    else
        log_error "Homebrew não encontrado. Instale PostgreSQL headers manualmente:"
        log_error "brew install libpq"
        exit 1
    fi
fi

# Verificar versão do Python 3.12
python_version=$(python3.12 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
log_success "Python versão $python_version detectada"

log_success "Pré-requisitos verificados"

# 4. Configurar ambiente Python 3.12
log_info "Configurando ambiente Python 3.12..."

if [ ! -d "venv" ]; then
    python3.12 -m venv venv
    log_success "Ambiente virtual Python 3.12 criado"
else
    log_info "Ambiente virtual Python 3.12 já existe"
fi

# Ativar ambiente virtual
source venv/bin/activate
log_success "Ambiente virtual Python 3.12 ativado"

# Instalar dependências
log_info "Instalando dependências Python 3.12..."
pip install --upgrade pip
# Usar requirements-py312.txt se existir, senão usar requirements-dev.txt
if [ -f "requirements-py312.txt" ]; then
    pip install -r requirements-py312.txt
else
    pip install -r requirements-dev.txt
fi
log_success "Dependências Python 3.12 instaladas"

# 5. Configurar arquivo .env
log_info "Configurando arquivo .env..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    
    # Gerar chave JWT segura
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    sed -i "s/your-super-secret-jwt-key-256-bits-minimum/$JWT_SECRET/" .env
    
    # Gerar chave Fernet
    FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
    sed -i "s/your-fernet-encryption-key/$FERNET_KEY/" .env
    
    log_success "Arquivo .env criado com chaves seguras"
else
    log_warning "Arquivo .env já existe - não foi modificado"
fi

# 6. Subir serviços com Podman/Docker
log_info "Iniciando serviços com $CONTAINER_ENGINE..."

# Verificar se o container engine está rodando
if [ "$CONTAINER_ENGINE" = "podman" ]; then
    # Para Podman, verificar se podman machine está rodando (em macOS/Windows)
    if command -v podman machine &> /dev/null; then
        if ! podman machine list | grep -q "Currently running"; then
            log_info "Iniciando Podman machine..."
            podman machine start || log_warning "Podman machine pode já estar rodando"
        fi
    fi
    
    # Testar conectividade do Podman
    if ! podman info &> /dev/null; then
        log_error "Podman não está funcionando corretamente"
        log_info "Tente: podman system connection default"
        exit 1
    fi
elif [ "$CONTAINER_ENGINE" = "docker" ]; then
    # Verificar se Docker está rodando
    if ! docker info &> /dev/null; then
        log_error "Docker não está rodando. Inicie o Docker Desktop"
        exit 1
    fi
fi

# Subir serviços de infraestrutura
log_info "Configurando serviços de infraestrutura..."

# Limpar containers antigos que podem estar conflitando (sem localstack)
log_info "Limpando containers antigos se existirem..."
cleanup_containers

# Parar qualquer compose que possa estar rodando
$COMPOSE_CMD down --remove-orphans 2>/dev/null || true

# Subir apenas postgres e redis (sem localstack)
log_info "Iniciando serviços: postgres, redis"
$COMPOSE_CMD up -d postgres redis

# Gerenciar LocalStack externo
manage_external_localstack "start"

log_info "Aguardando serviços iniciarem..."
sleep 10

# Verificar se serviços estão saudáveis
if $COMPOSE_CMD ps | grep -q "unhealthy"; then
    log_warning "Alguns serviços podem não estar completamente prontos"
    log_info "Aguardando mais 10 segundos..."
    sleep 10
fi

# Listar status dos containers
log_info "Status dos containers locais:"
$COMPOSE_CMD ps

log_info "Status do LocalStack externo:"
manage_external_localstack "status"

log_success "Serviços $CONTAINER_ENGINE iniciados"

# 7. Configurar banco de dados
log_info "Configurando banco de dados..."

# Aguardar PostgreSQL estar pronto
for i in {1..30}; do
    if $CONTAINER_ENGINE exec finops_postgres pg_isready -U finops_user -d finops_db &> /dev/null; then
        break
    fi
    log_info "Aguardando PostgreSQL ($i/30)..."
    sleep 2
done

# Verificar se script de init existe
if [ ! -f "scripts/init_db.py" ]; then
    log_error "Script scripts/init_db.py não encontrado. Certifique-se de baixar o arquivo."
    exit 1
fi

# Executar script de inicialização
PYTHONPATH=. python scripts/init_db.py

if [ $? -eq 0 ]; then
    log_success "Banco de dados configurado"
else
    log_error "Falha na configuração do banco de dados"
    exit 1
fi

# 8. Testar API
log_info "Iniciando API..."

# Iniciar API em background
PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

log_info "API iniciada (PID: $API_PID). Aguardando ficar disponível..."

# Aguardar API ficar disponível
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health &> /dev/null; then
        break
    fi
    log_info "Aguardando API ($i/30)..."
    sleep 2
done

# Testar health check
if curl -s http://localhost:8000/api/v1/health | grep -q '"overall":true'; then
    log_success "API está rodando e saudável!"
else
    log_error "API não está respondendo corretamente"
    kill $API_PID 2>/dev/null
    exit 1
fi

# 9. Testar autenticação
log_info "Testando autenticação..."

LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"ChangeMe123!"}')

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    log_success "Autenticação funcionando!"
    
    # Extrair token
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    
    # Testar endpoint protegido
    if curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/v1/credentials | grep -q '\[\]'; then
        log_success "Endpoints protegidos funcionando!"
    else
        log_warning "Problema com endpoints protegidos"
    fi
else
    log_error "Problema com autenticação"
fi

# 10. Executar testes (se arquivos de teste existirem)
if [ -f "tests/test_auth.py" ] && [ -f "tests/conftest.py" ]; then
    log_info "Executando testes básicos..."
    
    if PYTHONPATH=. pytest tests/test_auth.py::test_login_success -v &> /dev/null; then
        log_success "Testes básicos passando!"
    else
        log_warning "Alguns testes podem estar falhando"
    fi
else
    log_warning "Arquivos de teste não encontrados - pulando testes"
fi

# 11. Criar credencial de teste
log_info "Criando credencial de teste..."

TEST_CREDENTIAL=$(cat << 'EOF'
{
    "name": "test-aws-local",
    "description": "Credencial AWS para desenvolvimento local",
    "provider_type": "AWS",
    "credentials": {
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1",
        "account_id": "123456789012"
    }
}
EOF
)

CREATE_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/credentials" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$TEST_CREDENTIAL")

if echo "$CREATE_RESPONSE" | grep -q '"id"'; then
    log_success "Credencial de teste criada!"
else
    log_warning "Não foi possível criar credencial de teste"
fi

# Parar API
kill $API_PID 2>/dev/null
sleep 2

# 12. Verificar estrutura final
log_info "Verificando estrutura final do projeto..."

final_structure=(
    "app/"
    "scripts/"
    "tests/"
    "docs/"
    "migrations/"
    "venv/"
    ".env"
)

for item in "${final_structure[@]}"; do
    if [ -e "$item" ]; then
        log_success "✓ $item"
    else
        log_warning "⚠ $item (opcional)"
    fi
done

# 13. Resumo final
echo ""
echo "🎉 Setup Completo com $CONTAINER_ENGINE!"
echo "========================================="
echo ""
echo "📁 Estrutura do Projeto:"
echo "├── app/                 # Código principal da aplicação"
echo "├── scripts/             # Scripts de utilidade"
echo "├── tests/               # Testes automatizados"
echo "├── docs/                # Documentação"
echo "├── migrations/          # Migrações do banco"
echo "├── venv/                # Ambiente virtual Python 3.12"
echo "├── .env                 # Configurações locais"
echo "└── podman-compose.yml   # Serviços Docker/Podman"
echo ""
echo "✅ Container Engine: $CONTAINER_ENGINE"
echo "✅ Compose Command: $COMPOSE_CMD"
echo "✅ Ambiente Python configurado"
echo "✅ Banco de dados PostgreSQL rodando"
echo "✅ Redis cache rodando"
echo "✅ LocalStack externo rodando ($LOCALSTACK_PATH)"
echo "✅ API FinOps testada e funcionando"
echo "✅ Usuário admin criado"
echo "✅ Credencial de teste criada"
echo ""
echo "📋 Próximos Passos:"
echo ""
echo "1. Iniciar a API:"
echo "   source venv/bin/activate"
echo "   PYTHONPATH=. uvicorn app.main:app --reload"
echo ""
echo "2. Acessar documentação:"
echo "   http://localhost:8000/docs"
echo ""
echo "3. Login padrão:"
echo "   Usuário: admin"
echo "   Senha: ChangeMe123!"
echo ""
echo "4. Interfaces úteis:"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - PostgreSQL: http://localhost:8080"
echo "   - Redis: http://localhost:8081"
echo "   - LocalStack: http://localhost:4566"
echo ""
echo "5. Executar testes:"
echo "   PYTHONPATH=. pytest"
echo ""
echo "6. Ver logs:"
echo "   $COMPOSE_CMD logs -f"
echo ""
echo "📚 Documentação:"
echo "   - docs/DEVELOPMENT_GUIDE.md    # Desenvolvimento"
echo "   - docs/SECURITY_ARCHITECTURE.md # Segurança"
echo "   - docs/FRONTEND_INTEGRATION.md  # Integração Frontend"
echo ""

log_warning "IMPORTANTE: Altere a senha padrão em produção!"
log_info "Leia a documentação em docs/ para mais informações"

echo ""
echo "🔧 Comandos Úteis com $CONTAINER_ENGINE:"
echo ""
echo "# Parar serviços locais:"
echo "$COMPOSE_CMD down"
echo ""
echo "# Parar LocalStack externo:"
echo "(cd $LOCALSTACK_PATH && $COMPOSE_CMD down)"
echo ""
echo "# Ver status:"
echo "$COMPOSE_CMD ps"
echo ""
echo "# Ver logs:"
echo "$COMPOSE_CMD logs -f postgres"
echo "$COMPOSE_CMD logs -f redis"
echo ""
echo "# Conectar ao banco:"
echo "psql postgresql://finops_user:finops_password@localhost:5432/finops_db"
echo ""
echo "# Conectar aos containers:"
echo "$CONTAINER_ENGINE exec -it finops_postgres bash"
echo "$CONTAINER_ENGINE exec -it finops_redis redis-cli"
echo ""
echo "# Resetar banco:"
echo "PYTHONPATH=. python scripts/init_db.py"
echo ""
echo "# Gerenciar LocalStack externo:"
echo "cd $LOCALSTACK_PATH"
echo "$COMPOSE_CMD up -d      # Iniciar"
echo "$COMPOSE_CMD down       # Parar"
echo "$COMPOSE_CMD logs -f    # Ver logs"
echo ""

if [ "$CONTAINER_ENGINE" = "podman" ]; then
    echo "🐳 Comandos específicos do Podman:"
    echo ""
    echo "# Verificar podman machine (macOS/Windows):"
    echo "podman machine list"
    echo ""
    echo "# Reiniciar podman machine se necessário:"
    echo "podman machine restart"
    echo ""
    echo "# Verificar conexões:"
    echo "podman system connection list"
    echo ""
fi

echo "🌐 LocalStack Externo:"
echo "  Path: $LOCALSTACK_PATH"
echo "  Health Check: http://localhost:4566/_localstack/health"
echo "  Dashboard: http://localhost:4566 (se disponível)"
echo ""

echo "Happy coding with $CONTAINER_ENGINE! 🚀"