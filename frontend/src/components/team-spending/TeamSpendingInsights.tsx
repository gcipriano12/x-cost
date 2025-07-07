import React from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Lightbulb, 
  TrendingUp, 
  AlertTriangle, 
  Target,
  DollarSign,
  Users
} from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface SpendingTeam {
  name: string;
  value: number;
  color: string;
}

interface TeamSpendingInsightsProps {
  teamData: SpendingTeam[];
  totalCost: number;
  isLoading: boolean;
}

interface Insight {
  id: string;
  type: 'optimization' | 'alert' | 'recommendation';
  title: string;
  description: string;
  impact: 'high' | 'medium' | 'low';
  actionable: boolean;
  data?: any;
}

export const TeamSpendingInsights: React.FC<TeamSpendingInsightsProps> = ({
  teamData,
  totalCost,
  isLoading
}) => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Formatador de moeda
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
  
  // Gerar insights baseado nos dados
  const generateInsights = (): Insight[] => {
    if (teamData.length === 0) return [];
    
    const insights: Insight[] = [];
    const sortedTeams = [...teamData].sort((a, b) => b.value - a.value);
    
    // Insight 1: Concentração de gastos
    if (sortedTeams.length >= 3) {
      const top3Percentage = (sortedTeams.slice(0, 3).reduce((sum, team) => sum + team.value, 0) / totalCost) * 100;
      
      if (top3Percentage > 70) {
        insights.push({
          id: 'concentration',
          type: 'alert',
          title: t('teamSpending.insights.highConcentration.title'),
          description: t('teamSpending.insights.highConcentration.description', { 
            percentage: top3Percentage.toFixed(1),
            teams: sortedTeams.slice(0, 3).map(t => t.name).join(', ')
          }),
          impact: 'high',
          actionable: true,
          data: { percentage: top3Percentage, teams: sortedTeams.slice(0, 3) }
        });
      }
    }
    
    // Insight 2: Equipe com gasto desproporcional
    if (sortedTeams.length >= 2) {
      const topTeam = sortedTeams[0];
      const secondTeam = sortedTeams[1];
      const ratio = topTeam.value / secondTeam.value;
      
      if (ratio > 3) {
        insights.push({
          id: 'disproportional',
          type: 'recommendation',
          title: t('teamSpending.insights.disproportional.title'),
          description: t('teamSpending.insights.disproportional.description', {
            team: topTeam.name,
            amount: formatCurrency(topTeam.value),
            ratio: ratio.toFixed(1)
          }),
          impact: 'medium',
          actionable: true,
          data: { team: topTeam, ratio }
        });
      }
    }
    
    // Insight 3: Oportunidade de otimização
    const averageCost = totalCost / teamData.length;
    const teamsAboveAverage = teamData.filter(team => team.value > averageCost * 1.5);
    
    if (teamsAboveAverage.length > 0) {
      const potentialSavings = teamsAboveAverage.reduce((sum, team) => 
        sum + (team.value - averageCost), 0
      ) * 0.15; // Estimativa de 15% de economia possível
      
      insights.push({
        id: 'optimization',
        type: 'optimization',
        title: t('teamSpending.insights.optimization.title'),
        description: t('teamSpending.insights.optimization.description', {
          count: teamsAboveAverage.length,
          savings: formatCurrency(potentialSavings)
        }),
        impact: 'medium',
        actionable: true,
        data: { teams: teamsAboveAverage, potentialSavings }
      });
    }
    
    // Insight 4: Distribuição equilibrada
    if (teamData.length >= 5) {
      const coefficientOfVariation = calculateCoefficientOfVariation(teamData.map(t => t.value));
      
      if (coefficientOfVariation < 0.5) {
        insights.push({
          id: 'balanced',
          type: 'recommendation',
          title: t('teamSpending.insights.balanced.title'),
          description: t('teamSpending.insights.balanced.description'),
          impact: 'low',
          actionable: false,
          data: { cv: coefficientOfVariation }
        });
      }
    }
    
    return insights;
  };
  
  // Calcular coeficiente de variação
  const calculateCoefficientOfVariation = (values: number[]): number => {
    const mean = values.reduce((sum, val) => sum + val, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    const standardDeviation = Math.sqrt(variance);
    return standardDeviation / mean;
  };
  
  const insights = generateInsights();
  
  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'optimization':
        return <DollarSign className="h-5 w-5 text-green-600" />;
      case 'alert':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'recommendation':
        return <Lightbulb className="h-5 w-5 text-blue-600" />;
      default:
        return <Target className="h-5 w-5 text-purple-600" />;
    }
  };
  
  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };
  
  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="h-6 bg-gray-200 rounded animate-pulse" />
          <div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="p-4 border rounded-lg">
                <div className="h-5 bg-gray-200 rounded animate-pulse mb-2" />
                <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-yellow-600" />
          {t('teamSpending.insights.title')}
        </CardTitle>
        <CardDescription>
          {t('teamSpending.insights.description')}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {insights.length === 0 ? (
          <div className="text-center py-8">
            <Users className={cn(
              "h-12 w-12 mx-auto mb-3",
              isDark ? "text-slate-600" : "text-gray-400"
            )} />
            <p className={cn(
              "text-sm",
              isDark ? "text-slate-500" : "text-gray-500"
            )}>
              {t('teamSpending.insights.noInsights')}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {insights.map((insight) => (
              <div 
                key={insight.id}
                className={cn(
                  "p-4 rounded-lg border transition-colors",
                  isDark ? "bg-slate-800/50 border-slate-700" : "bg-gray-50/50 border-gray-200"
                )}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      {getInsightIcon(insight.type)}
                      <h3 className="font-medium">{insight.title}</h3>
                      <Badge variant={getImpactColor(insight.impact)} className="text-xs">
                        {t(`teamSpending.insights.impact.${insight.impact}`)}
                      </Badge>
                    </div>
                    <p className={cn(
                      "text-sm mb-3",
                      isDark ? "text-slate-300" : "text-gray-600"
                    )}>
                      {insight.description}
                    </p>
                    {insight.actionable && (
                      <Button size="sm" variant="outline">
                        {t('teamSpending.insights.takeAction')}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
