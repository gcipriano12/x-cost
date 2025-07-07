import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, ArrowUpRight, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { MockDataBadge } from '@/components/ui/mock-data-badge';
import { ProviderBadge } from '@/components/ui/provider-badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAnomalies } from '@/hooks/useOptimization';
import { formatSeverity, sortByPriority } from '@/utils/optimizationUtils';

// Função para formatar valores de forma inteligente (igual ao SavingsCard)
const formatSmartCurrency = (amount: number, currency: string = 'USD'): string => {
  if (amount >= 10000) {
    // Para valores >= $10,000, usar formato com K
    return `${(amount / 1000).toFixed(1)}K ${currency}`;
  } else {
    // Para valores menores, usar formato normal sem decimais
    return `$${Math.round(amount).toLocaleString()}`;
  }
};

// Helper function to get severity color for dots
const getSeverityDotColor = (severity: string): string => {
  const severityStyle = formatSeverity(severity as any);
  if (severityStyle.textColor.includes('green')) return '#10b981';
  if (severityStyle.textColor.includes('yellow') || severityStyle.textColor.includes('amber')) return '#f59e0b';
  if (severityStyle.textColor.includes('orange')) return '#f97316';
  if (severityStyle.textColor.includes('red')) return '#ef4444';
  return '#ef4444'; // default to red for critical
};

interface AnomaliesCardProps {
  provider?: string;
  days?: number;
  autoRefresh?: boolean;
}

