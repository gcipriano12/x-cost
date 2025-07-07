import React, { useState, useCallback } from 'react';
import { TopServicesCard } from '../TopServicesCard';
import { SpendingForecastCard } from '../SpendingForecastCard';
import { Layers } from 'lucide-react';
import { useTranslation } from 'react-i18next';
import { useForecast } from '@/hooks/useForecast';
import { useTopServices } from '@/hooks/useTopServices';

interface ServicesSectionProps {
  currency: string;
  credentialId?: string;
  providerName?: string;
  timeFilter?: string;
}

export function ServicesSection({ 
  currency, 
  credentialId, 
  providerName,
  timeFilter
}: ServicesSectionProps) {
  const { t } = useTranslation();
  
  // Pagination state for Top Services
  const [topServicesPage, setTopServicesPage] = useState(1);
  const [topServicesSortBy, setTopServicesSortBy] = useState('cost');
  const [topServicesSortOrder, setTopServicesSortOrder] = useState('desc');
  const topServicesPageSize = 5; // Fixed page size like Anomalies/Savings
  
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
  
  // Pagination handlers
  const handleTopServicesPageChange = useCallback((page: number) => {
    setTopServicesPage(page);
  }, []);
  
  // Sorting handlers
  const handleTopServicesSortChange = useCallback((sortBy: string, sortOrder: string) => {
    setTopServicesSortBy(sortBy);
    setTopServicesSortOrder(sortOrder);
    setTopServicesPage(1); // Reset to first page when sorting changes
  }, []);
  
  // Use Top Services hook with pagination
  const {
    data: topServicesApiData,
    totalServices,
    pagination: topServicesPagination,
    isUsingMockData: topServicesUsingMockData
  } = useTopServices({
    credentialId,
    startDate: topServicesStartDate,
    endDate: topServicesEndDate,
    providerName,
    page_size: topServicesPageSize,
    page: topServicesPage,
    sort_by: topServicesSortBy,
    sort_order: topServicesSortOrder,
    enabled: true
  });
  
  // Convert API data to component format
  const formattedTopServicesData = topServicesApiData.map(service => ({
    id: service.id,
    name: service.service_name,
    provider: service.provider,
    currentSpend: service.cost,
    previousSpend: service.cost * (1 - service.change_from_previous / 100), // Calculate previous spend
    trend: service.change_from_previous
  }));
  
  console.log('🔍 Top Services Debug:', {
    topServicesApiData,
    formattedTopServicesData,
    totalServices,
    topServicesPagination,
    topServicesUsingMockData,
    credentialId,
    providerName,
    startDate: topServicesStartDate,
    endDate: topServicesEndDate,
    apiDataLength: topServicesApiData.length,
    timeFilter
  });
  
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
      
      <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
        <div className="col-span-1">
          <TopServicesCard 
            services={formattedTopServicesData}
            currency={currency}
            isUsingMockData={topServicesUsingMockData}
            totalServices={totalServices}
            currentPage={topServicesPagination.page}
            pageSize={topServicesPagination.page_size}
            totalPages={topServicesPagination.total_pages}
            hasNext={topServicesPagination.has_next}
            hasPrevious={topServicesPagination.has_previous}
            onPageChange={handleTopServicesPageChange}
            sortBy={topServicesSortBy}
            sortOrder={topServicesSortOrder}
            onSortChange={handleTopServicesSortChange}
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
