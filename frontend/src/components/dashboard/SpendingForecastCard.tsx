import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { TrendingUp, AlertCircle } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
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
}

export function SpendingForecastCard({ data, currency }: SpendingForecastCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Verificar se o último valor previsto ultrapassa o orçamento
  const lastPoint = data[data.length - 1];
  const budgetExceeded = lastPoint.forecast && lastPoint.budget && lastPoint.forecast > lastPoint.budget;
  
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
  
  const CustomTooltip = ({ active, payload, label }: any) => {
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
            {label}
          </p>
          {payload.map((entry: any) => (
            <div key={entry.dataKey} className="flex items-center text-sm mb-1 last:mb-0">
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
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg font-medium">
            <TrendingUp className="mr-2 h-5 w-5 text-XCost-blue-light" />
            {t('spendingForecast.title')}
          </CardTitle>
          
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
      <CardContent>
        <div className="h-[330px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={data}
              margin={{ top: 10, right: 30, left: 0, bottom: 20 }}
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={isDark ? "#334155" : "#f5f5f5"} 
              />
              <XAxis 
                dataKey="month" 
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
              <ReferenceLine 
                y={data[0].budget} 
                stroke={isDark ? "#f87171" : "#F87171"} 
                strokeDasharray="3 3" 
                strokeWidth={2}
                label={{ 
                  position: 'right',
                  value: t('spendingForecast.budget'), 
                  fill: isDark ? "#f87171" : "#F87171", 
                  fontSize: 11,
                  offset: 10,
                  formatter: () => t('spendingForecast.budget'),
                  className: isDark ? 'text-red-400' : 'text-red-500'
                }}
              />
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
        
        <div className="mt-4 flex justify-between text-xs text-muted-foreground">
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
            <div className="w-3 h-3 rounded-full bg-[#F87171] mr-1"></div>
            <span>{t('spendingForecast.budget')}: {formatCurrency(data[0].budget || 0)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
