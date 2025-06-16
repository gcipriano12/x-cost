import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, ArrowUpRight, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAnomalies } from '@/hooks/useOptimization';
import { formatSeverity, formatCurrency, formatRelativeTime, sortByPriority } from '@/utils/optimizationUtils';

// Função para obter a cor da badge do provider
const getProviderBadgeColor = (provider: string) => {
  switch (provider?.toLowerCase()) {
    case 'aws':
      return 'bg-orange-100 text-orange-700 border-orange-200';
    case 'azure':
      return 'bg-blue-100 text-blue-700 border-blue-200';
    case 'gcp':
    case 'google':
      return 'bg-green-100 text-green-700 border-green-200';
    case 'oracle':
      return 'bg-red-500 text-white border-red-600';
    default:
      return 'bg-gray-100 text-gray-700 border-gray-200';
  }
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
  const itemsPerPage = 6; // 1 principal + 5 na lista
  const startIndex = currentIndex * itemsPerPage;
  const displayAnomalies = sortedAnomalies.slice(startIndex, startIndex + itemsPerPage);
  
  // Calculate total impact from all anomalies
  const totalImpact = sortedAnomalies.reduce((sum, anomaly) => sum + anomaly.cost_impact, 0);
  
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
      listAnomalies = displayAnomalies.filter(anomaly => anomaly.id !== selected.id).slice(0, 5);
    }
  } else {
    // Quando não há seleção, usar a lógica normal
    listAnomalies = displayAnomalies.slice(1, 6);
  }
  
  // Garantir que sempre tenhamos 5 itens na lista, buscando de outras páginas se necessário
  if (listAnomalies.length < 5) {
    let nextPageIndex = currentIndex + 1;
    while (listAnomalies.length < 5 && nextPageIndex * itemsPerPage < sortedAnomalies.length) {
      const nextPageStart = nextPageIndex * itemsPerPage;
      const nextPageAnomalies = sortedAnomalies.slice(nextPageStart, nextPageStart + itemsPerPage);
      
      for (const anomaly of nextPageAnomalies) {
        if (anomaly.id !== mainAnomaly.id && listAnomalies.length < 5) {
          listAnomalies.push(anomaly);
        }
      }
      nextPageIndex++;
    }
  }
  
  // Calculate total pages
  const totalPages = Math.ceil(sortedAnomalies.length / itemsPerPage);
  
  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : totalPages - 1));
    // Resetar a seleção ao mudar de página
    setSelectedAnomaly(null);
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < totalPages - 1 ? prev + 1 : 0));
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
            <Button variant="ghost" size="sm" onClick={refetch}>
              <RefreshCw className="h-4 w-4" />
            </Button>
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
          <CardTitle className="flex items-center text-lg font-medium whitespace-nowrap">
            <AlertTriangle className="mr-2 h-5 w-5 text-amber-500" />
            {isMobile ? 'Anomalies' : 'Anomalies Detected'}
          </CardTitle>
          <div className="flex items-center space-x-2">
            {severityCounts.critical > 0 && (
              <Badge className={formatSeverity('critical').color}>
                {severityCounts.critical} CRITICAL
              </Badge>
            )}
            {severityCounts.high > 0 && (
              <Badge className={formatSeverity('high').color}>
                {severityCounts.high} HIGH
              </Badge>
            )}
            <span className="text-xl font-bold text-amber-500">{sortedAnomalies.length}</span>
            {lastUpdated && (
              <Button variant="ghost" size="sm" onClick={refetch} title="Refresh">
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 pt-2 pb-0 overflow-auto">
          {displayAnomalies.length > 0 ? (
          <div className="flex flex-col">
            {/* Card principal */}
            <div className={`flex-shrink-0 p-2 rounded-lg border mb-1.5 ${formatSeverity(mainAnomaly.severity).bgColor} ${formatSeverity(mainAnomaly.severity).borderColor}`}>
              <div className="flex justify-between items-start">
                <div className="flex items-center flex-1 mr-2">
                  <AlertTriangle className={`h-5 w-5 mr-2 ${formatSeverity(mainAnomaly.severity).textColor}`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className={`font-medium text-sm ${formatSeverity(mainAnomaly.severity).textColor}`}>
                        {mainAnomaly.provider} {mainAnomaly.service}
                      </h4>
                      {shouldShowProviderTags && (
                        <Badge className={cn("text-[10px] px-1.5 py-0", getProviderBadgeColor(mainAnomaly.provider))}>
                          {mainAnomaly.provider.toUpperCase()}
                        </Badge>
                      )}
                    </div>
                  </div>
                </div>
                <Badge 
                  className={`ml-2 text-xs ${formatSeverity(mainAnomaly.severity).color}`}
                >
                  {formatSeverity(mainAnomaly.severity).label}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground my-1 ml-7 line-clamp-2">
                {mainAnomaly.description}
              </p>
              
              <div className="flex justify-between items-center mt-2 ml-7">
                <div className="flex items-center text-xs">
                  <span className="text-muted-foreground mr-1">Impact:</span>
                  <span className={`font-medium ${formatSeverity(mainAnomaly.severity).textColor}`}>
                    {formatCurrency(mainAnomaly.cost_impact, mainAnomaly.currency, 'en-US', true)}
                  </span>
                </div>
                
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className={`h-6 text-xs ${formatSeverity(mainAnomaly.severity).textColor}`}
                  onClick={() => navigate('/anomalies')}
                >
                  <span className="mr-1">View Details</span>
                  <ArrowUpRight className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Lista de outras anomalias */}
            <div className="space-y-1">
              {/* Sempre renderiza exatamente 5 itens na lista (slots) */}
              {Array.from({ length: 5 }).map((_, slotIdx) => {
                const anomaly = slotIdx < listAnomalies.length ? listAnomalies[slotIdx] : null;
                
                // Se não houver anomalia para este slot, renderiza um item vazio
                if (!anomaly) {
                  return (
                    <div 
                      key={`empty-slot-${slotIdx}`} 
                      className={cn(
                        "flex items-center justify-between p-1.5 border rounded-lg text-xs opacity-0",
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
                      "flex items-center justify-between p-1.5 border rounded-lg text-xs cursor-pointer hover:bg-accent/50 transition-colors",
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
                        style={{backgroundColor: severityStyle.icon}}
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-1.5">
                          <span className="font-medium truncate">
                            {anomaly.provider} {anomaly.service}
                          </span>
                          {shouldShowProviderTags && (
                            <Badge className={cn("text-[8px] px-1 py-0", getProviderBadgeColor(anomaly.provider))}>
                              {anomaly.provider.toUpperCase()}
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <span className={cn(
                      "font-medium ml-2 whitespace-nowrap",
                      isMobile && "text-[10px]",
                      severityStyle.textColor
                    )}>
                      {formatCurrency(anomaly.cost_impact, anomaly.currency, 'en-US', true)}
                    </span>
                  </div>
                );
              })}
            </div>
            
            {/* Total Impact Summary */}
            <div className={cn(
              "mt-2 pt-2 border-t flex justify-between items-center",
              isDark ? "border-slate-700" : "border-gray-100"
            )}>
              <span className="text-sm font-medium">Total Impact:</span>
              <span className="text-sm font-bold text-amber-500">
                {formatCurrency(totalImpact, 'USD', 'en-US', true)}
              </span>
            </div>
            
            {/* Paginação - só exibe se tiver mais de 1 página */}
            {shouldShowPagination && (
              <div className={cn(
                "flex justify-center items-center border-t mt-3 py-1",
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
                    {currentIndex + 1}/{totalPages}
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
