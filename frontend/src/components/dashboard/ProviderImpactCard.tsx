import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Cloud, TrendingUp, AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react';
import { ProviderBadge } from '@/components/ui/provider-badge';
import { Progress } from '@/components/ui/progress';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { useNavigate } from 'react-router-dom';
import { useAnomalies, useSavingsOpportunities } from '@/hooks/useOptimization';

// Função para formatar valores de forma inteligente
const formatSmartCurrency = (amount: number, currency: string = 'USD'): string => {
  if (amount >= 10000) {
    return `${(amount / 1000).toFixed(1)}K ${currency}`;
  } else {
    return `$${Math.round(amount).toLocaleString()}`;
  }
};

// Função para calcular score de eficiência
const calculateEfficiencyScore = (totalCost: number, potentialSavings: number, anomalyCost: number): number => {
  if (totalCost === 0) return 0;
  const savingsRatio = (potentialSavings / totalCost) * 100;
  const anomalyPenalty = (anomalyCost / totalCost) * 50;
  return Math.max(0, Math.min(100, savingsRatio - anomalyPenalty));
};

// Função para obter cor do score
const getScoreColor = (score: number): string => {
  if (score >= 75) return 'text-green-600 dark:text-green-400';
  if (score >= 50) return 'text-yellow-600 dark:text-yellow-400';
  return 'text-red-600 dark:text-red-400';
};

interface ProviderImpactCardProps {
  autoRefresh?: boolean;
}

