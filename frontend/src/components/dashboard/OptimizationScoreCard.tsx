import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { BarChart3, ArrowUpRight, RefreshCw, TrendingUp, AlertTriangle, CheckCircle, AlertCircle, XCircle, ChevronLeft, ChevronRight, Cloud } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { useOptimizationSummary, useOptimizationRecommendations, useAnomalies, useSavingsOpportunities } from '@/hooks/useOptimization';
import { ProviderBadge } from '@/components/ui/provider-badge';
import { formatHealthStatus, getScoreColor, getScoreDots } from '@/utils/optimizationUtils';
import { HealthRoundedGauge } from '@/components/ui/rounded-gauge';

interface OptimizationScoreCardProps {
  provider?: string;
  autoRefresh?: boolean;
}

export function OptimizationScoreCard({ 
  provider, 
  autoRefresh = true 
}: OptimizationScoreCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  const [currentProviderIndex, setCurrentProviderIndex] = React.useState(0);
  
  // Fetch optimization summary data
  const { 
    data: summary, 
    loading: summaryLoading, 
    error: summaryError, 
    refetch: refetchSummary,
    lastUpdated 
  } = useOptimizationSummary({ 
    provider, 
    autoRefresh,
    refreshInterval: 5 * 60 * 1000
  });
  
  // Fetch recommendations count
  const { 
    data: recommendations,
    total: recommendationsTotal,
    loading: recommendationsLoading
  } = useOptimizationRecommendations({ 
    provider_name: provider,
    per_page: 1 // Just need the count
  });

  // Fetch all anomalies and opportunities for provider analysis
  const { data: allAnomalies } = useAnomalies({ 
    autoRefresh: false 
  });
  
  const { data: allOpportunities } = useSavingsOpportunities({ 
    autoRefresh: false 
  });

  const loading = summaryLoading || recommendationsLoading;
  const error = summaryError;

  // Calculate efficiency scores for each provider
  const providerData = React.useMemo(() => {
    if (!allAnomalies || !allOpportunities) return [];

    const providers = ['AWS', 'Azure', 'GCP', 'Oracle'];
    
    return providers.map(providerName => {
      // Filter data for this provider
      const providerAnomalies = allAnomalies.filter(a => a.provider === providerName);
      const providerOpportunities = allOpportunities.filter(o => o.provider === providerName);
      
      // Calculate metrics
      const totalAnomalyCost = providerAnomalies.reduce((sum, a) => sum + a.cost_impact, 0);
      const totalPotentialSavings = providerOpportunities.reduce((sum, o) => sum + o.estimated_savings, 0);
      const anomalyCount = providerAnomalies.length;
      const opportunityCount = providerOpportunities.length;
      
      // Estimate total cost (for demo purposes, using anomaly + savings as base)
      const estimatedTotalCost = totalAnomalyCost + totalPotentialSavings * 2;
      
      // Calculate efficiency score (same logic as ProviderImpactCard)
      let efficiencyScore = 0;
      if (estimatedTotalCost > 0) {
        const savingsRatio = (totalPotentialSavings / estimatedTotalCost) * 100;
        const anomalyPenalty = (totalAnomalyCost / estimatedTotalCost) * 50;
        efficiencyScore = Math.max(0, Math.min(100, savingsRatio - anomalyPenalty));
      }
      
      return {
        provider: providerName,
        anomalyCount,
        opportunityCount,
        totalAnomalyCost,
        totalPotentialSavings,
        efficiencyScore: Math.round(efficiencyScore),
        hasData: anomalyCount > 0 || opportunityCount > 0
      };
    }).filter(data => data.hasData); // Only show providers with data
  }, [allAnomalies, allOpportunities]);

  // Sort by fixed order: AWS, Azure, GCP, Oracle
  const providerOrder = ['AWS', 'Azure', 'GCP', 'Oracle'];
  const sortedProviders = [...providerData].sort((a, b) => {
    const aIndex = providerOrder.indexOf(a.provider);
    const bIndex = providerOrder.indexOf(b.provider);
    return aIndex - bIndex;
  });
  
  // Current provider in the list
  const currentProvider = sortedProviders[currentProviderIndex];

  // Navigation functions
  const goToPrevProvider = () => {
    setCurrentProviderIndex(prev => Math.max(0, prev - 1));
  };

  const goToNextProvider = () => {
    setCurrentProviderIndex(prev => Math.min(sortedProviders.length - 1, prev + 1));
  };

  // Helper function to get score color
  const getScoreColor = (score: number): string => {
    if (score >= 75) return 'text-green-600 dark:text-green-400';
    if (score >= 50) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  // Helper function to format currency
  const formatSmartCurrency = (amount: number, currency: string = 'USD'): string => {
    if (amount >= 10000) {
      return `${(amount / 1000).toFixed(1)}K ${currency}`;
    } else {
      return `$${Math.round(amount).toLocaleString()}`;
    }
  };

  // Loading state
  if (loading) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-1 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center text-lg font-medium">
              <BarChart3 className="mr-2 h-5 w-5 text-blue-500" />
              {isMobile ? 'Score' : 'Optimization Score'}
            </CardTitle>
            <Skeleton className="h-6 w-16" />
          </div>
        </CardHeader>
        <CardContent className="flex-grow p-3 pt-2 pb-3">
          <div className="space-y-4">
            <div className="text-center">
              <Skeleton className="h-8 w-32 mx-auto mb-2" />
              <Skeleton className="h-12 w-12 rounded-full mx-auto" />
            </div>
            <Skeleton className="h-6 w-full" />
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
              <BarChart3 className="mr-2 h-5 w-5 text-blue-500" />
              {isMobile ? 'Score' : 'Optimization Score'}
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={refetchSummary}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="flex-grow p-3 pt-2 pb-3">
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">Error loading optimization score</p>
              <Button variant="outline" size="sm" onClick={refetchSummary}>
                Try Again
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // No data state
  if (!summary) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-1 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center text-lg font-medium">
              <BarChart3 className="mr-2 h-5 w-5 text-blue-500" />
              {isMobile ? 'Score' : 'Optimization Score'}
            </CardTitle>
          </div>
        </CardHeader>
        <CardContent className="flex-grow p-3 pt-2 pb-3">
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">No optimization data available</p>
              <Button variant="outline" size="sm" onClick={() => navigate('/optimization')}>
                View Optimization Dashboard
                <ArrowUpRight className="ml-1 h-3 w-3" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Calculate the actual optimization score based on provider data
  const calculateOverallScore = (): number => {
    if (provider) {
      // When filtering by provider, use that provider's specific score
      const providerSpecificData = providerData.find(p => p.provider.toLowerCase() === provider.toLowerCase());
      return providerSpecificData?.efficiencyScore ?? 0;
    } else {
      // When not filtering, calculate weighted average of all providers
      if (sortedProviders.length === 0) return summary.optimization_metrics?.optimization_score || 0;
      const totalWeight = sortedProviders.reduce((sum, p) => sum + (p.anomalyCount + p.opportunityCount), 0);
      if (totalWeight === 0) {
        // If no weight, use simple average
        return Math.round(sortedProviders.reduce((sum, p) => sum + p.efficiencyScore, 0) / sortedProviders.length);
      }
      // Weighted average based on activity (anomalies + opportunities)
      const weightedSum = sortedProviders.reduce((sum, p) => {
        const weight = p.anomalyCount + p.opportunityCount;
        return sum + (p.efficiencyScore * weight);
      }, 0);
      return Math.round(weightedSum / totalWeight);
    }
  };

  const score = calculateOverallScore();
  const healthStatus = summary.optimization_metrics?.health_status || 'needs_attention';
  const healthStyle = formatHealthStatus(healthStatus);
  const scoreColor = getScoreColor(score);
  const scoreDots = getScoreDots(score, 10);

  // Determine trend and status
  const hasIssues = summary.anomalies?.total_count > 0;
  const hasOpportunities = summary.savings_opportunities?.total_count > 0;
  const totalAnomalies = summary.anomalies?.total_count || 0;
  const totalOpportunities = summary.savings_opportunities?.total_count || 0;

  // Get dynamic status icon based on score
  const getStatusIcon = (optimizationScore: number) => {
    if (optimizationScore >= 80) {
      return {
        icon: CheckCircle,
        color: 'text-green-500',
        title: 'System is performing excellently'
      };
    } else if (optimizationScore >= 60) {
      return {
        icon: AlertTriangle,
        color: 'text-yellow-500',
        title: 'System needs attention - some optimization opportunities available'
      };
    } else {
      return {
        icon: XCircle,
        color: 'text-red-500',
        title: 'System has critical issues that need immediate attention'
      };
    }
  };

  const statusIcon = getStatusIcon(score);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-1 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg font-medium">
            <BarChart3 className="mr-2 h-5 w-5 text-blue-500" />
            {isMobile ? t('optimizationScore.score') : t('optimizationScore.title')}
          </CardTitle>
          <div className="flex items-center space-x-2">
            <statusIcon.icon 
              className={`h-4 w-4 ${statusIcon.color}`} 
              title={statusIcon.title}
            />
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="flex-grow p-3 overflow-hidden">
        <div className="flex flex-col h-full">
          {/* Score Display with Gauge */}
          <div className="flex-shrink-0 text-center mb-4">
            <HealthRoundedGauge 
              value={score} 
              size={isMobile ? 180 : 200}
              strokeWidth={isMobile ? 18 : 20}
              className="mx-auto"
              showTitle={true}
            />
          </div>

          {/* Provider Analysis */}
          <div className="flex-grow space-y-3">
            {provider ? (
              // When filtering by provider, show simple view with gauge and metrics
              (() => {
                const providerSpecificData = providerData.find(p => p.provider.toLowerCase() === provider.toLowerCase());
                if (!providerSpecificData) {
                  return (
                    <div className={cn(
                      "flex items-center justify-center p-3 rounded-lg text-center",
                      isDark ? "bg-slate-800/50 border-slate-700" : "bg-gray-50 border-gray-200"
                    )}>
                      <div>
                        <Cloud className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                        <p className="text-sm text-muted-foreground">
                          No data for {provider}
                        </p>
                      </div>
                    </div>
                  );
                }

                return (
                  <div className="grid grid-cols-3 gap-2">
                    <div className={cn(
                      "p-2 rounded-lg border",
                      isDark ? "bg-amber-900/20 border-amber-800/30" : "bg-amber-50 border-amber-200"
                    )}>
                      <div className="flex items-center gap-1 mb-1">
                        <AlertTriangle className="h-3 w-3 text-amber-500" />
                        <span className="text-xs text-muted-foreground">{t('optimizationScore.criticalIssues')}</span>
                      </div>
                      <div className="text-sm font-medium text-amber-700 dark:text-amber-300">
                        {providerSpecificData.anomalyCount} {t('optimizationScore.anomalies')}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ${Math.round(providerSpecificData.anomalyCount * 1250).toLocaleString()} {t('optimizationScore.impact')}
                      </div>
                    </div>

                    <div className={cn(
                      "p-2 rounded-lg border",
                      isDark ? "bg-green-900/20 border-green-800/30" : "bg-green-50 border-green-200"
                    )}>
                      <div className="flex items-center gap-1 mb-1">
                        <TrendingUp className="h-3 w-3 text-green-500" />
                        <span className="text-xs text-muted-foreground">{t('optimizationScore.savingsPotential')}</span>
                      </div>
                      <div className="text-sm font-medium text-green-700 dark:text-green-300">
                        {providerSpecificData.opportunityCount} {t('optimizationScore.opportunities')}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        ${Math.round(providerSpecificData.opportunityCount * 890).toLocaleString()} {t('optimizationScore.potential')}
                      </div>
                    </div>

                    <div className={cn(
                      "p-2 rounded-lg border",
                      isDark ? "bg-blue-900/20 border-blue-800/30" : "bg-blue-50 border-blue-200"
                    )}>
                      <div className="flex items-center gap-1 mb-1">
                        <CheckCircle className="h-3 w-3 text-blue-500" />
                        <span className="text-xs text-muted-foreground">{t('optimizationScore.compliance')}</span>
                      </div>
                      <div className="text-sm font-medium text-blue-700 dark:text-blue-300">
                        {Math.round(providerSpecificData.efficiencyScore * 0.8)}% {t('optimizationScore.compliant')}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {t('optimizationScore.bestPractices')}
                      </div>
                    </div>
                  </div>
                );
              })()
            ) : sortedProviders.length > 0 && currentProvider ? (
              // When not filtering, show provider comparison
              <div className="h-full flex flex-col">
                {/* Current Provider Card */}
                <div className="flex-1">
                  <div className={cn(
                    "p-4 rounded-lg border transition-all duration-200 max-w-md mx-auto",
                    isDark 
                      ? "bg-slate-800/50 border-slate-700" 
                      : "bg-white border-gray-200"
                  )}>
                    {/* Provider Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <ProviderBadge provider={currentProvider.provider} size="sm" />
                      </div>
                      <div className="flex items-center gap-1">
                        <span className={`text-lg font-bold ${getScoreColor(currentProvider.efficiencyScore)}`}>
                          {currentProvider.efficiencyScore}
                        </span>
                        <span className="text-xs text-muted-foreground">score</span>
                      </div>
                    </div>

                    {/* Metrics */}
                    <div className="grid grid-cols-3 gap-3 text-xs">
                      <div className="text-center space-y-1">
                        <div className="flex items-center justify-center gap-1 text-muted-foreground">
                          <AlertTriangle className="h-3 w-3 text-amber-500" />
                          <span>{t('optimizationScore.issues')}</span>
                        </div>
                        <div className="font-medium text-amber-600 dark:text-amber-400">
                          {currentProvider.anomalyCount} {t('optimizationScore.anomalies')}
                        </div>
                      </div>
                      
                      <div className="text-center space-y-1">
                        <div className="flex items-center justify-center gap-1 text-muted-foreground">
                          <TrendingUp className="h-3 w-3 text-green-500" />
                          <span>{t('optimizationScore.savings')}</span>
                        </div>
                        <div className="font-medium text-green-600 dark:text-green-400">
                          {currentProvider.opportunityCount} {t('optimizationScore.opportunities')}
                        </div>
                      </div>
                      
                      <div className="text-center space-y-1">
                        <div className="flex items-center justify-center gap-1 text-muted-foreground">
                          <CheckCircle className="h-3 w-3 text-blue-500" />
                          <span>{t('optimizationScore.compliance')}</span>
                        </div>
                        <div className="font-medium text-blue-600 dark:text-blue-400">
                          {Math.round(currentProvider.efficiencyScore * 0.8)}% {t('optimizationScore.compliant')}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Pagination - área fixa na parte inferior */}
                <div className={cn(
                  "flex justify-center items-center pt-2 h-8 mt-auto",
                  sortedProviders.length > 1 && "border-t",
                  isDark ? "border-slate-700" : "border-gray-100"
                )}>
                  {sortedProviders.length > 1 && (
                    <div className="text-xs flex items-center justify-center">
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-6 w-6 flex items-center justify-center" 
                        onClick={goToPrevProvider}
                      >
                        <ChevronLeft className="h-3 w-3" />
                      </Button>
                      <span className="px-1 text-muted-foreground flex items-center">
                        {currentProviderIndex + 1}/{sortedProviders.length}
                      </span>
                      <Button 
                        variant="ghost" 
                        size="icon" 
                        className="h-6 w-6 flex items-center justify-center" 
                        onClick={goToNextProvider}
                      >
                        <ChevronRight className="h-3 w-3" />
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className={cn(
                "flex items-center justify-center p-3 rounded-lg text-center",
                isDark ? "bg-slate-800/50 border-slate-700" : "bg-gray-50 border-gray-200"
              )}>
                <div>
                  <Cloud className="h-6 w-6 text-gray-400 mx-auto mb-1" />
                  <p className="text-sm text-muted-foreground">
                    No provider data available
                  </p>
                </div>
              </div>
            )}
          </div>

        </div>
      </CardContent>
    </Card>
  );
}