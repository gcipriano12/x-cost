import { useState } from 'react';
import { ChatBot } from '../chat/ChatBot';
import { DashboardContent } from './DashboardContent';
import { useDashboardData } from '../../hooks/useDashboardData';
import { SidebarProvider } from '@/components/ui/sidebar';
import { DashboardSidebar } from './sidebar/DashboardSidebar';
import { useIsMobile } from '@/hooks/use-mobile';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface DashboardProps {
  children?: React.ReactNode;
}

export default function Dashboard({ children }: DashboardProps) {
  const isMobile = useIsMobile();
  const { isDark } = useTheme();
  
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
    complianceData,
    kpiData,
    costEventsData,
    environmentsData,
    benchmarksData,
    newServicesData,
    regionHeatmapData,
    currency,
    isLoadingRealData,
    activeCredential,
    isTopServicesUsingMockData
  } = useDashboardData();
  
  return (
    <SidebarProvider>
      <div className="min-h-screen flex flex-row w-full overflow-hidden">
        <DashboardSidebar />
        
        {/* Conteúdo principal - adicionando margem esquerda para dispositivos móveis */}
        <div className={`flex-1 flex flex-col w-full overflow-hidden relative ${isMobile ? 'ml-[3.5rem]' : ''}`}>
          <main className={cn(
            "flex-1 w-full overflow-auto",
            isDark ? "bg-slate-950" : "bg-gray-50"
          )}>
            {children ? (
              children
            ) : (
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
                complianceData={complianceData}
                kpiData={kpiData}
                costEventsData={costEventsData}
                environmentsData={environmentsData}
                benchmarksData={benchmarksData}
                newServicesData={newServicesData}
                regionHeatmapData={regionHeatmapData}
                currency={currency}
                isLoadingRealData={isLoadingRealData}
                activeCredential={activeCredential}
                isTopServicesUsingMockData={isTopServicesUsingMockData}
              />
            )}
            
            <ChatBot />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
