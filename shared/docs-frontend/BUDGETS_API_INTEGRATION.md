# Guia de Integração Frontend - API Budgets Completa

## ✅ STATUS: IMPLEMENTAÇÃO COMPLETA

A API de Budgets está 100% funcional com todos os endpoints CRUD implementados e testados.

## 📋 ENDPOINTS DISPONÍVEIS

### 1. **Listar Budgets**
```typescript
GET /api/v1/budgets
```

**Query Parameters:**
- `skip`: number (offset para paginação, default: 0)
- `limit`: number (limite de resultados, default: 100)  
- `provider_name`: string (filtrar por provedor)
- `service_name`: string (filtrar por serviço)
- `is_active`: boolean (filtrar por status ativo/inativo)

**Response:**
```typescript
interface BudgetListResponse {
  budgets: BudgetResponse[];
  total_count: number;
  total_budget_amount: string; // Decimal
  total_consumption: string; // Decimal
  overall_consumption_percentage: string; // Decimal
}
```

### 2. **Criar Budget**
```typescript
POST /api/v1/budgets
```

**Request Body:**
```typescript
interface BudgetCreate {
  budget_name: string;
  provider_name?: string;
  service_name?: string;
  budget_amount: string; // Decimal com 4 casas decimais
  budget_period?: string; // "monthly" | "annual", default: "monthly"
  alert_threshold?: string; // Decimal, default: "80.00"
  is_active?: boolean; // default: true
  tags?: Record<string, any>;
}
```

**Response:** `BudgetResponse` (status 201)

### 3. **Obter Budget Específico**
```typescript
GET /api/v1/budgets/{budget_id}
```

**Response:**
```typescript
interface BudgetResponse {
  id: number;
  budget_name: string;
  provider_name?: string;
  service_name?: string;
  budget_amount: string;
  budget_period: string;
  alert_threshold: string;
  is_active: boolean;
  created_at: string; // ISO datetime
  tags?: Record<string, any>;
}
```

### 4. **Obter Dados de Consumo do Budget**
```typescript
GET /api/v1/budgets/{budget_id}/consumption
```

**Query Parameters:**
- `period_days`: number (período em dias, default: 30)

**Response:**
```typescript
interface BudgetConsumption {
  // Dados básicos do budget
  id: number;
  budget_name: string;
  provider_name?: string;
  service_name?: string;
  budget_amount: string;
  budget_period: string;
  alert_threshold: string;
  is_active: boolean;
  created_at: string;
  tags?: Record<string, any>;
  
  // Dados de consumo
  current_consumption: string; // Decimal
  consumption_percentage: string; // Decimal
  remaining_budget: string; // Decimal
  period_start: string; // Date (YYYY-MM-DD)
  period_end: string; // Date (YYYY-MM-DD)
  status: "under_budget" | "warning" | "over_budget";
  days_remaining: number;
  projected_consumption?: string; // Decimal, pode ser null
}
```

### 5. **Atualizar Budget**
```typescript
PUT /api/v1/budgets/{budget_id}
```

**Request Body (todos os campos opcionais):**
```typescript
interface BudgetUpdate {
  budget_name?: string;
  provider_name?: string;
  service_name?: string;
  budget_amount?: string;
  budget_period?: string;
  alert_threshold?: string;
  is_active?: boolean;
  tags?: Record<string, any>;
}
```

**Response:** `BudgetResponse`

### 6. **Deletar Budget**
```typescript
DELETE /api/v1/budgets/{budget_id}
```

**Response:** 204 No Content

### 7. **Obter Alertas do Budget**
```typescript
GET /api/v1/budgets/{budget_id}/alerts
```

**Response:**
```typescript
interface BudgetAlertsResponse {
  budget_id: number;
  budget_name: string;
  alerts: Array<{
    type: "threshold_exceeded" | "projected_overspend";
    severity: "warning" | "critical";
    message: string;
    current_consumption?: string;
    projected_consumption?: string;
    budget_amount?: string;
  }>;
  alert_count: number;
  last_check: string; // ISO datetime
}
```

