import { useState, useEffect } from 'react';
import { analyticsService } from '@/api/client';
import { CategoryDistribution } from './useDashboardData';
import { format } from 'date-fns';
import { getCategoryColor } from '@/utils/chartColors';

interface UseCategoryDistributionParams {
  timeFilter: string;
  customStartDate?: Date;
  customEndDate?: Date;
  credentialId?: string;
  providerName?: string;
}

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
        console.log('🔑 Token value:', localStorage.getItem('access_token')?.substring(0, 50) + '...');
        
        const response = await analyticsService.getCategoryDistribution(params);
        console.log('✅ Category distribution response:', response);
        console.log('✅ Response data structure:', JSON.stringify(response.data, null, 2));
        
        // Verificar se a resposta tem estrutura aninhada (response.data.data.category_breakdown)
        const categoryBreakdown = response.data?.data?.category_breakdown || response.data?.category_breakdown;
        
        if (categoryBreakdown && Array.isArray(categoryBreakdown)) {
          console.log('✅ Found category_breakdown with', categoryBreakdown.length, 'items');
          
          const categories: CategoryDistribution[] = categoryBreakdown
            .filter((item: any) => item && item.category && typeof item.total_cost === 'number')
            .map((item: {
              category: string;
              total_cost: number;
              percentage_of_total: number;
            }) => ({
              name: item.category || 'Unknown',
              value: item.total_cost || 0, // Use absolute cost values
              color: getCategoryColor(item.category || 'Unknown')
            }));

          console.log('📊 Processed categories:', categories);
          setCategoryData(categories);
        } else {
          console.warn('⚠️ No category_breakdown in response or invalid format. Response structure:', {
            hasData: !!response.data,
            hasNestedData: !!response.data?.data,
            hasCategoryBreakdown: !!response.data?.category_breakdown,
            hasNestedCategoryBreakdown: !!response.data?.data?.category_breakdown,
            isArray: Array.isArray(categoryBreakdown),
            categoryBreakdownType: typeof categoryBreakdown,
            categoryBreakdownValue: categoryBreakdown
          });
          setCategoryData([]); // Sempre set empty array para evitar undefined
        }
      } catch (err: unknown) {
        console.error('❌ Error fetching category distribution:', err);
        const error = err as { response?: { status: number; data?: any }; message?: string };
        if (error.response?.status === 404) {
          // Endpoint não existe ainda, não é um erro crítico
          setError('Category distribution endpoint not yet implemented');
        } else if (error.response?.status === 401) {
          setError('Token expired - please refresh the page and set a new token');
          console.error('🔐 Authentication error - token expired. Please run the token script again.');
          console.error('🔧 Run in console: localStorage.setItem("access_token", "NEW_TOKEN_HERE"); window.location.reload();');
        } else {
          setError(error.message || 'Failed to fetch category distribution');
          console.error('🚨 API Error details:', error.response?.data);
        }
        
        // Garantir que sempre temos um array, mesmo em caso de erro
        setCategoryData([]);
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