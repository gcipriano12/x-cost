
import React, { useState } from 'react';
import { EfficiencyKPIsCard } from '../EfficiencyKPIsCard';
import { CostEventCalendarCard } from '../CostEventCalendarCard';
import { KPIIndicators } from '../../kpi/KPIIndicators';
import { ChartBar, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
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
  const [showAdvancedKPIs, setShowAdvancedKPIs] = useState(false);
  
  return (
    <div className="mb-6 space-y-6">
      {/* Seção original com KPIs básicos e eventos */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <ChartBar className="h-5 w-5 mr-2 text-red-600" />
            <h2 className="text-lg font-semibold">{t('sections.indicatorsAndEvents')}</h2>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowAdvancedKPIs(!showAdvancedKPIs)}
          >
            <BarChart3 className="h-4 w-4 mr-2" />
            {showAdvancedKPIs ? 'Ocultar KPIs Avançados' : 'Mostrar KPIs Avançados'}
          </Button>
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

      {/* Seção avançada de KPIs */}
      {showAdvancedKPIs && (
        <div>
          <div className="flex items-center mb-4">
            <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
            <h2 className="text-lg font-semibold">KPIs Detalhados por Categoria</h2>
          </div>
          
          <KPIIndicators />
        </div>
      )}
    </div>
  );
}
