# Frontend - Implementação da Visualização de KPIs

## 📋 Visão Geral

Implementar componentes React para exibição e gerenciamento dos KPIs no dashboard X Cost.

## 🏗️ Arquitetura de Componentes

```
src/
├── components/
│   ├── kpi/
│   │   ├── KPICard.tsx              # Card individual de KPI
│   │   ├── KPICategorySection.tsx   # Seção por categoria
│   │   ├── KPIIndicators.tsx        # Container principal
│   │   ├── KPIDetailModal.tsx       # Modal com detalhes
│   │   └── KPIConfigModal.tsx       # Modal de configuração
├── hooks/
│   └── useKPIs.ts                   # Hook para dados de KPIs
├── api/
│   └── kpiService.ts                # Serviço de API
└── types/
    └── kpi.types.ts                 # Tipos TypeScript
```

## 📝 Tipos TypeScript

### types/kpi.types.ts

```typescript
// Enums para categorias
export enum KPICategory {
  EFFICIENCY = 'efficiency',
  PRICING = 'pricing',
  PLANNING = 'planning',
  GOVERNANCE = 'governance'
}

// Status do KPI
export type KPIStatus = 'good' | 'warning' | 'critical' | 'neutral';

// Interface principal do KPI
export interface KPIValue {
  kpi_id: string;
  code: string;
  name: string;
  category: KPICategory;
  value: number;
  unit?: string;
  target?: number;
  trend?: number;
  is_good_when_higher: boolean;
  status: KPIStatus;
  last_updated: string;
  metadata?: Record<string, any>;
}

// Resposta agrupada por categoria
export interface KPICategoryResponse {
  category: KPICategory;
  kpis: KPIValue[];
  summary: {
    total_kpis: number;
    status_distribution: {
      good: number;
      warning: number;
      critical: number;
    };
    health_score: number;
    average_trend: number;
  };
}

// Configuração de KPI
export interface KPIConfig {
  kpi_id: string;
  target_value?: number;
  warning_threshold?: number;
  critical_threshold?: number;
  is_enabled: boolean;
}

// Mapeamento de cores por categoria
export const KPI_CATEGORY_COLORS: Record<KPICategory, string> = {
  [KPICategory.EFFICIENCY]: '#3b82f6', // blue
  [KPICategory.PRICING]: '#8b5cf6',    // purple
  [KPICategory.PLANNING]: '#f97316',   // orange
  [KPICategory.GOVERNANCE]: '#10b981'  // green
};

// Mapeamento de ícones por status
export const KPI_STATUS_ICONS = {
  good: 'CheckCircle',
  warning: 'AlertTriangle',
  critical: 'XCircle',
  neutral: 'Circle'
};
```

## 🔌 Serviço de API

### api/kpiService.ts

```typescript
import apiClient from '@/api/client';
import { KPIValue, KPICategoryResponse, KPIConfig, KPICategory } from '@/types/kpi.types';

class KPIService {
  private baseUrl = '/api/v1/kpis';

  /**
   * Obtém KPIs atuais
   */
  async getCurrentKPIs(category?: KPICategory): Promise<KPIValue[]> {
    const params = category ? { category } : undefined;
    const response = await apiClient.get(`${this.baseUrl}/current`, { params });
    return response.data.data.kpis;
  }

  /**
   * Obtém KPIs agrupados por categoria
   */
  async getKPIsByCategory(): Promise<KPICategoryResponse[]> {
    const response = await apiClient.get(`${this.baseUrl}/by-category`);
    return response.data.data.categories;
  }

  /**
   * Obtém histórico de um KPI
   */
  async getKPIHistory(kpiCode: string, days: number = 30) {
    const response = await apiClient.get(`${this.baseUrl}/history/${kpiCode}`, {
      params: { days }
    });
    return response.data.data;
  }

  /**
   * Atualiza configuração de KPI
   */
  async updateKPIConfig(kpiCode: string, config: Partial<KPIConfig>) {
    const response = await apiClient.put(`${this.baseUrl}/config/${kpiCode}`, config);
    return response.data.data;
  }

  /**
   * Força recálculo de KPIs (admin)
   */
  async calculateKPIs(date?: string) {
    const response = await apiClient.post(`${this.baseUrl}/calculate`, { 
      calculation_date: date 
    });
    return response.data;
  }
}

export default new KPIService();
```

