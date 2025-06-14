
import React from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '@/hooks/useAuth';
import { Navigate } from 'react-router-dom';
import Dashboard from '../components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Globe } from 'lucide-react';
import { DashboardContent } from '@/components/dashboard/DashboardContent';
import { useDashboardData } from '@/hooks/useDashboardData';

const Index = () => {
  const { t } = useTranslation();
  const { isAuthenticated, loading } = useAuth();

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

  // Obter os dados do dashboard
  const {
    timeFilter,
    setTimeFilter,
    spendSummaryData,
    providerDistributionData,
    categoryDistributionData,
    topServicesData,
    anomaliesData,
    savingsOpportunitiesData,
    spendingTeamsData,
    forecastData,
    resourcesData,
    complianceData,
    kpiData,
    costEventsData,
    environmentsData,
    benchmarksData,
    newServicesData,
    regionHeatmapData,
    currency
  } = useDashboardData();

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={Globe} 
          title={t('common.megabill')}
          description={t('common.cloudCostManagementDashboard')}
          color="text-blue-600"
          showTimeFilter={true}
          timeFilter={timeFilter}
          onTimeFilterChange={setTimeFilter}
        />
        
        <div className="p-4 space-y-6">
          <DashboardContent
            timeFilter={timeFilter}
            onTimeFilterChange={setTimeFilter}
            spendSummaryData={spendSummaryData}
            providerDistributionData={providerDistributionData}
            categoryDistributionData={categoryDistributionData}
            topServicesData={topServicesData}
            anomaliesData={anomaliesData}
            savingsOpportunitiesData={savingsOpportunitiesData}
            spendingTeamsData={spendingTeamsData}
            forecastData={forecastData}
            resourcesData={resourcesData}
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
