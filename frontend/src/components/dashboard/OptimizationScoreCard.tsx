import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { BarChart3, ArrowUpRight, RefreshCw, TrendingUp, AlertTriangle, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { useOptimizationSummary, useOptimizationRecommendations } from '@/hooks/useOptimization';
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
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  
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

  const loading = summaryLoading || recommendationsLoading;
  const error = summaryError;

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

  const score = summary.optimization_metrics?.optimization_score || 0;
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
            {isMobile ? 'Score' : 'Optimization Score'}
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

          {/* Stats Summary */}
          <div className="flex-grow space-y-3">
            {/* Anomalies */}
            {totalAnomalies > 0 && (
              <div className={cn(
                "flex justify-between items-center p-2 rounded-lg",
                isDark ? "bg-amber-900/20 border border-amber-800/30" : "bg-amber-50 border border-amber-200"
              )}>
                <div className="flex items-center">
                  <AlertTriangle className="h-4 w-4 text-amber-500 mr-2" />
                  <span className="text-sm">Anomalies</span>
                </div>
                <span className="text-sm font-medium text-amber-600">
                  {totalAnomalies}
                </span>
              </div>
            )}

            {/* Opportunities */}
            {totalOpportunities > 0 && (
              <div className={cn(
                "flex justify-between items-center p-2 rounded-lg",
                isDark ? "bg-green-900/20 border border-green-800/30" : "bg-green-50 border border-green-200"
              )}>
                <div className="flex items-center">
                  <TrendingUp className="h-4 w-4 text-green-500 mr-2" />
                  <span className="text-sm">Opportunities</span>
                </div>
                <span className="text-sm font-medium text-green-600">
                  {totalOpportunities}
                </span>
              </div>
            )}

            {/* Recommendations */}
            {recommendationsTotal > 0 && (
              <div className={cn(
                "flex justify-between items-center p-2 rounded-lg",
                isDark ? "bg-blue-900/20 border border-blue-800/30" : "bg-blue-50 border border-blue-200"
              )}>
                <div className="flex items-center">
                  <BarChart3 className="h-4 w-4 text-blue-500 mr-2" />
                  <span className="text-sm">Recommendations</span>
                </div>
                <span className="text-sm font-medium text-blue-600">
                  {recommendationsTotal} pending
                </span>
              </div>
            )}

            {/* No issues state */}
            {totalAnomalies === 0 && totalOpportunities === 0 && recommendationsTotal === 0 && (
              <div className={cn(
                "flex items-center justify-center p-3 rounded-lg text-center",
                isDark ? "bg-green-900/20 border border-green-800/30" : "bg-green-50 border border-green-200"
              )}>
                <div>
                  <TrendingUp className="h-6 w-6 text-green-500 mx-auto mb-1" />
                  <p className="text-sm text-green-600 font-medium">
                    All systems optimized
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Action Button */}
          <div className="flex-shrink-0 mt-4">
            <Button 
              variant="outline" 
              size="sm" 
              className="w-full"
              onClick={() => navigate('/optimization')}
            >
              <span className="mr-1">View Details</span>
              <ArrowUpRight className="h-3 w-3" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}