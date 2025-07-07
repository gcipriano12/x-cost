import { useState, useEffect, useCallback } from 'react';
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
  pagination: {
    page: number;
    page_size: number;
    total_items: number;
    total_pages: number;
    has_next: boolean;
    has_previous: boolean;
  };
}

interface UseTopServicesParams {
  credentialId?: string;
  startDate?: string;
  endDate?: string;
  providerName?: string;
  page_size?: number;
  page?: number;
  sort_by?: string;
  sort_order?: string;
  enabled?: boolean;
}


// Map provider to credential ID
const getCredentialIdByProvider = (provider?: string): string => {
  switch (provider?.toLowerCase()) {
    case 'aws':
      return '1'; // aws-local-test
    case 'azure':
      return '2'; // azure-dev-subscription  
    case 'gcp':
      return '3'; // gcp-project-main
    case 'oracle cloud':
    case 'oracle':
      return '4'; // oracle-cloud-dev
    default:
      return '1'; // Default to AWS (for "All" or undefined, use AWS credential)
  }
};


export const useTopServices = ({
  credentialId,
  startDate,
  endDate,
  providerName,
  page_size = 10,
  page = 1,
  sort_by = 'cost',
  sort_order = 'desc',
  enabled = true
}: UseTopServicesParams) => {
  const [data, setData] = useState<TopServiceItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isUsingMockData, setIsUsingMockData] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    page_size: 10,
    total_pages: 1,
    total_items: 0,
    has_next: false,
    has_previous: false
  });
  const [totalServices, setTotalServices] = useState(0);
  
  // Initialize with empty state
  useEffect(() => {
    setIsUsingMockData(true); // Will be set to false if API succeeds
  }, []);


  const fetchTopServices = useCallback(async () => {
    if (!enabled) {
      return;
    }

    setLoading(true);
    setError(null);
    
    console.log('🔍 Fetching Top Services from API:', {
      credentialId,
      startDate,
      endDate,
      providerName,
      page_size,
      page,
      sort_by,
      sort_order
    });

    try {
      // Determine which credential to use based on provider filter
      const effectiveCredentialId = credentialId || getCredentialIdByProvider(providerName);
      
      const requestParams = {
        credentialId: effectiveCredentialId,
        startDate,
        endDate,
        providerName, // Pass the provider filter to the API
        page_size,
        page,
        sort_by,
        sort_order
      };
      
      console.log('📡 Top Services - Provider Filter:', providerName);
      console.log('📡 Top Services - Selected Credential ID:', effectiveCredentialId);
      console.log('📡 Top Services - API Request Params:', requestParams);
      console.log('🔑 Token available:', !!localStorage.getItem('access_token'));
      
      const response = await analyticsService.getTopServices(requestParams);

      console.log('📊 Top Services API Response:', response);

      if (response.data && response.data.status === 'success') {
        const servicesData = response.data.data.services || [];
        const responseData = response.data.data;
        
        console.log('✅ Top Services API Data:', {
          servicesData: servicesData.length,
          responseData,
          totalServices: responseData.total_services,
          pagination: responseData.pagination
        });
        
        setData(servicesData);
        setTotalServices(responseData.total_services || 0);
        setIsUsingMockData(servicesData.length === 0);
        
        // Update pagination info
        if (responseData.pagination) {
          console.log('✅ Using backend pagination info:', responseData.pagination);
          setPagination({
            page: responseData.pagination.page || page,
            page_size: responseData.pagination.page_size || page_size,
            total_pages: responseData.pagination.total_pages || 1,
            total_items: responseData.pagination.total_items || responseData.total_services || 0,
            has_next: responseData.pagination.has_next || false,
            has_previous: responseData.pagination.has_previous || false
          });
        } else {
          // Backend doesn't support pagination - just show current page
          console.log('⚠️ Backend pagination not implemented - showing fixed results');
          setPagination({
            page: 1,
            page_size: servicesData.length,
            total_pages: 1,
            total_items: servicesData.length,
            has_next: false,
            has_previous: false
          });
        }
        
        console.log('📄 Pagination updated:', {
          page,
          page_size,
          total_pages: responseData.pagination?.total_pages || Math.ceil((responseData.total_services || 0) / page_size),
          total_items: responseData.pagination?.total_items || responseData.total_services || 0,
          calculation: {
            totalServices: responseData.total_services,
            page_size,
            calculated_pages: Math.ceil((responseData.total_services || 0) / page_size)
          }
        });
        
      } else {
        console.error('❌ Invalid API response format:', response);
        setError('Invalid response format');
        setData([]);
        setTotalServices(0);
        setIsUsingMockData(true);
      }
    } catch (err: unknown) {
      console.error('❌ Error fetching top services:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch top services');
      setData([]);
      setTotalServices(0);
      setIsUsingMockData(true);
    } finally {
      setLoading(false);
    }
  }, [credentialId, startDate, endDate, providerName, page_size, page, sort_by, sort_order, enabled]);

  useEffect(() => {
    fetchTopServices();
  }, [fetchTopServices]);

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