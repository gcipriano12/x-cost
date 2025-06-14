import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CheckCircle, Lightbulb, ArrowUpRight, ChevronLeft, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Progress } from '@/components/ui/progress';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';

interface Opportunity {
  id: string;
  title: string;
  description: string;
  savings: number;
  effort: 'low' | 'medium' | 'high';
}

interface SavingsOpportunitiesProps {
  opportunities: ReadonlyArray<Opportunity> | Opportunity[];
  totalPotentialSavings: number;
  currency: string;
}

export function SavingsOpportunitiesCard({ 
  opportunities, 
  totalPotentialSavings, 
  currency 
}: SavingsOpportunitiesProps) {
  const { t } = useTranslation();
  const [currentIndex, setCurrentIndex] = useState(0);
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toLocaleString('en-US', {
        minimumFractionDigits: isMobile ? 1 : 2,
        maximumFractionDigits: isMobile ? 1 : 2
      })}M`;
    } else if (value >= 1000) {
      return `${currency}${(value / 1000).toLocaleString('en-US', {
        minimumFractionDigits: isMobile ? 1 : 2,
        maximumFractionDigits: isMobile ? 1 : 2
      })}K`;
    }
    return `${currency}${value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  const getEffortLabel = (effort: string) => {
    switch(effort) {
      case 'low': return t('savingsOpportunities.effortLow');
      case 'medium': return t('savingsOpportunities.effortMedium');
      case 'high': return t('savingsOpportunities.effortHigh');
      default: return '';
    }
  };
  
  const getEffortColor = (effort: string) => {
    switch(effort) {
      case 'low': return isDark ? 'bg-green-900 text-green-100 border-0' : 'bg-green-100 text-green-700 border-0';
      case 'medium': return isDark ? 'bg-amber-900 text-amber-100 border-0' : 'bg-amber-100 text-amber-700 border-0';
      case 'high': return isDark ? 'bg-red-900 text-red-100 border-0' : 'bg-red-100 text-red-700 border-0';
      default: return '';
    }
  };

  const getEffortCardColor = (effort: string) => {
    switch(effort) {
      case 'low': return isDark ? 'bg-green-900/50 border-green-800' : 'bg-green-50 border-green-100';
      case 'medium': return isDark ? 'bg-amber-900/50 border-amber-800' : 'bg-amber-50 border-amber-200';
      case 'high': return isDark ? 'bg-red-900/50 border-red-800' : 'bg-red-50 border-red-200';
      default: return isDark ? 'bg-green-900/50 border-green-800' : 'bg-green-50 border-green-100';
    }
  };

  const getEffortTextColor = (effort: string) => {
    switch(effort) {
      case 'low': return isDark ? 'text-green-400' : 'text-XCost-green';
      case 'medium': return isDark ? 'text-amber-400' : 'text-amber-600';
      case 'high': return isDark ? 'text-red-400' : 'text-XCost-red';
      default: return isDark ? 'text-green-400' : 'text-XCost-green';
    }
  };

  const handlePrevious = () => {
    setCurrentIndex(prev => (prev > 0 ? prev - 1 : opportunities.length - 1));
  };

  const handleNext = () => {
    setCurrentIndex(prev => (prev < opportunities.length - 1 ? prev + 1 : 0));
  };

  // Calcular a porcentagem de cada oportunidade em relação ao total
  const calculatePercentage = (savings: number) => {
    return (savings / totalPotentialSavings) * 100;
  };

  // Verificar se é necessário exibir a paginação
  const shouldShowPagination = opportunities.length > 7;

  // Definir a cor do texto para o cabeçalho com base na criticidade
  const headerTextColorClass = isDark ? "text-green-400" : "text-XCost-green";
  // Pegar a cor atual do texto com base na oportunidade selecionada
  const currentEffortColor = getEffortTextColor(opportunities[currentIndex]?.effort || 'low');
  
  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-1 flex-shrink-0">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg font-medium">
            <Lightbulb className={cn("mr-2 h-5 w-5", isDark ? "text-green-400" : "text-XCost-green")} />
            {isMobile ? t('savingsOpportunities.opportunities') : t('savingsOpportunities.title')}
          </CardTitle>
          <div className={`whitespace-nowrap ${isMobile ? 'text-lg' : 'text-xl'} font-bold ${headerTextColorClass}`}>
            {formatCurrency(totalPotentialSavings)}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-grow p-3 pt-2 pb-3 overflow-auto">
        {opportunities.length > 0 ? (
          <div className="flex flex-col h-full">
            {/* Card principal */}
            <div className={`flex-shrink-0 p-3 rounded-lg border mb-2 ${getEffortCardColor(opportunities[currentIndex].effort)}`}>
              <div className="flex justify-between items-start">
                <div className="flex items-center flex-1 mr-2">
                  <CheckCircle className={`${isMobile ? 'h-4 w-4' : 'h-5 w-5'} ${currentEffortColor} mr-2`} />
                  <h4 className={`font-medium ${isMobile ? 'text-xs' : 'text-sm'}`}>{opportunities[currentIndex].title}</h4>
                </div>
                <Badge className={`${isMobile ? 'text-[10px] px-1.5 py-0' : ''} ${getEffortColor(opportunities[currentIndex].effort)}`}>
                  {getEffortLabel(opportunities[currentIndex].effort)}
                </Badge>
              </div>
              <p className={`${isMobile ? 'text-[10px]' : 'text-xs'} text-muted-foreground my-1 line-clamp-2 ml-${isMobile ? '6' : '7'}`}>
                {opportunities[currentIndex].description}
              </p>
              
              <div className={`mt-2 mb-1 ml-${isMobile ? '6' : '7'}`}>
                <div className="flex justify-between items-center text-xs mb-0.5">
                  <span className={isMobile ? 'text-[10px]' : ''}>{t('savingsOpportunities.contribution')}</span>
                  <span className={`font-medium ${isMobile ? 'text-[10px]' : ''}`}>{calculatePercentage(opportunities[currentIndex].savings).toFixed(1)}%</span>
                </div>
                <Progress 
                  value={calculatePercentage(opportunities[currentIndex].savings)}
                  className={cn("h-1.5", isDark ? "bg-slate-700" : "bg-gray-100")}
                />
              </div>
              
              <div className={`flex justify-between items-center mt-2 ml-${isMobile ? '6' : '7'}`}>
                <div className="flex items-center">
                  <span className={`${isMobile ? 'text-xs' : 'text-sm'} font-medium ${currentEffortColor}`}>
                    {formatCurrency(opportunities[currentIndex].savings)}
                  </span>
                  <span className={`text-muted-foreground ml-1 ${isMobile ? 'text-[10px]' : 'text-xs'}`}>{t('savingsOpportunities.perMonth')}</span>
                </div>
                
                <Button 
                  size="sm" 
                  variant="ghost"
                  className={`h-6 ${isMobile ? 'text-[10px] px-2' : 'text-xs'} ${currentEffortColor}`}
                >
                  <span className="mr-1">{t('savingsOpportunities.implement')}</span>
                  <ArrowUpRight className="h-3 w-3" />
                </Button>
              </div>
            </div>

            {/* Lista de outras oportunidades */}
            <div className="flex-grow overflow-auto space-y-1.5">
              {opportunities.map((opportunity, idx) => {
                if (idx === currentIndex) return null;
                const opportunityColor = getEffortTextColor(opportunity.effort);
                const dotColor = opportunity.effort === 'low' 
                  ? (isDark ? '#4ade80' : '#22c55e') 
                  : opportunity.effort === 'medium' 
                    ? (isDark ? '#fcd34d' : '#f59e0b') 
                    : (isDark ? '#f87171' : '#ef4444');
                
                return (
                  <div 
                    key={opportunity.id} 
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
                        style={{backgroundColor: dotColor}}
                      />
                      <span className="font-medium truncate">{opportunity.title}</span>
                    </div>
                    <span className={`font-medium ml-2 ${opportunityColor}`}>
                      {formatCurrency(opportunity.savings)}
                    </span>
                  </div>
                );
              })}
            </div>
            
            {/* Paginação - só exibe se tiver mais de 7 itens */}
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
                    {currentIndex + 1}/{opportunities.length}
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
            <p className="text-muted-foreground text-sm">{t('savingsOpportunities.noOpportunitiesFound')}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
