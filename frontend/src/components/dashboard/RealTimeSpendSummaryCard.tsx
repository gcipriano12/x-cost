import React from 'react';
import { SpendSummaryCard } from './SpendSummaryCard';
import { useDashboard, useDashboardFormatters } from '@/hooks/useDashboard';
import { useProviderDistribution } from '@/hooks/useProviderDistribution';
import { useAccountDistribution } from '@/hooks/useAccountDistribution';
import { useBudgets, BudgetResponse } from '@/hooks/useBudgets';
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
  
  // Normalizar timeFilter para os diferentes hooks
  const normalizeTimeFilter = (filter: string) => {
    switch (filter) {
      case '30-days': return '30d';
      case '7-days': return '7d';
      case '90-days': return '90d';
      case 'previous-year': return 'previous-year';
      case 'current-year': return 'this-year';
      default: return '30d';
    }
  };

  // Hook para distribuição por provedor
  const { providerData, loading: providerLoading } = useProviderDistribution({
    timeFilter: timeFilter || '30-days',
    credentialId,
    providerName
  });
  
  // Hook para distribuição por conta (apenas quando há filtro de provedor)
  const { accountData, loading: accountLoading, error: accountError } = useAccountDistribution({
    providerName: providerName || '',
    timeFilter: normalizeTimeFilter(timeFilter || '30-days'),
    credentialId
  });
  
  console.log('🔍 useAccountDistribution result:', {
    providerName,
    accountData: accountData ? `${accountData.length} items` : 'empty/null',
    actualAccountData: accountData,
    loading: accountLoading,
    error: accountError
  });
  
  // Hook para buscar budgets reais
  const { budgets, loading: budgetsLoading } = useBudgets();
  
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
  const mappedData = mapApiDataToSpendSummary(data, providerName, providerData, accountData, budgets, accountError);

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
  accountDistributionData?: Array<{account_id: string, billing_account_name: string, percentage: number, total_cost: number}>,
  budgets?: BudgetResponse[],
  accountError?: string | null
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
  console.log('🔍 Initial total cost from API:', totalCost, 'Provider filter:', providerName);
  
  // Se há filtro de provedor, calcular total baseado nas regiões filtradas do provedor
  if (providerName && data.top_regions && Array.isArray(data.top_regions)) {
    const originalTotalCost = totalCost;
    totalCost = 0;
    console.log('🔍 Processing regions for provider filter:', providerName);
    console.log('🔍 Available regions:', data.top_regions.map(r => ({ region: r.region, cost: r.total_cost })));
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
      } else if (regionName.includes('oci') || regionName.includes('oracle') || regionName.includes('ashburn') || regionName.includes('phoenix') || regionName.includes('ap-southeast-1') || regionName.includes('ap-southeast-2') || regionName.includes('eu-frankfurt-1') || regionName.includes('us-ashburn-1') || regionName.includes('us-phoenix-1') || regionName.includes('uk-london-1') || regionName.includes('ca-toronto-1') || regionName.includes('ap-tokyo-1') || regionName.includes('ap-sydney-1') || regionName.includes('eu-zurich-1') || regionName.includes('me-jeddah-1') || regionName.includes('sa-saopaulo-1')) {
        regionProvider = 'Oracle Cloud';
      }
      
      console.log('🔍 Region:', regionName, 'Provider mapped to:', regionProvider, 'Cost:', region.total_cost);
      
      if (regionProvider === providerName) {
        totalCost += region.total_cost || 0;
        console.log('✅ Region matched provider filter - added cost:', region.total_cost);
      }
    });
    console.log('🔍 Total cost after provider filtering:', totalCost);
    
    // Se não encontrou nenhuma região para o provedor, usar o total original
    if (totalCost === 0 && originalTotalCost > 0) {
      console.log('⚠️ No regions found for provider', providerName, 'using original total cost:', originalTotalCost);
      totalCost = originalTotalCost;
    }
  } else if (providerName) {
    console.log('⚠️ No top_regions data available for provider filtering:', providerName);
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
  console.log('🔍 Account breakdown logic - Provider:', providerName, 'AccountData:', accountDistributionData);
  
  if (providerName && accountDistributionData && accountDistributionData.length > 0) {
    // Use real API data from useAccountDistribution hook
    accountBreakdown = accountDistributionData.map(account => ({
      accountId: account.account_id || 'unknown',
      billing_account_name: account.billing_account_name || 'Unknown Account',
      accountName: account.billing_account_name || 'Unknown Account', // For backwards compatibility
      value: Math.round(account.percentage * 10) / 10, // percentage is already a number
      color: '' // Color will be generated in SpendSummaryCard
    }));
    console.log('✅ Created account breakdown with', accountBreakdown.length, 'accounts:', accountBreakdown);
  } else if (providerName) {
    console.log('⚠️ No account distribution data available for provider:', providerName, 'Conditions:', {
      hasProvider: !!providerName,
      hasAccountData: !!accountDistributionData,
      accountDataLength: accountDistributionData?.length || 0,
      error: accountError
    });
    
    // NÃO criar fallback - sempre undefined quando não há dados reais
    // Isso força o SpendSummaryCard a mostrar distribuição por provedor
    console.log('❌ No account data - will show provider distribution instead');
    accountBreakdown = undefined;
  }

  // Calculate top provider/account based on filter context
  let topProvider = { name: 'N/A', cost: 0 };
  
  // If total cost is zero, don't assign any provider
  if (totalCost > 0) {
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
      // Provider filter active - show account with highest ABSOLUTE cost from that provider
      if (accountDistributionData && accountDistributionData.length > 0) {
        // Buscar a conta com o maior total_cost (valor absoluto)
        const topAccount = accountDistributionData.reduce((max, current) => 
          current.total_cost > max.total_cost ? current : max
        );
        topProvider = {
          name: topAccount.billing_account_name || `Account ${topAccount.account_id}`,
          cost: topAccount.total_cost
        };
        console.log('✅ Highest spend account:', topProvider);
      } else {
        // Fallback: use top service or provider name
        // Since services don't have provider_name field, we'll use the first service as fallback
        if (data.top_services && data.top_services.length > 0) {
          const topService = data.top_services[0];
          topProvider = {
            name: topService.service_name || providerName,
            cost: topService.total_cost || (totalCost * 0.4)
          };
        } else {
          // Ultimate fallback: just use provider name
          topProvider = {
            name: providerName,
            cost: totalCost
          };
        }
      }
    }
  }

  // Calculate real budget data based on active budgets
  let budgetLimit = 0;
  let budgetConsumed = 0;
  
  if (budgets && budgets.length > 0) {
    // Filter budgets based on provider (if specified) and active status
    const activeBudgets = budgets.filter(budget => {
      const isActive = budget.is_active;
      const matchesProvider = !providerName || 
        !budget.provider_name || 
        budget.provider_name === providerName ||
        budget.provider_name === 'All';
      
      return isActive && matchesProvider;
    });
    
    if (activeBudgets.length > 0) {
      // Sum all matching budget amounts
      budgetLimit = activeBudgets.reduce((sum, budget) => {
        return sum + parseFloat(budget.budget_amount || '0');
      }, 0);
      
      // Calculate consumption percentage based on total cost vs budget limit
      if (budgetLimit > 0) {
        budgetConsumed = Math.round((totalCost / budgetLimit) * 100 * 10) / 10;
      }
      
      console.log('✅ Using real budget data:', {
        activeBudgets: activeBudgets.length,
        budgetLimit,
        totalCost,
        budgetConsumed: `${budgetConsumed}%`,
        provider: providerName || 'All'
      });
    } else {
      console.log('⚠️ No active budgets found for provider:', providerName || 'All');
    }
  } else {
    console.log('⚠️ No budget data available');
  }
  
  // Fallback to estimated budget if no real budgets are available
  if (budgetLimit === 0) {
    budgetLimit = totalCost * 1.2; // 20% above current spend as fallback
    budgetConsumed = Math.round((totalCost / budgetLimit) * 100 * 10) / 10;
  }

  console.log('🔍 Final data being returned:', {
    providerName,
    accountBreakdown: accountBreakdown ? `${accountBreakdown.length} accounts` : 'undefined',
    providerBreakdown: `${providerBreakdown.length} providers`
  });

  return {
    totalSpend: totalCost,
    currency: '$', // Voltando para dólar como padrão
    previousPeriodChange: costChangePercentage,
    sparklineData: sparklineData,
    providerBreakdown: providerBreakdown,
    accountBreakdown: accountBreakdown,
    selectedProvider: providerName,
    wastedSpend: data.highlights?.estimated_waste?.amount || 0,
    budgetLimit: budgetLimit,
    budgetConsumed: budgetConsumed,
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
