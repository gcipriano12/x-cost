import React from 'react';
import { RealTimeSpendSummaryCard } from '../RealTimeSpendSummaryCard';
import { CategoryDistributionCard } from '../CategoryDistributionCard';
import { AnomaliesCard } from '../AnomaliesCard';
import { SavingsOpportunitiesCard } from '../SavingsOpportunitiesCard';
import { OptimizationScoreCard } from '../OptimizationScoreCard';
import { timeFilterToDays } from '@/utils/timeFrame';

interface SummarySectionProps {
  timeFilter?: string; // Adicionar timeFilter como prop
  providerFilter?: string; // Adicionar providerFilter como prop
  spendSummaryData: {
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
  };
  providerDistributionData: {
    name: string;
    value: number;
    color: string;
  }[];
  categoryDistributionData: {
    name: string;
    value: number;
    color: string;
  }[];
  anomaliesData: {
    id: string;
    severity: 'high' | 'medium' | 'low';
    title: string;
    description: string;
    impact: number;
  }[];
  savingsOpportunitiesData: {
    opportunities: {
      id: string;
      title: string;
      description: string;
      savings: number;
      effort: 'high' | 'medium' | 'low';
    }[];
    totalPotentialSavings: number;
    currency: string;
  };
  isLoadingRealData?: boolean;
}

export function SummarySection({ 
  timeFilter,
  providerFilter,
  spendSummaryData, 
  providerDistributionData,
  categoryDistributionData, 
  anomaliesData, 
  savingsOpportunitiesData,
  isLoadingRealData = false
}: SummarySectionProps) {
  // Suppress unused variable warnings for mock data that will be removed later
  void spendSummaryData;
  void providerDistributionData;
  void anomaliesData;
  void savingsOpportunitiesData;
  return (
    <div className="space-y-4 mb-6">
      {/* Resumo de Gastos com dados reais da API */}
      <div className="w-full">
        <RealTimeSpendSummaryCard
          timeFilter={timeFilter} // Passar o timeFilter
          providerName={providerFilter} // Passar o providerFilter
          // credentialId pode ser passado como prop se necessário
        />
      </div>
      
      {/* Grid with 4 optimization cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="col-span-1 h-[415px]">
          <CategoryDistributionCard 
            currency="$"
            timeFilter={timeFilter}
            providerName={providerFilter}
          />
        </div>
        
        <div className="col-span-1 h-[415px]">
          <AnomaliesCard 
            provider={providerFilter}
            days={timeFilter ? timeFilterToDays(timeFilter) : 30}
            autoRefresh={false}
          />
        </div>

        <div className="col-span-1 h-[415px]">
          <SavingsOpportunitiesCard 
            provider={providerFilter}
            days={timeFilter ? timeFilterToDays(timeFilter) : 30}
            autoRefresh={false}
          />
        </div>
        
        <div className="col-span-1 h-[415px]">
          <OptimizationScoreCard 
            provider={providerFilter}
            autoRefresh={false}
          />
        </div>
      </div>
    </div>
  );
}
