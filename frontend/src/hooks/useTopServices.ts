import { useState, useEffect } from 'react';
import { analyticsService } from '@/api/client';

export interface TopServiceItem {
  id: string;
  service_name: string;
  provider: string;
  cost: number;
  change_from_previous: number;
  region?: string;
  currency: string;
}

export interface TopServicesResponse {
  services: TopServiceItem[];
  total_services: number;
  period: {
    start_date: string;
    end_date: string;
  };
}

interface UseTopServicesParams {
  credentialId?: string;
  startDate?: string;
  endDate?: string;
  providerName?: string;
  limit?: number;
  enabled?: boolean;
}

export const useTopServices = ({
  credentialId,
  startDate,
  endDate,
  providerName,
  limit = 5,
  enabled = true
}: UseTopServicesParams) => {
  const [data, setData] = useState<TopServiceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUsingMockData, setIsUsingMockData] = useState(true);

  const fetchTopServices = async () => {
    if (!enabled || !credentialId) {
      setIsUsingMockData(true);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await analyticsService.getTopServices({
        credentialId,
        startDate,
        endDate,
        providerName,
        limit
      });

      if (response.data && response.data.status === 'success') {
        const servicesData = response.data.data.services || [];
        setData(servicesData);
        setIsUsingMockData(servicesData.length === 0);
      } else {
        setError('Invalid response format');
        setIsUsingMockData(true);
      }
    } catch (err: any) {
      console.error('Error fetching top services:', err);
      setError(err.message || 'Failed to fetch top services');
      setIsUsingMockData(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTopServices();
  }, [credentialId, startDate, endDate, providerName, limit, enabled]);

  return {
    data,
    loading,
    error,
    isUsingMockData,
    refetch: fetchTopServices
  };
};