## 🪝 Hook Customizado

### hooks/useKPIs.ts

```typescript
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
    cacheTime: 10 * 60 * 1000, // 10 minutos
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
    isUpdating: updateConfig.isLoading,
    isRecalculating: recalculate.isLoading,
  };
};
```

## 🎨 Componentes React

### components/kpi/KPICard.tsx

```tsx
import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Info,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Circle
} from 'lucide-react';
import { KPIValue, KPI_STATUS_ICONS } from '@/types/kpi.types';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';

interface KPICardProps {
  kpi: KPIValue;
  onClick?: () => void;
  compact?: boolean;
}

export const KPICard: React.FC<KPICardProps> = ({ kpi, onClick, compact = false }) => {
  const { isDark } = useTheme();
  
  // Ícone de status
  const StatusIcon = {
    good: CheckCircle,
    warning: AlertTriangle,
    critical: XCircle,
    neutral: Circle
  }[kpi.status];
  
  // Cor do status
  const statusColor = {
    good: 'text-green-500',
    warning: 'text-yellow-500',
    critical: 'text-red-500',
    neutral: 'text-gray-500'
  }[kpi.status];
  
  // Ícone de tendência
  const TrendIcon = kpi.trend && kpi.trend > 0 ? TrendingUp : 
                   kpi.trend && kpi.trend < 0 ? TrendingDown : Minus;
  
  // Cor da tendência baseada em is_good_when_higher
  const getTrendColor = () => {
    if (!kpi.trend || kpi.trend === 0) return 'text-gray-500';
    
    const isPositiveTrend = kpi.trend > 0;
    const isGoodTrend = kpi.is_good_when_higher ? isPositiveTrend : !isPositiveTrend;
    
    return isGoodTrend ? 'text-green-500' : 'text-red-500';
  };
  
  // Calcular progresso em relação ao target
  const progress = kpi.target ? (kpi.value / kpi.target) * 100 : 0;
  const progressCapped = Math.min(Math.max(progress, 0), 100);
  
  if (compact) {
    return (
      <div 
        className={cn(
          "flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors",
          isDark ? "hover:bg-gray-800" : "hover:bg-gray-100"
        )}
        onClick={onClick}
      >
        <div className="flex items-center gap-3">
          <StatusIcon className={cn("h-4 w-4", statusColor)} />
          <span className="text-sm font-medium">{kpi.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-mono">
            {kpi.value.toFixed(kpi.unit === '%' ? 1 : 2)}{kpi.unit}
          </span>
          <TrendIcon className={cn("h-4 w-4", getTrendColor())} />
        </div>
      </div>
    );
  }
  
  return (
    <Card 
      className={cn(
        "cursor-pointer transition-all hover:shadow-lg",
        isDark ? "hover:border-gray-600" : "hover:border-gray-300"
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <StatusIcon className={cn("h-5 w-5", statusColor)} />
            <h3 className="font-medium text-sm line-clamp-1">{kpi.name}</h3>
          </div>
          <Info className="h-4 w-4 text-gray-400" />
        </div>
        
        <div className="space-y-3">
          {/* Valor principal */}
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold">
              {kpi.value.toFixed(kpi.unit === '%' ? 1 : 2)}
            </span>
            <span className="text-sm text-gray-500">{kpi.unit}</span>
          </div>
          
          {/* Tendência */}
          <div className="flex items-center gap-2">
            <TrendIcon className={cn("h-4 w-4", getTrendColor())} />
            <span className={cn("text-sm", getTrendColor())}>
              {kpi.trend && kpi.trend > 0 ? '+' : ''}{kpi.trend?.toFixed(1)}%
            </span>
          </div>
          
          {/* Progresso em relação ao target */}
          {kpi.target && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-gray-500">
                <span>Target: {kpi.target}{kpi.unit}</span>
                <span>{progressCapped.toFixed(0)}%</span>
              </div>
              <Progress 
                value={progressCapped} 
                className="h-2"
                indicatorClassName={cn(
                  kpi.status === 'good' && "bg-green-500",
                  kpi.status === 'warning' && "bg-yellow-500",
                  kpi.status === 'critical' && "bg-red-500"
                )}
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
```

