import { getProviderFromRegion, getProviderColor } from './providerColors';
import type { 
  SpendSummary,
  ProviderDistribution,
  TopService
} from '../hooks/useDashboardData';
import type {
  ServiceCost,
  RegionCost
} from '../types/api';

export const transformServiceCostsToTopServices = (services: ServiceCost[]): TopService[] => {
  return services.slice(0, 5).map((service, index) => ({
    id: `service-${index}`,
    name: service.service_name,
    provider: 'AWS', // Default provider
    currentSpend: service.cost,
    previousSpend: service.cost - (service.cost * service.change_from_previous / 100),
    trend: service.change_from_previous
  }));
};

export const createProviderDistribution = (regions: RegionCost[]): ProviderDistribution[] => {
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

export const findHighestSpendProvider = (regions: RegionCost[]) => {
  const providerCosts = new Map<string, number>();
  
  regions.forEach(region => {
    const provider = getProviderFromRegion(region.region);
    const currentCost = providerCosts.get(provider) || 0;
    providerCosts.set(provider, currentCost + region.cost);
  });

  let highestSpendProvider = { name: 'AWS', cost: 0 };
  for (const [provider, cost] of providerCosts.entries()) {
    if (cost > highestSpendProvider.cost) {
      highestSpendProvider = { name: provider, cost };
    }
  }

  return highestSpendProvider;
};
