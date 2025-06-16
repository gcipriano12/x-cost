#!/bin/bash
"""
Script completo para testar o backend local com LocalStack
"""

set -e

echo "🚀 Configurando ambiente de teste completo"
echo "=========================================="

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
echo "🔍 Verificando dependências..."

if ! command_exists podman-compose; then
    echo "❌ podman-compose não encontrado"
    echo "   Instale com: brew install podman-compose"
    exit 1
fi

if ! command_exists python3; then
    echo "❌ python3 não encontrado"
    exit 1
fi

echo "✅ Dependências verificadas"

# Configurar ambiente
echo "⚙️ Configurando variáveis de ambiente..."
cp .env.localstack .env
echo "✅ Arquivo .env configurado para LocalStack"

# Iniciar serviços com podman-compose
echo "🐳 Iniciando serviços (PostgreSQL, Redis, LocalStack)..."
podman-compose up -d postgres redis localstack

# Aguardar serviços estarem prontos
echo "⏳ Aguardando serviços estarem prontos..."
sleep 10

# Verificar se serviços estão rodando
echo "🔍 Verificando status dos serviços..."

if ! curl -s http://localhost:4566/_localstack/health >/dev/null; then
    echo "❌ LocalStack não está respondendo"
    echo "   Logs do LocalStack:"
    podman-compose logs localstack | tail -10
    exit 1
fi

if ! curl -s http://localhost:6379 >/dev/null 2>&1; then
    if ! redis-cli ping >/dev/null 2>&1; then
        echo "❌ Redis não está respondendo"
        exit 1
    fi
fi

echo "✅ Serviços estão rodando"

# Popular LocalStack com dados
echo "📊 Populando LocalStack com dados de teste..."
python3 populate_localstack.py

# Instalar dependências Python se necessário
echo "📦 Verificando dependências Python..."
if ! python3 -c "import boto3" 2>/dev/null; then
    echo "   Instalando boto3..."
    pip3 install boto3
fi

if ! python3 -c "import requests" 2>/dev/null; then
    echo "   Instalando requests..."
    pip3 install requests
fi

# Iniciar backend em background
echo "🖥️ Iniciando backend..."
export PYTHONPATH="$PWD:$PYTHONPATH"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Aguardar backend estar pronto
echo "⏳ Aguardando backend estar pronto..."
sleep 15

# Verificar se backend está rodando
if ! curl -s http://localhost:8000/health >/dev/null; then
    echo "❌ Backend não está respondendo"
    echo "   Tentando iniciar novamente..."
    sleep 5
    if ! curl -s http://localhost:8000/health >/dev/null; then
        echo "❌ Backend falhou ao iniciar"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
fi

echo "✅ Backend está rodando"

# Executar testes
echo "🧪 Executando testes do backend local..."
python3 test_backend_local.py

# Limpeza opcional
echo ""
echo "🎉 Testes concluídos!"
echo ""
echo "📋 Serviços rodando:"
echo "   - Backend: http://localhost:8000"
echo "   - LocalStack: http://localhost:4566"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "🔗 Endpoints para testar manualmente:"
echo "   - http://localhost:8000/docs (Swagger UI)"
echo "   - http://localhost:8000/api/v1/savings-opportunities"
echo "   - http://localhost:8000/api/v1/anomalies"
echo "   - http://localhost:8000/api/v1/optimization/summary"
echo ""
echo "🛑 Para parar os serviços:"
echo "   kill $BACKEND_PID"
echo "   podman-compose down"
echo ""
read -p "Pressione Enter para finalizar e parar os serviços..."

# Limpeza
echo "🧹 Parando serviços..."
kill $BACKEND_PID 2>/dev/null || true
podman-compose down

echo "✅ Limpeza concluída!"
