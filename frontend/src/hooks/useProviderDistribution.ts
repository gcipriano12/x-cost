import { useState, useEffect } from 'react';
import { analyticsService } from '@/api/client';
import { getProviderColor } from '@/utils/providerColors';

interface ProviderBreakdown {
  name: string;
  value: number;
  color: string;
}

interface UseProviderDistributionParams {
  timeFilter: string;
  customStartDate?: Date;
  customEndDate?: Date;
  credentialId?: string;
  providerName?: string;
}

export const useProviderDistribution = ({
  timeFilter,
  customStartDate,
  customEndDate,
  credentialId,
  providerName
}: UseProviderDistributionParams) => {
  const [providerData, setProviderData] = useState<ProviderBreakdown[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProviderData = async () => {
      setLoading(true);
      setError(null);

      try {
        const params: {
          credentialId?: string;
          topN: number;
          days?: number;
          providerName?: string;
        } = {
          credentialId,
          topN: 10
        };
        
        // Só adicionar providerName se realmente existe
        if (providerName) {
          params.providerName = providerName;
        }

        // Determinar período baseado no timeFilter
        if (timeFilter === 'previous-year') {
          params.days = 365;
        } else if (timeFilter === 'current-year') {
          params.days = 365;
        } else if (timeFilter === '7-days') {
          params.days = 7;
        } else if (timeFilter === '30-days') {
          params.days = 30;
        } else if (timeFilter === '90-days') {
          params.days = 90;
        } else {
          params.days = 30; // default
        }

        console.log('🔍 Fetching provider distribution with params:', params);

        const response = await analyticsService.getProviderDistribution(params);
        
        console.log('📊 Provider distribution API response:', response.data);

        if (response.data?.data?.provider_breakdown && Array.isArray(response.data.data.provider_breakdown)) {
          const providers = response.data.data.provider_breakdown.map((item: {
            provider_name: string;
            total_cost: number;
            percentage_of_total: number;
          }) => ({
            name: item.provider_name,
            value: item.percentage_of_total || 0,
            color: getProviderColor(item.provider_name)
          }));

          console.log('📊 Processed providers:', providers);
          setProviderData(providers);
        } else {
          console.warn('⚠️ No provider_breakdown in response or invalid format:', response.data);
          setProviderData([]);
        }
      } catch (err: unknown) {
        console.error('❌ Error fetching provider distribution:', err);
        const error = err as { response?: { status: number; data?: any }; message?: string };
        if (error.response?.status === 404) {
          setError('Provider distribution endpoint not yet implemented');
        } else if (error.response?.status === 401) {
          setError('Authentication required - please login');
          console.error('🔐 Authentication error - token may be expired');
        } else {
          setError(error.message || 'Failed to fetch provider distribution');
          console.error('🚨 API Error details:', error.response?.data);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProviderData();
  }, [timeFilter, customStartDate, customEndDate, credentialId, providerName]);

  return {
    providerData,
    loading,
    error,
    hasData: providerData.length > 0
  };
};
