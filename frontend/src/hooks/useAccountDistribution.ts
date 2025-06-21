import { useState, useEffect } from 'react';
import { apiClient } from '@/api/client';
import { getDateRangeFromTimeFilter } from '@/utils/timeFrame';

interface AccountDistributionItem {
  account_id: string;
  billing_account_name: string;
  percentage: number;
  total_cost: number;
}

interface UseAccountDistributionParams {
  providerName: string;
  timeFilter?: string;
  credentialId?: string;
}

interface UseAccountDistributionReturn {
  accountData: AccountDistributionItem[];
  loading: boolean;
  error: string | null;
  hasData: boolean;
}

export function useAccountDistribution({
  providerName,
  timeFilter = '30d',
  credentialId
}: UseAccountDistributionParams): UseAccountDistributionReturn {
  const [accountData, setAccountData] = useState<AccountDistributionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasData, setHasData] = useState(false);

  useEffect(() => {
    // Só buscar se tiver providerName
    if (!providerName) {
      setAccountData([]);
      setHasData(false);
      return;
    }

    // Corrigir timeFilter para formatos aceitos pelo backend
    let apiTimeFilter = timeFilter;
    if (timeFilter === 'previous-year') {
      apiTimeFilter = '365d';
    } else if (timeFilter === 'this-year') {
      // Calcular dias desde 1º de janeiro até hoje
      const { days } = getDateRangeFromTimeFilter('this-year');
      apiTimeFilter = `${days}d`;
    }

    const fetchAccountDistribution = async () => {
      setLoading(true);
      setError(null);

      try {
        console.log('🔍 Fetching account distribution for provider:', providerName);
        
        // Construir URL com parâmetros
        const params = new URLSearchParams();
        params.append('provider', providerName);
        params.append('time_filter', apiTimeFilter);
        
        if (credentialId) {
          params.append('credential_id', credentialId);
        }

        const response = await apiClient.get(`/api/v1/dashboard/account-distribution?${params.toString()}`);
        
        console.log('✅ Account distribution API response:', response.data);

        // Backend returns data in response.data.data format
        if (response.data && response.data.success && Array.isArray(response.data.data)) {
          setAccountData(response.data.data);
          setHasData(response.data.data.length > 0);
          console.log('✅ Account data set:', response.data.data);
        } else {
          console.warn('⚠️ Account distribution API returned invalid data format:', response.data);
          setAccountData([]);
          setHasData(false);
        }
      } catch (error: any) {
        console.error('❌ Error fetching account distribution:', error);
        
        if (error.response?.status === 401) {
          setError('Token expired - please refresh the page and set a new token');
          console.error('🔐 Authentication error - token expired');
        } else if (error.response?.status === 404) {
          setError('Account distribution endpoint not found - backend may not implement this feature yet');
          console.error('🚫 Account distribution endpoint not implemented in backend');
        } else {
          setError(error.response?.data?.detail || error.message || 'Failed to fetch account distribution');
        }
        
        setAccountData([]);
        setHasData(false);
      } finally {
        setLoading(false);
      }
    };

    fetchAccountDistribution();
  }, [providerName, timeFilter, credentialId]);

  return {
    accountData,
    loading,
    error,
    hasData
  };
}