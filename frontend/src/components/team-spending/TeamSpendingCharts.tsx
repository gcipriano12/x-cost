import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { BarChart3, PieChart as PieChartIcon } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface SpendingTeam {
  name: string;
  value: number;
  color: string;
}

interface TeamSpendingChartsProps {
  teamData: SpendingTeam[];
  isLoading: boolean;
}

export const TeamSpendingCharts: React.FC<TeamSpendingChartsProps> = ({
  teamData,
  isLoading
}) => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Formatador de moeda para tooltips
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `$${(value / 1000000).toLocaleString('pt-BR', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
      })}M`;
    } else if (value >= 1000) {
      return `$${(value / 1000).toLocaleString('pt-BR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      })}K`;
    }
    return `$${value.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };
  
  // Processar dados para o pie chart (top 8 + outros)
  const processPieData = () => {
    if (teamData.length === 0) return [];
    
    const sortedData = [...teamData].sort((a, b) => b.value - a.value);
    const topTeams = sortedData.slice(0, 8);
    const remainingTeams = sortedData.slice(8);
    
    let processedData = topTeams;
    
    if (remainingTeams.length > 0) {
      const othersValue = remainingTeams.reduce((sum, team) => sum + team.value, 0);
      processedData.push({
        name: `Outros (${remainingTeams.length})`,
        value: othersValue,
        color: '#6B7280'
      });
    }
    
    return processedData;
  };
  
  const pieData = processPieData();
  const totalValue = teamData.reduce((sum, team) => sum + team.value, 0);
  
  // Calcular distribuição por faixas de gasto
  const calculateSpendingDistribution = () => {
    const ranges = [
      { name: 'Até $10K', min: 0, max: 10000, count: 0, color: '#10B981' },
      { name: '$10K - $50K', min: 10000, max: 50000, count: 0, color: '#3B82F6' },
      { name: '$50K - $100K', min: 50000, max: 100000, count: 0, color: '#F59E0B' },
      { name: 'Acima $100K', min: 100000, max: Infinity, count: 0, color: '#EF4444' }
    ];
    
    teamData.forEach(team => {
      const range = ranges.find(r => team.value >= r.min && team.value < r.max);
      if (range) range.count++;
    });
    
    return ranges.filter(r => r.count > 0);
  };
  
  const distributionData = calculateSpendingDistribution();
  
  if (isLoading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardHeader>
            <div className="h-6 bg-gray-200 rounded animate-pulse" />
            <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
          </CardHeader>
          <CardContent>
            <div className="h-64 bg-gray-200 rounded animate-pulse" />
          </CardContent>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Gráfico de Pizza - Distribuição por Equipes */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChartIcon className="h-5 w-5 text-blue-600" />
            {t('teamSpending.charts.pieTitle')}
          </CardTitle>
          <CardDescription>
            {t('teamSpending.charts.pieDescription')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pieData.length === 0 ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <PieChartIcon className={cn(
                  "h-12 w-12 mx-auto mb-3",
                  isDark ? "text-slate-600" : "text-gray-400"
                )} />
                <p className={cn(
                  "text-sm",
                  isDark ? "text-slate-500" : "text-gray-500"
                )}>
                  {t('teamSpending.charts.noData')}
                </p>
              </div>
            </div>
          ) : (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: number) => [formatCurrency(value), 'Gasto']}
                    contentStyle={{ 
                      backgroundColor: isDark ? '#1e293b' : 'white', 
                      border: `1px solid ${isDark ? '#334155' : '#f0f0f0'}`,
                      borderRadius: '6px',
                      color: isDark ? '#e2e8f0' : '#1e293b'
                    }}
                  />
                  <Legend 
                    verticalAlign="bottom" 
                    height={36}
                    iconType="circle"
                    wrapperStyle={{ 
                      paddingTop: '20px',
                      fontSize: '12px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Gráfico de Distribuição por Faixas */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-green-600" />
            {t('teamSpending.charts.distributionTitle')}
          </CardTitle>
          <CardDescription>
            {t('teamSpending.charts.distributionDescription')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {distributionData.length === 0 ? (
            <div className="flex items-center justify-center h-32">
              <p className={cn(
                "text-sm",
                isDark ? "text-slate-500" : "text-gray-500"
              )}>
                {t('teamSpending.charts.noData')}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {distributionData.map((range, index) => (
                <div key={range.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div 
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: range.color }}
                    />
                    <span className="text-sm font-medium">{range.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-muted-foreground">
                      {range.count} equipe{range.count !== 1 ? 's' : ''}
                    </span>
                    <div 
                      className="h-2 rounded-full bg-gray-200 w-20"
                      style={{ 
                        background: `linear-gradient(to right, ${range.color} ${(range.count / teamData.length) * 100}%, #e5e7eb ${(range.count / teamData.length) * 100}%)`
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
