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
  AlertTriangle
} from 'lucide-react';
import { useKPIs } from '@/hooks/useKPIs';
import { KPICategorySection } from './KPICategorySection';
import { KPICategory } from '@/types/kpi.types';
import { cn } from '@/lib/utils';
import { useTranslation } from 'react-i18next';

export const KPIIndicators: React.FC = () => {
  const { t } = useTranslation();
  const [selectedCategory, setSelectedCategory] = useState<KPICategory | 'all'>('all');
  const [selectedKPI, setSelectedKPI] = useState<string | null>(null);
  
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
              <CardTitle>{t('sections.kpis', 'Key Performance Indicators')}</CardTitle>
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
              <TabsTrigger value="efficiency">{t('sections.eficiencia', 'Eficiência')}</TabsTrigger>
              <TabsTrigger value="pricing">{t('sections.tarifacao', 'Tarifação')}</TabsTrigger>
              <TabsTrigger value="planning">{t('sections.planejamento', 'Planejamento')}</TabsTrigger>
              <TabsTrigger value="governance">{t('sections.governanca', 'Governança')}</TabsTrigger>
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
            onKPIClick={setSelectedKPI}
            defaultExpanded={selectedCategory === 'all' || selectedCategory === category.category}
          />
        ))}
      </div>
      
      {/* Mensagem quando não há KPIs */}
      {categorizedKPIs && categorizedKPIs.length === 0 && (
        <Card>
          <CardContent className="py-8 text-center">
            <BarChart3 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-600 mb-2">
              Nenhum KPI encontrado
            </h3>
            <p className="text-gray-500">
              Configure seus KPIs no backend para começar a visualizar os indicadores.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
};