### 8. **Ativar Budget**
```typescript
POST /api/v1/budgets/{budget_id}/activate
```

**Response:**
```typescript
{
  message: "Budget activated successfully";
  budget_id: number;
}
```

### 9. **Desativar Budget**
```typescript
POST /api/v1/budgets/{budget_id}/deactivate
```

**Response:**
```typescript
{
  message: "Budget deactivated successfully";
  budget_id: number;
}
```

## 🔐 AUTENTICAÇÃO

Todos os endpoints requerem autenticação JWT:

```typescript
// Headers obrigatórios
{
  "Authorization": "Bearer {jwt_token}",
  "Content-Type": "application/json"
}
```

## 📊 INTEGRAÇÃO COM DASHBOARD

O dashboard (`/api/v1/dashboard/summary`) já inclui dados de budget:

```typescript
interface DashboardSummary {
  main_metrics: {
    budget_consumption: {
      total_budget: number;
      current_spend: number;
      consumption_percentage: number;
      remaining_budget: number;
    };
    // outros campos...
  };
  // outros campos...
}
```

## 🚨 TRATAMENTO DE ERROS

### Status Codes Comuns:
- **200**: Sucesso
- **201**: Criado com sucesso
- **204**: Deletado com sucesso
- **400**: Dados inválidos (ex: nome duplicado)
- **401**: Token inválido/expirado
- **404**: Budget não encontrado
- **422**: Erro de validação de dados
- **500**: Erro interno do servidor

### Estrutura de Erro:
```typescript
interface ErrorResponse {
  detail: string | Array<{
    type: string;
    loc: string[];
    msg: string;
    input: any;
  }>;
}
```

## 🔧 EXEMPLO DE USO COMPLETO

### React Hook para Gerenciar Budgets:

```typescript
import { useState, useEffect } from 'react';

interface UseBudgetsReturn {
  budgets: BudgetResponse[];
  loading: boolean;
  error: string | null;
  createBudget: (data: BudgetCreate) => Promise<BudgetResponse>;
  updateBudget: (id: number, data: BudgetUpdate) => Promise<BudgetResponse>;
  deleteBudget: (id: number) => Promise<void>;
  getBudgetConsumption: (id: number, periodDays?: number) => Promise<BudgetConsumption>;
  refreshBudgets: () => Promise<void>;
}

export const useBudgets = (): UseBudgetsReturn => {
  const [budgets, setBudgets] = useState<BudgetResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiCall = async (url: string, options: RequestInit = {}) => {
    const token = localStorage.getItem('auth_token');
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'API Error');
    }

    if (response.status === 204) return null;
    return response.json();
  };

  const refreshBudgets = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiCall('/api/v1/budgets');
      setBudgets(data.budgets);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const createBudget = async (data: BudgetCreate): Promise<BudgetResponse> => {
    const result = await apiCall('/api/v1/budgets', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    await refreshBudgets(); // Refresh list
    return result;
  };

  const updateBudget = async (id: number, data: BudgetUpdate): Promise<BudgetResponse> => {
    const result = await apiCall(`/api/v1/budgets/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
    await refreshBudgets(); // Refresh list
    return result;
  };

  const deleteBudget = async (id: number): Promise<void> => {
    await apiCall(`/api/v1/budgets/${id}`, {
      method: 'DELETE',
    });
    await refreshBudgets(); // Refresh list
  };

  const getBudgetConsumption = async (id: number, periodDays = 30): Promise<BudgetConsumption> => {
    return apiCall(`/api/v1/budgets/${id}/consumption?period_days=${periodDays}`);
  };

  useEffect(() => {
    refreshBudgets();
  }, []);

  return {
    budgets,
    loading,
    error,
    createBudget,
    updateBudget,
    deleteBudget,
    getBudgetConsumption,
    refreshBudgets,
  };
};
```

### Componente Budget Card:

```tsx
import React from 'react';

interface BudgetCardProps {
  budget: BudgetResponse;
  onEdit: (budget: BudgetResponse) => void;
  onDelete: (id: number) => void;
  onViewDetails: (id: number) => void;
}