### components/kpi/KPICategorySection.tsx

```tsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ChevronDown, ChevronUp, Settings } from 'lucide-react';
import { KPICategoryResponse, KPI_CATEGORY_COLORS } from '@/types/kpi.types';
import { KPICard } from './KPICard';
import { KPIDetailModal } from './KPIDetailModal';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';

interface KPICategorySectionProps {
  categoryData: KPICategoryResponse;
  onConfigClick?: (kpiCode: string) => void;
  defaultExpanded?: boolean;
}

export const KPICategorySection: React.FC<KPICategorySectionProps> = ({ 
  categoryData, 
  onConfigClick,
  defaultExpanded = true 
}) => {
  const { isDark } = useTheme();
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);
  
  const categoryColor = KPI_CATEGORY_COLORS[categoryData.category];
  const { summary } = categoryData;
  
  // Tradução das categorias
  const categoryNames = {
    efficiency: 'Eficiência',
    pricing: 'Tarifação',
    planning: 'Planejamento',
    governance: 'Governança'
  };
  
  return (
    <>
      <Card className="overflow-hidden">
        <CardHeader 
          className={cn(
            "cursor-pointer select-none",
            isDark ? "hover:bg-gray-800" : "hover:bg-gray-50"
          )}
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div 
                className="w-1 h-8 rounded-full" 
                style={{ backgroundColor: categoryColor }}
              />
              <CardTitle className="text-lg">
                {categoryNames[categoryData.category]}
              </CardTitle>
              <Badge variant="secondary" className="ml-2">
                {summary.total_kpis} KPIs
              </Badge>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Mini status summary */}
              <div className="flex gap-2 text-sm">
                <span className="text-green-500">●{summary.status_distribution.good}</span>
                <span className="text-yellow-500">●{summary.status_distribution.warning}</span>
                <span className="text-red-500">●{summary.status_distribution.critical}</span>
              </div>
              
              {/* Health score */}
              <Badge 
                variant={
                  summary.health_score >= 80 ? 'default' :
                  summary.health_score >= 60 ? 'secondary' : 'destructive'
                }
              >
                {summary.health_score.toFixed(0)}%
              </Badge>
              
              {isExpanded ? <ChevronUp /> : <ChevronDown />}
            </div>
          </div>
        </CardHeader>
        
        {isExpanded && (
          <CardContent className="pt-0">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-4">
              {categoryData.kpis.map((kpi) => (
                <KPICard
                  key={kpi.kpi_id}
                  kpi={kpi}
                  onClick={() => setSelectedKPI(kpi.code)}
                />
              ))}
            </div>
          </CardContent>
        )}
      </Card>
      
      {/* Modal de detalhes */}
      {selectedKPI && (
        <KPIDetailModal
          kpiCode={selectedKPI}
          isOpen={!!selectedKPI}
          onClose={() => setSelectedKPI(null)}
          onConfigClick={onConfigClick}
        />
      )}
    </>
  );
};
```

### components/kpi/KPIIndicators.tsx

