import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Calendar, ChevronLeft, ChevronRight, RefreshCw, HelpCircle, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { MockDataBadge } from '@/components/ui/mock-data-badge';
import { 
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogClose
} from "@/components/ui/dialog";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useTheme } from '@/hooks/useTheme';
import { useSeasonality } from '@/hooks/useSeasonality';
import { cn } from '@/lib/utils';

interface SeasonalityMetric {
  key: string;
  label: string;
  value: number;
  tooltip: string;
}

export function SeasonalityCard() {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const { data, loading, error, retry } = useSeasonality();
  const [currentPage, setCurrentPage] = useState(0);
  const [selectedMetric, setSelectedMetric] = useState<SeasonalityMetric | null>(null);
  const itemsPerPage = 4;
  
  // Definir métricas baseadas nos dados
  const metrics: SeasonalityMetric[] = data ? [
    {
      key: 'monthlyComparison',
      label: t('seasonality.monthlyComparison'),
      value: data.monthlyComparison,
      tooltip: t('seasonality.monthlyComparisonTooltip', 'Comparison with historical average for this month')
    },
    {
      key: 'weeklyPattern',
      label: t('seasonality.weeklyPattern'),
      value: data.weeklyPattern,
      tooltip: t('seasonality.weeklyPatternTooltip', 'Weekly spending pattern consistency')
    },
    {
      key: 'seasonalProgress',
      label: t('seasonality.seasonalProgress'),
      value: data.seasonalProgress,
      tooltip: t('seasonality.seasonalProgressTooltip', 'Progress towards expected seasonal peak')
    },
    {
      key: 'trendVariation',
      label: t('seasonality.trendVariation'),
      value: data.trendVariation,
      tooltip: t('seasonality.trendVariationTooltip', 'Variation from projected trend')
    }
  ] : [];

  // Calcular a média de sazonalidade
  const averageSeasonality = data ? Math.round(
    (data.monthlyComparison + data.weeklyPattern + data.seasonalProgress + data.trendVariation) / 4
  ) : 0;

  // Determinar a classe de cor com base no status geral
  const getOverallStatusColor = () => {
    if (!data) return isDark ? 'text-slate-400' : 'text-muted-foreground';
    
    switch (data.status) {
      case 'alert':
        return isDark ? 'text-red-400' : 'text-XCost-red';
      case 'attention':
        return isDark ? 'text-amber-400' : 'text-amber-500';
      case 'normal':
      default:
        return isDark ? 'text-blue-400' : 'text-XCost-blue';
    }
  };

  // Determinar cor específica para cada métrica baseada no valor
  const getMetricColor = (key: string, value: number) => {
    let isGood = false;
    let isAcceptable = false;

    switch (key) {
      case 'monthlyComparison':
        // 90-110% = bom (normal vs histórico), 80-89% ou 111-120% = aceitável, resto = ruim
        isGood = value >= 90 && value <= 110;
        isAcceptable = (value >= 80 && value < 90) || (value > 110 && value <= 120);
        break;
      
      case 'weeklyPattern':
        // 80-100% = bom (alta consistência), 60-79% = aceitável, <60% = ruim
        isGood = value >= 80;
        isAcceptable = value >= 60 && value < 80;
        break;
      
      case 'seasonalProgress':
        // Depende do mês atual - valores entre 30-70% geralmente são bons
        isGood = value >= 40 && value <= 80;
        isAcceptable = (value >= 25 && value < 40) || (value > 80 && value <= 90);
        break;
      
      case 'trendVariation':
        // 70-100% = bom (seguindo tendência), 50-69% = aceitável, <50% = ruim  
        isGood = value >= 70;
        isAcceptable = value >= 50 && value < 70;
        break;
      
      default:
        isGood = value >= 70;
        isAcceptable = value >= 50 && value < 70;
    }

    if (isGood) {
      return {
        text: isDark ? 'text-green-400' : 'text-green-600',
        bg: isDark ? 'bg-green-500' : 'bg-green-500'
      };
    } else if (isAcceptable) {
      return {
        text: isDark ? 'text-amber-400' : 'text-amber-600', 
        bg: isDark ? 'bg-amber-500' : 'bg-amber-500'
      };
    } else {
      return {
        text: isDark ? 'text-red-400' : 'text-red-600',
        bg: isDark ? 'bg-red-500' : 'bg-red-500'
      };
    }
  };
  
  // Componente de barra de progresso personalizado
  const CustomProgressBar = React.forwardRef<
    React.ElementRef<typeof ProgressPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> & { 
      status?: string;
      metricKey?: string;
      metricValue?: number;
    }
  >(({ className, value, status = 'normal', metricKey, metricValue, ...props }, ref) => {
    let indicatorClass = "bg-primary";
    
    // Se temos metricKey e metricValue, usar cores específicas da métrica
    if (metricKey && metricValue !== undefined) {
      const metricColor = getMetricColor(metricKey, metricValue);
      indicatorClass = metricColor.bg;
    } else {
      // Fallback para status geral
      switch (status) {
        case 'alert':
          indicatorClass = isDark ? "bg-red-500" : "bg-red-500";
          break;
        case 'attention':
          indicatorClass = isDark ? "bg-amber-500" : "bg-amber-500";
          break;
        case 'normal':
        default:
          indicatorClass = isDark ? "bg-blue-500" : "bg-blue-500";
          break;
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
  const totalPages = Math.ceil(metrics.length / itemsPerPage);
  
  // Obter as métricas da página atual
  const paginatedMetrics = metrics.slice(
    currentPage * itemsPerPage, 
    (currentPage + 1) * itemsPerPage
  );
  
  // Verificar se é necessário exibir a paginação
  const shouldShowPagination = metrics.length > itemsPerPage;
  
  // Funções para navegação entre páginas
  const handlePrevious = () => {
    setCurrentPage(prev => (prev > 0 ? prev - 1 : totalPages - 1));
  };

  const handleNext = () => {
    setCurrentPage(prev => (prev < totalPages - 1 ? prev + 1 : 0));
  };

  // Loading skeleton
  if (loading) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-2 flex-shrink-0">
          <CardTitle className="flex items-center text-lg font-medium">
            <Calendar className="mr-2 h-5 w-5 text-amber-500" />
            <span className="hidden lg:inline">{t('seasonality.title')}</span>
            <span className="lg:hidden">{t('seasonality.titleShort')}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow pb-3 flex flex-col">
          <div className="flex-grow space-y-4">
            <div className="text-center mb-4">
              <div className="w-16 h-8 bg-gray-200 rounded animate-pulse mx-auto mb-2"></div>
              <div className="w-24 h-4 bg-gray-200 rounded animate-pulse mx-auto mb-2"></div>
              <div className="w-full h-2 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="space-y-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="space-y-1.5">
                  <div className="flex justify-between items-center">
                    <div className="w-24 h-4 bg-gray-200 rounded animate-pulse"></div>
                    <div className="w-8 h-4 bg-gray-200 rounded animate-pulse"></div>
                  </div>
                  <div className="w-full h-1.5 bg-gray-200 rounded animate-pulse"></div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error && !data) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-2 flex-shrink-0">
          <CardTitle className="flex items-center text-lg font-medium">
            <Calendar className="mr-2 h-5 w-5 text-amber-500" />
            <span className="hidden lg:inline">{t('seasonality.title')}</span>
            <span className="lg:hidden">{t('seasonality.titleShort')}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow pb-3 flex flex-col items-center justify-center">
          <div className="text-center">
            <p className="text-sm text-muted-foreground mb-4">
              {t('seasonality.errorMessage', 'Unable to load seasonality data')}
            </p>
            <Button onClick={retry} variant="outline" size="sm">
              <RefreshCw className="mr-2 h-4 w-4" />
              {t('common.retry', 'Retry')}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Sempre mostrar empty state quando não há dados da API
  if (!data) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-2 flex-shrink-0">
          <CardTitle className="flex items-center text-lg font-medium">
            <Calendar className="mr-2 h-5 w-5 text-amber-500" />
            <span className="hidden lg:inline">{t('seasonality.title')}</span>
            <span className="lg:hidden">{t('seasonality.titleShort')}</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-grow pb-3 flex flex-col items-center justify-center">
          <div className="text-center">
            <Calendar className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
            <p className="text-sm text-muted-foreground">
              {t('seasonality.noData', 'API endpoint not implemented yet')}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg font-medium">
            <Calendar className="mr-2 h-5 w-5 text-amber-500" />
            <span className="hidden lg:inline">{t('seasonality.title')}</span>
            <span className="lg:hidden">{t('seasonality.titleShort')}</span>
          </CardTitle>
          {error && <MockDataBadge />}
        </div>
      </CardHeader>
      <CardContent className="flex-grow pb-3 flex flex-col">
        <div className="flex-grow space-y-4">
          <div className="text-center mb-4">
            <div className={`text-3xl font-bold ${getOverallStatusColor()}`}>{averageSeasonality}%</div>
            <div className="text-sm text-muted-foreground">
              {t('seasonality.averageSeasonality')}
            </div>
            <div className="mt-2">
              <CustomProgressBar value={averageSeasonality} status={data.status} className="h-2" />
            </div>
          </div>
          
          <div className="space-y-3">
            {paginatedMetrics.map((metric) => (
              <div key={metric.key} className="space-y-1.5">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-1">
                    <span className="text-sm font-medium">{metric.label}</span>
                    
                    {/* Tooltip para desktop */}
                    <div className="hidden sm:block">
                      <TooltipProvider>
                        <Tooltip delayDuration={0}>
                          <TooltipTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-4 w-4 p-0 hover:bg-transparent">
                              <HelpCircle className="h-3 w-3 text-muted-foreground hover:text-foreground transition-colors" />
                            </Button>
                          </TooltipTrigger>
                          <TooltipContent className={cn(
                            "max-w-xs",
                            isDark ? "bg-slate-800 border-slate-700 text-white" : "bg-white border-gray-200 text-slate-900"
                          )}>
                            <div>
                              <p className="font-medium mb-1">{metric.label}</p>
                              <p className="text-xs">{metric.tooltip}</p>
                            </div>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                    </div>
                    
                    {/* Botão para dispositivos móveis que abre um diálogo */}
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="sm:hidden h-4 w-4 p-0 hover:bg-transparent"
                      onClick={() => setSelectedMetric(metric)}
                    >
                      <HelpCircle className="h-3 w-3 text-muted-foreground hover:text-foreground transition-colors" />
                    </Button>
                  </div>
                  <span className={cn(
                    "text-xs font-medium",
                    getMetricColor(metric.key, metric.value).text
                  )}>
                    {metric.value}%
                  </span>
                </div>
                <CustomProgressBar 
                  value={metric.value} 
                  metricKey={metric.key}
                  metricValue={metric.value}
                />
              </div>
            ))}
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
      
      {/* Diálogo para informações detalhadas no mobile */}
      <Dialog open={!!selectedMetric} onOpenChange={() => setSelectedMetric(null)}>
        <DialogContent className={cn(
          "sm:max-w-md",
          isDark ? "bg-slate-900 border-slate-700" : "bg-white border-gray-200"
        )}>
          <DialogHeader className="space-y-3">
            <div className="flex items-center justify-between">
              <DialogTitle className="text-lg font-semibold">
                {selectedMetric?.label}
              </DialogTitle>
              <DialogClose asChild>
                <Button variant="ghost" size="icon" className="h-6 w-6">
                  <X className="h-4 w-4" />
                </Button>
              </DialogClose>
            </div>
          </DialogHeader>
          
          {selectedMetric && (
            <div className="space-y-4">
              <div className="text-center">
                <div className={cn(
                  "text-2xl font-bold mb-1",
                  getMetricColor(selectedMetric.key, selectedMetric.value).text
                )}>
                  {selectedMetric.value}%
                </div>
                <div className="mb-3">
                  <CustomProgressBar 
                    value={selectedMetric.value} 
                    metricKey={selectedMetric.key}
                    metricValue={selectedMetric.value}
                    className="h-2"
                  />
                </div>
              </div>
              
              <div className={cn(
                "p-3 rounded-lg",
                isDark ? "bg-slate-800" : "bg-gray-50"
              )}>
                <p className="text-sm text-muted-foreground">
                  {selectedMetric.tooltip}
                </p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </Card>
  );
}