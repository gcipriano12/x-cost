import React from 'react';
import { RealTimeSpendSummaryCard } from '../RealTimeSpendSummaryCard';
import { CategoryDistributionCard } from '../CategoryDistributionCard';
import { AnomaliesCard } from '../AnomaliesCard';
import { SavingsOpportunitiesCard } from '../SavingsOpportunitiesCard';
import { ChartPie } from 'lucide-react';

interface SummarySectionProps {
  timeFilter?: string; // Adicionar timeFilter como prop
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
}

export function SummarySection({ 
  timeFilter, // Adicionar timeFilter aos parâmetros
  spendSummaryData, 
  providerDistributionData,
  categoryDistributionData, 
  anomaliesData, 
  savingsOpportunitiesData 
}: SummarySectionProps) {
  return (
    <div className="space-y-4 mb-6">
      {/* Resumo de Gastos com dados reais da API */}
      <div className="w-full">
        <RealTimeSpendSummaryCard
          timeFilter={timeFilter} // Passar o timeFilter
          // credentialId pode ser passado como prop se necessário
        />
      </div>
      
      {/* Os outros três cards ficam lado a lado abaixo */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <div className="col-span-1">
          <CategoryDistributionCard 
            data={categoryDistributionData}
            currency="R$"
          />
        </div>
        
        <div className="col-span-1">
          <AnomaliesCard 
            anomalies={anomaliesData}
            currency="R$"
          />
        </div>

        <div className="col-span-1">
          <SavingsOpportunitiesCard 
            opportunities={savingsOpportunitiesData.opportunities}
            totalPotentialSavings={savingsOpportunitiesData.totalPotentialSavings}
            currency={savingsOpportunitiesData.currency}
          />
        </div>
      </div>
    </div>
  );
}
