import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { KPICategoryResponse, KPI_CATEGORY_COLORS } from '@/types/kpi.types';
import { KPICard } from './KPICard';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { useTranslation } from 'react-i18next';

interface KPICategorySectionProps {
  categoryData: KPICategoryResponse;
  onKPIClick?: (kpiCode: string) => void;
  defaultExpanded?: boolean;
}

export const KPICategorySection: React.FC<KPICategorySectionProps> = ({ 
  categoryData, 
  onKPIClick,
  defaultExpanded = true 
}) => {
  const { isDark } = useTheme();
  const { t } = useTranslation();
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  
  const categoryColor = KPI_CATEGORY_COLORS[categoryData.category];
  const { summary } = categoryData;
  
  // Tradução das categorias
  const categoryNames = {
    efficiency: t('sections.eficiencia', 'Eficiência'),
    pricing: t('sections.tarifacao', 'Tarifação'),
    planning: t('sections.planejamento', 'Planejamento'),
    governance: t('sections.governanca', 'Governança')
  };
  
  return (
    <Card className="overflow-hidden">
      <CardHeader 
        className={cn(
          "cursor-pointer select-none",
          isDark ? "hover:bg-gray-800" : "hover:bg-gray-50"
        )}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div 
              className="w-1 h-8 rounded-full" 
              style={{ backgroundColor: categoryColor }}
            />
            <CardTitle className="text-lg">
              {categoryNames[categoryData.category]}
            </CardTitle>
            <Badge variant="secondary" className="ml-2">
              {summary.total_kpis} KPIs
            </Badge>
          </div>
          
          <div className="flex items-center gap-4">
            {/* Mini status summary */}
            <div className="flex gap-2 text-sm">
              <span className="text-green-500">●{summary.status_distribution.good}</span>
              <span className="text-yellow-500">●{summary.status_distribution.warning}</span>
              <span className="text-red-500">●{summary.status_distribution.critical}</span>
            </div>
            
            {/* Health score */}
            <Badge 
              variant={
                summary.health_score >= 80 ? 'default' :
                summary.health_score >= 60 ? 'secondary' : 'destructive'
              }
            >
              {summary.health_score.toFixed(0)}%
            </Badge>
            
            {isExpanded ? <ChevronUp /> : <ChevronDown />}
          </div>
        </div>
      </CardHeader>
      
      {isExpanded && (
        <CardContent className="pt-0">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
            {categoryData.kpis.map((kpi) => (
              <KPICard
                key={kpi.kpi_id}
                kpi={kpi}
                onClick={() => onKPIClick?.(kpi.code)}
              />
            ))}
          </div>
        </CardContent>
      )}
    </Card>
  );
};