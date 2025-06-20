# Account Distribution Endpoint - Testes e Documentação

## Endpoint Implementado: `/api/v1/dashboard/account-distribution`

### Funcionalidade
Retorna a distribuição de custos por conta (billing_account_name) para um provedor específico de cloud.

### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição | Valores Aceitos |
|-----------|------|-------------|-----------|-----------------|
| provider | string | Sim | Nome do provedor cloud | AWS, Azure, GCP, Oracle, Oracle Cloud |
| time_filter | string | Não | Período de tempo | 30d, 90d, 365d, 1y, 12m (padrão: 30d) |
| credential_id | string | Não | ID da credencial específica | Qualquer string válida |
| top_n | integer | Não | Número máximo de contas | 1-50 (padrão: 10) |

### Estrutura de Resposta

```json
{
  "success": true,
  "data": [
    {
      "account_id": "string",
      "billing_account_name": "string", 
      "percentage": number,
      "total_cost": number
    }
  ],
  "metadata": {
    "timestamp": "string",
    "api_version": "string",
    "processing_time": number
  }
}
```

### Exemplos de Uso

#### 1. Buscar contas AWS dos últimos 30 dias
```bash
GET /api/v1/dashboard/account-distribution?provider=AWS&time_filter=30d
```

#### 2. Buscar top 5 contas Oracle dos últimos 90 dias
```bash
GET /api/v1/dashboard/account-distribution?provider=Oracle&time_filter=90d&top_n=5
```

#### 3. Buscar contas Azure do último ano
```bash
GET /api/v1/dashboard/account-distribution?provider=Azure&time_filter=1y
```

### Resultados dos Testes

#### ✅ Teste 1: AWS (30 dias)
```json
{
  "account_id": "123456789012",
  "billing_account_name": "AWS Production Account", 
  "percentage": 100.0,
  "total_cost": 29844.01
}
```

#### ✅ Teste 2: Azure (30 dias)
```json
{
  "account_id": "sub-12345678-1234-1234-1234-123456789012",
  "billing_account_name": "Azure Production Subscription",
  "percentage": 100.0, 
  "total_cost": 29732.85
}
```

#### ✅ Teste 3: GCP (30 dias)
```json
{
  "account_id": "012345-ABCDEF-678901",
  "billing_account_name": "GCP Production Project",
  "percentage": 100.0,
  "total_cost": 38872.74
}
```

#### ✅ Teste 4: Oracle (30 dias) - Múltiplas Contas
```json
[
  {
    "account_id": "ocid1.tenancy.oc1..dev987654321",
    "billing_account_name": "Oracle Development Tenancy",
    "percentage": 53.44,
    "total_cost": 345364.14
  },
  {
    "account_id": "ocid1.tenancy.oc1..prod123456789", 
    "billing_account_name": "Oracle Production Tenancy",
    "percentage": 46.56,
    "total_cost": 300960.63
  }
]
```

### Validações Implementadas

#### ✅ Validação de Provider
- **Entrada inválida**: `InvalidProvider`
- **Resposta**: 400 Bad Request
- **Mensagem**: "Provider inválido. Valores aceitos: AWS, Azure, GCP, Oracle, Oracle Cloud"

#### ✅ Validação de Time Filter
- **Entrada inválida**: `invalid`
- **Resposta**: 400 Bad Request  
- **Mensagem**: "time_filter inválido. Use formato como '30d', '90d', '12m', '1y'"

#### ✅ Validação de Top N
- **Range aceito**: 1-50
- **Comportamento**: Limita resultados ao número especificado

### Cálculos Validados

#### ✅ Soma de Percentuais = 100%
Para Oracle (2 contas): 53.44% + 46.56% = 100.0%

#### ✅ Ordenação por Custo
Contas são retornadas em ordem decrescente de custo total.

### Integração Frontend

#### ✅ Hook Implementado
- **Arquivo**: `frontend/src/hooks/useAccountDistribution.ts`
- **Funcionalidade**: Consome a API e gerencia estado

#### ✅ Componente Integrado
- **Arquivo**: `frontend/src/components/dashboard/RealTimeSpendSummaryCard.tsx`
- **Funcionalidade**: Exibe gráfico de pizza com distribuição de contas quando provedor é filtrado

### Status: ✅ IMPLEMENTAÇÃO COMPLETA

O endpoint está funcionando corretamente e integrado ao frontend. Quando um provedor específico é selecionado, o gráfico de pizza mostra a distribuição por contas desse provedor ao invés da distribuição geral por provedores.
