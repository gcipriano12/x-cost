import React, { useState, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle, Lightbulb, ArrowUpRight, ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ProviderBadge } from '@/components/ui/provider-badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Progress } from '@/components/ui/progress';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { useNavigate } from 'react-router-dom';
import { useSavingsOpportunities } from '@/hooks/useOptimization';
import { formatEffortLevel, sortByPriority } from '@/utils/optimizationUtils';

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

// Helper function to get effort color for dots
const getEffortDotColor = (effort: string): string => {
  const effortStyle = formatEffortLevel(effort as any);
  if (effortStyle.textColor.includes('green')) return '#10b981';
  if (effortStyle.textColor.includes('yellow') || effortStyle.textColor.includes('amber')) return '#f59e0b';
  return '#ef4444'; // red for high effort
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
  const [selectedOpportunity, setSelectedOpportunity] = useState<string | null>(null);
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const navigate = useNavigate();
  
  // Determinar se deve mostrar as tags de provider (apenas quando o filtro for 'All' ou não definido)
  const shouldShowProviderTags = !provider || provider === 'all' || provider === '';
  
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
  const itemsPerPage = 5; // 1 principal + 4 na lista
  const startIndex = currentIndex * itemsPerPage;
  const displayOpportunities = sortedOpportunities.slice(startIndex, startIndex + itemsPerPage);
  
  // Calculate total savings (usando todas as oportunidades, não apenas as exibidas)
  const totalPotentialSavings = sortedOpportunities.reduce((sum, opp) => sum + opp.estimated_savings, 0);
  


  const totalPages = Math.ceil(sortedOpportunities.length / itemsPerPage);
  
  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : totalPages - 1));
    // Resetar a seleção ao mudar de página
    setSelectedOpportunity(null);
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < totalPages - 1 ? prev + 1 : 0));
    // Resetar a seleção ao mudar de página
    setSelectedOpportunity(null);
  };
  
  // Reset currentIndex when opportunities change
  React.useEffect(() => {
    if (totalPages > 0 && currentIndex >= totalPages) {
      setCurrentIndex(0);
    }
  }, [totalPages, currentIndex]);
  
  // Efeito separado para lidar com a seleção de oportunidade
  React.useEffect(() => {
    // Quando selecionar uma oportunidade, garantir que ela seja a primeira na lista
    if (selectedOpportunity && sortedOpportunities.length > 0) {
      const selectedIndex = sortedOpportunities.findIndex(opp => opp.id === selectedOpportunity);
      if (selectedIndex >= 0) {
        setCurrentIndex(Math.floor(selectedIndex / itemsPerPage));
      }
    }
  }, [selectedOpportunity, sortedOpportunities, itemsPerPage]);

  // Para o cálculo da porcentagem, usamos o total geral de todas as oportunidades
  const calculatePercentage = (savings: number) => {
    return totalPotentialSavings > 0 ? (savings / totalPotentialSavings) * 100 : 0;
  };

  const shouldShowPagination = totalPages > 1;
  // Determinar qual oportunidade deve ser mostrada como principal
  let mainOpportunity = displayOpportunities[0];
  let listOpportunities = displayOpportunities.slice(1);
  
  if (selectedOpportunity) {
    const selected = sortedOpportunities.find(opp => opp.id === selectedOpportunity);
    if (selected && displayOpportunities.includes(selected)) {
      // Quando uma oportunidade é selecionada, ela vira a principal
      // mas mantemos a lista original sem reordenar
      mainOpportunity = selected;
      // A lista mantém os outros itens na ordem original, excluindo apenas o selecionado
      listOpportunities = displayOpportunities.filter(opp => opp.id !== selected.id).slice(0, 4);
    }
  } else {
    // Quando não há seleção, usar a lógica normal
    listOpportunities = displayOpportunities.slice(1, 5);
  }
  
  // Garantir que sempre tenhamos 4 itens na lista, buscando de outras páginas se necessário
  if (listOpportunities.length < 4) {
    let nextPageIndex = currentIndex + 1;
    while (listOpportunities.length < 4 && nextPageIndex * itemsPerPage < sortedOpportunities.length) {
      const nextPageStart = nextPageIndex * itemsPerPage;
      const nextPageOpportunities = sortedOpportunities.slice(nextPageStart, nextPageStart + itemsPerPage);
      
      for (const opp of nextPageOpportunities) {
        if (opp.id !== mainOpportunity.id && listOpportunities.length < 4) {
          listOpportunities.push(opp);
        }
      }
      nextPageIndex++;
    }
  }
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
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 overflow-hidden relative">
        {displayOpportunities.length > 0 && mainOpportunity ? (
          <div className="h-full flex flex-col">
            {/* Card principal */}
            <div className={`flex-shrink-0 p-2 rounded-lg border mb-1.5 ${formatEffortLevel(mainOpportunity.implementation_effort).bgColor} ${formatEffortLevel(mainOpportunity.implementation_effort).borderColor}`}>
              <div className="flex justify-between items-start">
                <div className="flex items-center flex-1 mr-2">
                  <CheckCircle className={`${isMobile ? 'h-3 w-3' : 'h-4 w-4'} ${formatEffortLevel(mainOpportunity.implementation_effort).textColor} mr-2`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h4 className={`font-medium ${isMobile ? 'text-xs' : 'text-sm'} truncate`}>
                        {mainOpportunity.opportunity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </h4>
                      {shouldShowProviderTags && mainOpportunity.provider && (
                        <ProviderBadge 
                          provider={mainOpportunity.provider}
                          size="sm"
                        />
                      )}
                    </div>
                  </div>
                </div>
                <Badge className={`${isMobile ? 'text-[8px] px-1.5 py-0' : 'text-[10px] px-2 py-0.5'} whitespace-nowrap ${formatEffortLevel(mainOpportunity.implementation_effort).color}`}>
                  {formatEffortLevel(mainOpportunity.implementation_effort).label}
                </Badge>
              </div>
              <p className={`${isMobile ? 'text-[10px]' : 'text-xs'} text-muted-foreground my-1 line-clamp-1 ml-${isMobile ? '5' : '6'}`}>
                {mainOpportunity.description}
              </p>
              
              <div className={`mt-1 mb-1 ml-${isMobile ? '5' : '6'}`}>
                <div className="flex justify-between items-center text-xs mb-0.5">
                  <span className={isMobile ? 'text-[10px]' : ''}>Contribution</span>
                  <span className={`font-medium ${isMobile ? 'text-[10px]' : ''}`}>{calculatePercentage(mainOpportunity.estimated_savings).toFixed(1)}%</span>
                </div>
                <Progress 
                  value={calculatePercentage(mainOpportunity.estimated_savings)}
                  className={cn("h-1", isDark ? "bg-slate-700" : "bg-gray-100")}
                />
              </div>
              
              <div className={`flex justify-between items-center mt-1 ml-${isMobile ? '5' : '6'}`}>
                <div className="flex items-center">
                  <span className={`${isMobile ? 'text-xs' : 'text-sm'} font-medium ${formatEffortLevel(mainOpportunity.implementation_effort).textColor}`}>
                    {formatSmartCurrency(mainOpportunity.estimated_savings, mainOpportunity.currency)}
                  </span>
                  <span className={`text-muted-foreground ml-1 ${isMobile ? 'text-[10px]' : 'text-xs'}`}>annual</span>
                </div>
                
                <Button 
                  size="sm" 
                  variant="ghost"
                  className={`h-6 ${isMobile ? 'text-[10px] px-2' : 'text-xs'} ${formatEffortLevel(mainOpportunity.implementation_effort).textColor}`}
                  onClick={() => navigate('/savings-opportunities')}
                >
                  <span className="mr-1">Implement</span>
                  <ArrowUpRight className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Lista de outras oportunidades - altura fixa para garantir posicionamento estático da paginação */}
            <div className="flex-1 flex flex-col">
              <div className="space-y-1.5 h-[190px] overflow-hidden">
                {/* Sempre renderiza exatamente 4 itens na lista (slots) */}
                {Array.from({ length: 4 }).map((_, slotIdx) => {
                  const opportunity = slotIdx < listOpportunities.length ? listOpportunities[slotIdx] : null;
                  
                  // Se não houver oportunidade para este slot, renderiza um item vazio
                  if (!opportunity) {
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
                  
                  const effortStyle = formatEffortLevel(opportunity.implementation_effort);
                  
                  return (
                    <div 
                      key={`${opportunity.id}-${slotIdx}`} 
                      className={cn(
                        "flex items-center justify-between p-2 border rounded-lg text-sm cursor-pointer hover:bg-accent/50 transition-colors h-[40px]",
                        isDark 
                          ? "border-slate-700" 
                          : "border-gray-100",
                        selectedOpportunity === opportunity.id && "ring-1 ring-primary"
                      )}
                      onClick={() => {
                        setSelectedOpportunity(opportunity.id);
                        setCurrentIndex(Math.floor(sortedOpportunities.findIndex(opp => opp.id === opportunity.id) / itemsPerPage));
                      }}
                      role="button"
                      tabIndex={0}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' || e.key === ' ') {
                          setSelectedOpportunity(opportunity.id);
                          setCurrentIndex(Math.floor(sortedOpportunities.findIndex(opp => opp.id === opportunity.id) / itemsPerPage));
                        }
                      }}
                    >
                      <div className="flex items-center flex-1">
                        <div 
                          className="h-2 w-2 rounded-full mr-2"
                          style={{backgroundColor: getEffortDotColor(opportunity.implementation_effort)}}
                        />
                        <div className="flex-1">
                          <div className="flex items-center gap-1.5">
                            <span className="font-medium truncate">
                              {opportunity.opportunity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                            {shouldShowProviderTags && opportunity.provider && (
                              <ProviderBadge 
                                provider={opportunity.provider}
                                size="sm"
                              />
                            )}
                          </div>
                        </div>
                      </div>
                      <span className={`font-medium ml-2 ${effortStyle.textColor}`}>
                        {formatSmartCurrency(opportunity.estimated_savings, opportunity.currency)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
            
            {/* Paginação - posição fixa na parte inferior */}
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
