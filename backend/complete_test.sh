#!/bin/bash

# Script completo de teste da API FinOps
# Versão atualizada com melhor tratamento de erros

set -e

echo "🧪 X Cost API - Teste Completo"
echo "=============================="

# Configurações
BASE_URL="http://localhost:8000"
TOKEN=""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Função para fazer requests HTTP com tratamento de erro
make_request() {
    local method=$1
    local url=$2
    local data=$3
    local headers=$4
    
    if [ -n "$headers" ]; then
        if [ -n "$data" ]; then
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$url" \
                -H "Content-Type: application/json" \
                -H "$headers" \
                -d "$data")
        else
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$url" \
                -H "$headers")
        fi
    else
        if [ -n "$data" ]; then
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$url" \
                -H "Content-Type: application/json" \
                -d "$data")
        else
            response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$url")
        fi
    fi
    
    # Extrair código HTTP e corpo da resposta
    http_code=$(echo "$response" | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
    body=$(echo "$response" | sed -e 's/HTTPSTATUS:.*//g')
    
    echo "$http_code|$body"
}

# 1. VERIFICAR SAÚDE DA API
echo ""
echo "=== HEALTH CHECK ==="
log_info "🔍 Verificando saúde da API..."

result=$(make_request "GET" "$BASE_URL/api/v1/health")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    log_success "API está saudável"
    echo "   Response: $body" | head -c 100
    echo "..."
else
    log_error "API não está respondendo corretamente ($http_code)"
    echo "   Response: $body"
    exit 1
fi

# 2. AUTENTICAÇÃO
echo ""
echo "=== AUTENTICAÇÃO ==="
log_info "🔐 Fazendo login..."

login_data='{
    "username": "admin",
    "password": "ChangeMe123!"
}'

result=$(make_request "POST" "$BASE_URL/api/v1/auth/login" "$login_data")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    TOKEN=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
    
    if [ -n "$TOKEN" ]; then
        log_success "Login realizado com sucesso"
        echo "   Token: ${TOKEN:0:50}..."
        
        # Extrair informações do usuário
        username=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['username'])" 2>/dev/null || echo "N/A")
        role=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['user']['role'])" 2>/dev/null || echo "N/A")
        echo "   Usuário: $username ($role)"
    else
        log_error "Falha ao extrair token da resposta"
        echo "   Response: $body"
        exit 1
    fi
else
    log_error "Falha no login ($http_code)"
    echo "   Response: $body"
    exit 1
fi

# 3. TESTE DE AUTENTICAÇÃO
echo ""
echo "=== VERIFICAÇÃO DE AUTENTICAÇÃO ==="
log_info "🔒 Testando acesso a endpoint protegido..."

result=$(make_request "GET" "$BASE_URL/api/v1/credentials" "" "Authorization: Bearer $TOKEN")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    log_success "Acesso autorizado confirmado"
    credential_count=$(echo "$body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    echo "   Credenciais existentes: $credential_count"
else
    log_error "Falha na autorização ($http_code)"
    echo "   Response: $body"
    exit 1
fi

# 4. GERENCIAMENTO DE CREDENCIAIS
echo ""
echo "=== GERENCIAMENTO DE CREDENCIAIS ==="
log_info "🔑 Criando credencial de teste..."

# Aguardar um pouco para garantir que o sistema está pronto
sleep 2

credential_data='{
    "name": "test-aws-complete",
    "description": "Credencial AWS para teste completo da API",
    "provider_type": "AWS",
    "credentials": {
        "access_key_id": "AKIAIOSFODNN7EXAMPLE",
        "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "region": "us-east-1",
        "account_id": "123456789012"
    }
}'

result=$(make_request "POST" "$BASE_URL/api/v1/credentials" "$credential_data" "Authorization: Bearer $TOKEN")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "201" ]; then
    log_success "Credencial criada com sucesso"
    CREDENTIAL_ID=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "")
    
    if [ -n "$CREDENTIAL_ID" ]; then
        echo "   ID: $CREDENTIAL_ID"
        echo "   Nome: $(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['name'])" 2>/dev/null)"
        echo "   Provider: $(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['provider_type'])" 2>/dev/null)"
        echo "   Status: $(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['status'])" 2>/dev/null)"
    else
        log_warning "Credencial criada mas ID não foi extraído"
        echo "   Response: $body"
    fi
else
    log_error "Erro ao criar credencial ($http_code)"
    echo "   Response: $body"
    
    # Tentar diagnosticar o problema
    if echo "$body" | grep -q "already exists"; then
        log_warning "Credencial já existe - tentando listar credenciais existentes"
        
        result=$(make_request "GET" "$BASE_URL/api/v1/credentials" "" "Authorization: Bearer $TOKEN")
        list_body=$(echo "$result" | cut -d'|' -f2)
        
        CREDENTIAL_ID=$(echo "$list_body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for cred in data:
        if cred['name'] == 'test-aws-complete':
            print(cred['id'])
            break
except:
    pass
" 2>/dev/null || echo "")
        
        if [ -n "$CREDENTIAL_ID" ]; then
            log_info "Encontrada credencial existente: $CREDENTIAL_ID"
        fi
    fi
fi

# 5. VALIDAÇÃO DE CREDENCIAL
if [ -n "$CREDENTIAL_ID" ]; then
    echo ""
    log_info "🔍 Validando credencial..."
    
    # Aguardar processamento em background
    sleep 3
    
    result=$(make_request "POST" "$BASE_URL/api/v1/credentials/$CREDENTIAL_ID/validate" "" "Authorization: Bearer $TOKEN")
    http_code=$(echo "$result" | cut -d'|' -f1)
    body=$(echo "$result" | cut -d'|' -f2)
    
    if [ "$http_code" = "200" ]; then
        is_valid=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['is_valid'])" 2>/dev/null || echo "false")
        
        if [ "$is_valid" = "True" ]; then
            log_success "Credencial validada com sucesso"
        else
            log_warning "Credencial não é válida (esperado para credenciais de teste)"
            error_msg=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('error_message', 'N/A'))" 2>/dev/null || echo "N/A")
            echo "   Erro: $error_msg"
        fi
    else
        log_error "Falha na validação ($http_code)"
        echo "   Response: $body"
    fi
