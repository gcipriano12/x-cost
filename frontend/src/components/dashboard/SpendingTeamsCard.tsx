import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { BarChart3 } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface SpendingTeam {
  name: string;
  value: number;
  color: string;
}

interface SpendingTeamsCardProps {
  categories: SpendingTeam[];
  currency: string;
}

export function SpendingTeamsCard({ categories, currency }: SpendingTeamsCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toLocaleString('en-US', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
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
  
  // Cores padrão caso a propriedade color não esteja preenchida
  const defaultColors = ['#60A5FA', '#F97316', '#10B981', '#8B5CF6', '#EC4899'];

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="flex items-center justify-center text-lg font-medium">
          <BarChart3 className="mr-2 h-5 w-5 text-XCost-blue" />
          {t('spendingTeams.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow p-1 pb-2 flex flex-col">
        <div className="flex-grow h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={categories}
              margin={{ top: 5, right: 30, left: 5, bottom: 5 }}
              barGap={5}
              barCategoryGap={15}
              layout="vertical"
            >
              <CartesianGrid 
                strokeDasharray="3 3" 
                horizontal={true} 
                vertical={false} 
                stroke={isDark ? "#333333" : "#f0f0f0"} 
              />
              <XAxis 
                type="number"
                tickFormatter={formatCurrency}
                tick={{ 
                  fontSize: 11,
                  fill: isDark ? "#94a3b8" : "#64748b"
                }}
                tickLine={false}
                axisLine={{ stroke: isDark ? "#333333" : "#e0e0e0" }}
                tickCount={5}
              />
              <YAxis 
                dataKey="name"
                type="category" 
                width={120}
                tick={{ 
                  fontSize: 12, 
                  fontWeight: 500,
                  fill: isDark ? "#94a3b8" : "#64748b"
                }}
                tickLine={false}
                axisLine={{ stroke: isDark ? "#333333" : "#e0e0e0" }}
              />
              <Tooltip 
                formatter={(value: number) => [`${currency}${value.toLocaleString('en-US', {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2
                })}`, 'Valor']}
                labelFormatter={(label) => `Equipe: ${label}`}
                contentStyle={{ 
                  backgroundColor: isDark ? '#1e293b' : 'white', 
                  border: `1px solid ${isDark ? '#334155' : '#f0f0f0'}`,
                  borderRadius: '6px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
                  color: isDark ? '#e2e8f0' : '#1e293b'
                }}
                itemStyle={{
                  color: isDark ? '#94a3b8' : '#64748b'
                }}
                labelStyle={{
                  color: isDark ? '#e2e8f0' : '#1e293b'
                }}
              />
              <Bar 
                dataKey="value" 
                radius={[0, 4, 4, 0]}
                barSize={30}
                animationDuration={500}
              >
                {categories.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color || defaultColors[index % defaultColors.length]} 
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
