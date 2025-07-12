import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, TrendingDown, BarChart2, ChevronLeft, ChevronRight, HelpCircle, X } from 'lucide-react';
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
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';

type KPICategory = 'eficiencia' | 'tarifacao' | 'planejamento' | 'governanca';

interface KPI {
  name: string;
  value: number | string;
  unit?: string;
  trend?: number;
  target?: number;
  isGoodWhenHigher?: boolean;
  description?: string;
  formula?: string;
  category: KPICategory;
}

interface EfficiencyKPIsCardProps {
  kpis: KPI[];
  isUsingMockData?: boolean;
}

// Função para criar as definições de cores para cada categoria com suporte a dark mode
const createCategoryColors = (isDark: boolean) => {
  return {
    eficiencia: {
      bg: isDark ? 'bg-blue-900' : 'bg-blue-500',
      hover: isDark ? 'hover:bg-blue-800' : 'hover:bg-blue-600',
      text: isDark ? 'text-blue-400' : 'text-blue-500',
      tileBg: isDark ? 'bg-blue-900/50' : 'bg-blue-50',
      border: isDark ? 'border-blue-800' : 'border-blue-100'
    },
    tarifacao: {
      bg: isDark ? 'bg-purple-900' : 'bg-purple-500',
      hover: isDark ? 'hover:bg-purple-800' : 'hover:bg-purple-600',
      text: isDark ? 'text-purple-400' : 'text-purple-500',
      tileBg: isDark ? 'bg-purple-900/50' : 'bg-purple-50',
      border: isDark ? 'border-purple-800' : 'border-purple-100'
    },
    planejamento: {
      bg: isDark ? 'bg-amber-900' : 'bg-amber-500',
      hover: isDark ? 'hover:bg-amber-800' : 'hover:bg-amber-600',
      text: isDark ? 'text-amber-400' : 'text-amber-500',
      tileBg: isDark ? 'bg-amber-900/50' : 'bg-amber-50',
      border: isDark ? 'border-amber-800' : 'border-amber-100'
    },
    governanca: {
      bg: isDark ? 'bg-emerald-900' : 'bg-emerald-500',
      hover: isDark ? 'hover:bg-emerald-800' : 'hover:bg-emerald-600',
      text: isDark ? 'text-emerald-400' : 'text-emerald-500',
      tileBg: isDark ? 'bg-emerald-900/50' : 'bg-emerald-50',
      border: isDark ? 'border-emerald-800' : 'border-emerald-100'
    }
  } as const;
};

