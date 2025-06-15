import { useState, useEffect } from 'react';
import { analyticsService } from '@/api/client';
import { CategoryDistribution } from './useDashboardData';
import { format } from 'date-fns';

interface UseCategoryDistributionParams {
  timeFilter: string;
  customStartDate?: Date;
  customEndDate?: Date;
  credentialId?: string;
  providerName?: string;
}

const CATEGORY_COLORS = {
  'Computation': '#60A5FA',
  'Storage': '#F97316', 
  'Network': '#10B981',
  'Database': '#8B5CF6',
  'Security': '#EF4444',
  'AI/ML': '#F59E0B',
  'Monitoring': '#06B6D4',
  'Analytics': '#84CC16',
  'Others': '#EC4899'
};

export const useCategoryDistribution = ({
  timeFilter,
  customStartDate,
  customEndDate,
  credentialId,
  providerName
}: UseCategoryDistributionParams) => {
  const [categoryData, setCategoryData] = useState<CategoryDistribution[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategoryData = async () => {
      setLoading(true);
      setError(null);

      try {
        const params: {
          credentialId?: string;
          topN: number;
          startDate?: string;
          endDate?: string;
          days?: number;
          providerName?: string;
        } = {
          credentialId,
          topN: 10,
          providerName
        };

        // Determinar período baseado no timeFilter
        if (customStartDate && customEndDate) {
          params.startDate = format(customStartDate, 'yyyy-MM-dd');
          params.endDate = format(customEndDate, 'yyyy-MM-dd');
        } else if (timeFilter === 'previous-year') {
          // Ano anterior completo (2024)
          const currentYear = new Date().getFullYear();
          const previousYear = currentYear - 1;
          params.startDate = `${previousYear}-01-01`;
          params.endDate = `${previousYear}-12-31`;
        } else if (timeFilter === 'this-year') {
          // Este ano desde janeiro até hoje
          const currentYear = new Date().getFullYear();
          const today = new Date();
          params.startDate = `${currentYear}-01-01`;
          params.endDate = format(today, 'yyyy-MM-dd');
        } else {
          // Converter timeFilter para dias
          const dayMapping: { [key: string]: number } = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '12m': 365
          };
          params.days = dayMapping[timeFilter] || 30;
        }

        console.log('🔄 Calling getCategoryDistribution with params:', params);
        console.log('🔑 Token available:', !!localStorage.getItem('access_token'));
        
        const response = await analyticsService.getCategoryDistribution(params);
        console.log('✅ Category distribution response:', response.data);
        
        if (response.data?.category_breakdown) {
          const categories: CategoryDistribution[] = response.data.category_breakdown.map((item: {
            name: string;
            total_cost?: number;
          }) => ({
            name: item.name,
            value: item.total_cost || 0,
            color: CATEGORY_COLORS[item.name as keyof typeof CATEGORY_COLORS] || CATEGORY_COLORS.Others
          }));

          console.log('📊 Processed categories:', categories);
          setCategoryData(categories);
        } else {
          console.warn('⚠️ No category_breakdown in response:', response.data);
        }
      } catch (err: unknown) {
        console.error('❌ Error fetching category distribution:', err);
        const error = err as { response?: { status: number; data?: any }; message?: string };
        if (error.response?.status === 404) {
          // Endpoint não existe ainda, não é um erro crítico
          setError('Category distribution endpoint not yet implemented');
        } else if (error.response?.status === 401) {
          setError('Authentication required - please login');
          console.error('🔐 Authentication error - token may be expired');
        } else {
          setError(error.message || 'Failed to fetch category distribution');
          console.error('🚨 API Error details:', error.response?.data);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryData();
  }, [timeFilter, customStartDate, customEndDate, credentialId, providerName]);

  return {
    categoryData,
    loading,
    error,
    hasData: categoryData.length > 0
  };
};