import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Activity, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface ResourceUsage {
  name: string;
  usage: number;
  totalAvailable: number;
  warningThreshold: number;
}

interface ResourceUtilizationCardProps {
  resources: ResourceUsage[];
}

export function ResourceUtilizationCard({ resources }: ResourceUtilizationCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 5;
  
  // Calcular a média de utilização geral
  const averageUtilization = Math.round(
    resources.reduce((sum, resource) => {
      const utilizationPercentage = Math.round((resource.usage / resource.totalAvailable) * 100);
      return sum + utilizationPercentage;
    }, 0) / resources.length
  );

  // Determinar a classe de cor com base na média
  const getAverageUtilizationColor = () => {
    if (averageUtilization >= 85) return isDark ? 'text-red-400' : 'text-XCost-red';
    if (averageUtilization >= 70) return isDark ? 'text-amber-400' : 'text-amber-500';
    return isDark ? 'text-blue-400' : 'text-XCost-blue';
  };
  
  // Componente de barra de progresso personalizado
  const CustomProgressBar = React.forwardRef<
    React.ElementRef<typeof ProgressPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> & { warningThreshold?: number }
  >(({ className, value, warningThreshold = 85, ...props }, ref) => {
    let indicatorClass = "bg-primary";
    
    if (value && warningThreshold) {
      if (value >= warningThreshold) {
        indicatorClass = isDark ? "bg-red-500" : "bg-XCost-red";
      } else if (value >= warningThreshold * 0.8) {
        indicatorClass = isDark ? "bg-amber-500" : "bg-amber-500";
      } else {
        indicatorClass = isDark ? "bg-blue-500" : "bg-XCost-blue";
      }
    }
    
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
          className={cn("h-full w-full flex-1 transition-all", indicatorClass)}
          style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
        />
      </ProgressPrimitive.Root>
    );
  });
  CustomProgressBar.displayName = "CustomProgressBar";
  
  // Calcular o número total de páginas
  const totalPages = Math.ceil(resources.length / itemsPerPage);
  
  // Obter os recursos da página atual
  const paginatedResources = resources.slice(
    currentPage * itemsPerPage, 
    (currentPage + 1) * itemsPerPage
  );
  
  // Verificar se é necessário exibir a paginação
  const shouldShowPagination = resources.length > itemsPerPage;
  
  // Funções para navegação entre páginas
  const handlePrevious = () => {
    setCurrentPage(prev => (prev > 0 ? prev - 1 : totalPages - 1));
  };

  const handleNext = () => {
    setCurrentPage(prev => (prev < totalPages - 1 ? prev + 1 : 0));
  };

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="flex items-center text-lg font-medium">
          <Activity className="mr-2 h-5 w-5 text-amber-500" />
          <span className="hidden lg:inline">{t('resourceUtilization.title')}</span>
          <span className="lg:hidden">{t('resourceUtilization.titleShort')}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow pb-3 flex flex-col">
        <div className="flex-grow space-y-4">
          <div className="text-center mb-4">
            <div className={`text-3xl font-bold ${getAverageUtilizationColor()}`}>{averageUtilization}%</div>
            <div className="text-sm text-muted-foreground">
              {t('resourceUtilization.averageUtilization')}
            </div>
            <div className="mt-2">
              <CustomProgressBar value={averageUtilization} warningThreshold={85} className="h-2" />
            </div>
          </div>
          
          <div className="space-y-3">
            {paginatedResources.map((resource) => {
              const utilizationPercentage = Math.round((resource.usage / resource.totalAvailable) * 100);
              return (
                <div key={resource.name} className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">{resource.name}</span>
                    <span className={cn(
                      "text-xs font-medium",
                      utilizationPercentage >= resource.warningThreshold 
                        ? isDark ? "text-red-400" : "text-XCost-red"
                        : utilizationPercentage >= resource.warningThreshold * 0.8 
                          ? isDark ? "text-amber-400" : "text-amber-500"
                          : isDark ? "text-slate-400" : "text-muted-foreground"
                    )}>
                      {utilizationPercentage}%
                    </span>
                  </div>
                  <CustomProgressBar 
                    value={utilizationPercentage} 
                    warningThreshold={resource.warningThreshold}
                  />
                </div>
              );
            })}
          </div>
        </div>
        
        {/* Paginação - Só exibir se tiver mais de 4 itens */}
        {shouldShowPagination && (
          <div className={cn(
            "flex justify-center items-center mt-2 pt-1 border-t",
            isDark ? "border-slate-700" : "border-gray-100"
          )}>
            <div className="text-xs flex items-center">
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-6 w-6" 
                onClick={handlePrevious}
              >
                <ChevronLeft className="h-3 w-3" />
              </Button>
              <span className="px-1 text-muted-foreground">
                {currentPage + 1}/{totalPages}
              </span>
              <Button 
                variant="ghost" 
                size="icon" 
                className="h-6 w-6" 
                onClick={handleNext}
              >
                <ChevronRight className="h-3 w-3" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
