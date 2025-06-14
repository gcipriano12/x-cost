import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { AlertTriangle, Search } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { 
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle
} from '@/components/ui/resizable';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowUpRight, Layers, CalendarDays, DollarSign, Tag, Globe } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { format } from 'date-fns';
import { AnomalyDetails } from "@/components/dashboard/anomalies/AnomalyDetails";
import { useSearchParams } from 'react-router-dom';
import { useDashboardData } from '@/hooks/useDashboardData';

// Mock Anomaly Data
interface Anomaly {
  id: string;
  severity: 'low' | 'medium' | 'high';
  title: string;
  description: string;
  impact: number;
  resource?: string;
  provider?: string;
  dateDetected: string;
  tags?: string[];
}

const mockAnomalies: Anomaly[] = [
  {
    id: 'a1',
    severity: 'high',
    title: 'Aumento súbito em custos de VM',
    description: 'Detectado um aumento inesperado de 20% no custo de máquinas virtuais na região us-east-1. Possível causa: instância subdimensionada ou tráfego inesperado.',
    impact: 23450,
    resource: 'i-0abcdef1234567890',
    provider: 'AWS',
    dateDetected: '2025-05-20',
    tags: ['Environment:Production', 'Service:WebApp'],
  },
  {
    id: 'a2',
    severity: 'medium',
    title: 'Recursos ociosos',
    description: 'Identificadas 3 bases de dados de desenvolvimento que não foram acessadas nos últimos 30 dias.',
    impact: 12300,
    resource: 'db-xyz789',
    provider: 'GCP',
    dateDetected: '2025-05-19',
    tags: ['Environment:Development', 'Team:Data'],
  },
  {
    id: 'a3',
    severity: 'high',
    title: 'GPU não otimizadas',
    description: 'Instâncias com GPU de alto custo estão com baixa utilização média (<15%) nas últimas 72 horas.',
    impact: 19850,
    resource: 'gpu-instance-1',
    provider: 'Azure',
    dateDetected: '2025-05-18',
    tags: ['Project:ML', 'Environment:Research'],
  },
  {
    id: 'a4',
    severity: 'medium',
    title: 'Balanceadores ociosos',
    description: 'Dois balanceadores de carga em ambiente de staging não receberam tráfego nas últimas duas semanas.',
    impact: 4560,
    resource: 'lb-staging-01',
    provider: 'AWS',
    dateDetected: '2025-05-15',
    tags: ['Environment:Staging'],
  },
  {
    id: 'a5',
    severity: 'low',
    title: 'Banco de dados sobredimensionado',
    description: 'Análise sugere que o banco de dados principal pode ser redimensionado para uma instância menor, gerando economia significativa.',
    impact: 2960,
    resource: 'main-db-prod',
    provider: 'GCP',
    dateDetected: '2025-05-14',
    tags: ['Environment:Production'],
  },
  {
    id: 'a6',
    severity: 'high',
    title: 'IPs elásticos não associados',
    description: 'Três IPs elásticos estão provisionados mas não associados a nenhuma instância, gerando custo.',
    impact: 1870,
    resource: 'eipalloc-abcdefg',
    provider: 'AWS',
    dateDetected: '2025-05-12',
    tags: [],
  },
  {
    id: 'a7',
    severity: 'low',
    title: 'Snapshots expirados',
    description: 'Detectamos 27 snapshots mais antigos que 90 dias que podem ser arquivados ou excluídos.',
    impact: 3450,
    resource: 'snap-1234567890abcdef0',
    provider: 'Azure',
    dateDetected: '2025-05-10',
    tags: [],
  },
];

// Helper functions for styling based on severity
const getSeverityColor = (severity: string, isDark: boolean) => {
  switch(severity) {
    case 'high': return isDark ? 'text-red-400' : 'text-red-600';
    case 'medium': return isDark ? 'text-amber-400' : 'text-amber-600';
    case 'low': return isDark ? 'text-blue-400' : 'text-blue-600';
    default: return isDark ? 'text-slate-400' : 'text-slate-600';
  }
};

const getSeverityBadgeStyle = (severity: string, isDark: boolean) => {
  switch(severity) {
    case 'high': return isDark ? 'bg-red-900 text-red-100 border-0' : 'bg-red-100 text-red-700 border-0';
    case 'medium': return isDark ? 'bg-amber-900 text-amber-100 border-0' : 'bg-amber-100 text-amber-700 border-0';
    case 'low': return isDark ? 'bg-blue-900 text-blue-100 border-0' : 'bg-blue-100 text-blue-700 border-0';
    default: return isDark ? 'bg-slate-700 text-slate-100 border-0' : 'bg-slate-100 text-slate-700 border-0';
  }
};

const getSeverityLabel = (severity: string) => {
  switch(severity) {
    case 'high': return 'Alta';
    case 'medium': return 'Média';
    case 'low': return 'Baixa';
    default: return 'Desconhecida';
  }
};

const getSeverityDotColor = (severity: string, isDark: boolean) => {
  switch(severity) {
    case 'high': return isDark ? '#f87171' : '#ef4444';
    case 'medium': return isDark ? '#fcd34d' : '#f59e0b';
    case 'low': return isDark ? '#60a5fa' : '#3b82f6';
    default: return isDark ? '#94a3b8' : '#71717a';
  }
};

