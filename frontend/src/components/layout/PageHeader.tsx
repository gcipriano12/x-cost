import React from 'react';
import { useTranslation } from 'react-i18next';
import { DateRange } from 'react-day-picker';
import { TimeFilter } from '@/components/dashboard/TimeFilter';
import { CloudProviderFilter } from '@/components/dashboard/CloudProviderFilter';
import { cn } from '@/lib/utils';
import { LucideIcon } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { Button } from '@/components/ui/button';
import { useIsMobile } from '@/hooks/use-mobile';
import { ChevronRight } from 'lucide-react';

interface PageHeaderProps {
  icon: LucideIcon;
  title: string;
  description?: string;
  color?: string;
  showTimeFilter?: boolean;
  showProviderFilter?: boolean;
  actions?: React.ReactNode;
  timeFilter?: string;
  onTimeFilterChange?: (value: string) => void;
  onCustomDateRange?: (range: DateRange | undefined) => void;
  customDateRange?: DateRange;
  selectedProvider?: string;
  onProviderChange?: (provider: string) => void;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  icon: Icon,
  title,
  description,
  color = 'text-blue-600',
  showTimeFilter = true,
  showProviderFilter = false,
  actions,
  timeFilter = '30d',
  onTimeFilterChange = () => {},
  onCustomDateRange,
  customDateRange,
  selectedProvider,
  onProviderChange = () => {}
}) => {
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const { t } = useTranslation();
  
  return (
    <div className={cn(
      "w-full pb-4 pt-4",
      isDark ? "border-b border-slate-800" : "border-b border-slate-200",
    )}>
      <div className="flex flex-col gap-4 px-4">
        {/* Layout de três colunas com espaçamento proporcional */}
        <div className="flex flex-col lg:flex-row items-start lg:items-center gap-4 w-full">
          {/* Coluna 1: Logo e Título (25% da largura) */}
          <div className="flex items-center flex-shrink-0 lg:w-1/4">
            <div className={cn("flex items-center mr-2", color)}>
              <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
            </div>
            <h1 className="text-xl sm:text-2xl font-semibold">{title}</h1>
          </div>

          {/* Coluna 2: Filtro de Provedor (50% da largura - verdadeiramente centralizado) */}
          {showProviderFilter && (
            <div className="lg:w-1/2 flex justify-center">
              <CloudProviderFilter
                selectedProvider={selectedProvider}
                onProviderChange={onProviderChange}
              />
            </div>
          )}

          {/* Coluna 3: Filtros de Tempo (25% da largura) */}
          <div className="flex items-center gap-2 flex-shrink-0 lg:w-1/4 lg:justify-end">
            {showTimeFilter && (
              <TimeFilter
                value={timeFilter}
                onChange={onTimeFilterChange}
                onCustomDateRange={onCustomDateRange}
                currentCustomRange={customDateRange}
              />
            )}
            
            {actions}
          </div>
        </div>

        {/* Descrição (se fornecida) */}
        {description && (
          <div className="px-4">
            <p className="text-sm text-muted-foreground max-w-2xl">
              {description}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
