import React from 'react';
import { useTranslation } from 'react-i18next';
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { TrendingUp, TrendingDown, DollarSign, Calendar, AlertCircle, BarChart3, ArrowRight, Disc, Target, AlertTriangle, Coins, PieChart as PieChartIcon, Sparkles, Cloud } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Badge } from '@/components/ui/badge';
import { ProviderBadge } from '@/components/ui/provider-badge';
import { MockDataBadge } from '@/components/ui/mock-data-badge';
import { Progress } from '@/components/ui/progress';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip as RechartsTooltip, Sector } from 'recharts';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useIsMobile } from '@/hooks/use-mobile';
import { getProviderColor } from '@/utils/providerColors';

interface ProviderBreakdown {
  name: string;
  value: number;
  color: string;
}

interface AccountBreakdown {
  accountId: string;
  accountName?: string; // For backwards compatibility
  billing_account_name?: string; // Primary field from backend
  value: number;
  color: string;
}

interface SpendSummaryProps {
  totalSpend: number;
  currency: string;
  previousPeriodChange: number;
  sparklineData: number[];
  providerBreakdown?: ProviderBreakdown[];
  accountBreakdown?: AccountBreakdown[];
  selectedProvider?: string; // Add selected provider to determine which distribution to show
  wastedSpend?: number;
  budgetLimit?: number;
  budgetConsumed?: number;
  savingsRealized?: number;
  // Novos campos opcionais para dados da API
  topService?: {
    name: string;
    provider: string;
    cost: number;
  };
  topProvider?: {
    name: string;
    cost: number;
  };
  monthlyAverage?: number;
  monthlyAverageDescription?: string; // Adicionar descrição do período
  annualProjection?: number;
  nextMonthForecast?: {
    amount: number;
    change_percentage: number;
  };
  isUsingMockData?: boolean;
}

