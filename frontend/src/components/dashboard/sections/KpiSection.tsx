
import React from 'react';
import { EfficiencyKPIsCard } from '../EfficiencyKPIsCard';
import { CostEventCalendarCard } from '../CostEventCalendarCard';
import { ChartBar } from 'lucide-react';
import { useTranslation } from 'react-i18next';

type KPICategory = 'eficiencia' | 'tarifacao' | 'planejamento' | 'governanca';

interface KpiSectionProps {
  kpiData: {
    name: string;
    value: number;
    unit?: string;
    trend?: number;
    target?: number;
    isGoodWhenHigher?: boolean;
    description?: string;
    formula?: string;
    category: KPICategory;
  }[];
  costEventsData: {
    id: string;
    date: string;
    title: string;
    type: 'billing' | 'contract' | 'budget' | 'other';
    impact?: number;
    currency?: string;
  }[];
  currentMonth: string;
}

export function KpiSection({ kpiData, costEventsData, currentMonth }: KpiSectionProps) {
  const { t } = useTranslation();
  
  return (
    <div className="mb-6">
      <div className="flex items-center mb-4">
        <ChartBar className="h-5 w-5 mr-2 text-red-600" />
        <h2 className="text-lg font-semibold">{t('sections.indicatorsAndEvents')}</h2>
      </div>
      
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="col-span-1">
          <EfficiencyKPIsCard 
            kpis={kpiData}
          />
        </div>
        
        <div className="col-span-1">
          <CostEventCalendarCard 
            events={costEventsData}
          />
        </div>
      </div>
    </div>
  );
}
