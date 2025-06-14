import React from 'react';
import { useTranslation } from 'react-i18next';
import * as ProgressPrimitive from "@radix-ui/react-progress";
import { TrendingUp, TrendingDown, DollarSign, Calendar, AlertCircle, BarChart3, ArrowRight, Disc, Target, AlertTriangle, Coins, PieChart as PieChartIcon, Sparkles, Cloud } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Badge } from '@/components/ui/badge';
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

interface SpendSummaryProps {
  totalSpend: number;
  currency: string;
  previousPeriodChange: number;
  sparklineData: number[];
  providerBreakdown?: ProviderBreakdown[];
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
  annualProjection?: number;
  nextMonthForecast?: {
    amount: number;
    change_percentage: number;
  };
}

export function SpendSummaryCard({ 
  totalSpend, 
  currency, 
  previousPeriodChange, 
  sparklineData,
  providerBreakdown = [
    { name: 'AWS', value: 58, color: getProviderColor('AWS') },
    { name: 'Azure', value: 22, color: getProviderColor('Azure') },
    { name: 'GCP', value: 12, color: getProviderColor('GCP') },
    { name: 'Oracle Cloud', value: 8, color: getProviderColor('Oracle Cloud') }
  ],
  wastedSpend = totalSpend * 0.15,
  budgetLimit = totalSpend * 1.2,
  budgetConsumed = 75,
  savingsRealized = totalSpend * 0.08,
  topService,
  topProvider,
  monthlyAverage,
  annualProjection,
  nextMonthForecast
}: SpendSummaryProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const isMobile = useIsMobile();
  const isIncrease = previousPeriodChange > 0;
  const changeAbs = Math.abs(previousPeriodChange);
  const [activeIndex, setActiveIndex] = React.useState<number | null>(null);
  
  // Use API data when available, fallback to calculated values
  const calculatedMonthlyAverage = monthlyAverage || totalSpend / 6;
  const calculatedProjectedNextMonth = nextMonthForecast?.amount || totalSpend * (1 + (previousPeriodChange / 100));
  const calculatedTopProvider = topProvider || {
    name: "AWS",
    cost: totalSpend * 0.25
  };
  const calculatedAnnualProjection = annualProjection || totalSpend * 12;
  
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

  // Calcular valores absolutos para cada provedor
  const providerValues = providerBreakdown.map(provider => ({
    ...provider,
    absoluteValue: (provider.value / 100) * totalSpend
  }));

  // Dados para o gráfico de pizza
  const pieData = providerValues.map(provider => ({
    name: provider.name,
    value: provider.value,
    absoluteValue: provider.absoluteValue,
    color: provider.color
  }));
  
  const RADIAN = Math.PI / 180;
  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, index }: any) => {
    const radius = innerRadius + (outerRadius - innerRadius) * 0.6;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill={isDark ? "#FFFFFF" : "#000000"} 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={10}
        fontWeight="bold"
        stroke={isDark ? "#333" : "#fff"}
        strokeWidth={0.5}
        paintOrder="stroke"
      >
        {`${pieData[index].value.toFixed(1)}%`}
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

  // Tooltip customizado para o gráfico de pizza
  const CustomPieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      
      return (
        <div className={cn(
          "p-3 border rounded-md shadow-md",
          isDark 
            ? "bg-slate-800 border-slate-700 text-white" 
            : "bg-white border-gray-200 text-slate-900"
        )}>
          <p className="font-medium text-sm mb-1">{data.name}</p>
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
        <CardTitle className="flex items-center text-lg font-medium">
          <DollarSign className="mr-2 h-5 w-5 text-XCost-blue" />
          {t('spendSummary.title')}
        </CardTitle>
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
                  {t('spendSummary.lastSixMonths')}
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
                  <Badge 
                    className="text-xs py-0 text-white border-0"
                    style={{ backgroundColor: getProviderColor(calculatedTopProvider.name) }}
                  >
                    {calculatedTopProvider.name}
                  </Badge>
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
              <p className="text-sm text-muted-foreground">{t('spendSummary.providerDistribution')}</p>
            </div>

            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    activeIndex={activeIndex !== null ? activeIndex : undefined}
                    activeShape={renderActiveShape}
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={renderCustomizedLabel}
                    outerRadius={80}
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
                        stroke={isDark ? "#333" : "#fff"}
                        strokeWidth={2}
                      />
                    ))}
                  </Pie>
                  <Legend 
                    layout={isMobile ? "horizontal" : "vertical"}
                    verticalAlign={isMobile ? "bottom" : "middle"}
                    align={isMobile ? "center" : "right"}
                    formatter={(value) => <span className="text-xs">{value}</span>}
                    wrapperStyle={isMobile ? 
                      { paddingTop: '10px', color: isDark ? "#E2E8F0" : undefined }
                      : { color: isDark ? "#E2E8F0" : undefined }
                    }
                  />
                  <RechartsTooltip 
                    content={<CustomPieTooltip />}
                    wrapperStyle={{ outline: 'none' }}
                  />
                </PieChart>
              </ResponsiveContainer>
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
                    )}>{formatCurrency(calculatedProjectedNextMonth)}</span>
                    <ArrowRight className="h-3 w-3 mx-1 text-muted-foreground" />
                    <span className={cn(
                      "text-xs",
                      (nextMonthForecast?.change_percentage || previousPeriodChange) > 0 
                        ? isDark ? "text-red-400" : "text-XCost-red" 
                        : isDark ? "text-green-400" : "text-XCost-green"
                    )}>
                      {(() => {
                        const changeValue = nextMonthForecast?.change_percentage ?? previousPeriodChange;
                        return `${changeValue > 0 ? '+' : ''}${changeValue.toFixed(1)}%`;
                      })()}
                    </span>
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
                    )}>{formatCurrency(wastedSpend)}</span>
                    <span className={cn(
                      "text-xs ml-2",
                      isDark ? "text-red-400" : "text-XCost-red"
                    )}>
                      ({Math.round((wastedSpend/totalSpend)*100)}% {t('spendSummary.ofTotal')})
                    </span>
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
                    )}>{formatCurrency(savingsRealized)}</span>
                    <span className={cn(
                      "text-xs ml-2",
                      isDark ? "text-green-400" : "text-XCost-green"
                    )}>
                      ({Math.round((savingsRealized/totalSpend)*100)}% {t('spendSummary.ofTotal')})
                    </span>
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
