import { getProviderFromRegion, getProviderColor } from '@/utils/providerColors';
import type { 
  SpendSummary,
  ProviderDistribution,
  TopService
} from '../useDashboardData';
import type {
  ServiceCost,
  RegionCost
} from '../../types/api';

export const transformServiceCostsToTopServices = (services: ServiceCost[]): TopService[] => {
  return services.slice(0, 5).map((service, index) => ({
    id: `service-${index}`,
    name: service.service_name,
    provider: 'AWS', // TODO: Determinar provider real
    currentSpend: service.cost,
    previousSpend: service.cost - (service.cost * service.change_from_previous / 100),
    trend: service.change_from_previous
  }));
};

export const calculateProviderDistribution = (regions: RegionCost[]): ProviderDistribution[] => {
  const providerCosts = new Map<string, number>();
  
  regions.forEach(region => {
    const provider = getProviderFromRegion(region.region);
    const currentCost = providerCosts.get(provider) || 0;
    providerCosts.set(provider, currentCost + region.cost);
  });

  return Array.from(providerCosts.entries()).map(([provider, cost]) => ({
    name: provider,
    value: cost,
    color: getProviderColor(provider)
  }));
};

export const calculateSpendSummary = (
  services: ServiceCost[],
  providerDistribution: ProviderDistribution[],
  trendData: number[]
): SpendSummary => {
  const totalSpend = services.reduce((total, service) => total + service.cost, 0);
  const previousTotalSpend = services.reduce((total, service) => {
    const previousCost = service.cost - (service.cost * service.change_from_previous / 100);
    return total + previousCost;
  }, 0);
  
  const changePercentage = previousTotalSpend > 0 
    ? ((totalSpend - previousTotalSpend) / previousTotalSpend) * 100
    : 0;

  // Encontrar o provedor com maior custo
  const topProvider = providerDistribution.reduce(
    (max, current) => current.value > max.value ? current : max,
    { name: 'AWS', value: 0 }
  );

  const sparklineData = trendData.length > 0 
    ? trendData
    : [totalSpend * 0.9, totalSpend * 0.95, totalSpend * 1.05, totalSpend * 0.98, totalSpend * 1.02, totalSpend];

  return {
    totalSpend,
    currency: '$',
    previousPeriodChange: changePercentage,
    sparklineData,
    providerBreakdown: providerDistribution.map(p => ({
      name: p.name,
      value: totalSpend > 0 ? Math.round((p.value / totalSpend) * 1000) / 10 : 0,
      color: getProviderColor(p.name)
    })),
    topProvider: {
      name: topProvider.name,
      cost: topProvider.value
    }
  };
};