```tsx
import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import { 
  BarChart3, 
  RefreshCw, 
  Settings, 
  AlertTriangle,
  CheckCircle,
  XCircle 
} from 'lucide-react';
import { useKPIs } from '@/hooks/useKPIs';
import { KPICategorySection } from './KPICategorySection';
import { KPIConfigModal } from './KPIConfigModal';
import { KPICategory } from '@/types/kpi.types';
import { cn } from '@/lib/utils';

export const KPIIndicators: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState<KPICategory | 'all'>('all');
  const [configKPI, setConfigKPI] = useState<string | null>(null);
  
  const {
    categorizedKPIs,
    overallStats,
    isLoading,
    error,
    refetch,
    recalculate,
    isRecalculating
  } = useKPIs(selectedCategory === 'all' ? undefined : selectedCategory);
  
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>
          Erro ao carregar KPIs. Por favor, tente novamente.
        </AlertDescription>
      </Alert>
    );
  }
  
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i}>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <Skeleton className="h-32" />
                <Skeleton className="h-32" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {/* Header com estatísticas gerais */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="h-6 w-6 text-primary" />
              <CardTitle>Key Performance Indicators</CardTitle>
            </div>
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => refetch()}
                disabled={isLoading}
              >
                <RefreshCw className={cn("h-4 w-4 mr-2", isLoading && "animate-spin")} />
                Atualizar
              </Button>
              
              <Button
                variant="outline"
                size="sm"
                onClick={() => recalculate()}
                disabled={isRecalculating}
              >
                <Settings className={cn("h-4 w-4 mr-2", isRecalculating && "animate-spin")} />
                Recalcular
              </Button>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          {/* Resumo geral */}
          {overallStats && (
            <div className="grid grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold">{overallStats.total}</div>
                <div className="text-sm text-gray-500">Total KPIs</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-500">{overallStats.good}</div>
                <div className="text-sm text-gray-500">No Target</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-yellow-500">{overallStats.warning}</div>
                <div className="text-sm text-gray-500">Atenção</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-red-500">{overallStats.critical}</div>
                <div className="text-sm text-gray-500">Crítico</div>
              </div>
            </div>
          )}
          
          {/* Filtro por categoria */}
          <Tabs value={selectedCategory} onValueChange={(v) => setSelectedCategory(v as any)}>
            <TabsList className="grid grid-cols-5 w-full">
              <TabsTrigger value="all">Todos</TabsTrigger>
              <TabsTrigger value="efficiency">Eficiência</TabsTrigger>
              <TabsTrigger value="pricing">Tarifação</TabsTrigger>
              <TabsTrigger value="planning">Planejamento</TabsTrigger>
              <TabsTrigger value="governance">Governança</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardContent>
      </Card>
      
      {/* KPIs por categoria */}
      <div className="space-y-4">
        {categorizedKPIs?.map((category) => (
          <KPICategorySection
            key={category.category}
            categoryData={category}
            onConfigClick={setConfigKPI}
            defaultExpanded={selectedCategory === 'all' || selectedCategory === category.category}
          />
        ))}
      </div>
      
      {/* Modal de configuração */}
      {configKPI && (
        <KPIConfigModal
          kpiCode={configKPI}
          isOpen={!!configKPI}
          onClose={() => setConfigKPI(null)}
        />
      )}
    </div>
  );
};
```

### components/kpi/KPIDetailModal.tsx

