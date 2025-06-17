#!/bin/bash
# Script para iniciar X-Cost API com LocalStack
# Uso: ./start_localstack.sh

echo "🚀 Iniciando X-Cost API com LocalStack..."

# Configurar variáveis de ambiente para LocalStack
export ENVIRONMENT=development
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=test
export AWS_SECRET_ACCESS_KEY=test

# Configurações adicionais
export JWT_SECRET_KEY=dev-secret-key-localstack
export DATABASE_URL=sqlite:///./x-cost-localstack.db

echo "✅ Variáveis de ambiente configuradas:"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   AWS_ENDPOINT_URL: $AWS_ENDPOINT_URL"
echo "   AWS_REGION: $AWS_REGION"

echo ""
echo "📋 Para verificar se LocalStack está rodando:"
echo "   curl http://localhost:4566/health"

echo ""
echo "🔥 Iniciando aplicação..."
python -m uvicorn app.main:app --reload --port 8000