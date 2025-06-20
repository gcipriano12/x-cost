import React from 'react';
import { SpendSummaryCard } from './SpendSummaryCard';
import { useDashboard, useDashboardFormatters } from '@/hooks/useDashboard';
import { useProviderDistribution } from '@/hooks/useProviderDistribution';
import { useAccountDistribution } from '@/hooks/useAccountDistribution';
import { DashboardSummary } from '@/types/api';
import { Card, CardContent } from '@/components/ui/card';
import { AlertCircle, RefreshCw, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useTranslation } from 'react-i18next';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { getProviderColor } from '@/utils/providerColors';

// Função generateMockAccountBreakdown removida - agora usamos apenas dados reais da API

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
  
  // Hook para distribuição por provedor
  const { providerData, loading: providerLoading } = useProviderDistribution({
    timeFilter: timeFilter || '30-days',
    credentialId,
    providerName
  });
  
  // Hook para distribuição por conta (apenas quando há filtro de provedor)
  const { accountData, loading: accountLoading, error: accountError } = useAccountDistribution({
    providerName: providerName || '',
    timeFilter: timeFilter || '30d',
    credentialId
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
  const mappedData = mapApiDataToSpendSummary(data, providerName, providerData, accountData);

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
        accountBreakdown={mappedData.accountBreakdown}
        selectedProvider={mappedData.selectedProvider}
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
function mapApiDataToSpendSummary(
  data: DashboardSummary, 
  providerName?: string, 
  providerBreakdownData?: Array<{name: string, value: number, color: string}>,
  accountDistributionData?: Array<{account_id: string, billing_account_name: string, percentage: number, total_cost: number}>
) {
  // Verificar se data e metrics existem
  if (!data) {
    console.warn('mapApiDataToSpendSummary: data is null or undefined');
    return {
      totalSpend: 0,
      currency: '$',
      previousPeriodChange: 0,
      sparklineData: [0, 0, 0, 0, 0, 0],
      providerBreakdown: [],
      accountBreakdown: undefined,
      selectedProvider: providerName,
      wastedSpend: 0,
      budgetLimit: 0,
      budgetConsumed: 0,
      savingsRealized: 0,
      topService: { name: 'N/A', provider: 'N/A', cost: 0 },
      topProvider: { name: 'N/A', cost: 0 },
      monthlyAverage: 0,
      annualProjection: 0,
      nextMonthForecast: { amount: 0, change_percentage: 0 }
    };
  }

  // Verificar se cost_summary existe, senão usar valores padrão
  if (!data.cost_summary) {
    console.warn('mapApiDataToSpendSummary: data.cost_summary is undefined or null');
  }

  // Calcular total cost baseado no filtro de provedor
  let totalCost = data.cost_summary?.totals?.total_cost || 0;
  
  // Se há filtro de provedor, calcular total baseado nas regiões filtradas do provedor
  if (providerName && data.top_regions && Array.isArray(data.top_regions)) {
    totalCost = 0;
    data.top_regions.forEach(region => {
      const regionName = region.region?.toLowerCase() || '';
      let regionProvider = 'Unknown';
      
      // Usar a mesma lógica de mapeamento
      if (regionName.includes('us-') || regionName.includes('eu-') || regionName.startsWith('ap-') || regionName.includes('ca-') || regionName.includes('sa-')) {
        regionProvider = 'AWS';
      } else if (regionName.includes('east us') || regionName.includes('west us') || regionName.includes('west europe') || regionName.includes('north europe') || regionName.includes('central us')) {
        regionProvider = 'Azure';
      } else if (regionName.includes('central1') || regionName.includes('west1') || regionName.includes('east1') || regionName.includes('europe-west') || regionName.includes('asia-') || regionName.includes('australia-')) {
        regionProvider = 'GCP';
      } else if (regionName.includes('ap-southeast-1') || regionName.includes('oci') || regionName.includes('oracle') || regionName.includes('ashburn') || regionName.includes('phoenix')) {
        regionProvider = 'Oracle Cloud';
      }
      
      if (regionProvider === providerName) {
        totalCost += region.total_cost || 0;
      }
    });
  }
  
  const averageCost = data.cost_summary?.totals?.average_cost || 0;
  const recordCount = data.cost_summary?.totals?.record_count || 0;
  
  // Calcular métricas derivadas
  const costChangePercentage = 0; // TODO: Implementar cálculo de mudança percentual
  const monthlyAverage = averageCost * recordCount; // Estimativa baseada na média
  const annualProjection = totalCost * 12; // Projeção simples

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

  // Usar distribuição por provedor do hook em vez de calcular baseado em regiões
  const providerBreakdown = providerBreakdownData || [];

  // Use real account distribution data from dedicated hook
  let accountBreakdown = undefined;
  if (providerName && accountDistributionData && accountDistributionData.length > 0) {
    // Use real API data from useAccountDistribution hook
    accountBreakdown = accountDistributionData.map(account => ({
      accountId: account.account_id || 'unknown',
      billing_account_name: account.billing_account_name || 'Unknown Account',
      accountName: account.billing_account_name || 'Unknown Account', // For backwards compatibility
      value: Math.round(account.percentage * 10) / 10, // percentage is already a number
      color: '' // Color will be generated in SpendSummaryCard
    }));
    console.log('✅ Using real account distribution data:', accountBreakdown);
  } else if (providerName) {
    console.log('⚠️ No account distribution data available for provider:', providerName);
  }

  // Calculate top provider/account based on filter context
  let topProvider = { name: 'N/A', cost: 0 };
  
  if (!providerName) {
    // No provider filter - show top provider from breakdown
    if (providerBreakdownData && providerBreakdownData.length > 0) {
      const topProviderItem = providerBreakdownData.reduce((max, current) => 
        current.value > max.value ? current : max
      );
      topProvider = {
        name: topProviderItem.name,
        cost: (topProviderItem.value / 100) * totalCost // value is percentage
      };
    }
  } else {
    // Provider filter active - show top account from that provider
    if (accountBreakdown && accountBreakdown.length > 0) {
      const topAccount = accountBreakdown.reduce((max, current) => 
        current.value > max.value ? current : max
      );
      topProvider = {
        name: topAccount.billing_account_name || topAccount.accountName || topAccount.accountId,
        cost: (topAccount.value / 100) * totalCost // value is percentage
      };
    } else {
      // Fallback: use top service from that provider
      topProvider = {
        name: data.top_services?.[0]?.service_name || providerName,
        cost: data.top_services?.[0]?.total_cost || (totalCost * 0.4)
      };
    }
  }

  return {
    totalSpend: totalCost,
    currency: '$', // Voltando para dólar como padrão
    previousPeriodChange: costChangePercentage,
    sparklineData: sparklineData,
    providerBreakdown: providerBreakdown,
    accountBreakdown: accountBreakdown,
    selectedProvider: providerName,
    wastedSpend: data.highlights?.estimated_waste?.amount || 0,
    budgetLimit: data.budget_summary?.total_budget_amount || totalCost * 1.2,
    budgetConsumed: data.budget_summary?.active_budgets ? 
      Math.round((data.budget_summary.active_budgets / data.budget_summary.total_budgets) * 100 * 10) / 10 : 75,
    savingsRealized: data.highlights?.savings_achieved?.amount || 0,
    // Dados adicionais para enriquecer o SpendSummaryCard
    topService: {
      name: data.top_services?.[0]?.service_name || 'EC2',
      provider: providerName || data.top_services?.[0]?.category || 'AWS',
      cost: data.top_services?.[0]?.total_cost || (totalCost * 0.25) // 25% do total como fallback
    },
    topProvider: topProvider, // Novo campo com o provedor com maior gasto total
    monthlyAverage: monthlyAverage,
    annualProjection: annualProjection,
    nextMonthForecast: data.highlights?.next_month_forecast || { amount: 0, change_percentage: 0 }
  };
}
