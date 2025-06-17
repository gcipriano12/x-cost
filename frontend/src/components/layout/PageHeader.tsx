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
import { ChevronRight, RefreshCw } from 'lucide-react';

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
  onRefresh?: () => void;
  isRefreshing?: boolean;
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
  onProviderChange = () => {},
  onRefresh,
  isRefreshing = false
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
        {/* Layout responsivo com centralização absoluta */}
        <div className="flex flex-col lg:grid lg:grid-cols-3 items-start lg:items-center gap-4 w-full">
          {/* Coluna 1: Logo e Título (sempre à esquerda) */}
          <div className="flex items-center">
            <div className={cn("flex items-center mr-2", color)}>
              <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
            </div>
            <h1 className="text-xl sm:text-2xl font-semibold">{title}</h1>
          </div>

          {/* Coluna 2: Filtro de Provedor (sempre no centro absoluto) */}
          {showProviderFilter ? (
            <div className="flex justify-center w-full">
              <CloudProviderFilter
                selectedProvider={selectedProvider}
                onProviderChange={onProviderChange}
              />
            </div>
          ) : (
            <div></div>
          )}

          {/* Coluna 3: Filtros de Tempo e Refresh (sempre à direita) */}
          <div className="flex items-center gap-2 justify-start lg:justify-end">
            {showTimeFilter && (
              <TimeFilter
                value={timeFilter}
                onChange={onTimeFilterChange}
                onCustomDateRange={onCustomDateRange}
                currentCustomRange={customDateRange}
              />
            )}
            
            {onRefresh && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={onRefresh} 
                disabled={isRefreshing}
                title="Refresh all data"
                className="h-8 w-8 p-0"
              >
                <RefreshCw className={cn(
                  "h-4 w-4",
                  isRefreshing && "animate-spin"
                )} />
              </Button>
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
