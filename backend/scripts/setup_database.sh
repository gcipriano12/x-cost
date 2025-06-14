#!/bin/bash
# Script para configurar e popular o banco PostgreSQL com dados de teste
# para a aplicação X-Cost FinOps

set -e  # Parar em caso de erro

echo "🚀 X-Cost FinOps - Configuração do Banco de Dados"
echo "=================================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se o Python está disponível
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 não encontrado. Instale o Python 3.8+ primeiro."
        exit 1
    fi
    print_success "Python3 encontrado: $(python3 --version)"
}

# Verificar se as dependências Python estão instaladas
check_dependencies() {
    print_status "Verificando dependências Python..."
    
    if ! python3 -c "import sqlalchemy, psycopg2" &> /dev/null; then
        print_warning "Dependências faltando. Instalando..."
        pip install -r requirements-dev.txt
    fi
    
    print_success "Dependências verificadas"
}

# Verificar se o PostgreSQL está rodando
check_postgres() {
    print_status "Verificando PostgreSQL..."
    
    # Tentar conectar ao PostgreSQL
    if python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        user=os.getenv('POSTGRES_USER', 'finops_user'),
        password=os.getenv('POSTGRES_PASSWORD', 'finops_pass'),
        database='postgres'
    )
    conn.close()
    print('OK')
except:
    print('FAIL')
" | grep -q "OK"; then
        print_success "PostgreSQL está acessível"
        return 0
    else
        print_error "PostgreSQL não está acessível"
        print_warning "Configure o PostgreSQL primeiro:"
        echo ""
        echo "  🐳 Com Docker:"
        echo "    docker run -d --name postgres-finops \\"
        echo "      -e POSTGRES_USER=finops_user \\"
        echo "      -e POSTGRES_PASSWORD=finops_pass \\"
        echo "      -e POSTGRES_DB=finops_db \\"
        echo "      -p 5432:5432 \\"
        echo "      postgres:14"
        echo ""
        echo "  🐙 Com Podman (se disponível no projeto):"
        echo "    podman-compose up -d postgres"
        echo ""
        echo "  📦 Instalação local (Ubuntu/Debian):"
        echo "    sudo apt install postgresql postgresql-contrib"
        echo "    sudo -u postgres createuser finops_user"
        echo "    sudo -u postgres createdb finops_db"
        echo ""
        return 1
    fi
}

# Executar setup do PostgreSQL
setup_postgres() {
    print_status "Executando setup do PostgreSQL..."
    
    if python3 scripts/setup_postgres.py; then
        print_success "Setup do PostgreSQL concluído"
        return 0
    else
        print_error "Falha no setup do PostgreSQL"
        return 1
    fi
}

# Popular banco com dados de teste
populate_database() {
    print_status "Populando banco com dados de teste..."
    
    if python3 scripts/populate_database.py; then
        print_success "Banco populado com sucesso"
        return 0
    else
        print_error "Falha ao popular banco"
        return 1
    fi
}

# Verificar estrutura final
verify_setup() {
    print_status "Verificando setup final..."
    
    # Verificar número de registros criados
    python3 -c "
import os
import sys
from pathlib import Path
sys.path.append(str(Path('.').resolve()))

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://finops_user:finops_pass@localhost:5432/finops_db')

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        tables = [
            ('users', 'Usuários'),
            ('cloud_credentials', 'Credenciais'),
            ('focus_cost_data', 'Dados de Custo'),
            ('cost_analysis', 'Análises'),
            ('budgets', 'Budgets'),
            ('audit_logs', 'Logs de Auditoria')
        ]
        
        print('📊 Resumo dos dados no banco:')
        print('=' * 40)
        total_records = 0
        
        for table, name in tables:
            try:
                result = conn.execute(text(f'SELECT COUNT(*) FROM finops.{table}'))
                count = result.scalar()
                total_records += count
                print(f'  {name}: {count:,} registros')
            except Exception as e:
                print(f'  {name}: erro ao contar - {e}')
        
        print('=' * 40)
        print(f'  Total: {total_records:,} registros')
        
except Exception as e:
    print(f'❌ Erro ao verificar dados: {e}')
    sys.exit(1)
"
    
    print_success "Verificação concluída"
}

# Imprimir informações finais
print_final_info() {
    echo ""
    echo "🎉 Configuração Concluída!"
    echo "=========================="
    echo ""
    echo "📋 Dados de teste criados:"
    echo "  • Usuários com diferentes roles"
    echo "  • Credenciais de cloud providers"
    echo "  • Dados de custo FOCUS (90 dias)"
    echo "  • Análises de custo"
    echo "  • Budgets de exemplo"
    echo "  • Logs de auditoria"
    echo ""
    echo "🔑 Credenciais para teste:"
    echo "  • Admin: admin / AdminPass123!"
    echo "  • FinOps Manager: finops_manager / ManagerPass123!"
    echo "  • Operator: cloud_operator / OperatorPass123!"
    echo "  • Viewer: cost_viewer / ViewerPass123!"
    echo "  • Demo: demo_user / DemoPass123!"
    echo ""
    echo "🌐 Para iniciar a aplicação:"
    echo "  • Backend: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
    echo "  • Frontend: cd ../frontend && npm run dev"
    echo ""
    echo "📚 URLs úteis:"
    echo "  • API Docs: http://localhost:8000/docs"
    echo "  • Frontend: http://localhost:3000"
    echo ""
}

# Função principal
main() {
    echo ""
    print_status "Iniciando configuração..."
    
    # Verificações preliminares
    check_python
    check_dependencies
    
    # Verificar PostgreSQL
    if ! check_postgres; then
        exit 1
    fi
    
    # Setup e população
    if setup_postgres; then
        if populate_database; then
            verify_setup
            print_final_info
            print_success "✅ Configuração completa!"
        else
            print_error "❌ Falha na população do banco"
            exit 1
        fi
    else
        print_error "❌ Falha no setup do PostgreSQL"
        exit 1
    fi
}

# Verificar se script está sendo executado do diretório correto
if [[ ! -f "scripts/setup_postgres.py" ]]; then
    print_error "Execute este script do diretório backend/"
    print_warning "cd backend && ./scripts/setup_database.sh"
    exit 1
fi

# Executar função principal
main "$@"
