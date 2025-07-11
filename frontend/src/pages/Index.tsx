
import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/hooks/useAuth';
import { Navigate } from 'react-router-dom';
import Dashboard from '../components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Globe } from 'lucide-react';
import { DashboardContent } from '@/components/dashboard/DashboardContent';
import { useDashboardData } from '@/hooks/useDashboardData';
import { useAnomalies, useSavingsOpportunities, useOptimizationSummary } from '@/hooks/useOptimization';
import { useDashboard } from '@/hooks/useDashboard';
import { useToast } from '@/hooks/use-toast';

const Index = () => {
  const { t } = useTranslation();
  const { isAuthenticated, loading } = useAuth();
  const { toast } = useToast();
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Obter os dados do dashboard (hooks devem ser chamados antes de qualquer return condicional)
  const {
    timeFilter,
    setTimeFilter,
    customDateRange,
    handleCustomDateRange,
    selectedProvider,
    setSelectedProvider,
    spendSummaryData,
    providerDistributionData,
    categoryDistributionData,
    topServicesData,
    anomaliesData,
    savingsOpportunitiesData,
    spendingTeamsData,
    forecastData,
    complianceData,
    kpiData,
    costEventsData,
    environmentsData,
    benchmarksData,
    newServicesData,
    regionHeatmapData,
    currency
  } = useDashboardData();

  // Hooks de otimização para refetch
  const { refetch: refetchAnomalies } = useAnomalies({});
  const { refetch: refetchSavings } = useSavingsOpportunities({});
  const { refetch: refetchOptimizationSummary } = useOptimizationSummary({});
  
  // Hook do dashboard principal para refetch
  const { refetch: refetchDashboard } = useDashboard({
    timeFilter,
    providerName: selectedProvider
  });

  // Função de refresh global
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      // Refresh all dashboard data
      await Promise.all([
        refetchAnomalies(),
        refetchSavings(),
        refetchOptimizationSummary(),
        refetchDashboard()
      ]);
      
      toast({
        title: t('common.dataRefreshed'),
        description: t('common.allDataUpdated'),
      });
    } catch (error) {
      toast({
        title: t('common.refreshFailed'),
        description: t('common.refreshFailedDescription'),
        variant: "destructive",
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  // Show loading while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={Globe} 
          title={t('common.megabill')}
          color="text-blue-600"
          showTimeFilter={true}
          showProviderFilter={true}
          timeFilter={timeFilter}
          onTimeFilterChange={setTimeFilter}
          onCustomDateRange={handleCustomDateRange}
          customDateRange={customDateRange}
          selectedProvider={selectedProvider}
          onProviderChange={setSelectedProvider}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />
        
        <div className="p-4 space-y-6">
          <DashboardContent
            timeFilter={timeFilter}
            onTimeFilterChange={setTimeFilter}
            providerFilter={selectedProvider}
            spendSummaryData={spendSummaryData}
            providerDistributionData={providerDistributionData}
            categoryDistributionData={categoryDistributionData}
            topServicesData={topServicesData}
            anomaliesData={anomaliesData}
            savingsOpportunitiesData={savingsOpportunitiesData}
            spendingTeamsData={spendingTeamsData}
            forecastData={forecastData}
            complianceData={complianceData}
            kpiData={kpiData}
            costEventsData={costEventsData}
            environmentsData={environmentsData}
            benchmarksData={benchmarksData}
            newServicesData={newServicesData}
            regionHeatmapData={regionHeatmapData}
            currency={currency}
          />
        </div>
      </div>
    </Dashboard>
  );
};

export default Index;
