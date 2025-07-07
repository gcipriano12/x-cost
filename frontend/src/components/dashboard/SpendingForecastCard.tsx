import React, { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingUp, AlertCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { MockDataBadge } from '@/components/ui/mock-data-badge';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface ForecastDataPoint {
  month: string;
  actual?: number;
  forecast?: number;
  budget?: number;
}

interface SpendingForecastCardProps {
  data: ForecastDataPoint[];
  currency: string;
  budgetInfo?: {
    total_budget: number;
    monthly_budget: number;
    budget_exceeded_months: string[];
  };
  metadata?: {
    model_accuracy: number;
    confidence_level: number;
    data_completeness: number;
    forecast_method: string;
  };
  isUsingMockData?: boolean;
}

export function SpendingForecastCard({ data, currency, budgetInfo, metadata, isUsingMockData = false }: SpendingForecastCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Verificar se há meses onde a previsão excede o orçamento
  const budgetExceeded = budgetInfo?.budget_exceeded_months && budgetInfo.budget_exceeded_months.length > 0;
  
  // Usar o budget mensal da API ou fallback para o primeiro ponto de dados
  const monthlyBudget = budgetInfo?.monthly_budget || data[0]?.budget;
  
  // Função para determinar estilo da tag de acurácia
  const getAccuracyBadgeStyle = (accuracy: number) => {
    if (accuracy >= 80) {
      return {
        bgColor: isDark ? "bg-green-900/50" : "bg-green-50",
        textColor: isDark ? "text-green-100" : "text-green-700",
        borderColor: isDark ? "border-green-800" : "border-green-200",
        label: t('spendingForecast.highAccuracy')
      };
    } else if (accuracy >= 60) {
      return {
        bgColor: isDark ? "bg-yellow-900/50" : "bg-yellow-50",
        textColor: isDark ? "text-yellow-100" : "text-yellow-700",
        borderColor: isDark ? "border-yellow-800" : "border-yellow-200",
        label: t('spendingForecast.mediumAccuracy')
      };
    } else {
      return {
        bgColor: isDark ? "bg-orange-900/50" : "bg-orange-50",
        textColor: isDark ? "text-orange-100" : "text-orange-700",
        borderColor: isDark ? "border-orange-800" : "border-orange-200",
        label: t('spendingForecast.lowAccuracy')
      };
    }
  };
  
  // Processar dados com formatação correta das datas ANTES de passar para o gráfico
  const processedData = useMemo(() => {
    return data.map((item, index) => {
      const currentDate = new Date();
      const currentYear = currentDate.getFullYear(); // 2025
      
      // Lógica baseada nos dados reais (20 pontos total):
      // Índices 0-5: Jul/24 a Dec/24 (2024)
      // Índices 6-18: Jan/25 a Dec/25 (2025) 
      // Índice 19: Jan/26 (2026)
      let year: number;
      if (index <= 5) {
        year = currentYear - 1; // 2024
      } else if (index <= 18) {
        year = currentYear; // 2025
      } else {
        year = currentYear + 1; // 2026
      }
      
      const shortYear = year.toString().slice(-2);
      const formattedMonth = `${item.month}/${shortYear}`;
      
      return {
        ...item,
        formattedMonth, // Nova propriedade com mês/ano formatado
        originalMonth: item.month // Manter o mês original para referência
      };
    });
  }, [data]);

  // Função para converter mês abreviado para formato mês/ano (para tooltip)
  const formatMonthWithYear = (monthStr: string) => {
    // Encontrar o item nos dados processados que corresponde
    const matchingItem = processedData.find(item => 
      item.originalMonth === monthStr || item.formattedMonth === monthStr
    );
    
    if (matchingItem) {
      return matchingItem.formattedMonth;
    }
    
    // Fallback: se não encontrar, retornar como está
    return monthStr;
  };
  
  const formatCurrency = (value: number) => {
    if (!value) return '-';
    
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}M`;
    } else if (value >= 1000) {
      return `${currency}${(value / 1000).toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      })}K`;
    }
    return `${currency}${value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };
  
  // Formatador específico para o eixo Y que mantém espaçamento consistente
  const formatYAxisTick = (value: number) => {
    if (value === 0) return `${currency} 0K`;
    if (value >= 1000000) {
      return `${currency} ${(value / 1000000).toFixed(0)}M`;
    }
    return `${currency} ${(value / 1000).toFixed(0)}K`;
  };
  
  const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
    if (active && payload && payload.length) {
      return (
        <div className={cn(
          "p-3 border rounded-md shadow-md",
          isDark 
            ? "bg-slate-800 border-slate-700 text-white" 
            : "bg-white border-gray-200 text-slate-900"
        )}>
          <p className={cn(
            "font-medium text-xs border-b pb-1 mb-2",
            isDark ? "border-slate-700" : "border-gray-200"
          )}>
            {formatMonthWithYear(label || '')}
          </p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center text-sm mb-1 last:mb-0">
              <div
                className="w-3 h-3 rounded-full mr-2"
                style={{ backgroundColor: entry.color }}
              />
              <span className={cn(
                "mr-2 text-xs",
                isDark ? "text-slate-400" : "text-muted-foreground"
              )}>
                {entry.name}:
              </span>
              <span className="font-medium">
                {entry.value ? formatCurrency(entry.value) : '-'}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };
  
  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="pb-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CardTitle className="flex items-center text-lg font-medium">
              <TrendingUp className="mr-2 h-5 w-5 text-XCost-blue-light" />
              <span className="hidden lg:inline">{t('spendingForecast.title')}</span>
              <span className="lg:hidden">{t('spendingForecast.titleShort')}</span>
            </CardTitle>
            
            {/* Tag de Acurácia */}
            {metadata?.model_accuracy && (
              <Badge 
                variant="outline" 
                className={cn(
                  "text-xs",
                  getAccuracyBadgeStyle(metadata.model_accuracy).bgColor,
                  getAccuracyBadgeStyle(metadata.model_accuracy).textColor,
                  getAccuracyBadgeStyle(metadata.model_accuracy).borderColor
                )}
              >
                {metadata.model_accuracy.toFixed(0)}% {t('spendingForecast.accuracy')}
              </Badge>
            )}
            
            {isUsingMockData && <MockDataBadge />}
          </div>
          
          {budgetExceeded && (
            <Badge variant="outline" className={cn(
              isDark ? "bg-red-900/50 text-red-100 border-red-800" : "bg-red-50 text-red-700 border-red-200"
            )}>
              <AlertCircle className="h-3 w-3 mr-1" />
              <span className="text-xs">{t('spendingForecast.forecastExceedsBudget')}</span>
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="pt-2">
        <div className="h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={processedData}
              margin={{ top: 10, right: 25, left: 0, bottom: 20 }}
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={isDark ? "#334155" : "#f5f5f5"} 
              />
              <XAxis 
                dataKey="formattedMonth" 
                tick={{ fontSize: 12, fill: isDark ? "#cbd5e1" : undefined }} 
                tickLine={false}
                axisLine={{ stroke: isDark ? "#475569" : "#e5e7eb" }}
              />
              <YAxis 
                tickFormatter={formatYAxisTick}
                width={70}
                tick={{ fontSize: 12, fill: isDark ? "#cbd5e1" : undefined }}
                tickLine={false}
                axisLine={{ stroke: isDark ? "#475569" : "#e5e7eb" }}
              />
              <Tooltip content={<CustomTooltip />} />
              {monthlyBudget && (
                <ReferenceLine 
                  y={monthlyBudget} 
                  stroke={isDark ? "#f87171" : "#F87171"} 
                  strokeDasharray="3 3" 
                  strokeWidth={2}
                  label={{ 
                    position: 'insideTopLeft',
                    value: t('spendingForecast.budget'), 
                    fill: isDark ? "#f87171" : "#F87171", 
                    fontSize: 12,
                    offset: 5,
                    textAnchor: 'start'
                  }}
                />
              )}
              <Line 
                type="monotone" 
                dataKey="actual" 
                stroke={isDark ? "#94A3B8" : "#1A2B3C"} 
                strokeWidth={2} 
                dot={{ r: 4, fill: isDark ? "#94A3B8" : "#1A2B3C", strokeWidth: 0 }}
                name={t('spendingForecast.actualSpendChart')}
                activeDot={{ r: 6, fill: isDark ? "#94A3B8" : "#1A2B3C", stroke: isDark ? "#1e293b" : "white", strokeWidth: 2 }}
              />
              <Line 
                type="monotone" 
                dataKey="forecast" 
                stroke={isDark ? "#3B82F6" : "#60A5FA"} 
                strokeWidth={2} 
                strokeDasharray="5 5"
                dot={{ r: 4, fill: isDark ? "#3B82F6" : "#60A5FA", strokeWidth: 0 }}
                name={t('spendingForecast.forecastChart')}
                activeDot={{ r: 6, fill: isDark ? "#3B82F6" : "#60A5FA", stroke: isDark ? "#1e293b" : "white", strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="mt-1 flex justify-center items-center gap-4 text-xs text-muted-foreground">
          <div className="flex items-center">
            <div className={cn(
              "w-3 h-3 rounded-full mr-1",
              isDark ? "bg-[#94A3B8]" : "bg-[#1A2B3C]"
            )}></div>
            <span>{t('spendingForecast.actualSpend')}</span>
          </div>
          <div className="flex items-center">
            <div className={cn(
              "w-3 h-3 rounded-full mr-1", 
              isDark ? "bg-[#3B82F6]" : "bg-[#60A5FA]"
            )}></div>
            <span>{t('spendingForecast.forecast')}</span>
          </div>
          <div className="flex items-center">
            <div className="w-6 h-0 border-t-2 border-dashed border-[#F87171] mr-1 mt-1"></div>
            <span>{t('spendingForecast.budget')}: {formatCurrency(monthlyBudget || 0)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
