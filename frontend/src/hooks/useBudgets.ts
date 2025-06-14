import { useState, useEffect } from 'react';
import { useAuth } from './useAuth';
import { apiClient } from '../api/client';

// Types baseados na API documentation
export interface BudgetCreate {
  budget_name: string;
  provider_name?: string;
  service_name?: string;
  budget_amount: string; // Decimal com 4 casas decimais
  budget_period?: string; // "monthly" | "annual", default: "monthly"
  alert_threshold?: string; // Decimal, default: "80.00"
  is_active?: boolean; // default: true
  tags?: Record<string, any>;
}

export interface BudgetUpdate {
  budget_name?: string;
  provider_name?: string;
  service_name?: string;
  budget_amount?: string;
  budget_period?: string;
  alert_threshold?: string;
  is_active?: boolean;
  tags?: Record<string, any>;
}

export interface BudgetResponse {
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

export interface BudgetConsumption {
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

export interface BudgetListResponse {
  budgets: BudgetResponse[];
  total_count: number;
  total_budget_amount: string; // Decimal
  total_consumption: string; // Decimal
  overall_consumption_percentage: string; // Decimal
}

export interface BudgetAlertsResponse {
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

interface UseBudgetsOptions {
  skip?: number;
  limit?: number;
  provider_name?: string;
  service_name?: string;
  is_active?: boolean;
}

interface UseBudgetsReturn {
  budgets: BudgetResponse[];
  totalCount: number;
  totalBudgetAmount: string;
  totalConsumption: string;
  overallConsumptionPercentage: string;
  // Active budget summaries
  activeBudgetCount: number;
  activeBudgetAmount: string;
  activeBudgetConsumption: string;
  activeBudgetConsumptionPercentage: string;
  loading: boolean;
  error: string | null;
  createBudget: (data: BudgetCreate) => Promise<BudgetResponse>;
  updateBudget: (id: number, data: BudgetUpdate) => Promise<BudgetResponse>;
  deleteBudget: (id: number) => Promise<void>;
  getBudgetConsumption: (id: number, periodDays?: number) => Promise<BudgetConsumption>;
  getBudgetAlerts: (id: number) => Promise<BudgetAlertsResponse>;
  activateBudget: (id: number) => Promise<void>;
  deactivateBudget: (id: number) => Promise<void>;
  refreshBudgets: () => Promise<void>;
}

export const useBudgets = (options: UseBudgetsOptions = {}): UseBudgetsReturn => {
  const [budgets, setBudgets] = useState<BudgetResponse[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalBudgetAmount, setTotalBudgetAmount] = useState('0');
  const [totalConsumption, setTotalConsumption] = useState('0');
  const [overallConsumptionPercentage, setOverallConsumptionPercentage] = useState('0');
  // Active budget states
  const [activeBudgetCount, setActiveBudgetCount] = useState(0);
  const [activeBudgetAmount, setActiveBudgetAmount] = useState('0');
  const [activeBudgetConsumption, setActiveBudgetConsumption] = useState('0');
  const [activeBudgetConsumptionPercentage, setActiveBudgetConsumptionPercentage] = useState('0');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { isAuthenticated } = useAuth();


  const apiCall = async (url: string, options: { method?: string; body?: any } = {}) => {
    const { method = 'GET', body } = options;
    
    try {
      let response;
      switch (method.toUpperCase()) {
        case 'POST':
          response = await apiClient.post(url, body);
          break;
        case 'PUT':
          response = await apiClient.put(url, body);
          break;
        case 'DELETE':
          response = await apiClient.delete(url);
          break;
        default:
          response = await apiClient.get(url);
      }
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Network error');
    }
  };

  const refreshBudgets = async () => {
    console.log('🔄 [useBudgets] Starting refreshBudgets...');
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (options.skip !== undefined) params.append('skip', options.skip.toString());
      if (options.limit !== undefined) params.append('limit', options.limit.toString());
      if (options.provider_name) params.append('provider_name', options.provider_name);
      if (options.service_name) params.append('service_name', options.service_name);
      if (options.is_active !== undefined) params.append('is_active', options.is_active.toString());

      const queryString = params.toString();
      const url = `/api/v1/budgets${queryString ? `?${queryString}` : ''}`;
      
      console.log('🌐 [useBudgets] Making API call to:', url);
      console.log('🔑 [useBudgets] Authentication available:', isAuthenticated);
      
      const data: BudgetListResponse = await apiCall(url);
      
      console.log('✅ [useBudgets] API response received:', data);
      console.log('📋 [useBudgets] Budgets count:', data?.budgets?.length || 0);
      
      setBudgets(data?.budgets || []);
      setTotalCount(data?.total_count || 0);
      setTotalBudgetAmount(data?.total_budget_amount || '0');
      setTotalConsumption(data?.total_consumption || '0');
      setOverallConsumptionPercentage(data?.overall_consumption_percentage || '0');
    } catch (err) {
      console.error('❌ [useBudgets] Error loading budgets:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const createBudget = async (data: BudgetCreate): Promise<BudgetResponse> => {
    const result = await apiCall('/api/v1/budgets', {
      method: 'POST',
      body: data,
    });
    await refreshBudgets(); // Refresh list
    return result;
  };

  const updateBudget = async (id: number, data: BudgetUpdate): Promise<BudgetResponse> => {
    const result = await apiCall(`/api/v1/budgets/${id}`, {
      method: 'PUT',
      body: data,
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
    return apiCall(`/api/v1/budgets/${id}/usage?period_days=${periodDays}`);
  };

  const getBudgetAlerts = async (id: number): Promise<BudgetAlertsResponse> => {
    return apiCall(`/api/v1/budgets/${id}/alerts`);
  };

  const activateBudget = async (id: number): Promise<void> => {
    await apiCall(`/api/v1/budgets/${id}/activate`, {
      method: 'POST',
    });
    await refreshBudgets(); // Refresh list
  };

  const deactivateBudget = async (id: number): Promise<void> => {
    await apiCall(`/api/v1/budgets/${id}/deactivate`, {
      method: 'POST',
    });
    await refreshBudgets(); // Refresh list
  };

  // Calculate active budget summaries when data changes
  useEffect(() => {
    const activeBudgets = budgets.filter(budget => budget.is_active);
    
    const activeCount = activeBudgets.length;
    const activeBudgetSum = activeBudgets.reduce((sum, budget) => sum + parseFloat(budget.budget_amount), 0);
    
    setActiveBudgetCount(activeCount);
    setActiveBudgetAmount(activeBudgetSum.toString());
    
    // For consumption, we'll calculate proportionally based on the backend data
    // This is an approximation since we can't efficiently fetch all consumption data here
    const allBudgetSum = parseFloat(totalBudgetAmount);
    const totalConsumptionValue = parseFloat(totalConsumption);
    
    if (allBudgetSum > 0 && totalConsumptionValue > 0) {
      // Approximate active consumption based on proportion of active budgets
      const activeConsumptionApprox = (activeBudgetSum / allBudgetSum) * totalConsumptionValue;
      const activeConsumptionPercentage = activeBudgetSum > 0 
        ? (activeConsumptionApprox / activeBudgetSum) * 100 
        : 0;
      
      setActiveBudgetConsumption(activeConsumptionApprox.toString());
      setActiveBudgetConsumptionPercentage(activeConsumptionPercentage.toFixed(2));
    } else {
      setActiveBudgetConsumption('0');
      setActiveBudgetConsumptionPercentage('0');
    }
  }, [budgets, totalBudgetAmount, totalConsumption]);

  useEffect(() => {
    if (isAuthenticated) {
      refreshBudgets();
    }
  }, [isAuthenticated, options.skip, options.limit, options.provider_name, options.service_name, options.is_active]);

  return {
    budgets,
    totalCount,
    totalBudgetAmount,
    totalConsumption,
    overallConsumptionPercentage,
    // Active budget summaries
    activeBudgetCount,
    activeBudgetAmount,
    activeBudgetConsumption,
    activeBudgetConsumptionPercentage,
    loading,
    error,
    createBudget,
    updateBudget,
    deleteBudget,
    getBudgetConsumption,
    getBudgetAlerts,
    activateBudget,
    deactivateBudget,
    refreshBudgets,
  };
};
