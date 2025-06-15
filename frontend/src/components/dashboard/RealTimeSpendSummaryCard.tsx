import React from 'react';
import { SpendSummaryCard } from './SpendSummaryCard';
import { useDashboard, useDashboardFormatters } from '@/hooks/useDashboard';
import { DashboardSummary } from '@/types/api';
import { Card, CardContent } from '@/components/ui/card';
import { AlertCircle, RefreshCw, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { getProviderColor } from '@/utils/providerColors';

interface RealTimeSpendSummaryCardProps {
  periodDays?: number;
  timeFilter?: string; // Adicionar suporte ao timeFilter
  credentialId?: string;
  providerName?: string; // Adicionar suporte ao filtro de provedor
}

export function RealTimeSpendSummaryCard({ 
  periodDays = 30,
  timeFilter, 
  credentialId,
  providerName
}: RealTimeSpendSummaryCardProps) {
  const { data, loading, error, refetch, lastUpdated } = useDashboard({
    periodDays,
    timeFilter, // Passar timeFilter para o hook
    credentialId,
    providerName, // Passar providerName para o hook
    autoRefresh: false, // Desabilitar auto-refresh automático
    refreshInterval: 5 * 60 * 1000 // 5 minutos (não usado quando autoRefresh = false)
  });
  const { formatRelativeTime, formatUpdatedTime } = useDashboardFormatters();
  const { t } = useTranslation();
  const { isDark } = useTheme();

  // Loading state - só mostrar se não há dados E está carregando
  if (loading && !data) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-[400px]">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <p className="text-sm text-muted-foreground">{t('common.loadingDashboardData')}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error && !data) {
    return (
      <Card className="h-full">
        <CardContent className="flex flex-col items-center justify-center h-[400px] space-y-4">
          <AlertCircle className="h-12 w-12 text-destructive" />
          <div className="text-center space-y-2">
            <h3 className="font-semibold">Erro ao carregar dados</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button onClick={refetch} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Tentar novamente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Se não há dados, mostrar estado vazio
  if (!data) {
    return (
      <Card className="h-full">
        <CardContent className="flex items-center justify-center h-[400px]">
          <p className="text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  // Mapear dados da API para o formato esperado pelo SpendSummaryCard
  const mappedData = mapApiDataToSpendSummary(data);

  return (
    <div className="space-y-2">
      {/* Indicador de última atualização - só mostrar se há dados */}
      {lastUpdated && data && (
        <div className="flex items-center justify-between">
          <div className="flex items-center text-xs text-muted-foreground">
            <Clock className="h-3 w-3 mr-1" />
            {formatUpdatedTime(lastUpdated)}
          </div>
          {/* Só mostrar "Atualizando..." durante carregamentos explícitos */}
          {loading && (
            <div className="flex items-center text-xs text-muted-foreground">
              <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
              {t('common.updating')}
            </div>
          )}
        </div>
      )}
      
      {/* Card principal com dados reais */}
      <SpendSummaryCard
        totalSpend={mappedData.totalSpend}
        currency={mappedData.currency}
        previousPeriodChange={mappedData.previousPeriodChange}
        sparklineData={mappedData.sparklineData}
        providerBreakdown={mappedData.providerBreakdown}
        wastedSpend={mappedData.wastedSpend}
        budgetLimit={mappedData.budgetLimit}
        budgetConsumed={mappedData.budgetConsumed}
        savingsRealized={mappedData.savingsRealized}
        topService={mappedData.topService}
        topProvider={mappedData.topProvider}
        monthlyAverage={mappedData.monthlyAverage}
        annualProjection={mappedData.annualProjection}
        nextMonthForecast={mappedData.nextMonthForecast}
      />
    </div>
  );
}

// Função para mapear dados da API para o formato do SpendSummaryCard
function mapApiDataToSpendSummary(data: DashboardSummary) {
  // Converter strings para números
  const totalCost = parseFloat(data.metrics.total_cost);
  const costChangePercentage = parseFloat(data.metrics.cost_change_percentage);
  const monthlyAverage = parseFloat(data.metrics.monthly_average);
  const annualProjection = parseFloat(data.metrics.annual_projection);

  // Calcular sparkline baseado nos dados históricos (simulado)
  const baseValue = totalCost;
  const changePercent = costChangePercentage / 100;
  const sparklineData = [
    baseValue * (1 - changePercent * 1.5),
    baseValue * (1 - changePercent * 1.2),
    baseValue * (1 - changePercent * 0.8),
    baseValue * (1 - changePercent * 0.5),
    baseValue * (1 - changePercent * 0.2),
    baseValue
  ];

  // Map provider breakdown data
  const providerBreakdown = data.provider_distribution.map(provider => ({
    name: provider.provider_name,
    value: Math.round(parseFloat(provider.percentage) * 10) / 10, // Arredondar para 1 casa decimal
    color: getProviderColor(provider.provider_name)
  }));

  // Calculate top provider based on total cost - com verificação de array vazio
  const topProviderData = data.provider_distribution.length > 0 
    ? data.provider_distribution.reduce((top, current) => {
        const currentCost = (parseFloat(current.percentage) / 100) * totalCost;
        const topCost = (parseFloat(top.percentage) / 100) * totalCost;
        return currentCost > topCost ? current : top;
      })
    : null;

  const topProvider = topProviderData ? {
    name: topProviderData.provider_name,
    cost: (parseFloat(topProviderData.percentage) / 100) * totalCost
  } : {
    name: 'N/A',
    cost: 0
  };

  return {
    totalSpend: totalCost,
    currency: '$', // Voltando para dólar como padrão
    previousPeriodChange: costChangePercentage,
    sparklineData: sparklineData,
    providerBreakdown: providerBreakdown,
    wastedSpend: data.highlights.estimated_waste.amount,
    budgetLimit: data.metrics.budget_consumption?.total_budget || totalCost * 1.2,
    budgetConsumed: data.metrics.budget_consumption?.consumption_percentage || 75,
    savingsRealized: data.highlights.savings_achieved.amount,
    // Dados adicionais para enriquecer o SpendSummaryCard
    topService: {
      name: data.metrics.top_service.service_name,
      provider: data.metrics.top_service.provider_name,
      cost: data.metrics.top_service.total_cost
    },
    topProvider: topProvider, // Novo campo com o provedor com maior gasto total
    monthlyAverage: monthlyAverage,
    annualProjection: annualProjection,
    nextMonthForecast: data.highlights.next_month_forecast
  };
}
