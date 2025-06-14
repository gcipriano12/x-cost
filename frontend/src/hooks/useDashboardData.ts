import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { DateRange } from 'react-day-picker';
import { format, differenceInDays } from 'date-fns';
import { useXCostData } from './useXCostData';

// Types for dashboard data
export type SpendSummary = {
  totalSpend: number;
  currency: string;
  previousPeriodChange: number;
  sparklineData: number[];
  providerBreakdown?: Array<{
    name: string;
    value: number;
    color: string;
  }>;
  wastedSpend?: number;
  budgetLimit?: number;
  budgetConsumed?: number;
  savingsRealized?: number;
  topProvider?: {
    name: string;
    cost: number;
  };
};

export type ProviderDistribution = {
  name: string;
  value: number;
  color: string;
};

export type CategoryDistribution = {
  name: string;
  value: number;
  color: string;
};

export type TopService = {
  id: string;
  name: string;
  provider: string;
  currentSpend: number;
  previousSpend: number;
  trend: number;
};

export type ForecastData = {
  month: string;
  actual?: number;
  forecast?: number;
  budget?: number;
};

export type Anomaly = {
  id: string;
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  impact: number;
  resource?: string;
  provider?: string;
  dateDetected: string;
  tags?: string[];
};

export type SavingsOpportunity = {
  id: string;
  title: string;
  description: string;
  savings: number;
  effort: 'high' | 'medium' | 'low';
};

export type SavingsOpportunities = {
  opportunities: SavingsOpportunity[];
  totalPotentialSavings: number;
  currency: string;
};

export type SpendingTeam = {
  name: string;
  value: number;
  color: string;
};

export type Resource = {
  name: string;
  usage: number;
  totalAvailable: number;
  warningThreshold: number;
};

export type ComplianceItem = {
  id: string;
  name: string;
  status: 'compliant' | 'non-compliant';
  description: string;
};

export type KPICategory = 'eficiencia' | 'tarifacao' | 'planejamento' | 'governanca';

export type KPI = {
  name: string;
  value: number;
  unit?: string;
  trend?: number;
  target?: number;
  isGoodWhenHigher?: boolean;
  description?: string;
  formula?: string;
  category: KPICategory;
};

export type CostEvent = {
  id: string;
  date: string;
  title: string;
  type: 'billing' | 'contract' | 'budget' | 'other';
  impact?: number;
  currency?: string;
};

export type Environment = {
  name: string;
  cost: number;
  previousPeriodCost: number;
  efficiency: number;
};

export type Benchmark = {
  serviceType: string;
  yourCost: number;
  industryAverage: number;
  bestInClass: number;
  percentile: number;
};

export type NewService = {
  id: string;
  name: string;
  provider: string;
  addedDate: string;
  cost: number;
  currency: string;
  tags: string[];
};

export type RegionData = {
  name: string;
  value: number;
  children?: {
    name: string;
    value: number;
  }[];
};

export type DashboardData = {
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
};

