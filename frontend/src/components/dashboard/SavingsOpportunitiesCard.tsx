import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle, Lightbulb, ArrowUpRight, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Progress } from '@/components/ui/progress';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { useNavigate } from 'react-router-dom';
import { useSavingsOpportunities } from '@/hooks/useOptimization';
import { formatEffortLevel, formatCurrency, sortByPriority } from '@/utils/optimizationUtils';

// Função para formatar valores de forma inteligente
const formatSmartCurrency = (amount: number, currency: string = 'USD'): string => {
  if (amount >= 10000) {
    // Para valores >= $10,000, usar formato com K
    return `${(amount / 1000).toFixed(1)}K ${currency}`;
  } else {
    // Para valores menores, usar formato normal sem decimais
    return `$${Math.round(amount).toLocaleString()}`;
  }
};

interface SavingsOpportunitiesCardProps {
  provider?: string;
  days?: number;
  autoRefresh?: boolean;
}

export function SavingsOpportunitiesCard({ 
  provider,
  days = 30,
  autoRefresh = true
}: SavingsOpportunitiesCardProps) {
  const { t } = useTranslation();
  const [currentIndex, setCurrentIndex] = useState(0);
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  
  // Fetch savings opportunities data
  const { 
    data: opportunities, 
    loading, 
    error, 
    refetch, 
    lastUpdated 
  } = useSavingsOpportunities({ 
    provider, 
    days, 
    per_page: 20,
    autoRefresh: autoRefresh,
    refreshInterval: 5 * 60 * 1000
  });
  
  // Sort and process opportunities
  const sortedOpportunities = sortByPriority.opportunities(opportunities || []);
  const displayOpportunities = sortedOpportunities.slice(0, 4); // Máximo 4 itens (1 principal + 3 na lista)
  
  // Calculate totals
  const totalPotentialSavings = displayOpportunities.reduce((sum, opp) => sum + opp.estimated_savings, 0);
  


  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : displayOpportunities.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < displayOpportunities.length - 1 ? prev + 1 : 0));
  };
  
  // Reset currentIndex when opportunities change
  React.useEffect(() => {
    if (displayOpportunities.length > 0 && currentIndex >= displayOpportunities.length) {
      setCurrentIndex(0);
    }
  }, [displayOpportunities.length, currentIndex]);

  const calculatePercentage = (savings: number) => {
    return totalPotentialSavings > 0 ? (savings / totalPotentialSavings) * 100 : 0;
  };

  const shouldShowPagination = displayOpportunities.length > 1;
  const headerTextColorClass = isDark ? "text-green-400" : "text-XCost-green";
  
  // Loading state
  if (loading) {
    return (
      <Card className="h-full flex flex-col">
        <CardHeader className="pb-1 flex-shrink-0">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center text-lg font-medium">
              <Lightbulb className="mr-2 h-5 w-5 text-green-500" />
              {isMobile ? 'Opportunities' : 'Savings Opportunities'}
            </CardTitle>
            <Skeleton className="h-6 w-20" />
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
              <Lightbulb className="mr-2 h-5 w-5 text-green-500" />
              {isMobile ? 'Opportunities' : 'Savings Opportunities'}
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={refetch}>
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="flex-grow p-3 pt-2 pb-3">
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <p className="text-sm text-muted-foreground mb-2">Error loading opportunities</p>
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
          <CardTitle className="flex items-center text-lg font-medium">
            <Lightbulb className={cn("mr-2 h-5 w-5", isDark ? "text-green-400" : "text-XCost-green")} />
            {isMobile ? 'Opportunities' : 'Savings Opportunities'}
          </CardTitle>
          <div className="flex items-center space-x-2">
            <div className={`whitespace-nowrap ${isMobile ? 'text-lg' : 'text-xl'} font-bold ${headerTextColorClass}`}>
              {formatSmartCurrency(totalPotentialSavings)}
            </div>
            {lastUpdated && (
              <Button variant="ghost" size="sm" onClick={refetch} title="Refresh">
                <RefreshCw className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 pt-2 pb-3 overflow-auto">
        {displayOpportunities.length > 0 ? (
          <div className="flex flex-col h-full">
            {/* Card principal */}
            <div className={`flex-shrink-0 p-3 rounded-lg border mb-2 ${formatEffortLevel(displayOpportunities[currentIndex].implementation_effort).bgColor} ${formatEffortLevel(displayOpportunities[currentIndex].implementation_effort).borderColor}`}>
              <div className="flex justify-between items-start">
                <div className="flex items-center flex-1 mr-2">
                  <CheckCircle className={`${isMobile ? 'h-4 w-4' : 'h-5 w-5'} ${formatEffortLevel(displayOpportunities[currentIndex].implementation_effort).textColor} mr-2`} />
                  <h4 className={`font-medium ${isMobile ? 'text-xs' : 'text-sm'} truncate`}>
                    {displayOpportunities[currentIndex].opportunity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </h4>
                </div>
                <Badge className={`${isMobile ? 'text-[10px] px-1.5 py-0' : ''} ${formatEffortLevel(displayOpportunities[currentIndex].implementation_effort).color}`}>
                  {formatEffortLevel(displayOpportunities[currentIndex].implementation_effort).label}
                </Badge>
              </div>
              <p className={`${isMobile ? 'text-[10px]' : 'text-xs'} text-muted-foreground my-1 line-clamp-2 ml-${isMobile ? '6' : '7'}`}>
                {displayOpportunities[currentIndex].description}
              </p>
              
              <div className={`mt-2 mb-1 ml-${isMobile ? '6' : '7'}`}>
                <div className="flex justify-between items-center text-xs mb-0.5">
                  <span className={isMobile ? 'text-[10px]' : ''}>Contribution</span>
                  <span className={`font-medium ${isMobile ? 'text-[10px]' : ''}`}>{calculatePercentage(displayOpportunities[currentIndex].estimated_savings).toFixed(1)}%</span>
                </div>
                <Progress 
                  value={calculatePercentage(displayOpportunities[currentIndex].estimated_savings)}
                  className={cn("h-1.5", isDark ? "bg-slate-700" : "bg-gray-100")}
                />
              </div>
              
              <div className={`flex justify-between items-center mt-2 ml-${isMobile ? '6' : '7'}`}>
                <div className="flex items-center">
                  <span className={`${isMobile ? 'text-xs' : 'text-sm'} font-medium ${formatEffortLevel(displayOpportunities[currentIndex].implementation_effort).textColor}`}>
                    {formatCurrency(displayOpportunities[currentIndex].estimated_savings, displayOpportunities[currentIndex].currency, 'en-US', true)}
                  </span>
                  <span className={`text-muted-foreground ml-1 ${isMobile ? 'text-[10px]' : 'text-xs'}`}>annual</span>
                </div>
                
                <Button 
                  size="sm" 
                  variant="ghost"
                  className={`h-6 ${isMobile ? 'text-[10px] px-2' : 'text-xs'} ${formatEffortLevel(displayOpportunities[currentIndex].implementation_effort).textColor}`}
                  onClick={() => navigate('/savings-opportunities')}
                >
                  <span className="mr-1">Implement</span>
                  <ArrowUpRight className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Lista de outras oportunidades */}
            <div className="flex-grow overflow-auto space-y-1.5">
              {displayOpportunities.map((opportunity, idx) => {
                if (idx === currentIndex) return null;
                const effortStyle = formatEffortLevel(opportunity.implementation_effort);
                
                return (
                  <div 
                    key={`${opportunity.id}-${idx}`} 
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
                        style={{backgroundColor: effortStyle.textColor.includes('green') ? '#22c55e' : effortStyle.textColor.includes('amber') ? '#f59e0b' : '#ef4444'}}
                      />
                      <span className="font-medium truncate">
                        {opportunity.opportunity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </div>
                    <span className={`font-medium ml-2 ${effortStyle.textColor}`}>
                      {formatCurrency(opportunity.estimated_savings, opportunity.currency, 'en-US', true)}
                    </span>
                  </div>
                );
              })}
            </div>
            
            {/* Paginação - só exibe se tiver mais de 1 item */}
            {shouldShowPagination && displayOpportunities.length > 1 && (
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
                    {currentIndex + 1}/{displayOpportunities.length}
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
              <p className="text-muted-foreground text-sm mb-2">No savings opportunities found</p>
              <Button variant="outline" size="sm" onClick={() => navigate('/savings-opportunities')}>
                Explore Opportunities
                <ArrowUpRight className="ml-1 h-3 w-3" />
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