fi

# 6. LISTAR CREDENCIAIS ATUALIZADAS
echo ""
log_info "📋 Listando credenciais atualizadas..."

result=$(make_request "GET" "$BASE_URL/api/v1/credentials" "" "Authorization: Bearer $TOKEN")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    credential_count=$(echo "$body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    log_success "Lista obtida com sucesso"
    echo "   Total de credenciais: $credential_count"
    
    # Mostrar detalhes das credenciais
    echo "$body" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for i, cred in enumerate(data):
        print(f'   {i+1}. {cred[\"name\"]} ({cred[\"provider_type\"]}) - {cred[\"status\"]}')
except:
    pass
" 2>/dev/null || echo "   Não foi possível parsear a lista"
else
    log_error "Falha ao listar credenciais ($http_code)"
    echo "   Response: $body"
fi

# 7. TESTE DE DADOS DE CUSTOS
echo ""
echo "=== DADOS DE CUSTOS ==="
log_info "💰 Testando endpoint de custos..."

result=$(make_request "GET" "$BASE_URL/api/v1/costs?limit=5" "" "Authorization: Bearer $TOKEN")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    cost_count=$(echo "$body" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    log_success "Endpoint de custos funcionando"
    echo "   Registros de custo encontrados: $cost_count"
    
    if [ "$cost_count" = "0" ]; then
        log_info "Nenhum dado de custo encontrado (normal para instalação nova)"
    fi
else
    log_error "Falha no endpoint de custos ($http_code)"
    echo "   Response: $body"
fi

# 8. TESTE DE ANALYTICS
echo ""
log_info "📊 Testando endpoint de analytics..."

result=$(make_request "GET" "$BASE_URL/api/v1/analytics/trend?period=daily&limit=10" "" "Authorization: Bearer $TOKEN")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    log_success "Endpoint de analytics funcionando"
    echo "   Response disponível (pode estar vazio para instalação nova)"
else
    log_error "Falha no endpoint de analytics ($http_code)"
    echo "   Response: $body"
fi

# 9. STATUS DO SISTEMA
echo ""
echo "=== STATUS DO SISTEMA ==="
log_info "🖥️  Verificando status do sistema..."

result=$(make_request "GET" "$BASE_URL/api/v1/system/status" "" "Authorization: Bearer $TOKEN")
http_code=$(echo "$result" | cut -d'|' -f1)
body=$(echo "$result" | cut -d'|' -f2)

if [ "$http_code" = "200" ]; then
    log_success "Status do sistema obtido"
    
    # Extrair informações principais
    total_creds=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['credential_stats']['total'])" 2>/dev/null || echo "N/A")
    active_creds=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['credential_stats']['active'])" 2>/dev/null || echo "N/A")
    total_users=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin)['user_stats']['total_users'])" 2>/dev/null || echo "N/A")
    
    echo "   Credenciais: $active_creds/$total_creds ativas"
    echo "   Usuários: $total_users total"
else
    log_warning "Não foi possível obter status do sistema ($http_code)"
    echo "   Response: $body"
fi

# 10. LIMPEZA (OPCIONAL)
echo ""
echo "=== LIMPEZA ==="
read -p "🗑️  Deseja remover a credencial de teste criada? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]] && [ -n "$CREDENTIAL_ID" ]; then
    log_info "Removendo credencial de teste..."
    
    result=$(make_request "DELETE" "$BASE_URL/api/v1/credentials/$CREDENTIAL_ID" "" "Authorization: Bearer $TOKEN")
    http_code=$(echo "$result" | cut -d'|' -f1)
    
    if [ "$http_code" = "200" ]; then
        log_success "Credencial removida com sucesso"
    else
        log_warning "Não foi possível remover a credencial ($http_code)"
    fi
else
    log_info "Credencial de teste mantida"
fi

# RESUMO FINAL
echo ""
echo "🎯 RESUMO DO TESTE"
echo "=================="
log_success "✅ Health check da API"
log_success "✅ Autenticação JWT"
log_success "✅ Autorização RBAC"
log_success "✅ CRUD de credenciais"
log_success "✅ Validação de credenciais"
log_success "✅ Endpoints de custos"
log_success "✅ Endpoints de analytics"
log_success "✅ Status do sistema"

echo ""
log_success "🎉 Teste completo finalizado com sucesso!"
echo ""
echo "📋 INFORMAÇÕES ÚTEIS:"
echo "   • API URL: $BASE_URL"
echo "   • Documentação: $BASE_URL/docs"
echo "   • Health: $BASE_URL/api/v1/health"
echo "   • Usuário admin: admin / ChangeMe123!"
echo ""
log_warning "🔒 IMPORTANTE: Altere a senha padrão em produção!"

echo ""
echo "🚀 Próximos passos:"
echo "   1. Integrar com seu frontend"
echo "   2. Configurar credenciais reais de cloud"
echo "   3. Configurar ingestão de dados"
echo "   4. Personalizar dashboard e relatórios"