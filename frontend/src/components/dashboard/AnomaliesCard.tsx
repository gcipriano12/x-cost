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
  const displayAnomalies = sortedAnomalies.slice(0, 4); // Máximo 4 itens (1 principal + 3 na lista)
  
  // Calculate total impact
  const totalImpact = displayAnomalies.reduce((sum, anomaly) => sum + anomaly.cost_impact, 0);
  


  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : displayAnomalies.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < displayAnomalies.length - 1 ? prev + 1 : 0));
  };
  
  // Reset currentIndex when anomalies change
  React.useEffect(() => {
    if (displayAnomalies.length > 0 && currentIndex >= displayAnomalies.length) {
      setCurrentIndex(0);
    }
  }, [displayAnomalies.length, currentIndex]);
  
  // Get severity counts
  const severityCounts = displayAnomalies.reduce((counts, anomaly) => {
    counts[anomaly.severity] = (counts[anomaly.severity] || 0) + 1;
    return counts;
  }, {} as Record<string, number>);
  
  const shouldShowPagination = displayAnomalies.length > 1;
  
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
            <span className="text-xl font-bold text-amber-500">{displayAnomalies.length}</span>
            {lastUpdated && (
              <Button variant="ghost" size="sm" onClick={refetch} title="Refresh">
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 pt-2 pb-3 overflow-auto">
          {displayAnomalies.length > 0 ? (
          <div className="flex flex-col h-full">
            {/* Card principal */}
            <div className={`flex-shrink-0 p-3 rounded-lg border mb-2 ${formatSeverity(displayAnomalies[currentIndex].severity).bgColor} ${formatSeverity(displayAnomalies[currentIndex].severity).borderColor}`}>
              <div className="flex justify-between items-start">
                <div className="flex items-center">
                  <AlertTriangle className={`h-5 w-5 mr-2 ${formatSeverity(displayAnomalies[currentIndex].severity).textColor}`} />
                  <h4 className={`font-medium text-sm ${formatSeverity(displayAnomalies[currentIndex].severity).textColor}`}>
                    {displayAnomalies[currentIndex].provider} {displayAnomalies[currentIndex].service}
                  </h4>
                </div>
                <Badge 
                  className={`ml-2 text-xs ${formatSeverity(displayAnomalies[currentIndex].severity).color}`}
                >
                  {formatSeverity(displayAnomalies[currentIndex].severity).label}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground my-1 ml-7 line-clamp-2">
                {displayAnomalies[currentIndex].description}
              </p>
              
              <div className="flex justify-between items-center mt-2 ml-7">
                <div className="flex items-center text-xs">
                  <span className="text-muted-foreground mr-1">Impact:</span>
                  <span className={`font-medium ${formatSeverity(displayAnomalies[currentIndex].severity).textColor}`}>
                    {formatCurrency(displayAnomalies[currentIndex].cost_impact, displayAnomalies[currentIndex].currency, 'en-US', true)}
                  </span>
                </div>
                
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className={`h-6 text-xs ${formatSeverity(displayAnomalies[currentIndex].severity).textColor}`}
                  onClick={() => navigate('/anomalies')}
                >
                  <span className="mr-1">View Details</span>
                  <ArrowUpRight className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Lista de outras anomalias */}
            <div className="flex-grow overflow-auto space-y-1.5">
              {displayAnomalies.map((anomaly, idx) => {
                if (idx === currentIndex) return null;
                const severityStyle = formatSeverity(anomaly.severity);
                return (
                  <div 
                    key={`${anomaly.id}-${idx}`} 
                    className={cn(
                      "flex items-center justify-between p-2 border rounded-lg text-xs cursor-pointer",
                      isDark 
                        ? "border-slate-700 hover:bg-slate-800" 
                        : "border-gray-100 hover:bg-gray-50"
                    )}
                    onClick={() => setCurrentIndex(idx)}
                  >
                    <div className="flex items-center flex-1">
                      <div 
                        className="h-2 w-2 rounded-full mr-2"
                        style={{backgroundColor: severityStyle.icon}}
                      />
                      <span className="font-medium truncate">
                        {anomaly.provider} {anomaly.service}
                      </span>
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
            
            {/* Paginação - só exibe se tiver mais de 1 item */}
            {shouldShowPagination && displayAnomalies.length > 1 && (
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
                    {currentIndex + 1}/{displayAnomalies.length}
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
            "h-full flex items-center justify-center border rounded-lg",
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
