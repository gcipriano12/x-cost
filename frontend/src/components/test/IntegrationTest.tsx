import React, { useEffect, useState } from 'react';
import { useDashboard } from '@/hooks/useDashboard';
import { useXCostData } from '@/hooks/useXCostData';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

interface IntegrationTestProps {
  timeFilter: string;
}

export function IntegrationTest({ timeFilter }: IntegrationTestProps) {
  const [callCount, setCallCount] = useState(0);
  const [lastCallTime, setLastCallTime] = useState<Date | null>(null);
  
  // Test useDashboard hook
  const {
    data: dashboardData,
    loading: dashboardLoading,
    error: dashboardError,
    refetch: dashboardRefetch,
    lastUpdated: dashboardLastUpdated
  } = useDashboard({ 
    timeFilter, 
    autoRefresh: false // Desabilitar auto-refresh para teste
  });

  // Test useXCostData hook
  const {
    loading: xcostLoading,
    error: xcostError,
    spendSummary,
    hasCredentials
  } = useXCostData({ timeFilter });

  // Rastrear chamadas
  useEffect(() => {
    if (dashboardLoading || xcostLoading) {
      setCallCount(prev => prev + 1);
      setLastCallTime(new Date());
    }
  }, [dashboardLoading, xcostLoading]);

  const getStatusIcon = (loading: boolean, error: string | null, data: any) => {
    if (loading) return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
    if (error) return <XCircle className="h-4 w-4 text-red-500" />;
    if (data) return <CheckCircle className="h-4 w-4 text-green-500" />;
    return <Clock className="h-4 w-4 text-gray-500" />;
  };

  const formatTime = (date: Date | null) => {
    return date ? date.toLocaleTimeString() : 'Nunca';
  };

  return (
    <Card className="w-full max-w-4xl mx-auto">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5" />
          Teste de Integração - Dashboard & API
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Estatísticas Gerais */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium text-sm text-gray-600">Total de Chamadas</h3>
            <p className="text-2xl font-bold">{callCount}</p>
          </div>
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium text-sm text-gray-600">Última Chamada</h3>
            <p className="text-sm">{formatTime(lastCallTime)}</p>
          </div>
          <div className="p-4 border rounded-lg">
            <h3 className="font-medium text-sm text-gray-600">TimeFilter Atual</h3>
            <p className="text-lg font-semibold">{timeFilter}</p>
          </div>
        </div>

        {/* Status dos Hooks */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* useDashboard Status */}
          <div className="p-4 border rounded-lg space-y-3">
            <div className="flex items-center gap-2">
              {getStatusIcon(dashboardLoading, dashboardError, dashboardData)}
              <h3 className="font-medium">useDashboard Hook</h3>
            </div>
            <div className="space-y-2 text-sm">
              <p><strong>Loading:</strong> {dashboardLoading ? 'Sim' : 'Não'}</p>
              <p><strong>Error:</strong> {dashboardError || 'Nenhum'}</p>
              <p><strong>Dados:</strong> {dashboardData ? 'Carregados' : 'Não carregados'}</p>
              <p><strong>Última Atualização:</strong> {formatTime(dashboardLastUpdated)}</p>
              {dashboardData && (
                <p><strong>Total Cost:</strong> R$ {dashboardData.metrics.total_cost.toLocaleString()}</p>
              )}
            </div>
            <Button 
              onClick={() => dashboardRefetch()} 
              size="sm" 
              variant="outline"
              disabled={dashboardLoading}
            >
              <RefreshCw className="h-3 w-3 mr-1" />
              Refetch
            </Button>
          </div>

          {/* useXCostData Status */}
          <div className="p-4 border rounded-lg space-y-3">
            <div className="flex items-center gap-2">
              {getStatusIcon(xcostLoading, xcostError, spendSummary)}
              <h3 className="font-medium">useXCostData Hook</h3>
            </div>
            <div className="space-y-2 text-sm">
              <p><strong>Loading:</strong> {xcostLoading ? 'Sim' : 'Não'}</p>
              <p><strong>Error:</strong> {xcostError || 'Nenhum'}</p>
              <p><strong>Has Credentials:</strong> {hasCredentials ? 'Sim' : 'Não'}</p>
              <p><strong>Spend Summary:</strong> {spendSummary ? 'Carregado' : 'Não carregado'}</p>
              {spendSummary && (
                <p><strong>Total Spend:</strong> R$ {spendSummary.totalSpend.toLocaleString()}</p>
              )}
            </div>
          </div>
        </div>

        {/* Análise de Performance */}
        <div className="p-4 border rounded-lg bg-gray-50">
          <h3 className="font-medium mb-2">Análise de Performance</h3>
          <div className="space-y-1 text-sm">
            <p className={callCount > 5 ? "text-red-600" : "text-green-600"}>
              <strong>Status:</strong> {callCount > 5 ? "⚠️ Muitas chamadas detectadas" : "✅ Performance OK"}
            </p>
            <p className="text-gray-600">
              <strong>Recomendação:</strong> {callCount > 5 ? "Verificar otimizações" : "Sistema funcionando corretamente"}
            </p>
          </div>
        </div>

        {/* Reset Button */}
        <div className="flex justify-center">
          <Button 
            onClick={() => {
              setCallCount(0);
              setLastCallTime(null);
            }} 
            variant="outline"
          >
            Reset Contador
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
