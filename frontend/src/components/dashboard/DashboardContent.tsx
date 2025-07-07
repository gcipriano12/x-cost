import React from 'react';
import { SummarySection } from './sections/SummarySection';
import { ServicesSection } from './sections/ServicesSection';
import { TrendsSection } from './sections/TrendsSection';
import { KpiSection } from './sections/KpiSection';
import { ComparisonSection } from './sections/ComparisonSection';
import { TimeFilter } from './TimeFilter';
import { Globe } from 'lucide-react';
import { SpendSummaryCard } from './SpendSummaryCard';
import { CategoryDistributionCard } from './CategoryDistributionCard';
import { AnomaliesCard } from './AnomaliesCard';
import { SavingsOpportunitiesCard } from './SavingsOpportunitiesCard';
import { useIsMobile } from '@/hooks/use-mobile';
import type { 
  SpendSummary,
  ProviderDistribution,
  CategoryDistribution,
  TopService,
  Anomaly,
  SavingsOpportunities,
  SpendingTeam,
  ForecastData,
  Resource, 
  ComplianceItem,
  KPI,
  CostEvent,
  Environment,
  Benchmark,
  NewService,
  RegionData
} from '../../hooks/useDashboardData';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface DashboardContentProps {
  timeFilter: string;
  onTimeFilterChange: (filter: string) => void;
  providerFilter?: string; // Adicionar providerFilter como prop
  spendSummaryData: SpendSummary;
  providerDistributionData: ProviderDistribution[];
  categoryDistributionData: CategoryDistribution[];
  topServicesData: TopService[];
  anomaliesData: Anomaly[];
  savingsOpportunitiesData: SavingsOpportunities;
  spendingTeamsData: SpendingTeam[];
  forecastData: ForecastData[];
  resourcesData: Resource[];
  complianceData: ComplianceItem[];
  kpiData: KPI[];
  costEventsData: CostEvent[];
  environmentsData: Environment[];
  benchmarksData: Benchmark[];
  newServicesData: NewService[];
  regionHeatmapData: RegionData[];
  currency: string;
  isLoadingRealData?: boolean;
  activeCredential?: any;
  isTopServicesUsingMockData?: boolean;
}

export const DashboardContent: React.FC<DashboardContentProps> = ({
  timeFilter,
  onTimeFilterChange,
  providerFilter,
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
  currency,
  isLoadingRealData = false,
  activeCredential,
  isTopServicesUsingMockData = false
}) => {
  const { isDark } = useTheme();
  const isMobile = useIsMobile();

  return (
    <div className={cn(
      "pb-12 w-full h-full flex-1",
      isDark ? "bg-slate-950" : "bg-gray-50"
    )}>
      <div className="w-full">
        <SummarySection
          timeFilter={timeFilter}
          providerFilter={providerFilter}
          spendSummaryData={spendSummaryData}
          providerDistributionData={providerDistributionData}
          categoryDistributionData={categoryDistributionData}
          anomaliesData={anomaliesData}
          savingsOpportunitiesData={savingsOpportunitiesData}
          isLoadingRealData={isLoadingRealData}
        />
        
        <ServicesSection 
          topServicesData={topServicesData}
          currency={currency}
          credentialId={activeCredential?.id?.toString()}
          providerName={providerFilter}
          timeFilter={timeFilter}
          isTopServicesUsingMockData={isTopServicesUsingMockData}
        />
        
        <TrendsSection 
          spendingCategoriesData={spendingTeamsData}
          resourcesData={resourcesData}
          complianceData={complianceData}
          currency={currency}
        />
        
        <KpiSection 
          kpiData={kpiData}
          costEventsData={costEventsData}
          currentMonth="Maio 2025"
        />
        
        <ComparisonSection 
          environmentsData={environmentsData}
          benchmarksData={benchmarksData}
          newServicesData={newServicesData}
          regionHeatmapData={regionHeatmapData}
          currency={currency}
        />
      </div>
    </div>
  );
};

interface SummarySectionProps {
  spendSummaryData: SpendSummary;
  providerDistributionData: ProviderDistribution[];
  categoryDistributionData: CategoryDistribution[];
  anomaliesData: Anomaly[];
  savingsOpportunitiesData: SavingsOpportunities;
}
