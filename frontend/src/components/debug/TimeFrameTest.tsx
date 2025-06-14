import React from 'react';
import { useXCostData } from '@/hooks/useXCostData';
import { useDashboard } from '@/hooks/useDashboard';
import { timeFilterToDays } from '@/utils/timeFrame';

interface TimeFrameTestProps {
  timeFilter: string;
}

export function TimeFrameTest({ timeFilter }: TimeFrameTestProps) {
  const days = timeFilterToDays(timeFilter);
  
  // Teste do hook useXCostData
  const {
    loading: xcostLoading,
    error: xcostError,
    spendSummary,
    hasCredentials
  } = useXCostData({ timeFilter });

  // Teste do hook useDashboard
  const {
    data: dashboardData,
    loading: dashboardLoading,
    error: dashboardError
  } = useDashboard({ timeFilter, autoRefresh: false });

  return (
    <div className="p-4 border rounded-lg space-y-4">
      <h3 className="text-lg font-semibold">TimeFrame Test</h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <h4 className="font-medium">Configuração</h4>
          <p><strong>TimeFilter:</strong> {timeFilter}</p>
          <p><strong>Dias calculados:</strong> {days}</p>
          <p><strong>Has Credentials:</strong> {hasCredentials ? 'Sim' : 'Não'}</p>
        </div>

        <div className="space-y-2">
          <h4 className="font-medium">Status dos Hooks</h4>
          <p><strong>XCost Loading:</strong> {xcostLoading ? 'Sim' : 'Não'}</p>
          <p><strong>XCost Error:</strong> {xcostError || 'Nenhum'}</p>
          <p><strong>Dashboard Loading:</strong> {dashboardLoading ? 'Sim' : 'Não'}</p>
          <p><strong>Dashboard Error:</strong> {dashboardError || 'Nenhum'}</p>
        </div>
      </div>

      <div className="space-y-2">
        <h4 className="font-medium">Dados Carregados</h4>
        <p><strong>Spend Summary:</strong> {spendSummary ? `R$ ${spendSummary.totalSpend.toLocaleString()}` : 'Não carregado'}</p>
        <p><strong>Dashboard Data:</strong> {dashboardData ? `R$ ${dashboardData.metrics.total_cost.toLocaleString()}` : 'Não carregado'}</p>
      </div>

      <div className="text-xs text-gray-500">
        <p>Este componente mostra se o timeFilter está sendo corretamente convertido em dias e passado para as APIs</p>
      </div>
    </div>
  );
}
