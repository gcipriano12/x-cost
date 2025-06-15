import { useAnalytics } from '../useAnalytics';
import type {
  TrendData,
  ServiceCost,
  RegionCost
} from '../../types/api';

interface DateRange {
  startDate?: Date;
  endDate?: Date;
}

export const useApiDataFetcher = () => {
  const { getTrend, getServiceCosts, getRegionCosts } = useAnalytics();

  const fetchAllData = async (
    credentialId: number,
    days: number,
    dateRange?: DateRange,
    provider?: string
  ): Promise<{
    trends: TrendData[];
    services: ServiceCost[];
    regions: RegionCost[];
  }> => {
    const [trends, services, regions] = await Promise.all([
      getTrend(credentialId, days, dateRange, provider).catch(() => []),
      getServiceCosts(credentialId, days, dateRange, provider).catch(() => []),
      getRegionCosts(credentialId, days, dateRange, provider).catch(() => [])
    ]);

    return {
      trends: Array.isArray(trends) ? trends : [],
      services: Array.isArray(services) ? services : [],
      regions: Array.isArray(regions) ? regions : []
    };
  };

  return { fetchAllData };
};