```tsx
import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';
import { Settings, TrendingUp, TrendingDown, Info } from 'lucide-react';
import { useKPIs } from '@/hooks/useKPIs';
import { KPIValue } from '@/types/kpi.types';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useTheme } from '@/hooks/useTheme';

interface KPIDetailModalProps {
  kpiCode: string;
  isOpen: boolean;
  onClose: () => void;
  onConfigClick?: (kpiCode: string) => void;
}

export const KPIDetailModal: React.FC<KPIDetailModalProps> = ({
  kpiCode,
  isOpen,
  onClose,
  onConfigClick
}) => {
  const { isDark } = useTheme();
  const { categorizedKPIs, kpiHistory, setSelectedKPI } = useKPIs();
  
  // Buscar KPI nos dados categorizados
  const kpi = categorizedKPIs?.flatMap(cat => cat.kpis).find(k => k.code === kpiCode);
  
  React.useEffect(() => {
    if (isOpen && kpiCode) {
      setSelectedKPI(kpiCode);
    }
  }, [isOpen, kpiCode, setSelectedKPI]);
  
  if (!kpi) return null;
  
  // Formatar dados do histórico para o gráfico
  const chartData = kpiHistory?.history?.map((h: any) => ({
    date: format(new Date(h.date), 'dd/MM', { locale: ptBR }),
    value: h.value,
    trend: h.trend
  })) || [];
  
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <DialogTitle>{kpi.name}</DialogTitle>
              <DialogDescription>
                Detalhes e histórico do indicador
              </DialogDescription>
            </div>
            
            {onConfigClick && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  onConfigClick(kpiCode);
                  onClose();
                }}
              >
                <Settings className="h-4 w-4 mr-2" />
                Configurar
              </Button>
            )}
          </div>
        </DialogHeader>
        
        <Tabs defaultValue="overview" className="mt-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">Visão Geral</TabsTrigger>
            <TabsTrigger value="history">Histórico</TabsTrigger>
            <TabsTrigger value="details">Detalhes</TabsTrigger>
          </TabsList>
          
          <TabsContent value="overview" className="space-y-4">
            {/* Valor atual e status */}
            <Card>
              <CardContent className="pt-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Valor Atual</p>
                    <p className="text-3xl font-bold">
                      {kpi.value.toFixed(kpi.unit === '%' ? 1 : 2)}{kpi.unit}
                    </p>
                    <div className="flex items-center gap-2 mt-2">
                      {kpi.trend && kpi.trend > 0 ? (
                        <TrendingUp className="h-4 w-4 text-green-500" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-500" />
                      )}
                      <span className="text-sm">
                        {kpi.trend && kpi.trend > 0 ? '+' : ''}{kpi.trend?.toFixed(1)}%
                      </span>
                    </div>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-500">Meta</p>
                    <p className="text-3xl font-bold">
                      {kpi.target?.toFixed(kpi.unit === '%' ? 1 : 2)}{kpi.unit}
                    </p>
                    <Badge 
                      className="mt-2"
                      variant={
                        kpi.status === 'good' ? 'default' :
                        kpi.status === 'warning' ? 'secondary' : 'destructive'
                      }
                    >
                      {kpi.status === 'good' ? 'No Target' :
                       kpi.status === 'warning' ? 'Atenção' : 'Crítico'}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
            
            {/* Descrição e fórmula */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Sobre este KPI</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-gray-500 mb-1">Descrição</p>
                  <p className="text-sm">
                    {getKPIDescription(kpi.code)}
                  </p>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500 mb-1">Fórmula</p>
                  <code className="text-xs bg-gray-100 dark:bg-gray-800 p-2 rounded block">
                    {getKPIFormula(kpi.code)}
                  </code>
                </div>
                
                <div>
                  <p className="text-sm text-gray-500 mb-1">Direção Positiva</p>
                  <p className="text-sm">
                    {kpi.is_good_when_higher ? 
                      'Quanto maior, melhor ↑' : 
                      'Quanto menor, melhor ↓'}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="history">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Últimos 30 dias</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis 
                        dataKey="date" 
                        stroke={isDark ? '#94a3b8' : '#64748b'}
                      />
                      <YAxis 
                        stroke={isDark ? '#94a3b8' : '#64748b'}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: isDark ? '#1e293b' : '#ffffff',
                          border: '1px solid #e2e8f0'
                        }}
                      />
                      {kpi.target && (
                        <ReferenceLine 
                          y={kpi.target} 
                          stroke="#ef4444" 
                          strokeDasharray="5 5"
                          label="Meta"
                        />
                      )}
                      <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
          
          <TabsContent value="details">
            <Card>
              <CardContent className="pt-6">
                <dl className="space-y-4">
                  <div>
                    <dt className="text-sm text-gray-500">Categoria</dt>
                    <dd className="text-sm font-medium capitalize">{kpi.category}</dd>
                  </div>
                  
                  <div>
                    <dt className="text-sm text-gray-500">Última Atualização</dt>
                    <dd className="text-sm font-medium">
                      {format(new Date(kpi.last_updated), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                    </dd>
                  </div>
                  
                  <div>
                    <dt className="text-sm text-gray-500">Frequência de Cálculo</dt>
                    <dd className="text-sm font-medium">Diária</dd>
                  </div>
                  
                  {kpi.metadata && (
                    <div>
                      <dt className="text-sm text-gray-500">Metadados</dt>
                      <dd className="text-sm">
                        <pre className="bg-gray-100 dark:bg-gray-800 p-2 rounded text-xs overflow-x-auto">
                          {JSON.stringify(kpi.metadata, null, 2)}
                        </pre>
                      </dd>
                    </div>
                  )}
                </dl>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};

// Funções auxiliares para descrições e fórmulas
const getKPIDescription = (code: string): string => {
  const descriptions: Record<string, string> = {
    'resource_utilization_rate': 'Mede o percentual de recursos provisionados que estão sendo efetivamente utilizados. Ajuda a identificar superprovisionamento.',
    'cloud_waste_percentage': 'Identifica a porção do gasto em recursos ociosos como VMs paradas, volumes não anexados e snapshots órfãos.',
    'power_schedule_adherence': 'Verifica se a automação de start/stop está funcionando conforme planejado para workloads não-produtivos.',
    'legacy_resources_percentage': 'Quantifica quantas instâncias ainda estão em famílias antigas e menos eficientes.',
    'effective_savings_rate': 'Economia líquida comparada com preços on-demand, unificando cobertura e utilização de RI/SP/CUD.',
    'commitment_discount_waste': 'Quanto da capacidade de RI/SP/CUD comprada permanece não utilizada.',
    'compute_covered_by_commitments': 'Profundidade da cobertura de taxa; valores baixos sinalizam vazamento de instâncias on-demand.',
    'cost_per_vcpu_hour': 'Normaliza o custo para uma unidade técnica, ideal para comparações de preço entre provedores.',
    'budget_forecast_variation': 'Quão próximo seu forecast contínuo está do orçamento acumulado no ano.',
    'cloud_spend_variation': 'O sinal clássico de gasto acima/abaixo do orçamento.',
    'forecast_accuracy_rate': 'Precisão preditiva para capacidade ou valores; orienta ajustes no modelo de previsão.',
    'unallocated_cost_percentage': 'Quanto do gasto ainda não possui tag ou proprietário.',
    'tag_compliance_rate': 'Saúde da sua disciplina de tagging; valores baixos comprometem todos os outros KPIs.',
    'anomaly_detection_savings': 'Economias realizadas ao detectar picos de gasto antecipadamente com alertas.'
  };
  
  return descriptions[code] || 'Descrição não disponível.';
};

const getKPIFormula = (code: string): string => {
  const formulas: Record<string, string> = {
    'resource_utilization_rate': '(Capacidade Consumida ÷ Capacidade Alocada) × 100',
    'cloud_waste_percentage': '(Custo de Recursos Ociosos ÷ Gasto Total na Nuvem) × 100',
    'power_schedule_adherence': '(Horas de Runtime Planejadas ÷ Horas de Runtime Reais) × 100',
    'legacy_resources_percentage': '(Contagem de Instâncias Legacy ÷ Total de Instâncias) × 100',
    'effective_savings_rate': '(Economias de Todos os Instrumentos de Desconto ÷ Gasto On-Demand Equivalente)',
    'commitment_discount_waste': '(Custo de Commitment Não Usado ÷ Custo Total de Commitment) × 100',
    'compute_covered_by_commitments': '(Gasto de Compute com Desconto de Commitment ÷ Gasto Total de Compute) × 100',
    'cost_per_vcpu_hour': '(Custo de Compute por Hora ÷ Número de vCPUs ou GPUs)',
    'budget_forecast_variation': '((Orçado - Previsto) ÷ Orçado) × 100',
    'cloud_spend_variation': '((Orçado - Real) ÷ Orçado) × 100',
    'forecast_accuracy_rate': '100 - abs((Previsto - Real) ÷ Previsto) × 100',
    'unallocated_cost_percentage': '(Custos Não Alocados ÷ Gasto Total na Nuvem) × 100',
    'tag_compliance_rate': '(Recursos Tagueados Corretamente ÷ Total de Recursos) × 100',
    'anomaly_detection_savings': 'Soma de (Custo de Pico Previsto - Custo no Desligamento)'
  };
  
  return formulas[code] || 'Fórmula não disponível.';
};
```