export function ProviderImpactCard({ autoRefresh = true }: ProviderImpactCardProps) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  
  // Fetch data from both hooks
  const { data: anomalies, loading: anomaliesLoading } = useAnomalies({ 
    autoRefresh, 
    refreshInterval: 5 * 60 * 1000 
  });
  
  const { data: opportunities, loading: opportunitiesLoading } = useSavingsOpportunities({ 
    autoRefresh, 
    refreshInterval: 5 * 60 * 1000 
  });

  const loading = anomaliesLoading || opportunitiesLoading;

  // Process data by provider
  const providerData = React.useMemo(() => {
    if (!anomalies || !opportunities) return [];

    const providers = ['AWS', 'Azure', 'GCP', 'Oracle'];
    
    return providers.map(provider => {
      // Filter data for this provider
      const providerAnomalies = anomalies.filter(a => a.provider === provider);
      const providerOpportunities = opportunities.filter(o => o.provider === provider);
      
      // Calculate metrics
      const totalAnomalyCost = providerAnomalies.reduce((sum, a) => sum + a.cost_impact, 0);
      const totalPotentialSavings = providerOpportunities.reduce((sum, o) => sum + o.estimated_savings, 0);
      const anomalyCount = providerAnomalies.length;
      const opportunityCount = providerOpportunities.length;
      
      // Estimate total cost (for demo purposes, using anomaly + savings as base)
      const estimatedTotalCost = totalAnomalyCost + totalPotentialSavings * 2;
      
      // Calculate efficiency score
      const efficiencyScore = calculateEfficiencyScore(estimatedTotalCost, totalPotentialSavings, totalAnomalyCost);
      
      return {
        provider,
        anomalyCount,
        opportunityCount,
        totalAnomalyCost,
        totalPotentialSavings,
        estimatedTotalCost,
        efficiencyScore: Math.round(efficiencyScore),
        hasData: anomalyCount > 0 || opportunityCount > 0
      };
    }).filter(data => data.hasData); // Only show providers with data
  }, [anomalies, opportunities]);

  // Sort by efficiency score (descending)
  const sortedProviders = [...providerData].sort((a, b) => b.efficiencyScore - a.efficiencyScore);
  
  const itemsPerPage = 2;
  const totalPages = Math.ceil(sortedProviders.length / itemsPerPage);
  const startIndex = currentIndex * itemsPerPage;
  const displayProviders = sortedProviders.slice(startIndex, startIndex + itemsPerPage);

  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : totalPages - 1));
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < totalPages - 1 ? prev + 1 : 0));
  };

  const shouldShowPagination = totalPages > 1;

  // Loading state
  if (loading) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-1 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center text-lg font-medium">
              <Cloud className="mr-2 h-5 w-5 text-blue-500" />
              Provider Impact Analysis
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex-grow p-3 pt-2 pb-3">
          <div className="space-y-3">
            <div className="h-20 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />
            <div className="h-20 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse" />
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
            <Cloud className="mr-2 h-5 w-5 text-blue-500" />
            {isMobile ? 'Provider Impact' : 'Provider Impact Analysis'}
          </CardTitle>
          <div className="flex items-center space-x-2">
            <div className={`whitespace-nowrap ${isMobile ? 'text-lg' : 'text-xl'} font-bold text-blue-600 dark:text-blue-400`}>
              {sortedProviders.length} Active
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 overflow-hidden relative">
        {displayProviders.length > 0 ? (
          <div className="h-full flex flex-col">
            {/* Provider cards */}
            <div className="flex-1 space-y-3">
              {displayProviders.map((data) => (
                <div 
                  key={data.provider}
                  className={cn(
                    "p-3 rounded-lg border transition-all duration-200",
                    isDark 
                      ? "bg-slate-800/50 border-slate-700 hover:bg-slate-800/70" 
                      : "bg-white border-gray-200 hover:bg-gray-50"
                  )}
                >
                  {/* Header */}
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <ProviderBadge provider={data.provider} size="sm" />
                      <span className={`font-medium ${isMobile ? 'text-sm' : 'text-base'}`}>
                        {data.provider}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`text-2xl font-bold ${getScoreColor(data.efficiencyScore)}`}>
                        {data.efficiencyScore}
                      </span>
                      <span className="text-xs text-muted-foreground">score</span>
                    </div>
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-2 gap-3">
                    {/* Anomalies */}
                    <div className="space-y-1">
                      <div className="flex items-center gap-1">
                        <AlertTriangle className="h-3 w-3 text-amber-500" />
                        <span className="text-xs text-muted-foreground">Anomalies</span>
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="text-xs">{data.anomalyCount} issues</span>
                          <span className="text-xs font-medium text-red-600 dark:text-red-400">
                            {formatSmartCurrency(data.totalAnomalyCost)}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Opportunities */}
                    <div className="space-y-1">
                      <div className="flex items-center gap-1">
                        <TrendingUp className="h-3 w-3 text-green-500" />
                        <span className="text-xs text-muted-foreground">Savings</span>
                      </div>
                      <div className="space-y-1">
                        <div className="flex justify-between items-center">
                          <span className="text-xs">{data.opportunityCount} opps</span>
                          <span className="text-xs font-medium text-green-600 dark:text-green-400">
                            {formatSmartCurrency(data.totalPotentialSavings)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Efficiency Progress */}
                  <div className="mt-2">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-xs text-muted-foreground">Efficiency</span>
                      <span className="text-xs font-medium">{data.efficiencyScore}%</span>
                    </div>
                    <Progress 
                      value={data.efficiencyScore}
                      className={cn("h-1.5", isDark ? "bg-slate-700" : "bg-gray-100")}
                    />
                  </div>
                </div>
              ))}
            </div>
            
            {/* Pagination */}
            {shouldShowPagination && (
              <div className={cn(
                "flex justify-center items-center border-t pt-2 h-8 mt-auto",
                isDark ? "border-slate-700" : "border-gray-100"
              )}>
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
              </div>
            )}
          </div>
        ) : (
          <div className={cn(
            "flex items-center justify-center border rounded-lg mx-1 my-2 py-12",
            isDark ? "border-slate-700 border-dashed" : "border-dashed"
          )}>
            <div className="text-center">
              <p className="text-muted-foreground text-sm mb-2">No provider data available</p>
              <Button variant="outline" size="sm" onClick={() => navigate('/dashboard')}>
                Refresh Data
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}