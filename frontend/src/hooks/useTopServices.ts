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
  pagination?: {
    page: number;
    per_page: number;
    total_pages: number;
    total_items: number;
  };
}

interface UseTopServicesParams {
  credentialId?: string;
  startDate?: string;
  endDate?: string;
  providerName?: string;
  limit?: number;
  page?: number;
  enabled?: boolean;
}

export const useTopServices = ({
  credentialId,
  startDate,
  endDate,
  providerName,
  limit = 5,
  page = 1,
  enabled = true
}: UseTopServicesParams) => {
  const [data, setData] = useState<TopServiceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUsingMockData, setIsUsingMockData] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 5,
    total_pages: 1,
    total_items: 0
  });
  const [totalServices, setTotalServices] = useState(0);

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
        limit,
        page
      });

      if (response.data && response.data.status === 'success') {
        const servicesData = response.data.data.services || [];
        const responseData = response.data.data;
        
        setData(servicesData);
        setTotalServices(responseData.total_services || 0);
        setIsUsingMockData(servicesData.length === 0);
        
        // Update pagination info
        if (responseData.pagination) {
          setPagination({
            page: responseData.pagination.page || page,
            per_page: responseData.pagination.per_page || limit,
            total_pages: responseData.pagination.total_pages || 1,
            total_items: responseData.pagination.total_items || responseData.total_services || 0
          });
        } else {
          // Fallback if no pagination info from backend
          const totalPages = Math.ceil((responseData.total_services || 0) / limit);
          setPagination({
            page: page,
            per_page: limit,
            total_pages: totalPages,
            total_items: responseData.total_services || 0
          });
        }
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
  }, [credentialId, startDate, endDate, providerName, limit, page, enabled]);

  return {
    data,
    loading,
    error,
    isUsingMockData,
    totalServices,
    pagination,
    refetch: fetchTopServices
  };
};