import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useToast } from '@/hooks/use-toast';
import { apiClient } from '@/api/client';
import { 
  CloudAnomaly,
  SavingsOpportunity,
  OptimizationRecommendation,
  OptimizationSummary,
  AnomaliesResponse,
  SavingsOpportunitiesResponse,
  OptimizationRecommendationsResponse,
  OptimizationFilters,
  AnomaliesFilters,
  SavingsFilters
} from '@/types/optimization';

// Error handling helper
interface ApiError {
  response?: {
    data?: {
      detail?: string;
    };
  };
  message?: string;
}

const getErrorMessage = (error: unknown, defaultMessage: string): string => {
  const err = error as ApiError;
  return err.response?.data?.detail || err.message || defaultMessage;
};

// Base optimization API service
export const optimizationService = {
  getAnomalies: (filters?: AnomaliesFilters) =>
    apiClient.get<AnomaliesResponse>('/api/v1/anomalies', { params: filters }),

  getSavings: (filters?: SavingsFilters) =>
    apiClient.get<SavingsOpportunitiesResponse>('/api/v1/savings-opportunities', { params: filters }),

  getRecommendations: (filters?: OptimizationFilters) =>
    apiClient.get<OptimizationRecommendationsResponse>('/api/v1/optimization/recommendations', { params: filters }),

  getSummary: (provider?: string) =>
    apiClient.get<OptimizationSummary>('/api/v1/optimization/summary', { 
      params: provider ? { provider } : {} 
    }),

  invalidateCache: () =>
    apiClient.post('/api/v1/optimization/cache/invalidate'),

  getProviders: () =>
    apiClient.get<string[]>('/api/v1/optimization/providers'),

  getTypes: () =>
    apiClient.get<string[]>('/api/v1/optimization/types'),

  // Bulk actions
  bulkActionOpportunities: (data: {
    action: string;
    opportunity_ids: string[];
    plan_id?: string;
    notes?: string;
  }) =>
    apiClient.post('/api/v1/savings-opportunities/bulk-action', data),

  // Implementation plans
  getImplementationPlans: (filters?: {
    status?: string;
    page?: number;
    per_page?: number;
  }) =>
    apiClient.get('/api/v1/implementation-plans', { params: filters }),

  createImplementationPlan: (data: {
    name: string;
    description: string;
    opportunity_ids?: string[];
    timeline_months?: number;
    risk_assessment?: string;
  }) =>
    apiClient.post('/api/v1/implementation-plans', data)
};

