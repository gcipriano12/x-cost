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
  maxTeamsToShow?: number; // Novo: limite de equipes a mostrar
}

export function SpendingTeamsCard({ categories, currency, maxTeamsToShow = 15 }: SpendingTeamsCardProps) {
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

  // Processar dados para grandes quantidades de equipes
  const processTeamsData = (teams: SpendingTeam[]): { 
    displayData: SpendingTeam[], 
    hiddenTeamsCount: number,
    hiddenTeamsValue: number 
  } => {
    if (teams.length <= maxTeamsToShow) {
      return { displayData: teams, hiddenTeamsCount: 0, hiddenTeamsValue: 0 };
    }

    // Ordenar por valor decrescente e pegar os top N
    const sortedTeams = [...teams].sort((a, b) => b.value - a.value);
    const topTeams = sortedTeams.slice(0, maxTeamsToShow - 1); // -1 para deixar espaço para "Outros"
    const hiddenTeams = sortedTeams.slice(maxTeamsToShow - 1);
    
    const hiddenTeamsValue = hiddenTeams.reduce((sum, team) => sum + team.value, 0);
    const hiddenTeamsCount = hiddenTeams.length;

    // Criar item "Outros" se houver equipes ocultas
    const othersItem: SpendingTeam = {
      name: `Outros (${hiddenTeamsCount})`,
      value: hiddenTeamsValue,
      color: '#6B7280' // Cor neutra para "outros"
    };

    return {
      displayData: [...topTeams, othersItem],
      hiddenTeamsCount,
      hiddenTeamsValue
    };
  };

  const { displayData, hiddenTeamsCount, hiddenTeamsValue } = processTeamsData(categories);
  
  // Componente personalizado para truncar nomes longos
  const CustomYAxisTick = (props: any) => {
    const { x, y, payload } = props;
    const maxLength = 12; // Máximo de caracteres antes de truncar
    
    let displayName = payload.value;
    if (displayName.length > maxLength) {
      displayName = displayName.substring(0, maxLength - 3) + '...';
    }
    
    return (
      <g transform={`translate(${x},${y})`}>
        <text 
          x={0} 
          y={0} 
          dy={4} 
          textAnchor="end" 
          fill={isDark ? "#94a3b8" : "#64748b"}
          fontSize={11}
          fontWeight={500}
        >
          {displayName}
        </text>
      </g>
    );
  };
  
  // Calcular altura dinâmica baseada no número de itens
  const calculateHeight = (itemCount: number) => {
    const minHeight = 320;
    const maxHeight = 600;
    const itemHeight = 35; // Altura aproximada por item
    const calculatedHeight = Math.max(minHeight, Math.min(maxHeight, itemCount * itemHeight + 100));
    return calculatedHeight;
  };

  const chartHeight = calculateHeight(displayData.length);

  return (
    <Card className="h-full flex flex-col">
      <CardHeader className="pb-2 flex-shrink-0">
        <CardTitle className="flex items-center justify-start text-lg font-medium text-left">
          <BarChart3 className="mr-2 h-5 w-5 text-XCost-blue" />
          {t('spendingTeams.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-grow p-0 pb-2 flex flex-col">
        {displayData.length === 0 ? (
          <div className="flex-grow flex items-center justify-center">
            <div className="text-center py-8">
              <div className={cn(
                "w-12 h-12 rounded-full flex items-center justify-center mb-3 mx-auto",
                isDark ? "bg-slate-800/50" : "bg-gray-100/50"
              )}>
                <BarChart3 className={cn(
                  "h-6 w-6",
                  isDark ? "text-slate-600" : "text-gray-400"
                )} />
              </div>
              <h4 className={cn(
                "text-sm font-medium mb-1",
                isDark ? "text-slate-300" : "text-gray-700"
              )}>
                {t('spendingTeams.noData')}
              </h4>
              <p className={cn(
                "text-xs max-w-xs",
                isDark ? "text-slate-500" : "text-gray-500"
              )}>
                {t('spendingTeams.noDataDescription')}
              </p>
            </div>
          </div>
        ) : (
          <div className="flex-grow" style={{ height: `${chartHeight}px` }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={displayData}
                margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                barGap={3}
                barCategoryGap={8}
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
                  width={90} // Reduzido para menos espaço à esquerda
                  tick={<CustomYAxisTick />}
                  tickLine={false}
                  axisLine={{ stroke: isDark ? "#333333" : "#e0e0e0" }}
                  interval={0} // Mostrar todos os labels
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
                  barSize={Math.max(20, Math.min(30, 600 / displayData.length))} // Altura adaptativa das barras
                  animationDuration={500}
                >
                  {displayData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color || defaultColors[index % defaultColors.length]} 
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            {hiddenTeamsCount > 0 && (
              <div className={cn(
                "mt-2 text-xs text-center",
                isDark ? "text-slate-500" : "text-gray-500"
              )}>
                Mostrando top {maxTeamsToShow - 1} equipes. {hiddenTeamsCount} equipes menores agrupadas em "Outros"
                ({formatCurrency(hiddenTeamsValue)})
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