export function EfficiencyKPIsCard({ kpis, isUsingMockData = false }: EfficiencyKPIsCardProps) {
  const { isDark } = useTheme();
  const [activeCategory, setActiveCategory] = useState<KPICategory>('eficiencia');
  const [currentPage, setCurrentPage] = useState(0);
  const [activeKpiInfo, setActiveKpiInfo] = useState<KPI | null>(null);
  const [showMobileDialog, setShowMobileDialog] = useState(false);
  const itemsPerPage = 4;
  const { t } = useTranslation();

  // Definir labels para as categorias usando i18n
  const CATEGORY_LABELS: Record<KPICategory, string> = {
    eficiencia: t('sections.eficiencia'),
    tarifacao: t('sections.tarifacao'),
    planejamento: t('sections.planejamento'),
    governanca: t('sections.governanca')
  };

  // Labels curtos para telas pequenas
  const CATEGORY_LABELS_SHORT: Record<KPICategory, string> = {
    eficiencia: t('sections.eficienciaShort'),
    tarifacao: t('sections.tarifacaoShort'),
    planejamento: t('sections.planejamentoShort'),
    governanca: t('sections.governancaShort')
  };

  // Gerar cores de categoria com base no tema atual
  const CATEGORY_COLORS = createCategoryColors(isDark);

  // Filtrando KPIs pela categoria selecionada
  const filteredKPIs = kpis.filter(kpi => kpi.category === activeCategory);

  // Calcular o número total de páginas
  const totalPages = Math.ceil(filteredKPIs.length / itemsPerPage);
  
  // Resetar página atual ao trocar de categoria
  const handleCategoryChange = (category: KPICategory) => {
    setActiveCategory(category);
    setCurrentPage(0);
  };

  // Obter os KPIs da página atual
  const paginatedKPIs = filteredKPIs.slice(
    currentPage * itemsPerPage, 
    (currentPage + 1) * itemsPerPage
  );
  
  // Verificar se é necessário exibir a paginação
  const shouldShowPagination = filteredKPIs.length > itemsPerPage;
  
  // Funções para navegação entre páginas
  const handlePrevious = () => {
    setCurrentPage(prev => (prev > 0 ? prev - 1 : totalPages - 1));
  };

  const handleNext = () => {
    setCurrentPage(prev => (prev < totalPages - 1 ? prev + 1 : 0));
  };

  const getTrendIcon = (trend: number | undefined, isGoodWhenHigher = true) => {
    if (trend === undefined) return null;
    
    const isPositive = trend > 0;
    const isGoodTrend = isGoodWhenHigher ? isPositive : !isPositive;
    const TrendIcon = isPositive ? TrendingUp : TrendingDown;
    
    return (
      <TrendIcon 
        className={`h-4 w-4 ml-2 ${isGoodTrend 
          ? isDark ? 'text-green-400' : 'text-XCost-green' 
          : isDark ? 'text-red-400' : 'text-XCost-red'
        }`} 
      />
    );
  };

  // Função para mostrar informações do KPI em dispositivos móveis
  const handleShowKpiInfo = (kpi: KPI) => {
    setActiveKpiInfo(kpi);
    setShowMobileDialog(true);
  };

  // Lista de todas as categorias
  const categories: KPICategory[] = ['eficiencia', 'tarifacao', 'planejamento', 'governanca'];

  const activeColor = CATEGORY_COLORS[activeCategory];
  
  return (
    <Card className="h-full flex flex-col overflow-hidden">
      <CardHeader className="pb-2 flex-shrink-0">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center">
          <div className="flex items-center gap-2 mb-2 sm:mb-0">
            <CardTitle className="flex items-center text-lg font-medium">
              <BarChart2 className={`h-5 w-5 mr-2 ${activeColor.text}`} />
              {t('sections.kpis')}
            </CardTitle>
            {isUsingMockData && <MockDataBadge />}
          </div>
          
          {/* Container com scroll horizontal para telas pequenas */}
          <div className="w-full sm:w-auto overflow-x-auto pb-2 sm:pb-0 -mx-2 px-1">
            <div className="flex space-x-0.5 sm:space-x-1 min-w-max">
              {categories.map((category) => (
                <Button
                  key={category}
                  variant={activeCategory === category ? "default" : "outline"}
                  size="sm"
                  className={`px-1.5 sm:px-3 py-1 h-8 text-xs whitespace-nowrap ${
                    activeCategory === category 
                      ? `${CATEGORY_COLORS[category].bg} ${CATEGORY_COLORS[category].hover} text-white` 
                      : cn(
                        "bg-transparent",
                        isDark 
                          ? `border-slate-700 ${CATEGORY_COLORS[category].text} hover:text-white` 
                          : `border-gray-200 ${CATEGORY_COLORS[category].text} hover:text-white`,
                        `hover:${CATEGORY_COLORS[category].bg}`
                      )
                  }`}
                  onClick={() => handleCategoryChange(category)}
                >
                  <span className="hidden md:inline">{CATEGORY_LABELS[category]}</span>
                  <span className="md:hidden">{CATEGORY_LABELS_SHORT[category]}</span>
                </Button>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent className={`flex-grow pb-3 flex flex-col border-t-2 ${activeColor.border}`}>
        {filteredKPIs.length > 0 ? (
          <>
            <div className="flex-grow pt-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {paginatedKPIs.map((kpi) => (
                  <div 
                    key={kpi.name} 
                    className={`p-3 rounded-md border ${activeColor.border} ${activeColor.tileBg}`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-muted-foreground">{kpi.name}</div>
                      {kpi.description && (
                        <>
                          {/* Tooltip para desktop */}
                          <div className="hidden sm:block">
                            <TooltipProvider>
                              <Tooltip delayDuration={0}>
                                <TooltipTrigger asChild>
                                  <Button variant="ghost" size="icon" className="h-5 w-5 p-0 hover:bg-transparent">
                                    <HelpCircle className={`h-4 w-4 ${activeColor.text}`} />
                                  </Button>
                                </TooltipTrigger>
                                <TooltipContent className={cn(
                                  "max-w-xs",
                                  isDark ? "bg-slate-800 border-slate-700 text-white" : "bg-white border-gray-200 text-slate-900"
                                )}>
                                  <div>
                                    <p className="font-medium mb-1">{kpi.name}</p>
                                    <p className="text-xs mb-1">{kpi.description}</p>
                                    {kpi.formula && (
                                      <div className={cn(
                                        "p-1 rounded text-xs font-mono",
                                        isDark ? "bg-slate-700" : "bg-slate-100"
                                      )}>
                                        {kpi.formula}
                                      </div>
                                    )}
                                  </div>
                                </TooltipContent>
                              </Tooltip>
                            </TooltipProvider>
                          </div>
                          
                          {/* Botão para dispositivos móveis que abre um diálogo */}
                          <Button 
                            variant="ghost" 
                            size="icon" 
                            className="sm:hidden h-5 w-5 p-0 hover:bg-transparent"
                            onClick={() => handleShowKpiInfo(kpi)}
                          >
                            <HelpCircle className={`h-4 w-4 ${activeColor.text}`} />
                          </Button>
                        </>
                      )}
                    </div>
                    <div className="flex items-center mt-1">
                      <div className={`text-xl font-bold ${activeColor.text}`}>
                        {typeof kpi.value === 'number' 
                          ? kpi.value.toLocaleString('en-US', {
                              minimumFractionDigits: kpi.value % 1 !== 0 ? 2 : 0,
                              maximumFractionDigits: 2
                            }) 
                          : kpi.value}
                        {kpi.unit && <span className="text-sm font-normal ml-1">{t(kpi.unit, kpi.unit)}</span>}
                      </div>
                      {getTrendIcon(kpi.trend, kpi.isGoodWhenHigher)}
                    </div>
                    {kpi.target !== undefined && (
                      <div className="text-xs text-muted-foreground mt-1">
                        {t('kpis.target')}: {kpi.target.toLocaleString('en-US', {
                          minimumFractionDigits: kpi.target % 1 !== 0 ? 2 : 0,
                          maximumFractionDigits: 2
                        })}{kpi.unit && t(kpi.unit, kpi.unit)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
            
            {/* Paginação */}
            {shouldShowPagination && (
              <div className={cn(
                "flex justify-center items-center mt-4 pt-2 border-t",
                isDark ? "border-slate-700" : "border-gray-100"
              )}>
                <div className="text-xs flex items-center">
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className={`h-6 w-6 ${activeColor.text}`}
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
                    className={`h-6 w-6 ${activeColor.text}`}
                    onClick={handleNext}
                  >
                    <ChevronRight className="h-3 w-3" />
                  </Button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">{t('sections.noKpisForCategory')}</p>
          </div>
        )}
      </CardContent>
      
      {/* Diálogo para mostrar informações do KPI em dispositivos móveis */}
      <Dialog open={showMobileDialog} onOpenChange={setShowMobileDialog}>
        <DialogContent className={cn(
          "sm:hidden px-4 pt-4 pb-4 max-w-[90%]",
          isDark ? "bg-slate-900" : ""
        )}>
          <DialogHeader className="flex items-center justify-between pb-0">
            <DialogTitle className="text-base font-medium">{activeKpiInfo?.name}</DialogTitle>
            <DialogClose asChild>
            </DialogClose>
          </DialogHeader>
          <div className="mt-0">
            <p className="text-sm mt-1 mb-2">{activeKpiInfo?.description}</p>
            {activeKpiInfo?.formula && (
              <div className={cn(
                "p-2 mt-1 rounded text-xs font-mono",
                isDark ? "bg-slate-800" : "bg-slate-100"
              )}>
                {activeKpiInfo.formula}
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
