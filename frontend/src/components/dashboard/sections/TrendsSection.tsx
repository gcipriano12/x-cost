
import React from 'react';
import { SpendingTeamsCard } from '../SpendingTeamsCard';
import { SeasonalityCard } from '../SeasonalityCard';
import { FinOpsComplianceCard } from '../FinOpsComplianceCard';
import { ChartLine } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface TrendsSectionProps {
  spendingCategoriesData: {
    name: string;
    value: number;
    color: string;
  }[];
  complianceData: {
    id: string;
    name: string;
    status: 'compliant' | 'non-compliant';
    description: string;
  }[];
  currency: string;
}

export function TrendsSection({ 
  spendingCategoriesData, 
  complianceData, 
  currency 
}: TrendsSectionProps) {
  const { t } = useTranslation();
  
  return (
    <div className="mb-6">
      <div className="flex items-center mb-4">
        <ChartLine className="h-5 w-5 mr-2 text-amber-600" />
        <h2 className="text-lg font-semibold">{t('sections.trendsAndUtilization')}</h2>
      </div>
      
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <div className="col-span-1 lg:col-span-2">
          <SpendingTeamsCard 
            categories={spendingCategoriesData}
            currency={currency}
          />
        </div>
        
        <div className="col-span-1">
          <SeasonalityCard />
        </div>
        
        <div className="col-span-1">
          <FinOpsComplianceCard 
            items={complianceData}
          />
        </div>
      </div>
    </div>
  );
}
