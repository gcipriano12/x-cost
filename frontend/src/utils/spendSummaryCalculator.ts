import { getProviderColor } from './providerColors';
import type { 
  SpendSummary,
  ProviderDistribution
} from '../hooks/useDashboardData';
import type {
  TrendData,
  ServiceCost
} from '../types/api';

interface SpendSummaryOptions {
  services: ServiceCost[];
  trends: TrendData[];
  providerDistribution: ProviderDistribution[];
  topProvider: { name: string; cost: number };
}

export const calculateSpendSummary = ({
  services,
  trends,
  providerDistribution,
  topProvider
}: SpendSummaryOptions): SpendSummary => {
  const totalSpend = services.reduce((total, service) => total + service.cost, 0);
  const previousTotalSpend = services.reduce((total, service) => {
    const previousCost = service.cost - (service.cost * service.change_from_previous / 100);
    return total + previousCost;
  }, 0);
  
  const changePercentage = previousTotalSpend > 0 
    ? ((totalSpend - previousTotalSpend) / previousTotalSpend) * 100
    : 0;

  // Create sparkline data based on trends or simulated data
  const sparklineData = trends.length > 0 
    ? trends.map(t => t.total_cost)
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
    topProvider
  };
};
