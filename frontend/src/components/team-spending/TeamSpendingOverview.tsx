import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Users, DollarSign, TrendingUp, TrendingDown, Target } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface SpendingTeam {
  name: string;
  value: number;
  color: string;
}

interface TeamSpendingOverviewProps {
  teamData: SpendingTeam[];
  totalCost: number;
  isLoading: boolean;
  currency: string;
}

export const TeamSpendingOverview: React.FC<TeamSpendingOverviewProps> = ({
  teamData,
  totalCost,
  isLoading,
  currency
}) => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Formatador de moeda
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toLocaleString('pt-BR', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
      })}M`;
    } else if (value >= 1000) {
      return `${currency}${(value / 1000).toLocaleString('pt-BR', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      })}K`;
    }
    return `${currency}${value.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };
  
  // Calcular estatísticas
  const activeTeamsCount = teamData.length;
  const averageCostPerTeam = activeTeamsCount > 0 ? totalCost / activeTeamsCount : 0;
  const topTeam = teamData.length > 0 ? teamData.reduce((prev, current) => 
    prev.value > current.value ? prev : current
  ) : null;
  
  // Simular crescimento (TODO: implementar cálculo real com dados históricos)
  const mockGrowth = 12.5; // 12.5% de crescimento
  const isGrowthPositive = mockGrowth > 0;
  
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded animate-pulse mb-2" />
              <div className="h-3 bg-gray-200 rounded animate-pulse w-2/3" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {/* Total de Gastos */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-green-600" />
            {t('teamSpending.overview.totalSpend')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(totalCost)}</div>
          <div className="flex items-center text-sm text-muted-foreground">
            {isGrowthPositive ? (
              <TrendingUp className="h-3 w-3 text-green-500 mr-1" />
            ) : (
              <TrendingDown className="h-3 w-3 text-red-500 mr-1" />
            )}
            <span className={cn(
              "font-medium",
              isGrowthPositive ? "text-green-600" : "text-red-600"
            )}>
              {Math.abs(mockGrowth)}%
            </span>
            <span className="ml-1">vs período anterior</span>
          </div>
        </CardContent>
      </Card>
      
      {/* Número de Equipes Ativas */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Users className="h-4 w-4 text-blue-600" />
            {t('teamSpending.overview.activeTeams')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{activeTeamsCount}</div>
          <div className="text-sm text-muted-foreground">
            {t('teamSpending.overview.teamsWithCosts')}
          </div>
        </CardContent>
      </Card>
      
      {/* Custo Médio por Equipe */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Target className="h-4 w-4 text-purple-600" />
            {t('teamSpending.overview.averageCost')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{formatCurrency(averageCostPerTeam)}</div>
          <div className="text-sm text-muted-foreground">
            {t('teamSpending.overview.perTeam')}
          </div>
        </CardContent>
      </Card>
      
      {/* Top Equipe */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-orange-600" />
            {t('teamSpending.overview.topTeam')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {topTeam ? (
            <>
              <div className="text-2xl font-bold">{formatCurrency(topTeam.value)}</div>
              <div className="flex items-center gap-2">
                <Badge 
                  variant="secondary" 
                  className="text-xs"
                  style={{ backgroundColor: topTeam.color + '20', color: topTeam.color }}
                >
                  {topTeam.name}
                </Badge>
              </div>
            </>
          ) : (
            <div className="text-sm text-muted-foreground">
              {t('teamSpending.overview.noData')}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
