import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import kpiService from '@/api/kpiService';
import { KPICategory } from '@/types/kpi.types';
import { toast } from '@/components/ui/use-toast';

export const useKPIs = (category?: KPICategory) => {
  const queryClient = useQueryClient();
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);

  // Query para KPIs por categoria
  const {
    data: categorizedKPIs,
    isLoading,
    error,
    refetch
  } = useQuery({
    queryKey: ['kpis', 'categorized'],
    queryFn: () => kpiService.getKPIsByCategory(),
    staleTime: 5 * 60 * 1000, // 5 minutos
    gcTime: 10 * 60 * 1000, // 10 minutos (anteriormente cacheTime)
  });

  // Query para histórico de KPI específico
  const {
    data: kpiHistory,
    isLoading: isLoadingHistory,
  } = useQuery({
    queryKey: ['kpi-history', selectedKPI],
    queryFn: () => selectedKPI ? kpiService.getKPIHistory(selectedKPI, 30) : null,
    enabled: !!selectedKPI,
  });

  // Mutation para atualizar configuração
  const updateConfig = useMutation({
    mutationFn: ({ kpiCode, config }: { kpiCode: string; config: any }) =>
      kpiService.updateKPIConfig(kpiCode, config),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['kpis'] });
      toast({
        title: 'Configuração atualizada',
        description: 'As metas do KPI foram atualizadas com sucesso.',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Erro ao atualizar',
        description: error.message || 'Ocorreu um erro ao atualizar a configuração.',
        variant: 'destructive',
      });
    },
  });

  // Mutation para recalcular KPIs
  const recalculate = useMutation({
    mutationFn: (date?: string) => kpiService.calculateKPIs(date),
    onSuccess: () => {
      toast({
        title: 'Recálculo iniciado',
        description: 'O recálculo dos KPIs foi iniciado em segundo plano.',
      });
      // Aguardar um pouco e recarregar
      setTimeout(() => {
        queryClient.invalidateQueries({ queryKey: ['kpis'] });
      }, 3000);
    },
  });

  // Filtrar por categoria se especificado
  const filteredData = category && categorizedKPIs
    ? categorizedKPIs.filter(cat => cat.category === category)
    : categorizedKPIs;

  // Calcular estatísticas gerais
  const overallStats = categorizedKPIs?.reduce((acc, cat) => {
    acc.total += cat.summary.total_kpis;
    acc.good += cat.summary.status_distribution.good;
    acc.warning += cat.summary.status_distribution.warning;
    acc.critical += cat.summary.status_distribution.critical;
    return acc;
  }, { total: 0, good: 0, warning: 0, critical: 0 });

  return {
    categorizedKPIs: filteredData,
    overallStats,
    isLoading,
    error,
    refetch,
    selectedKPI,
    setSelectedKPI,
    kpiHistory,
    isLoadingHistory,
    updateConfig: updateConfig.mutate,
    recalculate: recalculate.mutate,
    isUpdating: updateConfig.isPending,
    isRecalculating: recalculate.isPending,
  };
};