## 🔄 Integração com Dashboard

### Adicionar ao Dashboard Principal

```tsx
// Em src/pages/Home.tsx ou Dashboard.tsx

import { KPIIndicators } from '@/components/kpi/KPIIndicators';

// Adicionar uma nova seção no dashboard
<section className="mb-8">
  <h2 className="text-2xl font-bold mb-4">Key Performance Indicators</h2>
  <KPIIndicators />
</section>

// Ou adicionar como uma aba
<Tabs defaultValue="overview">
  <TabsList>
    <TabsTrigger value="overview">Visão Geral</TabsTrigger>
    <TabsTrigger value="kpis">KPIs</TabsTrigger>
    <TabsTrigger value="costs">Custos</TabsTrigger>
  </TabsList>
  
  <TabsContent value="kpis">
    <KPIIndicators />
  </TabsContent>
</Tabs>
```

## 📱 Responsividade

```tsx
// Ajustes para mobile em KPICard
<div className={cn(
  "grid gap-4",
  "grid-cols-1",
  "sm:grid-cols-2",
  "lg:grid-cols-3",
  "xl:grid-cols-4"
)}>
  {kpis.map(kpi => (
    <KPICard key={kpi.id} kpi={kpi} />
  ))}
</div>

// Versão compacta para mobile
{isMobile ? (
  <KPICard compact kpi={kpi} />
) : (
  <KPICard kpi={kpi} />
)}
```