export function AnomaliesCard({ provider, days = 30, autoRefresh = true }: AnomaliesCardProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  const { t } = useTranslation();
  
  // Fetch anomalies data
  const { 
    data: anomalies, 
    loading, 
    error, 
    refetch, 
    lastUpdated 
  } = useAnomalies({ 
    provider, 
    days, 
    per_page: 20, // Get more for better display
    autoRefresh,
    refreshInterval: 5 * 60 * 1000 // 5 minutes
  });
  
  // Sort anomalies by priority and get top ones
  const sortedAnomalies = sortByPriority.anomalies(anomalies || []);
  // Calculate items per page based on screen size and available height
  const getItemsPerPage = () => {
    // Only use reduced items for very small screens (phones)
    if (typeof window !== 'undefined' && window.innerWidth < 640) return 3; // 1 principal + 2 na lista (small mobile)
    return 5; // 1 principal + 4 na lista (tablet, laptop, desktop)
  };
  
  const itemsPerPage = getItemsPerPage();
  const startIndex = currentIndex * itemsPerPage;
  const displayAnomalies = sortedAnomalies.slice(startIndex, startIndex + itemsPerPage);
  
  // Calculate total impact from all anomalies
  const totalImpact = sortedAnomalies.reduce((sum, anomaly) => sum + anomaly.cost_impact, 0);
  
  const headerTextColorClass = isDark ? "text-amber-400" : "text-amber-600";
  
  // Estado para rastrear a anomalia selecionada
  const [selectedAnomaly, setSelectedAnomaly] = useState<string | null>(null);
  
  // Determinar se deve mostrar as tags de provider (apenas quando o filtro for 'All' ou não definido)
  const shouldShowProviderTags = !provider || provider === 'all' || provider === '';
  
  // Separar a anomalia principal e a lista
  // Determinar qual anomalia deve ser mostrada como principal
  let mainAnomaly = displayAnomalies[0];
  let listAnomalies = displayAnomalies.slice(1);
  
  if (selectedAnomaly) {
    const selected = sortedAnomalies.find(anomaly => anomaly.id === selectedAnomaly);
    if (selected && displayAnomalies.includes(selected)) {
      // Quando uma anomalia é selecionada, ela vira a principal
      // mas mantemos a lista original sem reordenar
      mainAnomaly = selected;
      // A lista mantém os outros itens na ordem original, excluindo apenas o selecionado
      const maxListItems = itemsPerPage - 1; // Subtract 1 for main anomaly
      listAnomalies = displayAnomalies.filter(anomaly => anomaly.id !== selected.id).slice(0, maxListItems);
    }
  } else {
    // Quando não há seleção, usar a lógica normal
    const maxListItems = itemsPerPage - 1; // Subtract 1 for main anomaly
    listAnomalies = displayAnomalies.slice(1, maxListItems + 1);
  }
  
  // Garantir que sempre tenhamos o número correto de itens na lista, buscando de outras páginas se necessário
  const maxListItems = itemsPerPage - 1; // Subtract 1 for main anomaly
  if (listAnomalies.length < maxListItems) {
    let nextPageIndex = currentIndex + 1;
    while (listAnomalies.length < maxListItems && nextPageIndex * itemsPerPage < sortedAnomalies.length) {
      const nextPageStart = nextPageIndex * itemsPerPage;
      const nextPageAnomalies = sortedAnomalies.slice(nextPageStart, nextPageStart + itemsPerPage);
      
      for (const anomaly of nextPageAnomalies) {
        if (anomaly.id !== mainAnomaly.id && listAnomalies.length < maxListItems) {
          listAnomalies.push(anomaly);
        }
      }
      nextPageIndex++;
    }
  }
  
  // Calculate total pages
  const totalPages = Math.ceil(sortedAnomalies.length / itemsPerPage);
  
  const handlePrevious = () => {
    setCurrentIndex(prev => Math.max(0, prev - 1));
    // Resetar a seleção ao mudar de página
    setSelectedAnomaly(null);
  };

  const handleNext = () => {
    setCurrentIndex(prev => Math.min(totalPages - 1, prev + 1));
    // Resetar a seleção ao mudar de página
    setSelectedAnomaly(null);
  };
  
  // Reset currentIndex when anomalies change
  React.useEffect(() => {
    if (totalPages > 0 && currentIndex >= totalPages) {
      setCurrentIndex(0);
    }
  }, [totalPages, currentIndex]);
  
  // Get severity counts from all anomalies
  const severityCounts = sortedAnomalies.reduce((counts, anomaly) => {
    counts[anomaly.severity] = (counts[anomaly.severity] || 0) + 1;
    return counts;
  }, {} as Record<string, number>);
  
  // Reset currentIndex when anomalies change
  React.useEffect(() => {
    if (totalPages > 0 && currentIndex >= totalPages) {
      setCurrentIndex(0);
    }
  }, [totalPages, currentIndex]);
  
  // Efeito separado para lidar com a seleção de anomalia
  React.useEffect(() => {
    // Quando selecionar uma anomalia, garantir que ela seja a primeira na lista
    if (selectedAnomaly && sortedAnomalies.length > 0) {
      const selectedIndex = sortedAnomalies.findIndex(anomaly => anomaly.id === selectedAnomaly);
      if (selectedIndex >= 0) {
        setCurrentIndex(Math.floor(selectedIndex / itemsPerPage));
      }
    }
  }, [selectedAnomaly, sortedAnomalies, itemsPerPage]);
  
  const shouldShowPagination = totalPages > 1;
  
  // Loading state
  if (loading) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-1 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center text-lg font-medium">
              <AlertTriangle className="mr-2 h-5 w-5 text-amber-500" />
              {isMobile ? 'Anomalies' : 'Anomalies Detected'}
            </CardTitle>
            <Skeleton className="h-6 w-16" />
          </div>
        </CardHeader>
        <CardContent className="flex-grow p-3 pt-2 pb-3">
          <div className="space-y-3">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }
  
  // Error state
  if (error) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-1 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center text-lg font-medium">
              <AlertTriangle className="mr-2 h-5 w-5 text-amber-500" />
              {isMobile ? 'Anomalies' : 'Anomalies Detected'}
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex-grow p-3 pt-2 pb-3">
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">Error loading anomalies</p>
              <Button variant="outline" size="sm" onClick={refetch}>
                Try Again
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-1 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center text-lg font-medium">
              <AlertTriangle className="mr-2 h-5 w-5 text-amber-500" />
              <span className="hidden lg:inline">{t('anomalies.detected')}</span>
              <span className="lg:hidden">{t('common.anomalies')}</span>
            </CardTitle>
            {(!anomalies || anomalies.length === 0) && <MockDataBadge />}
          </div>
          <div className="flex items-center space-x-2">
            <div className={`whitespace-nowrap ${isMobile ? 'text-lg' : 'text-xl'} font-bold ${headerTextColorClass}`}>
              {totalImpact >= 1000 ? `$${(totalImpact / 1000).toFixed(1)}K` : `$${Math.round(totalImpact).toLocaleString()}`}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 overflow-hidden relative">
          {displayAnomalies.length > 0 ? (
          <div className="h-full flex flex-col">
            {/* Card principal */}
            <div className={`flex-shrink-0 p-2 rounded-lg border mb-1.5 ${formatSeverity(mainAnomaly.severity).bgColor} ${formatSeverity(mainAnomaly.severity).borderColor}`}>
              <div className="flex justify-between items-start">
                <div className="flex items-center flex-1 mr-2">
                  <AlertTriangle className={`h-5 w-5 mr-2 ${formatSeverity(mainAnomaly.severity).textColor}`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className={cn(
                        "font-medium text-sm truncate whitespace-nowrap overflow-hidden max-w-[120px]",
                        isDark ? "text-white" : "text-slate-900"
                      )}>
                        {mainAnomaly.provider} {mainAnomaly.service}
                      </h4>
                      {shouldShowProviderTags && (
                        <ProviderBadge 
                          provider={mainAnomaly.provider}
                          size="xs"
                        />
                      )}
                    </div>
                  </div>
                </div>
                <Badge 
                  className={`ml-2 text-xs whitespace-nowrap ${formatSeverity(mainAnomaly.severity).color}`}
                >
                  {formatSeverity(mainAnomaly.severity).label}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground my-1 ml-7 truncate whitespace-nowrap overflow-hidden">
                {mainAnomaly.description}
              </p>
              
              <div className="flex justify-between items-center mt-2 ml-7">
                <div className="flex items-center text-xs">
                  <span className="text-muted-foreground mr-1">{t('anomalies.impact')}:</span>
                  <span className={`font-medium ${formatSeverity(mainAnomaly.severity).textColor}`}>
                    {formatSmartCurrency(mainAnomaly.cost_impact, mainAnomaly.currency)}
                  </span>
                </div>
                
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className={`h-6 text-xs ${formatSeverity(mainAnomaly.severity).textColor}`}
                  onClick={() => navigate('/anomalies')}
                >
                  <span className="mr-1">{t('anomalies.investigate')}</span>
                  <ArrowUpRight className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Lista de outras anomalias - altura fixa para garantir posicionamento estático da paginação */}
            <div className="flex-1 flex flex-col">
              <div className={`space-y-1.5 overflow-hidden ${typeof window !== 'undefined' && window.innerWidth < 640 ? 'h-[84px]' : 'h-[196px]'}`}>
                {/* Sempre renderiza exatamente o número correto de itens na lista (slots) */}
                {Array.from({ length: maxListItems }).map((_, slotIdx) => {
                  const anomaly = slotIdx < listAnomalies.length ? listAnomalies[slotIdx] : null;
                  
                  // Se não houver anomalia para este slot, renderiza um item vazio
                  if (!anomaly) {
                    return (
                      <div 
                        key={`empty-slot-${slotIdx}`} 
                        className={cn(
                          "flex items-center justify-between p-2 border rounded-lg text-sm opacity-0 h-[40px]",
                          isDark 
                            ? "border-slate-700"
                            : "border-gray-100"
                        )}
                      >
                        <div className="flex items-center flex-1">
                          <div className="h-2 w-2 rounded-full mr-2" />
                          <span className="font-medium truncate">Item vazio</span>
                        </div>
                        <span className="font-medium ml-2">$0</span>
                      </div>
                    );
                  }
                  
                  const severityStyle = formatSeverity(anomaly.severity);
                  
                  return (
                    <div 
                      key={`${anomaly.id}-${slotIdx}`} 
                      className={cn(
                        "flex items-center justify-between p-2 border rounded-lg text-sm cursor-pointer hover:bg-accent/50 transition-colors h-[40px] min-h-[40px] max-h-[40px]",
                        isDark 
                          ? "border-slate-700" 
                          : "border-gray-100",
                        selectedAnomaly === anomaly.id && "ring-1 ring-primary"
                      )}
                      onClick={() => {
                        setSelectedAnomaly(anomaly.id);
                        setCurrentIndex(Math.floor(sortedAnomalies.findIndex(a => a.id === anomaly.id) / itemsPerPage));
                      }}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          setSelectedAnomaly(anomaly.id);
                          setCurrentIndex(Math.floor(sortedAnomalies.findIndex(a => a.id === anomaly.id) / itemsPerPage));
                        }
                      }}
                    >
                      <div className="flex items-center flex-1">
                        <div 
                          className="h-2 w-2 rounded-full mr-2"
                          style={{backgroundColor: getSeverityDotColor(anomaly.severity)}}
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-1.5">
                            <span className="font-medium truncate text-xs whitespace-nowrap overflow-hidden">
                              {anomaly.provider} {anomaly.service}
                            </span>
                            {shouldShowProviderTags && (
                              <ProviderBadge 
                                provider={anomaly.provider}
                                size="xs"
                              />
                            )}
                          </div>
                        </div>
                      </div>
                      <span className={cn(
                        "font-medium ml-2 whitespace-nowrap",
                        isMobile && "text-[10px]",
                        severityStyle.textColor
                      )}>
                        {formatSmartCurrency(anomaly.cost_impact, anomaly.currency)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Paginação - área fixa na parte inferior */}
            <div className={cn(
              "flex justify-center items-center pt-2 h-8 mt-auto",
              shouldShowPagination && "border-t",
              isDark ? "border-slate-700" : "border-gray-100"
            )}>
              {shouldShowPagination && (
                <div className="text-xs flex items-center justify-center">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6 flex items-center justify-center" 
                    onClick={handlePrevious}
                  >
                    <ChevronLeft className="h-3 w-3" />
                  </Button>
                  <span className="px-1 text-muted-foreground flex items-center">
                    {currentIndex + 1}/{totalPages}
                  </span>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6 flex items-center justify-center" 
                    onClick={handleNext}
                  >
                    <ChevronRight className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </div>
        </div>
        ) : (
          <div className={cn(
            "flex items-center justify-center border rounded-lg mx-1 my-2 py-12",
            isDark ? "border-slate-700 border-dashed" : "border-dashed"
          )}>
            <div className="text-center">
              <p className="text-muted-foreground text-sm mb-2">No anomalies detected</p>
              <Button variant="outline" size="sm" onClick={() => navigate('/anomalies')}>
                View All Anomalies
                <ArrowUpRight className="ml-1 h-3 w-3" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
