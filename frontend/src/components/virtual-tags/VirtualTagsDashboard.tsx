import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { 
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip 
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  CheckCircle2,
  DollarSign,
  Tags,
  Activity,
  Clock
} from 'lucide-react';
import { useDashboardMetrics } from '@/hooks/useVirtualTags';
import { DashboardMetrics } from '@/types/virtualTags';
import { formatCurrency } from '@/lib/utils';

interface VirtualTagsDashboardProps {
  className?: string;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const VirtualTagsDashboard: React.FC<VirtualTagsDashboardProps> = ({ className }) => {
  const { data: metrics, isLoading, error } = useDashboardMetrics();

  if (isLoading) {
    return (
      <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader className="space-y-0 pb-2">
              <div className="h-4 bg-muted rounded w-3/4"></div>
              <div className="h-8 bg-muted rounded w-1/2 mt-2"></div>
            </CardHeader>
          </Card>
        ))}
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="text-center text-muted-foreground">
            <AlertTriangle className="mx-auto h-12 w-12 mb-2" />
            <p>Erro ao carregar métricas do dashboard</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { coverage_metrics, allocation_breakdown, unallocated_summary, recent_processing } = metrics;

  // Prepare chart data
  const pieChartData = [
    { name: 'Alocado', value: parseFloat(coverage_metrics.allocated_cost), color: '#10B981' },
    { name: 'Não Alocado', value: parseFloat(coverage_metrics.unallocated_cost), color: '#EF4444' }
  ];

  const barChartData = allocation_breakdown.slice(0, 5).map(item => ({
    name: item.virtual_tag_name,
    cost: parseFloat(item.total_cost),
    records: item.record_count
  }));

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Cobertura Total</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {coverage_metrics.allocation_percentage.toFixed(1)}%
            </div>
            <p className="text-xs text-muted-foreground">
              {formatCurrency(parseFloat(coverage_metrics.allocated_cost))} de{' '}
              {formatCurrency(parseFloat(coverage_metrics.total_cost))}
            </p>
            <Progress 
              value={coverage_metrics.allocation_percentage} 
              className="mt-2"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Virtual Tags Ativas</CardTitle>
            <Tags className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{coverage_metrics.virtual_tags_count}</div>
            <p className="text-xs text-muted-foreground">
              {coverage_metrics.rules_count} regras configuradas
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Registros Processados</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {coverage_metrics.allocated_records.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              de {coverage_metrics.total_records.toLocaleString()} registros
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Custo Não Alocado</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {formatCurrency(parseFloat(coverage_metrics.unallocated_cost))}
            </div>
            <p className="text-xs text-muted-foreground">
              {(100 - coverage_metrics.allocation_percentage).toFixed(1)}% do total
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Allocation Overview - Pie Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Visão Geral de Alocação</CardTitle>
            <CardDescription>
              Distribuição entre custos alocados e não alocados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Top Virtual Tags - Bar Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Top Virtual Tags</CardTitle>
            <CardDescription>
              Virtual Tags com maior custo alocado
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="name" 
                    angle={-45}
                    textAnchor="end"
                    height={60}
                  />
                  <YAxis tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`} />
                  <Tooltip 
                    formatter={(value) => [formatCurrency(Number(value)), 'Custo']}
                    labelFormatter={(label) => `Virtual Tag: ${label}`}
                  />
                  <Bar dataKey="cost" fill="#0088FE" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Details Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Unallocated Services */}
        <Card>
          <CardHeader>
            <CardTitle>Maiores Custos Não Alocados</CardTitle>
            <CardDescription>
              Serviços que mais contribuem para custos não alocados
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {unallocated_summary.top_unallocated_services.slice(0, 5).map((service, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{service.service_name}</p>
                    <p className="text-sm text-muted-foreground">
                      {service.provider_name} • {service.record_count} registros
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{formatCurrency(parseFloat(service.cost_amount))}</p>
                    <p className="text-sm text-muted-foreground">
                      {service.percentage_of_unallocated.toFixed(1)}%
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Processing */}
        <Card>
          <CardHeader>
            <CardTitle>Processamentos Recentes</CardTitle>
            <CardDescription>
              Histórico de processamento de alocações
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recent_processing.slice(0, 5).map((process, index) => (
                <div key={index} className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge 
                        variant={process.status === 'completed' ? 'default' : 
                               process.status === 'failed' ? 'destructive' : 'secondary'}
                      >
                        {process.status === 'completed' ? 'Concluído' :
                         process.status === 'failed' ? 'Falhado' :
                         process.status === 'processing' ? 'Processando' : 'Pendente'}
                      </Badge>
                      {process.status === 'completed' && <CheckCircle2 className="h-4 w-4 text-green-600" />}
                      {process.status === 'failed' && <AlertTriangle className="h-4 w-4 text-red-600" />}
                      {process.status === 'processing' && <Clock className="h-4 w-4 text-blue-600" />}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {new Date(process.created_at).toLocaleDateString()} - 
                      {process.records_processed.toLocaleString()} registros
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">
                      {formatCurrency(process.total_cost_allocated)}
                    </p>
                    {process.processing_time_seconds && (
                      <p className="text-sm text-muted-foreground">
                        {process.processing_time_seconds}s
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VirtualTagsDashboard;