// Hook for anomalies
interface UseAnomaliesOptions extends AnomaliesFilters {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseAnomaliesReturn {
  data: CloudAnomaly[];
  total: number;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  lastUpdated: Date | null;
  pagination: {
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export const useAnomalies = ({
  provider,
  days = 30,
  severity,
  anomaly_type,
  service_name,
  page = 1,
  per_page = 10,
  autoRefresh = false,
  refreshInterval = 5 * 60 * 1000
}: UseAnomaliesOptions = {}): UseAnomaliesReturn => {
  const [data, setData] = useState<CloudAnomaly[]>([]);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ page: 1, per_page: 10, total_pages: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { toast } = useToast();
  
  const isLoadingRef = useRef(false);
  const lastParamsRef = useRef<string>('');

  const fetchAnomalies = useCallback(async (showLoadingState = true) => {
    const currentParams = `anomalies-${provider || 'all'}-${days}-${severity || 'all'}-${page}-${per_page}`;
    
    if (isLoadingRef.current) {
      return;
    }
    
    // Para refresh silencioso, verificar se já temos dados e os parâmetros não mudaram
    if (currentParams === lastParamsRef.current && !showLoadingState && (data?.length ?? 0) > 0) {
      return;
    }
    
    try {
      isLoadingRef.current = true;
      
      // Só atualizar lastParamsRef se for uma chamada com loading ou parâmetros diferentes
      if (showLoadingState || currentParams !== lastParamsRef.current) {
        lastParamsRef.current = currentParams;
      }
      
      if (showLoadingState) setLoading(true);
      setError(null);

      const response = await optimizationService.getAnomalies({
        provider,
        days,
        severity,
        anomaly_type,
        service_name,
        page,
        per_page
      });

      setData(response.data.anomalies);
      setTotal(response.data.total_count);
      setPagination({
        page: response.data.page,
        per_page: response.data.per_page,
        total_pages: response.data.total_pages
      });
      setLastUpdated(new Date());

      if (!showLoadingState && (data?.length ?? 0) > 0) {
        toast({
          title: "Anomalies updated",
          description: "Anomaly data refreshed successfully",
        });
      }
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error loading anomalies');
      setError(errorMessage);
      
      if (showLoadingState) {
        toast({
          title: "Error loading anomalies",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } finally {
      isLoadingRef.current = false;
      if (showLoadingState) setLoading(false);
    }
  }, [provider, days, severity, anomaly_type, service_name, page, per_page, toast, data?.length]);

  const refetch = useCallback(async () => {
    lastParamsRef.current = '';
    await fetchAnomalies(true);
  }, [fetchAnomalies]);

  useEffect(() => {
    const currentParams = `anomalies-${provider || 'all'}-${days}-${severity || 'all'}-${anomaly_type || ''}-${service_name || ''}-${page}-${per_page}`;
    if (currentParams !== lastParamsRef.current) {
      fetchAnomalies(true);
    }
  }, [provider, days, severity, anomaly_type, service_name, page, per_page, fetchAnomalies]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchAnomalies(false);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  return {
    data,
    total,
    loading,
    error,
    refetch,
    lastUpdated,
    pagination
  };
};

// Hook for savings opportunities
interface UseSavingsOpportunitiesOptions extends SavingsFilters {
  implementation_effort?: string;
  risk_level?: string;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseSavingsOpportunitiesReturn {
  data: SavingsOpportunity[];
  total: number;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  lastUpdated: Date | null;
  pagination: {
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export const useSavingsOpportunities = ({
  provider,
  days = 30,
  min_savings,
  max_savings,
  category,
  confidence_level,
  implementation_effort,
  risk_level,
  service_name,
  search,
  sort_by,
  sort_order,
  page = 1,
  per_page = 10,
  autoRefresh = false,
  refreshInterval = 5 * 60 * 1000
}: UseSavingsOpportunitiesOptions = {}): UseSavingsOpportunitiesReturn => {
  const [data, setData] = useState<SavingsOpportunity[]>([]);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ page: 1, per_page: 10, total_pages: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { toast } = useToast();
  
  const isLoadingRef = useRef(false);
  const lastParamsRef = useRef<string>('');

  const fetchSavings = useCallback(async (showLoadingState = true) => {
    const currentParams = `savings-${provider || 'all'}-${days}-${min_savings || 0}-${max_savings || 0}-${category || ''}-${confidence_level || ''}-${implementation_effort || ''}-${risk_level || ''}-${service_name || ''}-${search || ''}-${sort_by || ''}-${sort_order || ''}-${page}-${per_page}`;
    
    if (isLoadingRef.current) {
      return;
    }
    
    // Para refresh silencioso, verificar se já temos dados e os parâmetros não mudaram
    if (currentParams === lastParamsRef.current && !showLoadingState && (data?.length ?? 0) > 0) {
      return;
    }
    
    try {
      isLoadingRef.current = true;
      
      // Só atualizar lastParamsRef se for uma chamada com loading ou parâmetros diferentes
      if (showLoadingState || currentParams !== lastParamsRef.current) {
        lastParamsRef.current = currentParams;
      }
      
      if (showLoadingState) setLoading(true);
      setError(null);

      const response = await optimizationService.getSavings({
        provider,
        days,
        min_savings,
        max_savings,
        category,
        confidence_level,
        implementation_effort,
        risk_level,
        service_name,
        search,
        sort_by,
        sort_order,
        page,
        per_page
      });

      setData(response.data.opportunities);
      setTotal(response.data.total_count);
      setPagination({
        page: response.data.page,
        per_page: response.data.per_page,
        total_pages: response.data.total_pages
      });
      setLastUpdated(new Date());

      if (!showLoadingState && (data?.length ?? 0) > 0) {
        toast({
          title: "Opportunities updated",
          description: "Savings opportunities refreshed successfully",
        });
      }
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error loading savings opportunities');
      setError(errorMessage);
      
      if (showLoadingState) {
        toast({
          title: "Error loading opportunities",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } finally {
      isLoadingRef.current = false;
      if (showLoadingState) setLoading(false);
    }
  }, [provider, days, min_savings, max_savings, category, confidence_level, implementation_effort, risk_level, service_name, search, sort_by, sort_order, page, per_page, toast, data?.length]);

  const refetch = useCallback(async () => {
    lastParamsRef.current = '';
    await fetchSavings(true);
  }, [fetchSavings]);

  useEffect(() => {
    const currentParams = `savings-${provider || 'all'}-${days}-${min_savings || 0}-${max_savings || 0}-${category || ''}-${confidence_level || ''}-${implementation_effort || ''}-${risk_level || ''}-${service_name || ''}-${search || ''}-${sort_by || ''}-${sort_order || ''}-${page}-${per_page}`;
    if (currentParams !== lastParamsRef.current) {
      fetchSavings(true);
    }
  }, [provider, days, min_savings, max_savings, category, confidence_level, implementation_effort, risk_level, service_name, search, sort_by, sort_order, page, per_page, fetchSavings]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchSavings(false);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  return {
    data,
    total,
    loading,
    error,
    refetch,
    lastUpdated,
    pagination
  };
};

// Hook for optimization recommendations
interface UseOptimizationRecommendationsOptions extends OptimizationFilters {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseOptimizationRecommendationsReturn {
  data: OptimizationRecommendation[];
  total: number;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  lastUpdated: Date | null;
  pagination: {
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export const useOptimizationRecommendations = ({
  provider,
  days = 30,
  category,
  page = 1,
  per_page = 10,
  autoRefresh = false,
  refreshInterval = 5 * 60 * 1000
}: UseOptimizationRecommendationsOptions = {}): UseOptimizationRecommendationsReturn => {
  const [data, setData] = useState<OptimizationRecommendation[]>([]);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ page: 1, per_page: 10, total_pages: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { toast } = useToast();
  
  const isLoadingRef = useRef(false);
  const lastParamsRef = useRef<string>('');

  const fetchRecommendations = useCallback(async (showLoadingState = true) => {
    const currentParams = `recommendations-${provider || 'all'}-${days}-${category || 'all'}-${page}-${per_page}`;
    
    if (isLoadingRef.current) {
      return;
    }
    
    // Para refresh silencioso, verificar se já temos dados e os parâmetros não mudaram  
    if (currentParams === lastParamsRef.current && !showLoadingState && (data?.length ?? 0) > 0) {
      return;
    }
    
    try {
      isLoadingRef.current = true;
      
      // Só atualizar lastParamsRef se for uma chamada com loading ou parâmetros diferentes
      if (showLoadingState || currentParams !== lastParamsRef.current) {
        lastParamsRef.current = currentParams;
      }
      
      if (showLoadingState) setLoading(true);
      setError(null);

      const response = await optimizationService.getRecommendations({
        provider,
        days,
        category,
        page,
        per_page
      });

      setData(response.data.recommendations);
      setTotal(response.data.total_count);
      setPagination({
        page: response.data.page,
        per_page: response.data.per_page,
        total_pages: response.data.total_pages
      });
      setLastUpdated(new Date());

      if (!showLoadingState && (data?.length ?? 0) > 0) {
        toast({
          title: "Recommendations updated",
          description: "Optimization recommendations refreshed successfully",
        });
      }
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error loading recommendations');
      setError(errorMessage);
      
      if (showLoadingState) {
        toast({
          title: "Error loading recommendations",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } finally {
      isLoadingRef.current = false;
      if (showLoadingState) setLoading(false);
    }
  }, [provider, days, category, page, per_page, toast, data?.length]);

  const refetch = useCallback(async () => {
    lastParamsRef.current = '';
    await fetchRecommendations(true);
  }, [fetchRecommendations]);

  useEffect(() => {
    const currentParams = `recommendations-${provider || 'all'}-${days}-${category || 'all'}-${page}-${per_page}`;
    if (currentParams !== lastParamsRef.current) {
      fetchRecommendations(true);
    }
  }, [provider, days, category, page, per_page]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchRecommendations(false);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  return {
    data,
    total,
    loading,
    error,
    refetch,
    lastUpdated,
    pagination
  };
};

// Hook for optimization summary
interface UseOptimizationSummaryOptions {
  provider?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface UseOptimizationSummaryReturn {
  data: OptimizationSummary | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  lastUpdated: Date | null;
}

export const useOptimizationSummary = ({
  provider,
  autoRefresh = true,
  refreshInterval = 5 * 60 * 1000
}: UseOptimizationSummaryOptions = {}): UseOptimizationSummaryReturn => {
  const [data, setData] = useState<OptimizationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { toast } = useToast();
  
  const isLoadingRef = useRef(false);
  const lastParamsRef = useRef<string>('');

  const fetchSummary = useCallback(async (showLoadingState = true) => {
    const currentParams = `summary-${provider || 'all'}`;
    
    if (isLoadingRef.current) {
      return;
    }
    
    // Para refresh silencioso, verificar se já temos dados e os parâmetros não mudaram
    if (currentParams === lastParamsRef.current && !showLoadingState && data) {
      return;
    }
    
    try {
      isLoadingRef.current = true;
      
      // Só atualizar lastParamsRef se for uma chamada com loading ou parâmetros diferentes
      if (showLoadingState || currentParams !== lastParamsRef.current) {
        lastParamsRef.current = currentParams;
      }
      
      if (showLoadingState) setLoading(true);
      setError(null);

      const response = await optimizationService.getSummary(provider);
      setData(response.data);
      setLastUpdated(new Date());

      if (!showLoadingState && data) {
        toast({
          title: "Summary updated",
          description: "Optimization summary refreshed successfully",
        });
      }
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error loading optimization summary');
      setError(errorMessage);
      
      if (showLoadingState) {
        toast({
          title: "Error loading summary",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } finally {
      isLoadingRef.current = false;
      if (showLoadingState) setLoading(false);
    }
  }, [provider, toast, data]);

  const refetch = useCallback(async () => {
    lastParamsRef.current = '';
    await fetchSummary(true);
  }, [fetchSummary]);

  useEffect(() => {
    const currentParams = `summary-${provider || 'all'}`;
    if (currentParams !== lastParamsRef.current) {
      fetchSummary(true);
    }
  }, [provider]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchSummary(false);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  return {
    data,
    loading,
    error,
    refetch,
    lastUpdated
  };
};

// Hook for cache invalidation
export const useInvalidateCache = () => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const invalidateCache = useCallback(async () => {
    try {
      setLoading(true);
      await optimizationService.invalidateCache();
      
      toast({
        title: "Cache invalidated",
        description: "Optimization cache cleared successfully",
      });
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error invalidating cache');
      toast({
        title: "Error invalidating cache", 
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  return {
    invalidateCache,
    loading
  };
};

// Hook for providers and types metadata
export const useOptimizationMetadata = () => {
  const [providers, setProviders] = useState<string[]>([]);
  const [types, setTypes] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        setLoading(true);
        const [providersResponse, typesResponse] = await Promise.all([
          optimizationService.getProviders(),
          optimizationService.getTypes()
        ]);

        setProviders(providersResponse.data);
        setTypes(typesResponse.data);
      } catch (err: unknown) {
        setError(getErrorMessage(err, 'Error loading metadata'));
      } finally {
        setLoading(false);
      }
    };

    fetchMetadata();
  }, []);

  return {
    providers,
    types,
    loading,
    error
  };
};

// Hook for bulk actions on savings opportunities
export const useBulkActions = () => {
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const performBulkAction = useCallback(async (
    action: string,
    opportunityIds: string[],
    options?: { planId?: string; notes?: string }
  ) => {
    try {
      setLoading(true);
      
      const response = await optimizationService.bulkActionOpportunities({
        action,
        opportunity_ids: opportunityIds,
        plan_id: options?.planId,
        notes: options?.notes
      });

      toast({
        title: "Bulk action completed",
        description: `Successfully ${action.replace('_', ' ')} ${opportunityIds.length} opportunities`,
      });

      return response.data;
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error performing bulk action');
      toast({
        title: "Bulk action failed",
        description: errorMessage,
        variant: "destructive",
      });
      throw err;
    } finally {
      setLoading(false);
    }
  }, [toast]);

  return {
    performBulkAction,
    loading
  };
};

// Hook for implementation plans
interface UseImplementationPlansOptions {
  status?: string;
  page?: number;
  per_page?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

interface ImplementationPlan {
  id: string;
  name: string;
  description: string;
  opportunity_ids: string[];
  estimated_total_savings: number;
  timeline_months: number;
  risk_assessment: string;
  status: string;
  created_at: string;
  updated_at: string;
}

interface UseImplementationPlansReturn {
  data: ImplementationPlan[];
  total: number;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  createPlan: (planData: {
    name: string;
    description: string;
    opportunity_ids?: string[];
    timeline_months?: number;
    risk_assessment?: string;
  }) => Promise<ImplementationPlan>;
  pagination: {
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export const useImplementationPlans = ({
  status,
  page = 1,
  per_page = 20,
  autoRefresh = false,
  refreshInterval = 5 * 60 * 1000
}: UseImplementationPlansOptions = {}): UseImplementationPlansReturn => {
  const [data, setData] = useState<ImplementationPlan[]>([]);
  const [total, setTotal] = useState(0);
  const [pagination, setPagination] = useState({ page: 1, per_page: 20, total_pages: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();
  
  const isLoadingRef = useRef(false);
  const lastParamsRef = useRef<string>('');

  const fetchPlans = useCallback(async (showLoadingState = true) => {
    const currentParams = `plans-${status || 'all'}-${page}-${per_page}`;
    
    if (isLoadingRef.current) {
      return;
    }
    
    if (currentParams === lastParamsRef.current && !showLoadingState && (data?.length ?? 0) > 0) {
      return;
    }
    
    try {
      isLoadingRef.current = true;
      
      if (showLoadingState || currentParams !== lastParamsRef.current) {
        lastParamsRef.current = currentParams;
      }
      
      if (showLoadingState) setLoading(true);
      setError(null);

      const response = await optimizationService.getImplementationPlans({
        status,
        page,
        per_page
      });

      setData(response.data.plans);
      setTotal(response.data.total_count);
      setPagination({
        page: response.data.page,
        per_page: response.data.per_page,
        total_pages: response.data.total_pages
      });

      if (!showLoadingState && (data?.length ?? 0) > 0) {
        toast({
          title: "Plans updated",
          description: "Implementation plans refreshed successfully",
        });
      }
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error loading implementation plans');
      setError(errorMessage);
      
      if (showLoadingState) {
        toast({
          title: "Error loading plans",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } finally {
      isLoadingRef.current = false;
      if (showLoadingState) setLoading(false);
    }
  }, [status, page, per_page, toast, data?.length]);

  const createPlan = useCallback(async (planData: {
    name: string;
    description: string;
    opportunity_ids?: string[];
    timeline_months?: number;
    risk_assessment?: string;
  }) => {
    try {
      const response = await optimizationService.createImplementationPlan(planData);
      
      toast({
        title: "Plan created",
        description: `Implementation plan "${planData.name}" created successfully`,
      });

      // Refresh the plans list
      await fetchPlans(false);
      
      return response.data.plan;
    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err, 'Error creating implementation plan');
      toast({
        title: "Error creating plan",
        description: errorMessage,
        variant: "destructive",
      });
      throw err;
    }
  }, [fetchPlans, toast]);

  const refetch = useCallback(async () => {
    lastParamsRef.current = '';
    await fetchPlans(true);
  }, [fetchPlans]);

  useEffect(() => {
    const currentParams = `plans-${status || 'all'}-${page}-${per_page}`;
    if (currentParams !== lastParamsRef.current) {
      fetchPlans(true);
    }
  }, [status, page, per_page, fetchPlans]);

  // Auto-refresh
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      fetchPlans(false);
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchPlans]);

  return {
    data,
    total,
    loading,
    error,
    refetch,
    createPlan,
    pagination
  };
};