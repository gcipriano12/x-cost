import React from 'react';
import { useTranslation } from 'react-i18next';
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { GitCompare, ArrowRight } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { MockDataBadge } from '@/components/ui/mock-data-badge';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface Environment {
  name: string;
  cost: number;
  previousPeriodCost: number;
  efficiency: number;
}

interface EnvironmentComparisonCardProps {
  environments: Environment[];
  currency: string;
  isUsingMockData?: boolean;
}

export function EnvironmentComparisonCard({ environments, currency, isUsingMockData = false }: EnvironmentComparisonCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  // Find the environment with the highest cost for scaling
  const maxCost = Math.max(...environments.map(env => env.cost));
  
  // Função para determinar a cor da eficiência com mais nuances
  const getEfficiencyColor = (efficiency: number) => {
    if (efficiency >= 80) return isDark ? 'text-green-400' : 'text-XCost-green';
    if (efficiency >= 65) return isDark ? 'text-amber-400' : 'text-amber-500';
    return isDark ? 'text-red-400' : 'text-XCost-red';
  };
  
  // Função para determinar a cor do valor de variação (positivo ou negativo)
  const getChangeColor = (isIncrease: boolean) => {
    return isIncrease 
      ? isDark ? 'text-red-400' : 'text-XCost-red' 
      : isDark ? 'text-green-400' : 'text-XCost-green';
  };
  
  // Componente personalizado para barra de progresso
  const CustomProgressBar = React.forwardRef<
    React.ElementRef<typeof ProgressPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> & { environmentName?: string }
  >(({ className, value, environmentName, ...props }, ref) => {
    // Cor baseada no ambiente para diferenciar visualmente
    const getEnvironmentColor = () => {
      if (environmentName === t('mockData.environments.production')) return isDark ? "bg-blue-500" : "bg-blue-500";
      if (environmentName === t('mockData.environments.staging')) return isDark ? "bg-purple-500" : "bg-purple-500";
      if (environmentName === t('mockData.environments.development')) return isDark ? "bg-amber-500" : "bg-amber-500";
      return isDark ? "bg-slate-500" : "bg-gray-500";
    };
    
    return (
      <ProgressPrimitive.Root
        ref={ref}
        className={cn(
          "relative h-1.5 w-full overflow-hidden rounded-full",
          isDark ? "bg-slate-700" : "bg-gray-100",
          className
        )}
        {...props}
      >
        <ProgressPrimitive.Indicator
          className={cn("h-full w-full flex-1 transition-all", getEnvironmentColor())}
          style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
        />
      </ProgressPrimitive.Root>
    );
  });
  CustomProgressBar.displayName = "CustomProgressBar";
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-base font-semibold">
            <GitCompare className={cn(
              "h-5 w-5 mr-2", 
              isDark ? "text-blue-400" : "text-blue-500"
            )} />
            <span className="hidden lg:inline">{t('environmentComparison.title')}</span>
            <span className="lg:hidden">{t('environmentComparison.titleShort')}</span>
          </CardTitle>
          {isUsingMockData && <MockDataBadge />}
        </div>
      </CardHeader>
      <CardContent className="flex-grow px-4 pt-2 pb-3 overflow-auto">
        <div className="space-y-3">
          {environments.map((env) => {
            const changePercentage = ((env.cost - env.previousPeriodCost) / env.previousPeriodCost) * 100;
            const isIncrease = changePercentage > 0;
            return (
              <div key={env.name} className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium truncate max-w-[40%]">{env.name}</span>
                  <span className="text-base font-bold truncate max-w-[55%] text-right">
                    {currency}{env.cost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}
                  </span>
                </div>
                <CustomProgressBar 
                  value={(env.cost / maxCost) * 100}
                  environmentName={env.name}
                />
                <div className="flex justify-between items-center text-xs text-muted-foreground mt-1">
                  <div className="flex items-center truncate max-w-[70%]">
                    <span className="whitespace-nowrap">{currency}{env.previousPeriodCost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                    <ArrowRight className="h-3 w-3 mx-1 flex-shrink-0" />
                    <span className="whitespace-nowrap">{currency}{env.cost.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                  </div>
                  <div className={`whitespace-nowrap ${getChangeColor(isIncrease)}`}>
                    {isIncrease ? '+' : ''}{changePercentage.toFixed(1)}%
                  </div>
                </div>
                <div className="flex justify-between items-center text-xs mt-0.5">
                  <span>{t('environmentComparison.efficiency')}</span>
                  <span className={getEfficiencyColor(env.efficiency)}>
                    {env.efficiency}%
                  </span>
                </div>
                <hr className={cn(
                  "my-1 border-t last:hidden",
                  isDark ? "border-slate-700" : "border-gray-100"
                )} />
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
