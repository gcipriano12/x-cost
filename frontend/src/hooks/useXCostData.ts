
import { useState, useEffect, useMemo } from 'react';
import { useCredentials } from './useCredentials';
import { timeFilterToDays } from '@/utils/timeFrame';
import { useDataLoadingControl } from './utils/useDataLoadingControl';
import { useApiDataFetcher } from './utils/useApiDataFetcher';
import { 
  transformServiceCostsToTopServices,
  calculateProviderDistribution,
  calculateSpendSummary
} from './utils/dataTransformers';
import type { 
  SpendSummary,
  ProviderDistribution,
  TopService
} from './useDashboardData';
import type {
  TrendData,
  ServiceCost,
  RegionCost
} from '../types/api';

interface UseXCostDataOptions {
  timeFilter?: string;
  credentialId?: number;
  customStartDate?: Date;
  customEndDate?: Date;
  providerName?: string;
}

export const useXCostData = (options: UseXCostDataOptions = {}) => {
  const { timeFilter, credentialId: optionsCredentialId, customStartDate, customEndDate, providerName } = options;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { credentials } = useCredentials();
  const { fetchAllData } = useApiDataFetcher();
  const loadingControl = useDataLoadingControl();

  // Estado para dados integrados
  const [spendSummary, setSpendSummary] = useState<SpendSummary | null>(null);
  const [providerDistribution, setProviderDistribution] = useState<ProviderDistribution[]>([]);
  const [topServices, setTopServices] = useState<TopService[]>([]);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [serviceCosts, setServiceCosts] = useState<ServiceCost[]>([]);
  const [regionCosts, setRegionCosts] = useState<RegionCost[]>([]);

  // Memorizar credencial ativa
  const activeCredential = useMemo(() => {
    return optionsCredentialId 
      ? credentials.find(c => c.id === optionsCredentialId)
      : credentials.find(c => c.is_active) || credentials[0];
  }, [credentials, optionsCredentialId]);

  // Função para carregar dados de uma credencial específica
  const loadDataForCredential = async (credentialId: number, timeFilterOrDays?: string | number, provider?: string) => {
    const dateRangeKey = customStartDate && customEndDate 
      ? `${customStartDate.toISOString()}-${customEndDate.toISOString()}`
      : '';
    
    const currentParams = loadingControl.createParamsKey(credentialId, timeFilterOrDays, provider, dateRangeKey);
    
    if (loadingControl.shouldSkipLoad(currentParams)) {
      return;
    }
    
    loadingControl.startLoading(currentParams);
    setLoading(true);
    setError(null);

    // Determinar range de datas
    let dateRange: { startDate?: Date; endDate?: Date } | undefined;
    let days = 30;

    if (customStartDate && customEndDate) {
      dateRange = { startDate: customStartDate, endDate: customEndDate };
    } else {
      days = typeof timeFilterOrDays === 'string' 
        ? timeFilterToDays(timeFilterOrDays) 
        : (timeFilterOrDays || 30);
    }

    try {
      const { trends, services, regions } = await fetchAllData(credentialId, days, dateRange, provider);

      // Atualizar estado com dados brutos
      setTrendData(trends);
      setServiceCosts(services);
      setRegionCosts(regions);

      // Transformar dados
      const topServicesData = transformServiceCostsToTopServices(services);
      const providerDist = calculateProviderDistribution(regions);
      const sparklineData = trends.map(t => t.total_cost);
      const summary = calculateSpendSummary(services, providerDist, sparklineData);

      setTopServices(topServicesData);
      setProviderDistribution(providerDist);
      setSpendSummary(summary);

    } catch (err: any) {
      setError(err.message || 'Failed to load data');
    } finally {
      loadingControl.finishLoading();
      setLoading(false);
    }
  };

  // Carregar dados automaticamente se houver credenciais
  useEffect(() => {
    if (credentials.length > 0 && activeCredential && !loadingControl.isLoading()) {
      const currentParams = `${activeCredential.id}-${timeFilter || '30'}-${providerName || 'all'}`;
      loadDataForCredential(activeCredential.id, timeFilter, providerName);
    }
  }, [credentials.length, activeCredential?.id, timeFilter, providerName]);

  return {
    loading,
    error,
    spendSummary,
    providerDistribution,
    topServices,
    trendData,
    serviceCosts,
    regionCosts,
    loadDataForCredential,
    hasCredentials: credentials.length > 0,
    activeCredential
  };
};