export function SpendSummaryCard({ 
  totalSpend, 
  currency, 
  previousPeriodChange, 
  sparklineData,
  providerBreakdown = [], // SEM FALLBACK - apenas dados reais da API
  accountBreakdown,
  selectedProvider,
  wastedSpend = 0, // SEM FALLBACK - apenas dados reais da API
  budgetLimit = totalSpend * 1.2,
  budgetConsumed = 75,
  savingsRealized = 0, // SEM FALLBACK - apenas dados reais da API
  topService,
  topProvider,
  monthlyAverage,
  monthlyAverageDescription,
  annualProjection,
  nextMonthForecast,
  isUsingMockData = false
}: SpendSummaryProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const isIncrease = previousPeriodChange > 0;
  const changeAbs = Math.abs(previousPeriodChange);
  const [activeIndex, setActiveIndex] = React.useState<number | null>(null);
  
  // Usar APENAS dados reais da API - sem fallbacks mockados
  const calculatedMonthlyAverage = monthlyAverage || 0;
  const calculatedProjectedNextMonth = nextMonthForecast?.amount || 0;
  const calculatedTopProvider = topProvider || {
    name: "Unknown",
    cost: 0
  };
  const calculatedAnnualProjection = annualProjection || 0;
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}M`;
    } else if (value >= 1000) {
      return `${currency}${(value / 1000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}K`;
    }
    return `${currency}${value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  const getBudgetStatusColor = () => {
    if (budgetConsumed >= 90) return isDark ? 'text-red-400' : 'text-XCost-red';
    if (budgetConsumed >= 75) return isDark ? 'text-amber-400' : 'text-amber-500';
    return isDark ? 'text-green-400' : 'text-XCost-green';
  };

  // Função para converter hex para rgba com glassmorphism
  const hexToRgba = (hex: string, alpha: number = 0.3) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  // Determine which distribution to show based on selected provider
  const showAccountDistribution = !!selectedProvider; // SEMPRE mostrar Account Distribution quando há filtro de provedor
  const distributionTitle = showAccountDistribution 
    ? t('spendSummary.accountDistribution') 
    : t('spendSummary.providerDistribution');

  // Function to generate account colors based on account index
  const generateAccountColor = (index: number): string => {
    const accountColors = [
      '#FBB040', // Orange
      '#4A9EF1', // Blue
      '#7BA7F7', // Light blue
      '#F87171', // Red
      '#34D399', // Green
      '#A78BFA', // Purple
      '#67E8F9', // Cyan
      '#F472B6', // Pink
      '#9CA3AF', // Gray
      '#FDE047', // Yellow
    ];
    return accountColors[index % accountColors.length];
  };

  // Função para truncar nomes longos
  const truncateAccountName = (name: string, maxLength: number = 25): string => {
    if (name.length <= maxLength) return name;
    return name.substring(0, maxLength - 3) + '...';
  };

  // Prepare account breakdown with colors if not already set
  const processedAccountBreakdown = accountBreakdown?.map((account, index) => ({
    ...account,
    color: account.color || generateAccountColor(index)
  })) || [];

  // Calcular valores absolutos para cada item (provider ou account)
  let currentBreakdown = showAccountDistribution ? processedAccountBreakdown : providerBreakdown;
  
  // Se está mostrando Account Distribution mas não há dados de conta, criar fallback
  if (showAccountDistribution && processedAccountBreakdown.length === 0 && selectedProvider) {
    console.log('🔧 Creating fallback account data for provider:', selectedProvider);
    currentBreakdown = [{
      accountId: 'fallback-account',
      billing_account_name: `${selectedProvider} Account`,
      accountName: `${selectedProvider} Account`,
      value: 100, // 100% do provedor selecionado
      color: getProviderColor(selectedProvider)
    }];
  }
  const distributionValues = currentBreakdown.map(item => ({
    ...item,
    absoluteValue: (item.value / 100) * totalSpend,
    displayName: showAccountDistribution 
      ? (item as AccountBreakdown).billing_account_name || (item as AccountBreakdown).accountName || (item as AccountBreakdown).accountId
      : item.name,
    fullDisplayName: showAccountDistribution 
      ? (item as AccountBreakdown).billing_account_name || (item as AccountBreakdown).accountName || (item as AccountBreakdown).accountId
      : item.name
  }));

  // Função para intensificar cores mantendo a identidade de cada provedor
  const intensifyColor = (color: string): string => {
    // Mapeamento para intensificar cores mantendo identidade visual dos provedores
    const intensifiedColors: { [key: string]: string } = {
      // Oracle Cloud - manter vermelho mas intensificar
      '#F87171': '#EF4444', // Vermelho Oracle -> vermelho mais vivo
      
      // Azure - manter azul mas intensificar  
      '#4A9EF1': '#3B82F6', // Azul Azure -> azul mais vivo
      
      // GCP - manter azul claro mas intensificar
      '#7BA7F7': '#60A5FA', // Azul GCP -> azul claro mais vivo
      
      // AWS - manter laranja mas intensificar
      '#FBB040': '#F59E0B', // Laranja AWS -> laranja mais vivo
      
      // Outras cores para compatibilidade
      '#34D399': '#10B981', // Verde -> verde vivo
      '#A78BFA': '#8B5CF6', // Roxo -> roxo vivo
      '#67E8F9': '#06B6D4', // Ciano -> ciano vivo
      '#F472B6': '#EC4899', // Rosa -> rosa vivo
      '#9CA3AF': '#6B7280', // Cinza -> cinza vivo
    };
    
    return intensifiedColors[color] || color;
  };

  const getBorderColor = (originalColor: string): string => {
    // Mapeamento para bordas mais intensas mantendo identidade de cada provedor
    const borderColors: { [key: string]: string } = {
      // Oracle Cloud - vermelho mais escuro (estilo Estimated Waste)
      '#F87171': '#DC2626',
      
      // Azure - azul mais escuro  
      '#4A9EF1': '#1D4ED8',
      
      // GCP - azul claro mais escuro
      '#7BA7F7': '#2563EB',
      
      // AWS - laranja mais escuro
      '#FBB040': '#D97706',
      
      // Cores adicionais para compatibilidade
      '#34D399': '#059669', // Verde -> verde escuro
      '#A78BFA': '#7C3AED', // Roxo -> roxo escuro
      '#67E8F9': '#0891B2', // Ciano -> ciano escuro
      '#F472B6': '#BE185D', // Rosa -> rosa escuro
      '#9CA3AF': '#475569', // Cinza -> cinza escuro
    };
    
    return borderColors[originalColor] || originalColor;
  };

  // Dados para o gráfico de pizza com cores originais e glassmorphism
  const pieData = distributionValues.map(item => ({
    name: truncateAccountName(item.displayName, 15), // Nome truncado para display na legenda
    fullName: item.fullDisplayName, // Nome completo para tooltip
    value: item.value,
    absoluteValue: item.absoluteValue,
    color: hexToRgba(intensifyColor(item.color), 0.4), // Usar cor intensificada com transparência
    originalColor: item.color // Manter cor original para borders
  }));
  
  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }: any) => {
    const value = pieData[index].value;
    
    // Só exibir texto se a fatia for grande o suficiente (maior que 8%)
    if (value < 8) {
      return null;
    }
    
    // Calcular posição do texto - fatias menores mais externas, fatias grandes mais centralizadas
    let radiusMultiplier = 0.8; // Posição padrão
    
    // Para fatias menores (8-15%), posicionar próximo da borda externa
    if (value < 15) {
      radiusMultiplier = 0.75;
    }
    // Para fatias médias (15-40%), posição externa
    else if (value < 40) {
      radiusMultiplier = 0.8;
    }
    // Para fatias grandes (40%+), posição mais centralizada
    else {
      radiusMultiplier = 0.55;
    }
    
    const radius = innerRadius + (outerRadius - innerRadius) * radiusMultiplier;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    
    // Usar a cor intensificada específica do provedor
    const providerColor = intensifyColor(pieData[index].originalColor);

    return (
      <text 
        x={x} 
        y={y} 
        fill={providerColor} 
        textAnchor="middle" // Centralizar o texto para evitar sobreposição
        dominantBaseline="central"
        fontSize={value < 15 ? 13 : 14} // Fonte maior: 13px para fatias menores, 14px para maiores
        fontWeight="bold"
        className="drop-shadow-sm"
        stroke={isDark ? "#333" : "#fff"}
        strokeWidth={0.5}
        paintOrder="stroke"
      >
        {`${value.toFixed(1)}%`}
      </text>
    );
  };

  // Componente para setor ativo (quando o mouse passa por cima)
  const renderActiveShape = (props: any) => {
    const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, value } = props;
    
    return (
      <g>
        <Sector
          cx={cx}
          cy={cy}
          innerRadius={innerRadius}
          outerRadius={outerRadius + 6}
          startAngle={startAngle}
          endAngle={endAngle}
          fill={fill}
          strokeWidth={2}
          stroke={isDark ? "#fff" : "#000"}
        />
      </g>
    );
  };

  // Componente de legenda customizado para replicar o estilo das fatias da pizza
  const CustomLegend = (props: any) => {
    const { payload } = props;
    
    return (
      <TooltipProvider>
        <div className={cn(
          "flex flex-col space-y-2 text-sm",
          isMobile ? "flex-row flex-wrap justify-center gap-4 space-y-0" : ""
        )}>
          {payload.map((entry: any, index: number) => {
            // Encontrar os dados correspondentes do pieData
            const pieEntry = pieData.find(item => item.name === entry.value);
            const backgroundColor = pieEntry ? pieEntry.color : entry.color; // Cor transparente como na pizza
            const borderColor = pieEntry ? getBorderColor(pieEntry.originalColor) : entry.color; // Borda vibrante como na pizza
            const fullName = pieEntry?.fullName || entry.value;
            // Verificar se nome será truncado baseado na largura máxima
            const maxLength = isMobile ? 12 : 18; // Caracteres aproximados para as larguras max-w
            const isNameTruncated = fullName.length > maxLength;
            
            const legendItem = (
              <div key={`legend-${index}`} className="flex items-center space-x-2 cursor-default">
                {/* Quadrado com mesmo estilo da pizza: fundo transparente + borda vibrante */}
                <div
                  className="w-3 h-3 rounded-sm flex-shrink-0"
                  style={{
                    backgroundColor: backgroundColor, // Cor transparente igual à pizza
                    border: `1px solid ${borderColor}`, // Borda vibrante igual à pizza (mesma espessura das fatias)
                    backdropFilter: 'blur(10px)', // Mesmo efeito glassmorphism da pizza
                    boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)' // Mesma sombra da pizza
                  }}
                />
                <span 
                  className={cn(
                    "font-semibold text-left leading-tight truncate",
                    isMobile ? "text-xs max-w-[100px]" : "text-sm max-w-[140px]"
                  )}
                  style={{ 
                    color: isDark ? "#F8FAFC" : "#0F172A",
                    textShadow: isDark ? "0 1px 2px rgba(0,0,0,0.8)" : "0 1px 2px rgba(0,0,0,0.1)"
                  }}
                  title={fullName} // Mostrar nome completo no hover
                >
                  {entry.value}
                </span>
              </div>
            );

            // Se o nome foi truncado, envolver em tooltip
            if (isNameTruncated) {
              return (
                <Tooltip key={`legend-${index}`}>
                  <TooltipTrigger asChild>
                    {legendItem}
                  </TooltipTrigger>
                  <TooltipContent>
                    <p className="max-w-xs break-words">{fullName}</p>
                  </TooltipContent>
                </Tooltip>
              );
            }

            return legendItem;
          })}
        </div>
      </TooltipProvider>
    );
  };

  // Tooltip customizado para o gráfico de pizza
  const CustomPieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      
      return (
        <div className={cn(
          "p-3 border rounded-md shadow-md max-w-xs",
          isDark 
            ? "bg-slate-800 border-slate-700 text-white" 
            : "bg-white border-gray-200 text-slate-900"
        )}>
          <p className="font-medium text-sm mb-1 break-words">{data.fullName || data.name}</p>
          <p className="text-sm">
            <span className="font-semibold">{formatCurrency(data.absoluteValue)}</span>
          </p>
          <p className={cn(
            "text-xs mt-1",
            isDark ? "text-slate-400" : "text-muted-foreground"
          )}>
            {data.value.toFixed(1)}{t('spendSummary.percentOfTotal')}
          </p>
        </div>
      );
    }
    
    return null;
  };
  
  // Função para lidar com o hover/touch no gráfico de pizza
  const onPieEnter = (_: any, index: number) => {
    setActiveIndex(index);
  };

  // Função para lidar com o mouse saindo do gráfico
  const onPieLeave = () => {
    setActiveIndex(null);
  };
  
  // Personalizado para a barra de progresso
  const CustomProgressBar = React.forwardRef<
    React.ElementRef<typeof ProgressPrimitive.Root>,
    React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root>
  >(({ className, value, ...props }, ref) => {
    let indicatorClass = "bg-primary";
    if (value && value >= 90) {
      indicatorClass = isDark ? "bg-red-500" : "bg-XCost-red";
    } else if (value && value >= 75) {
      indicatorClass = isDark ? "bg-amber-500" : "bg-amber-500";
    } else {
      indicatorClass = isDark ? "bg-green-500" : "bg-XCost-green";
    }
    
    return (
      <ProgressPrimitive.Root
        ref={ref}
        className={cn(
          "relative h-1.5 w-full overflow-hidden rounded-full",
          isDark ? "bg-slate-700" : "bg-gray-100",
          className
        )}
        {...props}
      >
        <ProgressPrimitive.Indicator
          className={cn("h-full w-full flex-1 transition-all", indicatorClass)}
          style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
        />
      </ProgressPrimitive.Root>
    );
  });
  CustomProgressBar.displayName = "CustomProgressBar";

  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg font-medium">
            <DollarSign className="mr-2 h-5 w-5 text-XCost-blue" />
            {t('spendSummary.title')}
          </CardTitle>
          {isUsingMockData && <MockDataBadge />}
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 md:col-span-4 space-y-3">
          <div>
              <p className={`text-sm text-muted-foreground mb-${isMobile ? '0' : '1'}`}>
                {t('spendSummary.totalSpend')}
              </p>
              <div className="flex items-baseline">
                <span className={`${isMobile ? 'text-2xl' : 'text-4xl'} font-bold tracking-tight`}>
                  {currency}{totalSpend.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                  })}
                </span>
              </div>
              
              <div className={cn(
                `mt-2 inline-flex items-center px-2 py-1 rounded-md ${isMobile ? 'text-xs' : 'text-sm'} font-medium`, 
                isIncrease 
                  ? isDark ? "bg-red-900/50 border border-red-800 text-red-400" : "bg-red-50 text-XCost-red" 
                  : isDark ? "bg-green-900/50 border border-green-800 text-green-400" : "bg-green-50 text-XCost-green"
              )}>
                {isIncrease ? (
                  <TrendingUp className={`${isMobile ? 'h-3 w-3' : 'h-4 w-4'} mr-1 flex-shrink-0`} />
                ) : (
                  <TrendingDown className={`${isMobile ? 'h-3 w-3' : 'h-4 w-4'} mr-1 flex-shrink-0`} />
                )}
                <span>
                  {isIncrease ? '+' : '-'}{changeAbs.toFixed(1)}% {t('spendSummary.vsPreviousPeriod')}
                </span>
              </div>
            </div>
            
            <div className={cn(
              "grid grid-cols-3 gap-3 pt-3 border-t",
              isDark ? "border-slate-700" : "border-gray-100"
            )}>
              <div className="text-center">
                <p className="text-xs text-muted-foreground mb-1">
                  {isMobile ? t('spendSummary.averageMobile') : t('spendSummary.monthlyAverage')}
                </p>
                <div className={`${isMobile ? 'text-sm' : 'text-lg'} font-semibold`}>
                  {formatCurrency(calculatedMonthlyAverage)}
                </div>
                <div className="text-xs text-muted-foreground">
                  {monthlyAverageDescription || "Baseado em dados atuais"}
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-xs text-muted-foreground mb-1">
                  {isMobile ? t('spendSummary.highestMobile') : t('spendSummary.highestSpend')}
                </p>
                <div className={`${isMobile ? 'text-sm' : 'text-lg'} font-semibold`}>
                  {formatCurrency(calculatedTopProvider.cost)}
                </div>
                <div className="mt-0.5 flex justify-center">
                  {calculatedTopProvider.name !== 'N/A' ? (
                    <ProviderBadge 
                      provider={calculatedTopProvider.name}
                      size="xs"
                    />
                  ) : (
                    <span className={cn(
                      "text-xs px-2 py-1 rounded-full",
                      isDark ? "text-slate-500 bg-slate-800" : "text-gray-500 bg-gray-100"
                    )}>
                      N/A
                    </span>
                  )}
                </div>
              </div>
              
              <div className="text-center">
                <p className="text-xs text-muted-foreground mb-1">
                  {isMobile ? t('spendSummary.projectionMobile') : t('spendSummary.annualProjection')}
                </p>
                <div className={`${isMobile ? 'text-sm' : 'text-lg'} font-semibold`}>
                  {formatCurrency(calculatedAnnualProjection)}
                </div>
                <div className="text-xs text-muted-foreground">
                  {t('spendSummary.currentYear')}
                </div>
              </div>
            </div>

            <div className={cn(
              "pt-3 border-t",
              isDark ? "border-slate-700" : "border-gray-100"
            )}>
              <div className="flex justify-between items-center">
                <p className={`${isMobile ? 'text-xs' : 'text-sm'} text-muted-foreground`}>
                  {isMobile ? t('spendSummary.budgetMobile') : t('spendSummary.budgetLimit')}
                </p>
                <span className={`text-xs font-medium ${getBudgetStatusColor()}`}>{budgetConsumed}%</span>
              </div>
              <div className="mt-1.5">
                <CustomProgressBar value={budgetConsumed} />
              </div>
              <div className="flex justify-between text-xs mt-1 text-muted-foreground">
                <span>{t('spendSummary.consumed')}</span>
                <span>{formatCurrency(budgetLimit)}</span>
              </div>
            </div>
          </div>
          
          <div className="col-span-12 md:col-span-4">
            <div className="flex items-center mb-2">
              <p className="text-sm text-muted-foreground">{distributionTitle}</p>
            </div>

            <div className="h-64 w-full relative">
              <div className="absolute inset-0 backdrop-blur-sm bg-white/5 dark:bg-black/5 rounded-lg"></div>
              {pieData.length === 0 || totalSpend === 0 ? (
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-4">
                  <div className={cn(
                    "w-12 h-12 rounded-full flex items-center justify-center mb-3",
                    isDark ? "bg-slate-800/50" : "bg-gray-100/50"
                  )}>
                    <PieChartIcon className={cn(
                      "h-6 w-6",
                      isDark ? "text-slate-600" : "text-gray-400"
                    )} />
                  </div>
                  <h4 className={cn(
                    "text-sm font-medium mb-1",
                    isDark ? "text-slate-300" : "text-gray-700"
                  )}>
                    {t('spendSummary.noDistributionData')}
                  </h4>
                  <p className={cn(
                    "text-xs max-w-xs",
                    isDark ? "text-slate-500" : "text-gray-500"
                  )}>
                    {showAccountDistribution 
                      ? t('spendSummary.noAccountDataForProvider')
                      : t('spendSummary.noProviderData')
                    }
                  </p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    activeIndex={activeIndex !== null ? activeIndex : undefined}
                    activeShape={renderActiveShape}
                    data={pieData.map(entry => ({
                      ...entry,
                      // Adicionar propriedade legendColor para ser usada pela legenda
                      legendColor: getBorderColor(entry.originalColor)
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                    onMouseEnter={onPieEnter}
                    onMouseLeave={onPieLeave}
                    onClick={onPieEnter}
                  >
                    {pieData.map((entry, index) => (
                      <Cell 
                        key={`cell-${index}`} 
                        fill={entry.color} 
                        stroke={getBorderColor(entry.originalColor)}
                        strokeWidth={1}
                        style={{
                          filter: 'drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1))',
                          backdropFilter: 'blur(10px)'
                        }}
                      />
                    ))}
                  </Pie>
                  <Legend 
                    layout={isMobile ? "horizontal" : "vertical"}
                    verticalAlign={isMobile ? "bottom" : "middle"}
                    align={isMobile ? "center" : "right"}
                    content={<CustomLegend />}
                    wrapperStyle={isMobile ? 
                      { paddingTop: '10px' }
                      : { paddingLeft: '15px', marginLeft: '10px' }
                    }
                  />
                  <RechartsTooltip 
                    content={<CustomPieTooltip />}
                    wrapperStyle={{ outline: 'none' }}
                  />
                </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
          
          <div className="col-span-12 md:col-span-4 space-y-3">
            <div className="flex items-center mb-2">
              <p className="text-sm text-muted-foreground">{t('spendSummary.highlights')}</p>
            </div>
            
            <div className={cn(
              "rounded-md p-3 border",
              isDark ? "bg-blue-900/50 border-blue-800" : "bg-blue-50 border-blue-100"
            )}>
              <div className="flex items-start">
                <Calendar className={cn(
                  "h-5 w-5 mr-2 mt-0.5",
                  isDark ? "text-blue-400" : "text-XCost-blue"
                )} />
                <div>
                  <p className="text-xs text-muted-foreground">{t('spendSummary.nextMonthForecast')}</p>
                  <div className="flex items-center">
                    <span className={cn(
                      "text-lg font-bold",
                      isDark ? "text-blue-400" : "text-XCost-blue"
                    )}>
                      {formatCurrency(calculatedProjectedNextMonth)}
                    </span>
                    {nextMonthForecast?.change_percentage !== undefined && (
                      <>
                        <ArrowRight className="h-3 w-3 mx-1 text-muted-foreground" />
                        <span className={cn(
                          "text-xs",
                          nextMonthForecast.change_percentage > 0 
                            ? isDark ? "text-red-400" : "text-XCost-red" 
                            : isDark ? "text-green-400" : "text-XCost-green"
                        )}>
                          {nextMonthForecast.change_percentage > 0 ? '+' : ''}{nextMonthForecast.change_percentage.toFixed(1)}%
                        </span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            <div className={cn(
              "rounded-md p-3 border",
              isDark ? "bg-red-900/50 border-red-800" : "bg-red-50 border-red-100"
            )}>
              <div className="flex items-start">
                <AlertTriangle className={cn(
                  "h-5 w-5 mr-2 mt-0.5",
                  isDark ? "text-red-400" : "text-XCost-red"
                )} />
                <div>
                  <p className="text-xs text-muted-foreground">{t('spendSummary.estimatedWaste')}</p>
                  <div className="flex items-center">
                    <span className={cn(
                      "text-lg font-bold",
                      isDark ? "text-red-400" : "text-XCost-red"
                    )}>
                      {formatCurrency(wastedSpend)}
                    </span>
                    {wastedSpend > 0 && totalSpend > 0 && (
                      <span className={cn(
                        "text-xs ml-2",
                        isDark ? "text-red-400" : "text-XCost-red"
                      )}>
                        ({Math.round((wastedSpend/totalSpend)*100)}% {t('spendSummary.ofTotal')})
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
            
            <div className={cn(
              "rounded-md p-3 border",
              isDark ? "bg-green-900/50 border-green-800" : "bg-green-50 border-green-100"
            )}>
              <div className="flex items-start">
                <Coins className={cn(
                  "h-5 w-5 mr-2 mt-0.5",
                  isDark ? "text-green-400" : "text-XCost-green"
                )} />
                <div>
                  <p className="text-xs text-muted-foreground">{t('spendSummary.realizedSavings')}</p>
                  <div className="flex items-center">
                    <span className={cn(
                      "text-lg font-bold",
                      isDark ? "text-green-400" : "text-XCost-green"
                    )}>
                      {formatCurrency(savingsRealized)}
                    </span>
                    {savingsRealized > 0 && totalSpend > 0 && (
                      <span className={cn(
                        "text-xs ml-2",
                        isDark ? "text-green-400" : "text-XCost-green"
                      )}>
                        ({Math.round((savingsRealized/totalSpend)*100)}% {t('spendSummary.ofTotal')})
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