const formatCurrency = (value: number) => {
  // Using USD formatting consistently throughout the application
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(value);
};

const Anomalies = () => {
  const { isDark } = useTheme();
  const { timeFilter, setTimeFilter } = useDashboardData();
  const [searchParams] = useSearchParams();
  const anomalyIdFromUrl = searchParams.get('id');
  const [selectedAnomaly, setSelectedAnomaly] = React.useState<Anomaly | null>(null); // Inicia como null para que o useEffect defina o inicial
  const [selectedAnomalyId, setSelectedAnomalyId] = React.useState<string | null>(null);
  
  // Effect to select anomaly based on URL parameter or default
  React.useEffect(() => {
    let anomalyToSelect: Anomaly | undefined;
    if (anomalyIdFromUrl) {
      // Tenta encontrar a anomalia pelo ID da URL
      anomalyToSelect = mockAnomalies.find(anomaly => anomaly.id === anomalyIdFromUrl);
    }

    if (anomalyToSelect) {
      // Se encontrou a anomalia pelo ID da URL
      setSelectedAnomaly(anomalyToSelect);
      setSelectedAnomalyId(anomalyToSelect.id);
    } else if (mockAnomalies.length > 0) {
      // Se não encontrou pelo ID da URL ou não havia ID, seleciona a primeira anomalia mockada
      setSelectedAnomaly(mockAnomalies[0]);
      setSelectedAnomalyId(mockAnomalies[0].id);
    } else {
      // Se não há anomalias mockadas
      setSelectedAnomaly(null);
      setSelectedAnomalyId(null);
    }
  }, [anomalyIdFromUrl, mockAnomalies]); // Depende do ID da URL e dos dados mockados (caso venham de API real)

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={AlertTriangle} 
          title="Anomalies" 
          description="Detect and resolve unexpected cost patterns."
          color="text-amber-500"
          timeFilter={timeFilter}
          onTimeFilterChange={setTimeFilter}
        />
        
        <div className="p-4">
          <ResizablePanelGroup direction="horizontal">
            {/* Anomaly List Panel */}
            <ResizablePanel defaultSize={30} minSize={20}>
              <Card className="h-full flex flex-col">
                <CardHeader className={cn("border-b", isDark ? "border-slate-700" : "border-slate-200")}>
                  <CardTitle className="text-lg font-medium">Lista de Anomalias ({mockAnomalies.length})</CardTitle>
                </CardHeader>
                <CardContent className="flex-grow p-0">
                  <ScrollArea className="h-full">
                    {mockAnomalies.map((anomaly) => (
                      <div
                        key={anomaly.id}
                        className={cn(
                          "flex items-center justify-between p-3 border-b cursor-pointer transition-colors",
                          isDark ? "border-slate-700 hover:bg-slate-800" : "border-slate-200 hover:bg-slate-100",
                          selectedAnomaly?.id === anomaly.id && (isDark ? "bg-slate-800" : "bg-slate-100")
                        )}
                        onClick={() => {
                          setSelectedAnomaly(anomaly);
                          setSelectedAnomalyId(anomaly.id);
                        }}
                      >
                        <div className="flex items-start">
                          <div
                            className={cn("h-2 w-2 rounded-full mt-1 mr-2 flex-shrink-0", `bg-${getSeverityDotColor(anomaly.severity, isDark)}`)}
                            style={{ backgroundColor: getSeverityDotColor(anomaly.severity, isDark) }}
                          />
                          <div className="flex-1">
                            <p className="font-medium text-sm leading-tight">{anomaly.title}</p>
                            <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">{anomaly.description}</p>
                          </div>
                        </div>
                        <div className="flex flex-col items-end ml-2 flex-shrink-0">
                          <Badge className={cn(
                            "text-xs px-1 py-0.5",
                            getSeverityBadgeStyle(anomaly.severity, isDark)
                          )}>
                            {getSeverityLabel(anomaly.severity)}
                          </Badge>
                          <span className={cn("text-sm font-bold mt-1", getSeverityColor(anomaly.severity, isDark))}>
                            {formatCurrency(anomaly.impact)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </ScrollArea>
                </CardContent>
              </Card>
            </ResizablePanel>

            <ResizableHandle withHandle />

            {/* Anomaly Details Panel */}
            <ResizablePanel defaultSize={70} minSize={40}>
              <Card className="h-full flex flex-col">
                <CardHeader className={cn("border-b", isDark ? "border-slate-700" : "border-slate-200")}>
                  <CardTitle className="text-lg font-medium">Detalhes da Anomalia</CardTitle>
                </CardHeader>
                <CardContent className="flex-grow p-4 overflow-auto">
                  <ScrollArea className="h-full pr-4">
                    {selectedAnomaly ? (
                      <AnomalyDetails anomaly={selectedAnomaly} />
                    ) : (  
                      <div className="h-full flex items-center justify-center text-muted-foreground">
                        Selecione uma anomalia na lista para ver os detalhes.
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      </div>
    </Dashboard>
  );
};

export default Anomalies;
