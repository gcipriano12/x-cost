import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { DateRange } from 'react-day-picker';
import { Download, Filter, Search, Users } from 'lucide-react';
import { useTeamCosts } from '@/hooks/useTeamCosts';
import { useXCostData } from '@/hooks/useXCostData';
import { SpendingTeamsCard } from '@/components/dashboard/SpendingTeamsCard';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

const TeamSpending = () => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // State para filtros
  const [timeFilter, setTimeFilter] = useState('30d');
  const [customDateRange, setCustomDateRange] = useState<DateRange | undefined>();
  const [selectedProvider, setSelectedProvider] = useState<string | undefined>(undefined);
  const [selectedEnvironment, setSelectedEnvironment] = useState<string | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Hook para credenciais ativas
  const { hasCredentials, activeCredential } = useXCostData({ 
    timeFilter,
    customStartDate: customDateRange?.from,
    customEndDate: customDateRange?.to,
    providerName: selectedProvider
  });
  
  // Hook para dados de team costs
  const {
    data: teamCostsData,
    isLoading: teamCostsLoading,
    error: teamCostsError
  } = useTeamCosts({
    timePeriod: customDateRange?.from && customDateRange?.to ? 'custom' : timeFilter,
    customStartDate: customDateRange?.from?.toISOString().split('T')[0],
    customEndDate: customDateRange?.to?.toISOString().split('T')[0],
    provider: selectedProvider,
    environment: selectedEnvironment,
    limit: 50, // Pegar todas as equipes disponíveis
    enabled: !!activeCredential?.id
  });
  
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
  
  // Transformar dados para o formato dos componentes
  const transformedTeamData = teamCostsData?.data?.map(team => ({
    name: team.team_name,
    value: team.total_cost,
    color: team.color || `#${Math.floor(Math.random()*16777215).toString(16)}`
  })) || [];
  
  // Filtrar dados baseado na busca
  const filteredTeamData = transformedTeamData.filter(team =>
    team.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Handlers para filtros
  const handleTimeFilterChange = (value: string) => {
    setTimeFilter(value);
    if (value !== 'custom') {
      setCustomDateRange(undefined);
    }
  };
  
  const handleExport = (format: 'csv' | 'pdf' | 'excel') => {
    // TODO: Implementar exportação
    console.log(`Exportando dados em formato ${format}`);
  };

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={Users} 
          title={t('teamSpending.title')}
          color="text-blue-600"
          showTimeFilter={false}
          actions={
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => handleExport('csv')}>
                <Download className="h-4 w-4 mr-2" />
                CSV
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport('excel')}>
                <Download className="h-4 w-4 mr-2" />
                Excel
              </Button>
              <Button variant="outline" size="sm" onClick={() => handleExport('pdf')}>
                <Download className="h-4 w-4 mr-2" />
                PDF
              </Button>
            </div>
          }
        />
        
        <div className="p-4 space-y-6">
      
      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Filter className="h-5 w-5" />
            {t('teamSpending.filters')}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            {/* Filtro de período */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('common.period')}</label>
              <Select value={timeFilter} onValueChange={handleTimeFilterChange}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7d">7 dias</SelectItem>
                  <SelectItem value="30d">30 dias</SelectItem>
                  <SelectItem value="90d">90 dias</SelectItem>
                  <SelectItem value="this-year">Este ano</SelectItem>
                  <SelectItem value="previous-year">Ano anterior</SelectItem>
                  <SelectItem value="custom">Personalizado</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Filtro de provedor */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('teamSpending.provider')}</label>
              <Select value={selectedProvider} onValueChange={setSelectedProvider}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os provedores" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="aws">AWS</SelectItem>
                  <SelectItem value="azure">Azure</SelectItem>
                  <SelectItem value="gcp">Google Cloud</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Filtro de ambiente */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('teamSpending.environment')}</label>
              <Select value={selectedEnvironment} onValueChange={setSelectedEnvironment}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os ambientes" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="production">Produção</SelectItem>
                  <SelectItem value="staging">Staging</SelectItem>
                  <SelectItem value="development">Desenvolvimento</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Busca por equipe */}
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('teamSpending.searchTeam')}</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Buscar equipe..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            {/* Limpar filtros */}
            <div className="space-y-2">
              <label className="text-sm font-medium opacity-0">Ações</label>
              <Button 
                variant="outline" 
                onClick={() => {
                  setSelectedProvider(undefined);
                  setSelectedEnvironment(undefined);
                  setSearchQuery('');
                }}
                className="w-full"
              >
                {t('teamSpending.clearFilters')}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Overview Cards - Temporariamente comentado */}
      {/* <TeamSpendingOverview 
        teamData={filteredTeamData}
        totalCost={teamCostsData?.total_cost || 0}
        isLoading={teamCostsLoading}
        currency="$"
      /> */}
      
      {/* Cards de resumo básicos */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total de Gastos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${(teamCostsData?.total_cost || 0).toLocaleString('pt-BR')}
            </div>
            <p className="text-xs text-muted-foreground">
              Gasto total de todas as equipes
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Equipes Ativas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredTeamData.length}</div>
            <p className="text-xs text-muted-foreground">
              Equipes com custos registrados
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Custo Médio</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${filteredTeamData.length > 0 ? 
                Math.round((teamCostsData?.total_cost || 0) / filteredTeamData.length).toLocaleString('pt-BR') : 
                '0'
              }
            </div>
            <p className="text-xs text-muted-foreground">
              Por equipe
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Top Equipe</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ${filteredTeamData.length > 0 ? 
                Math.max(...filteredTeamData.map(t => t.value)).toLocaleString('pt-BR') : 
                '0'
              }
            </div>
            <p className="text-xs text-muted-foreground">
              {filteredTeamData.length > 0 ? 
                filteredTeamData.reduce((prev, current) => prev.value > current.value ? prev : current).name :
                'Nenhuma equipe'
              }
            </p>
          </CardContent>
        </Card>
      </div>
      
      {/* Gráficos principais */}
      <div className="grid gap-6 md:grid-cols-1">
        {/* Gráfico de barras expandido */}
        <Card>
          <CardHeader>
            <CardTitle>{t('teamSpending.barChartTitle')}</CardTitle>
            <CardDescription>
              {t('teamSpending.barChartDescription')}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SpendingTeamsCard 
              categories={filteredTeamData}
              currency="$"
              maxTeamsToShow={20} // Mostrar mais equipes na página dedicada
            />
          </CardContent>
        </Card>
      </div>
      
      {/* Tabela básica */}
      <Card>
        <CardHeader>
          <CardTitle>Detalhamento por Equipe</CardTitle>
          <CardDescription>
            Lista completa com todos os dados de custos
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredTeamData.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">Nenhuma equipe encontrada</p>
            </div>
          ) : (
            <div className="rounded-md border">
              <div className="p-4">
                <div className="space-y-2">
                  {filteredTeamData.map((team, index) => (
                    <div key={team.name} className="flex items-center justify-between p-2 border rounded">
                      <div className="flex items-center gap-3">
                        <div 
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: team.color }}
                        />
                        <span className="font-medium">{team.name}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-mono">${team.value.toLocaleString('pt-BR')}</div>
                        <div className="text-xs text-muted-foreground">
                          {((team.value / (teamCostsData?.total_cost || 1)) * 100).toFixed(1)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
      
      {/* Insights básicos */}
      <Card>
        <CardHeader>
          <CardTitle>Insights e Recomendações</CardTitle>
          <CardDescription>
            Análises automáticas e sugestões de otimização
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {filteredTeamData.length > 0 ? (
              <>
                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="font-medium text-blue-900">Distribuição de Gastos</h3>
                  <p className="text-sm text-blue-700 mt-1">
                    Você tem {filteredTeamData.length} equipes ativas com um gasto total de ${(teamCostsData?.total_cost || 0).toLocaleString('pt-BR')}.
                  </p>
                </div>
                
                {filteredTeamData.length >= 3 && (
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h3 className="font-medium text-yellow-900">Oportunidade de Otimização</h3>
                    <p className="text-sm text-yellow-700 mt-1">
                      As 3 principais equipes concentram {
                        ((filteredTeamData.slice(0, 3).reduce((sum, team) => sum + team.value, 0) / (teamCostsData?.total_cost || 1)) * 100).toFixed(1)
                      }% dos custos. Considere revisar a alocação de recursos.
                    </p>
                  </div>
                )}
              </>
            ) : (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Nenhum insight disponível no momento</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
        </div>
      </div>
    </Dashboard>
  );
};

export default TeamSpending;
