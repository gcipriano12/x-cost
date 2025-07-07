import React, { useState, useCallback } from 'react';
import { TopServicesCard } from '../TopServicesCard';
import { SpendingForecastCard } from '../SpendingForecastCard';
import { Layers } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useForecast } from '@/hooks/useForecast';

interface ServicesSectionProps {
  topServicesData: any[];
  currency: string;
  credentialId?: string;
  providerName?: string;
  timeFilter?: string;
  isTopServicesUsingMockData?: boolean;
}

export function ServicesSection({ 
  topServicesData,
  currency, 
  credentialId, 
  providerName,
  timeFilter,
  isTopServicesUsingMockData = false
}: ServicesSectionProps) {
  const { t } = useTranslation();
  
  // Converter timeFilter para parâmetros de data
  const getDateRangeFromTimeFilter = (filter?: string) => {
    const now = new Date();
    let startDate: string | undefined;
    let endDate: string | undefined;
    
    switch (filter) {
      case '7-days':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        endDate = now.toISOString().split('T')[0];
        break;
      case '30-days':
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        endDate = now.toISOString().split('T')[0];
        break;
      case '90-days':
        startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        endDate = now.toISOString().split('T')[0];
        break;
      case 'current-year':
        startDate = new Date(now.getFullYear(), 0, 1).toISOString().split('T')[0];
        endDate = now.toISOString().split('T')[0];
        break;
      case 'previous-year':
        startDate = new Date(now.getFullYear() - 1, 0, 1).toISOString().split('T')[0];
        endDate = new Date(now.getFullYear() - 1, 11, 31).toISOString().split('T')[0];
        break;
      default:
        // Default para último mês
        startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
        endDate = now.toISOString().split('T')[0];
    }
    
    return { startDate, endDate };
  };

  // Para forecast, sempre usar um período histórico amplo (12 meses)
  // independente do timeFilter, pois o forecast precisa de dados históricos suficientes
  const getForecastDateRange = () => {
    const now = new Date();
    const startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate()).toISOString().split('T')[0]; // 12 meses atrás
    const endDate = now.toISOString().split('T')[0]; // hoje
    return { startDate, endDate };
  };

  const { startDate: topServicesStartDate, endDate: topServicesEndDate } = getDateRangeFromTimeFilter(timeFilter);
  const { startDate: forecastStartDate, endDate: forecastEndDate } = getForecastDateRange();
  
  console.log('📊 ServicesSection dates:', {
    timeFilter,
    topServices: { start: topServicesStartDate, end: topServicesEndDate },
    forecast: { start: forecastStartDate, end: forecastEndDate }
  });
  
  // Usar hook de forecast para buscar dados da API
  const { 
    data: forecastData, 
    metadata: forecastMetadata,
    budget_info: budgetInfo,
    isLoading: forecastLoading, 
    isUsingMockData 
  } = useForecast({
    credentialId,
    providerName,
    startDate: forecastStartDate,
    endDate: forecastEndDate,
    months: 7,
    enabled: true
  });

  return (
    <div className="mb-6">
      <div className="flex items-center mb-4">
        <Layers className="h-5 w-5 mr-2 text-green-600" />
        <h2 className="text-lg font-semibold">{t('sections.servicesAndForecasts')}</h2>
      </div>
      
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="col-span-1">
          <TopServicesCard 
            services={topServicesData}
            currency={currency}
            isUsingMockData={isTopServicesUsingMockData}
          />
        </div>

        <div className="col-span-1">
          <SpendingForecastCard 
            data={forecastData}
            currency={currency}
            budgetInfo={budgetInfo}
            metadata={forecastMetadata}
            isUsingMockData={isUsingMockData}
          />
        </div>
      </div>
    </div>
  );
}
