# 🚀 Prompt para Integração Dashboard no Lovable

## 📋 Contexto
Preciso integrar meu dashboard de custos multi-cloud existente com dados reais da API X Cost que acabou de ser implementada. O endpoint `/api/v1/dashboard/summary` está funcionando perfeitamente e retornando dados reais de custos AWS, Azure, GCP e Oracle Cloud.

## 🎯 Objetivo Principal
Substituir os dados mockados do dashboard atual pelos dados reais vindos da API `/api/v1/dashboard/summary`, mantendo o design e UX existentes, mas conectando com informações reais de custos.

## 📊 Especificações Técnicas

### 🔗 Endpoint da API
- **URL**: `GET /api/v1/dashboard/summary?period_days=30`
- **Base URL**: `http://localhost:8000`
- **Autenticação**: Bearer Token JWT (usar token já existente no app)
- **Content-Type**: `application/json`

### 📋 Interface TypeScript para Resposta
```typescript
interface DashboardSummary {
  metrics: {
    total_cost: number;
    cost_change_percentage: number;
    monthly_average: number;
    top_service: {
      service_name: string;
      provider_name: string;
      total_cost: number;
    };
    annual_projection: number;
    budget_consumption: {
      percentage: number;
      consumed: number;
      total_budget: number;
    } | null;
  };
  provider_distribution: {
    provider_name: string;
    total_cost: number;
    percentage: number;
  }[];
  highlights: {
    next_month_forecast: {
      amount: number;
      change_percentage: number;
    };
    estimated_waste: {
      amount: number;
      percentage: number;
    };
    savings_achieved: {
      amount: number;
      percentage: number;
    };
  };
  generated_at: string;
  period: {
    days: number;
    start_date: string;
    end_date: string;
  };
}
```

## 🎨 Mapeamento de Dados

### 💰 Card "Resumo de Gastos"
```typescript
// Substituir dados estáticos por:
const gastoTotal = data.metrics.total_cost; // R$ 208.672,76
const variacao = data.metrics.cost_change_percentage; // -0.4%
const mediaMensal = data.metrics.monthly_average; // R$ 208.672,76
const maiorGasto = {
  servico: data.metrics.top_service.service_name, // "Compute"
  provider: data.metrics.top_service.provider_name, // "Oracle Cloud"
  valor: data.metrics.top_service.total_cost // R$ 20.633,52
};
const projecaoAnual = data.metrics.annual_projection; // R$ 2.504.073,12
const orcamento = {
  percentual: data.metrics.budget_consumption?.percentage || 0, // 136.1%
  consumido: data.metrics.budget_consumption?.consumed || 0,
  total: data.metrics.budget_consumption?.total_budget || 0
};
```

### 🥧 Gráfico "Distribuição por Provedor"
```typescript
// Mapear para gráfico de pizza:
const pieData = data.provider_distribution.map(provider => ({
  name: provider.provider_name,
  value: provider.percentage,
  cost: provider.total_cost,
  color: getProviderColor(provider.provider_name)
}));

// Cores sugeridas para consistência visual
const cores = {
  'AWS': '#FF9900',
  'Azure': '#0078D4', 
  'GCP': '#4285F4',
  'Oracle Cloud': '#F80000'
};
```

### 🎯 Cards "Highlights"
```typescript
// Card 1: Previsão Próximo Mês
const previsao = {
  valor: data.highlights.next_month_forecast.amount,
  variacao: data.highlights.next_month_forecast.change_percentage
};

// Card 2: Desperdício Estimado  
const desperdicio = {
  valor: data.highlights.estimated_waste.amount,
  percentual: data.highlights.estimated_waste.percentage
};

// Card 3: Economias Realizadas
const economias = {
  valor: data.highlights.savings_achieved.amount,
  percentual: data.highlights.savings_achieved.percentage
};
```

## 🔧 Implementação Requerida

### 1. **Hook Personalizado** (criar `useDashboard.ts`)
```typescript
export const useDashboard = (periodDays = 30, autoRefresh = true) => {
  // Implementar fetch do endpoint com:
  // - Estado de loading/error
  // - Auto-refresh a cada 5 minutos
  // - Cache de dados
  // - Retry automático em caso de erro
};
```

### 2. **Serviço de API** (atualizar `apiClient.ts`)
```typescript
// Adicionar método específico para dashboard
export const dashboardService = {
  getSummary: (periodDays?: number, credentialId?: string) => 
    apiClient.get('/dashboard/summary', { params: { period_days: periodDays, credential_id: credentialId }})
};
```

### 3. **Componente Dashboard** (atualizar componente existente)
- Manter design atual EXATAMENTE igual
- Substituir apenas a fonte de dados
- Adicionar loading states elegantes
- Implementar error handling com retry
- Adicionar seletor de período (7, 30, 90 dias)

### 4. **Formatação de Valores**
```typescript
// Implementar formatação consistente
const formatCurrency = (value: number) => 
  new Intl.NumberFormat('pt-BR', { 
    style: 'currency', 
    currency: 'BRL' 
  }).format(value);

const formatPercentage = (value: number) => 
  `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
```

## 🚨 Requisitos Importantes

### ✅ Obrigatório
1. **Manter design atual** - zero mudanças visuais
2. **Estados de loading** - skeleton/shimmer durante carregamento
3. **Error handling** - tela de erro com botão "Tentar Novamente"
4. **Auto-refresh** - atualizar dados a cada 5 minutos
5. **Responsividade** - manter comportamento mobile
6. **Filtro de período** - dropdown com 7, 30, 90 dias
7. **Performance** - não fazer requests desnecessários

### 🎯 Funcionalidades Adicionais
1. **Indicador de última atualização** - "Atualizado há 2 minutos"
2. **Animações suaves** - transições nos números
3. **Tooltip no gráfico** - mostrar valores detalhados
4. **Export de dados** - botão para baixar CSV/PDF
5. **Comparação de períodos** - "vs período anterior"

## 🧪 Dados de Teste Reais
A API está retornando dados reais funcionais:
- **Total**: R$ 208.672,76 (variação -0,4%)
- **Providers**: Oracle Cloud (28%), AWS (26%), GCP (23,6%), Azure (22,4%)
- **Desperdício**: R$ 3.225,20 (1,5%)
- **Economias**: R$ 810,06 (0,4%)

## 🔄 Fluxo de Integração
1. Criar hook `useDashboard` com fetch da API
2. Atualizar componente principal substituindo dados mockados
3. Implementar formatação de valores brasileiros
4. Adicionar loading states e error handling
5. Testar com dados reais da API
6. Implementar auto-refresh e seletor de período

## 💡 Resultado Esperado
Um dashboard funcionalmente idêntico ao atual, mas conectado aos dados reais da API X Cost, mostrando custos reais de multi-cloud com atualizações automáticas e interações suaves.