import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { dashboardService } from '@/api/client';
import { DashboardSummary } from '@/types/api';
import { useToast } from '@/hooks/use-toast';
import { timeFilterToDays } from '@/utils/timeFrame';
import { getProviderColor as getChartProviderColor } from '@/utils/chartColors';

interface UseDashboardOptions {
  periodDays?: number;
  timeFilter?: string; // Adicionar suporte a timeFilter
  credentialId?: string;
  providerName?: string; // Adicionar suporte a filtro de provedor
  autoRefresh?: boolean;
  refreshInterval?: number; // em milissegundos
}

interface UseDashboardReturn {
  data: DashboardSummary | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  lastUpdated: Date | null;
}

export const useDashboard = ({
  periodDays,
  timeFilter,
  credentialId,
  providerName,
  autoRefresh = false, // Definir como false por padrão para evitar excesso de requisições
  refreshInterval = 5 * 60 * 1000 // 5 minutos
}: UseDashboardOptions = {}): UseDashboardReturn => {
  // Usar useMemo para evitar recálculo desnecessário
  const calculatedPeriodDays = useMemo(() => {
    return timeFilter ? timeFilterToDays(timeFilter) : (periodDays || 30);
  }, [timeFilter, periodDays]);
  
  const [data, setData] = useState<DashboardSummary | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const { toast } = useToast();
  
  // Usar ref para evitar chamadas duplicadas
  const isLoadingRef = useRef(false);
  const lastParamsRef = useRef<string>('');

  const fetchDashboardData = useCallback(async (showLoadingState = true) => {
    // Criar chave única para os parâmetros atuais
    const currentParams = `${calculatedPeriodDays}-${credentialId || 'default'}-${providerName || 'all'}`;
    
    // Evitar chamadas duplicadas
    if (isLoadingRef.current || (currentParams === lastParamsRef.current && data)) {
      return;
    }
    
    try {
      isLoadingRef.current = true;
      lastParamsRef.current = currentParams;
      
      console.log(`🔄 Dashboard API call: ${currentParams}`);
      
      if (showLoadingState) {
        setLoading(true);
      }
      setError(null);

      const response = await dashboardService.getSummary(calculatedPeriodDays, credentialId, providerName);
      setData(response.data);
      setLastUpdated(new Date());
      
      console.log(`✅ Dashboard data loaded successfully`);
      
      // Se não é o carregamento inicial, mostrar toast de sucesso
      if (!showLoadingState && data) {
        toast({
          title: "Dados atualizados",
          description: "Dashboard atualizado com sucesso",
        });
      }
    } catch (err: any) {
      console.error(`❌ Dashboard API error:`, err);
      const errorMessage = err.response?.data?.detail || 
                          err.message || 
                          'Erro ao carregar dados do dashboard';
      setError(errorMessage);
      
      // Só mostrar toast de erro para carregamento inicial
      if (showLoadingState) {
        toast({
          title: "Erro ao carregar dados",
          description: errorMessage,
          variant: "destructive",
        });
      }
    } finally {
      isLoadingRef.current = false;
      if (showLoadingState) {
        setLoading(false);
      }
    }
  }, [calculatedPeriodDays, credentialId, providerName, data, toast]);

  const refetch = useCallback(async () => {
    // Forçar nova requisição resetando a referência
    lastParamsRef.current = '';
    await fetchDashboardData(true);
  }, [fetchDashboardData]);

  // Carregamento inicial - usar useEffect com dependências específicas
  useEffect(() => {
    // Só fazer requisição se os parâmetros mudaram significativamente
    const currentParams = `${calculatedPeriodDays}-${credentialId || 'default'}-${providerName || 'all'}`;
    if (currentParams !== lastParamsRef.current) {
      fetchDashboardData(true);
    }
  }, [calculatedPeriodDays, credentialId, providerName, fetchDashboardData]);

  // Auto-refresh - Desabilitado por padrão
  useEffect(() => {
    if (!autoRefresh || !data) return;

    const interval = setInterval(() => {
      fetchDashboardData(false); // Não mostrar loading durante auto-refresh
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchDashboardData, data]);

  return {
    data,
    loading,
    error,
    refetch,
    lastUpdated
  };
};

// Hook para formatação de valores
export const useDashboardFormatters = () => {
  const { t } = useTranslation();
  const formatCurrency = useCallback((value: number): string => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }, []);

  const formatPercentage = useCallback((value: number): string => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  }, []);

  const formatCompactCurrency = useCallback((value: number): string => {
    if (value >= 1_000_000) {
      return `$${(value / 1_000_000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}M`;
    } else if (value >= 1_000) {
      return `$${(value / 1_000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}K`;
    }
    return formatCurrency(value);
  }, [formatCurrency]);

  const getProviderColor = useCallback((providerName: string): string => {
    return getChartProviderColor(providerName);
  }, []);

  const formatRelativeTime = useCallback((date: Date): string => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) {
      return t('common.timeRelative.justNow');
    } else if (diffInMinutes < 60) {
      return t('common.timeRelative.minutesAgo', { count: diffInMinutes });
    } else {
      const diffInHours = Math.floor(diffInMinutes / 60);
      return t('common.timeRelative.hoursAgo', { count: diffInHours });
    }
  }, [t]);

  const formatUpdatedTime = useCallback((date: Date): string => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) {
      return t('common.timeRelative.updatedJustNow');
    } else if (diffInMinutes < 60) {
      return t('common.timeRelative.updatedMinutesAgo', { count: diffInMinutes });
    } else {
      const diffInHours = Math.floor(diffInMinutes / 60);
      return t('common.timeRelative.updatedHoursAgo', { count: diffInHours });
    }
  }, [t]);

  return {
    formatCurrency,
    formatPercentage,
    formatCompactCurrency,
    getProviderColor,
    formatRelativeTime,
    formatUpdatedTime
  };
};
