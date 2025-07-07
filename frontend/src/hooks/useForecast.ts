import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/api/client';
import { ForecastResponse, ForecastDataPoint } from '@/types/api';

interface UseForecastParams {
  credentialId?: string;
  months?: number;
  startDate?: string;
  endDate?: string;
  providerName?: string;
  enabled?: boolean;
}

interface ForecastData {
  data: ForecastDataPoint[];
  metadata?: {
    model_accuracy: number;
    confidence_level: number;
    data_completeness: number;
    forecast_method: string;
  };
  budget_info?: {
    total_budget: number;
    monthly_budget: number;
    budget_exceeded_months: string[];
  };
}

// Dados mock para fallback
const mockForecastData: ForecastDataPoint[] = [
  { month: 'Jan', actual: 280000, budget: 350000 },
  { month: 'Feb', actual: 320000, budget: 350000 },
  { month: 'Mar', actual: 290000, budget: 350000 },
  { month: 'Apr', actual: 310000, budget: 350000 },
  { month: 'May', actual: 340000, budget: 350000 },
  { month: 'Jun', forecast: 360000, budget: 350000 },
  { month: 'Jul', forecast: 370000, budget: 350000 },
];

export function useForecast({
  credentialId,
  months = 7,
  startDate,
  endDate,
  providerName,
  enabled = true
}: UseForecastParams = {}) {
  const [forecastData, setForecastData] = useState<ForecastData>({
    data: mockForecastData,
    metadata: {
      model_accuracy: 85,
      confidence_level: 90,
      data_completeness: 95,
      forecast_method: 'mock'
    }
  });
  const [isUsingMockData, setIsUsingMockData] = useState(true);

  // Query para buscar dados reais da API
  const {
    data: apiData,
    isLoading,
    isError,
    error,
    refetch
  } = useQuery<ForecastResponse>({
    queryKey: [
      'forecast',
      credentialId,
      months,
      startDate,
      endDate,
      providerName
    ],
    queryFn: async () => {
      const response = await analyticsService.getForecastData({
        credentialId,
        months,
        startDate,
        endDate,
        providerName
      });
      return response.data.data;
    },
    enabled: enabled,
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutos
    cacheTime: 10 * 60 * 1000, // 10 minutos
  });

  // Atualizar dados quando a API responder
  useEffect(() => {
    if (apiData?.forecast_data && apiData.forecast_data.length > 0) {
      setForecastData({
        data: apiData.forecast_data,
        metadata: apiData.metadata,
        budget_info: apiData.budget_info
      });
      setIsUsingMockData(false);
    } else if (isError) {
      // Em caso de erro, manter dados mock
      setForecastData({
        data: mockForecastData,
        metadata: {
          model_accuracy: 85,
          confidence_level: 90,
          data_completeness: 95,
          forecast_method: 'mock'
        }
      });
      setIsUsingMockData(true);
    }
  }, [apiData, isError]);

  // Função para transformar dados da API para o formato esperado pelo componente
  const transformForecastData = (data: ForecastDataPoint[], budgetInfo?: any): ForecastDataPoint[] => {
    const monthlyBudget = budgetInfo?.monthly_budget;
    
    return data.map(point => ({
      month: point.month,
      actual: point.actual,
      forecast: point.forecast,
      budget: monthlyBudget || point.budget, // Usar budget da API se disponível
      variance: point.variance,
      confidence_interval: point.confidence_interval
    }));
  };

  return {
    data: transformForecastData(forecastData.data, forecastData.budget_info),
    metadata: forecastData.metadata,
    budget_info: forecastData.budget_info,
    isLoading,
    isError,
    error,
    isUsingMockData,
    refetch
  };
}