export const BudgetCard: React.FC<BudgetCardProps> = ({
  budget,
  onEdit,
  onDelete,
  onViewDetails,
}) => {
  const [consumption, setConsumption] = useState<BudgetConsumption | null>(null);
  const { getBudgetConsumption } = useBudgets();

  useEffect(() => {
    const loadConsumption = async () => {
      try {
        const data = await getBudgetConsumption(budget.id);
        setConsumption(data);
      } catch (error) {
        console.error('Failed to load consumption:', error);
      }
    };
    loadConsumption();
  }, [budget.id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'under_budget': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'over_budget': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold">{budget.budget_name}</h3>
        <span className={`px-2 py-1 rounded text-sm ${budget.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
          {budget.is_active ? 'Ativo' : 'Inativo'}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between">
          <span className="text-gray-600">Orçamento:</span>
          <span className="font-medium">R$ {parseFloat(budget.budget_amount).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
        </div>

        {consumption && (
          <>
            <div className="flex justify-between">
              <span className="text-gray-600">Consumido:</span>
              <span className="font-medium">R$ {parseFloat(consumption.current_consumption).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-gray-600">Percentual:</span>
              <span className={`font-medium ${getStatusColor(consumption.status)}`}>
                {parseFloat(consumption.consumption_percentage).toFixed(1)}%
              </span>
            </div>

            {/* Progress Bar */}
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full ${
                  consumption.status === 'under_budget' ? 'bg-green-500' :
                  consumption.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${Math.min(parseFloat(consumption.consumption_percentage), 100)}%` }}
              />
            </div>
          </>
        )}

        {budget.provider_name && (
          <div className="flex justify-between">
            <span className="text-gray-600">Provedor:</span>
            <span>{budget.provider_name}</span>
          </div>
        )}

        {budget.service_name && (
          <div className="flex justify-between">
            <span className="text-gray-600">Serviço:</span>
            <span>{budget.service_name}</span>
          </div>
        )}
      </div>

      <div className="flex space-x-2">
        <button
          onClick={() => onViewDetails(budget.id)}
          className="flex-1 bg-blue-500 text-white px-3 py-2 rounded text-sm hover:bg-blue-600"
        >
          Detalhes
        </button>
        <button
          onClick={() => onEdit(budget)}
          className="flex-1 bg-gray-500 text-white px-3 py-2 rounded text-sm hover:bg-gray-600"
        >
          Editar
        </button>
        <button
          onClick={() => onDelete(budget.id)}
          className="flex-1 bg-red-500 text-white px-3 py-2 rounded text-sm hover:bg-red-600"
        >
          Excluir
        </button>
      </div>
    </div>
  );
};
```

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

- [x] **Endpoints CRUD completos** - Todos os 9 endpoints implementados
- [x] **Autenticação JWT** - Integrada com sistema de auth existente
- [x] **Validação de dados** - Pydantic models com validação completa
- [x] **Tratamento de erros** - HTTP status codes apropriados
- [x] **Cálculo de consumo** - Integração com dados reais de custo
- [x] **Sistema de alertas** - Baseado em thresholds configuráveis
- [x] **Projeção de gastos** - Cálculo automático baseado em tendência
- [x] **Filtros e paginação** - Para listagem eficiente
- [x] **Ativação/Desativação** - Controle de status dos budgets
- [x] **Testes completos** - Todos os endpoints testados e funcionando

## 🎯 PRÓXIMOS PASSOS

1. **Integrar no Frontend Lovable** - Usar os hooks e componentes acima
2. **Implementar notificações** - Sistema de alertas em tempo real
3. **Dashboards específicos** - Visualizações avançadas de consumo
4. **Relatórios** - Geração de relatórios de budget
5. **Configurações avançadas** - Budgets por tags, múltiplos thresholds

## 📞 SUPORTE

A API está 100% funcional e testada. Para dúvidas ou problemas:
- Verifique os logs da API em caso de erro 500
- Valide autenticação JWT se receber erro 401
- Confirme formato dos dados se receber erro 422

**Status:** ✅ PRONTO PARA PRODUÇÃO
