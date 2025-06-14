
import { useState, useEffect, useRef, useMemo } from 'react';
import { useCredentials } from './useCredentials';
import { useAnalytics } from './useAnalytics';
import { timeFilterToDays } from '@/utils/timeFrame';
import type { 
  SpendSummary,
  ProviderDistribution,
  CategoryDistribution,
  TopService,
  Anomaly,
  SavingsOpportunities
} from './useDashboardData';
import type {
  TrendData,
  ServiceCost,
  RegionCost
} from '../types/api';

interface UseXCostDataOptions {
  timeFilter?: string;
  credentialId?: number;
}

export const useXCostData = (options: UseXCostDataOptions = {}) => {
  const { timeFilter, credentialId: optionsCredentialId } = options;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { credentials } = useCredentials();
  const { getTrend, getServiceCosts, getRegionCosts } = useAnalytics();

  // Estado para dados integrados
  const [spendSummary, setSpendSummary] = useState<SpendSummary | null>(null);
  const [providerDistribution, setProviderDistribution] = useState<ProviderDistribution[]>([]);
  const [topServices, setTopServices] = useState<TopService[]>([]);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [serviceCosts, setServiceCosts] = useState<ServiceCost[]>([]);
  const [regionCosts, setRegionCosts] = useState<RegionCost[]>([]);

  // Usar ref para evitar chamadas duplicadas
  const lastParamsRef = useRef<string>('');
  const isLoadingRef = useRef(false);

  // Memorizar credencial ativa para evitar recálculo
  const activeCredential = useMemo(() => {
    return optionsCredentialId 
      ? credentials.find(c => c.id === optionsCredentialId)
      : credentials.find(c => c.is_active) || credentials[0];
  }, [credentials, optionsCredentialId]);

  // Função para carregar dados de uma credencial específica
  const loadDataForCredential = async (credentialId: number, timeFilterOrDays?: string | number) => {
    // Criar chave única para os parâmetros atuais
    const currentParams = `${credentialId}-${timeFilterOrDays || '30'}`;
    
    // Evitar chamadas duplicadas
    if (isLoadingRef.current || currentParams === lastParamsRef.current) {
      return;
    }
    
    isLoadingRef.current = true;
    lastParamsRef.current = currentParams;
    setLoading(true);
    setError(null);

    // Calcular dias baseado no parâmetro
    const days = typeof timeFilterOrDays === 'string' 
      ? timeFilterToDays(timeFilterOrDays) 
      : (timeFilterOrDays || 30);

    try {
      console.log(`🔄 X Cost API call: ${currentParams}`);
      
      const [trends, services, regions] = await Promise.all([
        getTrend(credentialId, days).catch(err => {
          console.log('⚠️ Trend data not available:', err.message);
          return [];
        }),
        getServiceCosts(credentialId, days).catch(err => {
          console.log('⚠️ Service costs not available:', err.message);
          return [];
        }),
        getRegionCosts(credentialId, days).catch(err => {
          console.log('⚠️ Region costs not available:', err.message);
          return [];
        })
      ]);

      // Converter dados da API para o formato do dashboard com verificações de segurança
      const safeTrends = Array.isArray(trends) ? trends : [];
      const safeServices = Array.isArray(services) ? services : [];
      const safeRegions = Array.isArray(regions) ? regions : [];

      setTrendData(safeTrends);
      setServiceCosts(safeServices);
      setRegionCosts(safeRegions);

      // Converter ServiceCost[] para TopService[]
      const convertedTopServices: TopService[] = safeServices.slice(0, 5).map((service, index) => ({
        id: `service-${index}`,
        name: service.service_name,
        provider: 'AWS', // Assumindo AWS por padrão
        currentSpend: service.cost,
        previousSpend: service.cost - (service.cost * service.change_from_previous / 100),
        trend: service.change_from_previous
      }));
      setTopServices(convertedTopServices);

      // Criar distribuição por provedor baseada nos custos por região
      const providerDist: ProviderDistribution[] = safeRegions.map(region => ({
        name: region.region,
        value: region.cost,
        color: getColorForProvider(region.region)
      }));
      setProviderDistribution(providerDist);

      // Criar resumo de gastos
      const totalSpend = safeServices.reduce((total, service) => total + service.cost, 0);
      const previousTotalSpend = safeServices.reduce((total, service) => {
        const previousCost = service.cost - (service.cost * service.change_from_previous / 100);
        return total + previousCost;
      }, 0);
      
      const changePercentage = previousTotalSpend > 0 
        ? ((totalSpend - previousTotalSpend) / previousTotalSpend) * 100
        : 0;

      // Criar sparkline data baseado nos trends ou dados simulados
      const sparklineData = safeTrends.length > 0 
        ? safeTrends.map(t => t.total_cost)
        : [totalSpend * 0.9, totalSpend * 0.95, totalSpend * 1.05, totalSpend * 0.98, totalSpend * 1.02, totalSpend];

      const summary: SpendSummary = {
        totalSpend,
        currency: 'R$',
        previousPeriodChange: changePercentage,
        sparklineData,
        providerBreakdown: providerDist.map(p => ({
          name: p.name,
          value: totalSpend > 0 ? (p.value / totalSpend) * 100 : 0,
          color: p.color
        }))
      };
      setSpendSummary(summary);

      console.log('X Cost data loaded successfully');
    } catch (err: any) {
      console.error('Error loading X Cost data:', err);
      setError(err.message || 'Failed to load data');
    } finally {
      isLoadingRef.current = false;
      setLoading(false);
    }
  };

  // Função auxiliar para obter cores dos provedores
  const getColorForProvider = (region: string): string => {
    if (region.includes('us-') || region.includes('sa-')) return '#FF9900'; // AWS
    if (region.includes('East') || region.includes('Brazil')) return '#0078D4'; // Azure
    if (region.includes('central')) return '#4285F4'; // GCP
    return '#F80000'; // Oracle Cloud
  };

  // Carregar dados automaticamente se houver credenciais
  useEffect(() => {
    if (credentials.length > 0 && activeCredential && !isLoadingRef.current) {
      const currentParams = `${activeCredential.id}-${timeFilter || '30'}`;
      
      // Só carregar se os parâmetros mudaram
      if (currentParams !== lastParamsRef.current) {
        loadDataForCredential(activeCredential.id, timeFilter);
      }
    }
  }, [credentials.length, activeCredential?.id, timeFilter]);

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
