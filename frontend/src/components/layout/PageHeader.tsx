import React from 'react';
import { useTranslation } from 'react-i18next';
import { DateRange } from 'react-day-picker';
import { TimeFilter } from '@/components/dashboard/TimeFilter';
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
  actions?: React.ReactNode;
  timeFilter?: string;
  onTimeFilterChange?: (value: string) => void;
  onCustomDateRange?: (range: DateRange | undefined) => void;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  icon: Icon,
  title,
  description,
  color = 'text-blue-600',
  showTimeFilter = true,
  actions,
  timeFilter = '30d',
  onTimeFilterChange = () => {},
  onCustomDateRange
}) => {
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const { t } = useTranslation();
  
  return (
    <div className={cn(
      "w-full pb-4 pt-4",
      isDark ? "border-b border-slate-800" : "border-b border-slate-200",
    )}>
      <div className="flex flex-col sm:flex-row justify-between gap-4 px-4">
        <div className="flex flex-col pl-4">
          <div className="flex items-center">
            <div className={cn("flex items-center mr-2", color)}>
              <Icon className="h-4 w-4 sm:h-5 sm:w-5" />
            </div>
            <h1 className="text-xl sm:text-2xl font-semibold">{title}</h1>
          </div>
          {description && (
            <p className="text-sm text-muted-foreground mt-1 max-w-2xl">
              {description}
            </p>
          )}
        </div>

        <div className="flex items-center gap-2 self-end">
          {showTimeFilter && (
            <TimeFilter
              value={timeFilter}
              onChange={onTimeFilterChange}
              onCustomDateRange={onCustomDateRange}
            />
          )}
          
          {actions}
        </div>
      </div>
    </div>
  );
};