## 🔧 Configuração Inicial

### Formulário de Setup Inicial

```tsx
// components/kpi/KPISetupWizard.tsx

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

const setupSchema = z.object({
  resourceUtilizationTarget: z.number().min(0).max(100),
  wasteReductionTarget: z.number().min(0).max(100),
  commitmentCoverageTarget: z.number().min(0).max(100),
  complianceTarget: z.number().min(0).max(100),
  monthlyBudget: z.number().positive(),
  companySize: z.enum(['small', 'medium', 'large', 'enterprise']),
});

type SetupFormData = z.infer<typeof setupSchema>;

export const KPISetupWizard: React.FC = () => {
  const [step, setStep] = useState(1);
  const totalSteps = 4;
  
  const form = useForm<SetupFormData>({
    resolver: zodResolver(setupSchema),
    defaultValues: {
      resourceUtilizationTarget: 75,
      wasteReductionTarget: 15,
      commitmentCoverageTarget: 80,
      complianceTarget: 95,
      monthlyBudget: 50000,
      companySize: 'medium'
    }
  });
  
  const onSubmit = async (data: SetupFormData) => {
    // Enviar configurações para o backend
    console.log('Setup data:', data);
    // TODO: Implementar chamada API
  };
  
  const progress = (step / totalSteps) * 100;
  
  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Configuração de KPIs</CardTitle>
        <CardDescription>
          Vamos configurar as metas iniciais para seus indicadores
        </CardDescription>
        <Progress value={progress} className="mt-4" />
      </CardHeader>
      
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <CardContent className="space-y-6">
          {step === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Metas de Eficiência</h3>
              
              <div className="space-y-2">
                <Label>Taxa de Utilização de Recursos Alvo (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('resourceUtilizationTarget', { valueAsNumber: true })}
                    defaultValue={[75]}
                    max={100}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('resourceUtilizationTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Meta recomendada: 70-80% para ambientes de produção
                </p>
              </div>
              
              <div className="space-y-2">
                <Label>Meta de Redução de Desperdício (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('wasteReductionTarget', { valueAsNumber: true })}
                    defaultValue={[15]}
                    max={50}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('wasteReductionTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Empresas maduras em FinOps alcançam menos de 10%
                </p>
              </div>
            </div>
          )}
          
          {step === 2 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Estratégia de Tarifação</h3>
              
              <div className="space-y-2">
                <Label>Meta de Cobertura por Commitments (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('commitmentCoverageTarget', { valueAsNumber: true })}
                    defaultValue={[80]}
                    max={100}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('commitmentCoverageTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Workloads estáveis devem ter alta cobertura (70-90%)
                </p>
              </div>
            </div>
          )}
          
          {step === 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Planejamento Financeiro</h3>
              
              <div className="space-y-2">
                <Label>Orçamento Mensal de Cloud (R$)</Label>
                <Input
                  type="number"
                  {...form.register('monthlyBudget', { valueAsNumber: true })}
                  placeholder="50000"
                />
                <p className="text-sm text-gray-500">
                  Base para cálculo de variações e alertas
                </p>
              </div>
              
              <div className="space-y-2">
                <Label>Porte da Empresa</Label>
                <select
                  {...form.register('companySize')}
                  className="w-full p-2 border rounded"
                >
                  <option value="small">Pequena (até 50 funcionários)</option>
                  <option value="medium">Média (50-250 funcionários)</option>
                  <option value="large">Grande (250-1000 funcionários)</option>
                  <option value="enterprise">Enterprise (1000+ funcionários)</option>
                </select>
              </div>
            </div>
          )}
          
          {step === 4 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Governança</h3>
              
              <div className="space-y-2">
                <Label>Meta de Compliance de Tags (%)</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    {...form.register('complianceTarget', { valueAsNumber: true })}
                    defaultValue={[95]}
                    max={100}
                    step={5}
                    className="flex-1"
                  />
                  <span className="w-12 text-right">
                    {form.watch('complianceTarget')}%
                  </span>
                </div>
                <p className="text-sm text-gray-500">
                  Tags essenciais: owner, environment, project, cost-center
                </p>
              </div>
            </div>
          )}
        </CardContent>
        
        <CardFooter className="flex justify-between">
          <Button
            type="button"
            variant="outline"
            onClick={() => setStep(Math.max(1, step - 1))}
            disabled={step === 1}
          >
            Anterior
          </Button>
          
          {step < totalSteps ? (
            <Button
              type="button"
              onClick={() => setStep(step + 1)}
            >
              Próximo
            </Button>
          ) : (
            <Button type="submit">
              Finalizar Configuração
            </Button>
          )}
        </CardFooter>
      </form>
    </Card>
  );
};
```

## 🚀 Próximas Etapas

1. **Testes**
   - Criar testes unitários para componentes
   - Testes de integração com API
   - Testes de performance

2. **Otimizações**
   - Implementar lazy loading
   - Adicionar skeleton loaders
   - Otimizar queries com React Query

3. **Features Avançadas**
   - Exportação de relatórios
   - Comparação temporal
   - Alertas em tempo real
   - Dashboard customizável