export const useDashboardData = () => {
  const [timeFilter, setTimeFilter] = useState('7d');
  const [customDateRange, setCustomDateRange] = useState<DateRange | undefined>();
  const { t } = useTranslation();
  
  // Function to handle custom date range
  const handleCustomDateRange = (range: DateRange | undefined) => {
    setCustomDateRange(range);
    if (range?.from && range?.to) {
      // Calculate days difference and update timeFilter to custom
      const days = differenceInDays(range.to, range.from) + 1;
      console.log(`Custom date range selected: ${format(range.from, 'dd/MM/yyyy')} - ${format(range.to, 'dd/MM/yyyy')} (${days} days)`);
    }
  };
  
  // Integração com X Cost API - passar timeFilter e datas customizadas
  const {
    spendSummary: apiSpendSummary,
    providerDistribution: apiProviderDistribution,
    topServices: apiTopServices,
    trendData: apiTrendData,
    serviceCosts: apiServiceCosts,
    regionCosts: apiRegionCosts,
    loading: apiLoading,
    hasCredentials
  } = useXCostData({ 
    timeFilter,
    customStartDate: customDateRange?.from,
    customEndDate: customDateRange?.to
  });
  
  // Mock data for the dashboard
  const mockDashboardData: DashboardData = {
    currency: '$',
    // Dados para a seção de resumo
    spendSummaryData: {
      totalSpend: 1245678.90,
      currency: '$',
      previousPeriodChange: -12.5,
      sparklineData: [45000, 48000, 52000, 49000, 54000, 59000, 58000],
      providerBreakdown: [
        { name: 'AWS', value: 58, color: '#F5A623' },
        { name: 'Azure', value: 22, color: '#0078D4' },
        { name: 'GCP', value: 12, color: '#4285F4' },
        { name: 'Oracle Cloud', value: 8, color: '#f80404' }
      ],
      wastedSpend: 186851.83,
      budgetLimit: 1500000,
      budgetConsumed: 83,
      savingsRealized: 99654.31
    },
    
    providerDistributionData: [
      { name: 'AWS', value: 543210.50, color: '#FF9900' },
      { name: 'Azure', value: 324567.80, color: '#0078D4' },
      { name: 'GCP', value: 234567.40, color: '#4285F4' },
      { name: 'Oracle Cloud', value: 143333.20, color: '#F80000' },
    ],
    
    categoryDistributionData: [
      { name: t('mockData.categories.computation'), value: 623210.50, color: '#60A5FA' },
      { name: t('mockData.categories.storage'), value: 274567.80, color: '#F97316' },
      { name: t('mockData.categories.network'), value: 184567.40, color: '#10B981' },
      { name: t('mockData.categories.database'), value: 114567.20, color: '#8B5CF6' },
      { name: t('mockData.categories.others'), value: 48765.90, color: '#EC4899' },
    ],
    
    topServicesData: [
      { id: '1', name: 'EC2', provider: 'AWS', currentSpend: 245678.30, previousSpend: 225432.10, trend: 9 },
      { id: '2', name: 'S3', provider: 'AWS', currentSpend: 124567.80, previousSpend: 134567.80, trend: -7 },
      { id: '3', name: 'Azure VM', provider: 'Azure', currentSpend: 98765.40, previousSpend: 88123.45, trend: 12 },
      { id: '4', name: 'GCP Compute', provider: 'GCP', currentSpend: 87654.30, previousSpend: 77654.30, trend: 13 },
      { id: '5', name: 'RDS', provider: 'AWS', currentSpend: 76543.20, previousSpend: 81234.56, trend: -6 },
    ],
    
    anomaliesData: [
      {
        id: 'a3',
        severity: 'low',
        title: t('mockData.anomalyTitles.expiredSnapshots'),
        description: t('mockData.anomalyDescriptions.expiredSnapshots'),
        impact: 3450.20,
        dateDetected: '2023-10-20'
      },
      {
        id: 'a1',
        severity: 'high',
        title: t('mockData.anomalyTitles.vmCostIncrease'),
        description: t('mockData.anomalyDescriptions.vmCostIncrease'),
        impact: 23450.60,
        dateDetected: '2023-10-26'
      },
      {
        id: 'a2',
        severity: 'medium',
        title: t('mockData.anomalyTitles.idleResources'),
        description: t('mockData.anomalyDescriptions.idleResources'),
        impact: 12300.80,
        dateDetected: '2023-10-25'
      },
      {
        id: 'a4',
        severity: 'high',
        title: t('mockData.anomalyTitles.unoptimizedGPUs'),
        description: t('mockData.anomalyDescriptions.unoptimizedGPUs'),
        impact: 19850.75,
        dateDetected: '2023-10-24'
      },
      {
        id: 'a5',
        severity: 'medium',
        title: t('mockData.anomalyTitles.idleBalancers'),
        description: t('mockData.anomalyDescriptions.idleBalancers'),
        impact: 4560.30,
        dateDetected: '2023-10-23'
      },
      {
        id: 'a6',
        severity: 'low',
        title: t('mockData.anomalyTitles.oversizedDatabase'),
        description: t('mockData.anomalyDescriptions.oversizedDatabase'),
        impact: 2960.45,
        dateDetected: '2023-10-22'
      },
      {
        id: 'a7',
        severity: 'high',
        title: t('mockData.anomalyTitles.unassociatedIPs'),
        description: t('mockData.anomalyDescriptions.unassociatedIPs'),
        impact: 1870.20,
        dateDetected: '2023-10-21'
      }
    ],
    
    savingsOpportunitiesData: {
      opportunities: [
        {
          id: 'op1',
          title: t('mockData.savingsOpportunities.reservedInstances'),
          description: t('mockData.savingsDescriptions.reservedInstances'),
          savings: 67890.50,
          effort: 'low'
        },
        {
          id: 'op2',
          title: t('mockData.savingsOpportunities.rightsizing'),
          description: t('mockData.savingsDescriptions.rightsizing'),
          savings: 23456.70,
          effort: 'medium'
        },
        {
          id: 'op3',
          title: t('mockData.savingsOpportunities.storageLifecycle'),
          description: t('mockData.savingsDescriptions.storageLifecycle'),
          savings: 12345.60,
          effort: 'low'
        },
        {
          id: 'op4',
          title: t('mockData.savingsOpportunities.savingsPlans'),
          description: t('mockData.savingsDescriptions.savingsPlans'),
          savings: 18750.30,
          effort: 'low'
        },
        {
          id: 'op5',
          title: t('mockData.savingsOpportunities.unusedVolumes'),
          description: t('mockData.savingsDescriptions.unusedVolumes'),
          savings: 5960.75,
          effort: 'low'
        },
        {
          id: 'op6',
          title: t('mockData.savingsOpportunities.kubernetesClusters'),
          description: t('mockData.savingsDescriptions.kubernetesClusters'),
          savings: 14850.60,
          effort: 'medium'
        },
        {
          id: 'op7',
          title: t('mockData.savingsOpportunities.storageTiers'),
          description: t('mockData.savingsDescriptions.storageTiers'),
          savings: 9320.40,
          effort: 'medium'
        }
      ],
      totalPotentialSavings: 152574.85,
      currency: '$'
    },

    // Dados para a seção de categorias e tendências
    spendingTeamsData: [
      { name: t('mockData.teams.development'), value: 495000.50, color: '#4B5563' },
      { name: t('mockData.teams.infrastructure'), value: 358000.80, color: '#1D4ED8' },
      { name: t('mockData.teams.dataScience'), value: 276500.40, color: '#9333EA' },
      { name: t('mockData.teams.marketing'), value: 116177.20, color: '#16A34A' },
    ],

    forecastData: [
      { month: t('mockData.months.jan'), actual: 320000, forecast: undefined, budget: 350000 },
      { month: t('mockData.months.feb'), actual: 340000, forecast: undefined, budget: 350000 },
      { month: t('mockData.months.mar'), actual: 360000, forecast: undefined, budget: 350000 },
      { month: t('mockData.months.apr'), actual: 330000, forecast: undefined, budget: 350000 },
      { month: t('mockData.months.may'), actual: 345000, forecast: undefined, budget: 350000 },
      { month: t('mockData.months.jun'), actual: undefined, forecast: 350000, budget: 350000 },
      { month: t('mockData.months.jul'), actual: undefined, forecast: 355000, budget: 350000 },
    ],

    resourcesData: [
      { name: t('mockData.resources.vcpus'), usage: 280, totalAvailable: 320, warningThreshold: 85 },
      { name: t('mockData.resources.ram'), usage: 620, totalAvailable: 768, warningThreshold: 90 },
      { name: t('mockData.resources.storage'), usage: 5.8, totalAvailable: 8, warningThreshold: 80 },
      { name: t('mockData.resources.sqlLicenses'), usage: 42, totalAvailable: 50, warningThreshold: 95 },
      { name: t('mockData.resources.ebsVolumes'), usage: 125, totalAvailable: 150, warningThreshold: 90 },
      { name: t('mockData.resources.bandwidth'), usage: 18, totalAvailable: 25, warningThreshold: 85 },
    ],

    complianceData: [
      { id: 'c1', name: t('mockData.compliance.instanceTags'), status: 'compliant', description: t('mockData.complianceDescriptions.instanceTags') },
      { id: 'c2', name: t('mockData.compliance.encryptedVolumes'), status: 'compliant', description: t('mockData.complianceDescriptions.encryptedVolumes') },
      { id: 'c3', name: t('mockData.compliance.costReports'), status: 'compliant', description: t('mockData.complianceDescriptions.costReports') },
      { id: 'c4', name: t('mockData.compliance.retentionPolicies'), status: 'non-compliant', description: t('mockData.complianceDescriptions.retentionPolicies') },
      { id: 'c5', name: t('mockData.compliance.costAllocation'), status: 'non-compliant', description: t('mockData.complianceDescriptions.costAllocation') },
    ],

    kpiData: [
      { 
        name: t('kpis.names.resourceUtilizationRate'), 
        value: 68, 
        unit: '%', 
        trend: 3.5, 
        target: 75, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.resourceUtilizationRate'),
        formula: t('kpis.formulas.resourceUtilizationRate'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.cloudWastePercentage'), 
        value: 24, 
        unit: '%', 
        trend: -5.2, 
        target: 15, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.cloudWastePercentage'),
        formula: t('kpis.formulas.cloudWastePercentage'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.powerScheduleAdherence'), 
        value: 82, 
        unit: '%', 
        trend: 7.3, 
        target: 95, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.powerScheduleAdherence'),
        formula: t('kpis.formulas.powerScheduleAdherence'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.legacyResourcesPercentage'), 
        value: 37, 
        unit: '%', 
        trend: -2.1, 
        target: 20, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.legacyResourcesPercentage'),
        formula: t('kpis.formulas.legacyResourcesPercentage'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.reservedInstancesCoverage'), 
        value: 45, 
        unit: '%', 
        trend: 8.2, 
        target: 75, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.reservedInstancesCoverage'),
        formula: t('kpis.formulas.reservedInstancesCoverage'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.costEfficiencyPerService'), 
        value: 0.31, 
        unit: t('kpis.units.currencyPerUnit'), 
        trend: -6.3, 
        target: 0.25, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.costEfficiencyPerService'),
        formula: t('kpis.formulas.costEfficiencyPerService'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.containerDensity'), 
        value: 12, 
        unit: 'pods/nó', 
        trend: 3.8, 
        target: 15, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.containerDensity'),
        formula: t('kpis.formulas.containerDensity'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.costPerWorkload'), 
        value: 3240, 
        unit: '$', 
        trend: -4.2, 
        target: 3000, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.costPerWorkload'),
        formula: t('kpis.formulas.costPerWorkload'),
        category: 'eficiencia'
      },
      { 
        name: t('kpis.names.effectiveSavingsRate'), 
        value: 22, 
        unit: '%', 
        trend: 5.7, 
        target: 30, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.effectiveSavingsRate'),
        formula: t('kpis.formulas.effectiveSavingsRate'),
        category: 'tarifacao'
      },
      { 
        name: t('kpis.names.commitmentDiscountWaste'), 
        value: 18, 
        unit: '%', 
        trend: -3.5, 
        target: 10, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.commitmentDiscountWaste'),
        formula: t('kpis.formulas.commitmentDiscountWaste'),
        category: 'tarifacao'
      },
      { 
        name: t('kpis.names.computeCoveredByCommitments'), 
        value: 65, 
        unit: '%', 
        trend: 8.3, 
        target: 80, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.computeCoveredByCommitments'),
        formula: t('kpis.formulas.computeCoveredByCommitments'),
        category: 'tarifacao'
      },
      { 
        name: t('kpis.names.costPerVcpuGpuHour'), 
        value: 0.42, 
        unit: '$/h', 
        trend: -2.8, 
        target: 0.35, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.costPerVcpuGpuHour'),
        formula: t('kpis.formulas.costPerVcpuGpuHour'),
        category: 'tarifacao'
      },
      { 
        name: t('kpis.names.budgetVsForecastVariation'), 
        value: 8.5, 
        unit: '%', 
        trend: -2.3, 
        target: 5, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.budgetVsForecastVariation'),
        formula: t('kpis.formulas.budgetVsForecastVariation'),
        category: 'planejamento'
      },
      { 
        name: t('kpis.names.cloudSpendVariation'), 
        value: 12.3, 
        unit: '%', 
        trend: -4.1, 
        target: 7, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.cloudSpendVariation'),
        formula: t('kpis.formulas.cloudSpendVariation'),
        category: 'planejamento'
      },
      { 
        name: t('kpis.names.forecastAccuracyRate'), 
        value: 84, 
        unit: '%', 
        trend: 6.2, 
        target: 90, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.forecastAccuracyRate'),
        formula: t('kpis.formulas.forecastAccuracyRate'),
        category: 'planejamento'
      },
      { 
        name: t('kpis.names.unallocatedCostPercentage'), 
        value: 18, 
        unit: '%', 
        trend: -4.7, 
        target: 5, 
        isGoodWhenHigher: false,
        description: t('kpis.descriptions.unallocatedCostPercentage'),
        formula: t('kpis.formulas.unallocatedCostPercentage'),
        category: 'governanca'
      },
      { 
        name: t('kpis.names.tagPolicyComplianceRate'), 
        value: 76, 
        unit: '%', 
        trend: 8.5, 
        target: 95, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.tagPolicyComplianceRate'),
        formula: t('kpis.formulas.tagPolicyComplianceRate'),
        category: 'governanca'
      },
      { 
        name: t('kpis.names.anomalyDetectionSavings'), 
        value: 45250, 
        unit: '$', 
        trend: 12.8, 
        target: 50000, 
        isGoodWhenHigher: true,
        description: t('kpis.descriptions.anomalyDetectionSavings'),
        formula: t('kpis.formulas.anomalyDetectionSavings'),
        category: 'governanca'
      }
    ],

    costEventsData: [
      // Eventos passados (serão destacados em vermelho)
      { id: 'e1', date: '2025-04-20', title: 'Faturamento AWS (anterior)', type: 'billing', impact: 543210.50, currency: '$' },
      { id: 'e2', date: '2025-05-02', title: 'Renovação licenças (anterior)', type: 'contract', impact: 85000.00, currency: '$' },
      
      // Eventos do mês atual
      { id: 'e3', date: '2025-05-20', title: 'Faturamento AWS', type: 'billing', impact: 543210.50, currency: '$' },
      { id: 'e4', date: '2025-05-25', title: 'Renovação contrato Azure', type: 'contract', impact: 120000.00, currency: '$' },
      { id: 'e5', date: '2025-05-28', title: 'Revisão de orçamento', type: 'budget' },
      
      // Eventos futuros
      { id: 'e6', date: '2025-06-05', title: 'Faturamento GCP', type: 'billing', impact: 234567.40, currency: '$' },
      { id: 'e7', date: '2025-06-15', title: 'Renovação suporte', type: 'contract', impact: 75000.00, currency: '$' },
    ],

    environmentsData: [
      { name: t('mockData.environments.production'), cost: 890450.60, previousPeriodCost: 850340.20, efficiency: 82 },
      { name: t('mockData.environments.staging'), cost: 234560.30, previousPeriodCost: 220450.10, efficiency: 65 },
      { name: t('mockData.environments.development'), cost: 120667.80, previousPeriodCost: 145890.40, efficiency: 58 },
    ],

    regionHeatmapData: [
      {
        name: 'AWS',
        value: 543210.50,
        children: [
          { name: 'us-east-1', value: 243210.30 },
          { name: 'sa-east-1', value: 120000.20 }
        ]
      },
      {
        name: 'Azure',
        value: 324567.80,
        children: [
          { name: 'East US', value: 124567.50 },
          { name: 'Brazil South', value: 100000.30 }
        ]
      },
      {
        name: 'GCP',
        value: 234567.40,
        children: [
          { name: 'us-central1', value: 114567.20 }
        ]
      },
    ],

    benchmarksData: [
      { 
        serviceType: t('mockData.benchmarks.computeInstances'),
        yourCost: 12.50,
        industryAverage: 18.75,
        bestInClass: 8.25,
        percentile: 35
      },
      { 
        serviceType: t('mockData.benchmarks.storagePerGB'),
        yourCost: 0.085,
        industryAverage: 0.095,
        bestInClass: 0.065,
        percentile: 25
      },
      { 
        serviceType: t('mockData.benchmarks.database'),
        yourCost: 42.30,
        industryAverage: 45.20,
        bestInClass: 39.10,
        percentile: 85
      },
    ],

    newServicesData: [
      { 
        id: 'ns1',
        name: 'AWS Lambda',
        provider: 'AWS',
        addedDate: '2025-05-10',
        cost: 5430.20,
        currency: '$',
        tags: ['serverless', 'novo-projeto']
      },
      { 
        id: 'ns2',
        name: 'Azure DevOps',
        provider: 'Azure',
        addedDate: '2025-05-08',
        cost: 3200.50,
        currency: '$',
        tags: ['devops', 'ci-cd'] 
      },
      { 
        id: 'ns3',
        name: 'GCP BigQuery',
        provider: 'GCP',
        addedDate: '2025-05-02',
        cost: 7800.30,
        currency: '$',
        tags: ['analytics', 'big-data'] 
      },
    ]
  };

  // Usar dados reais quando disponíveis, senão usar mock data
  const finalDashboardData: DashboardData = {
    ...mockDashboardData,
    // Substituir com dados reais da API quando disponíveis
    spendSummaryData: apiSpendSummary || mockDashboardData.spendSummaryData,
    providerDistributionData: apiProviderDistribution.length > 0 ? apiProviderDistribution : mockDashboardData.providerDistributionData,
    topServicesData: apiTopServices.length > 0 ? apiTopServices : mockDashboardData.topServicesData,
  };

  return {
    timeFilter,
    setTimeFilter,
    customDateRange,
    handleCustomDateRange,
    ...finalDashboardData,
    isLoadingRealData: apiLoading,
    hasRealData: hasCredentials
  };
};
