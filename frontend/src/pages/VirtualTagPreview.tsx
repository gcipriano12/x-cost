import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Dashboard from '@/components/dashboard/Dashboard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import DatePickerWithRange from '@/components/ui/date-range-picker';
import { PageHeader } from '@/components/layout/PageHeader';
import { 
  ArrowLeft, 
  Play, 
  RefreshCw, 
  AlertTriangle, 
  CheckCircle2,
  TrendingUp,
  DollarSign,
  Calendar,
  Database,
  Eye
} from 'lucide-react';
import { useVirtualTag, useVirtualTagPreview } from '@/hooks/useVirtualTags';
import { DateRangeFilter } from '@/types/virtualTags';
import { formatCurrency } from '@/lib/utils';
import { toast } from 'sonner';
import { addDays, subDays } from 'date-fns';

const VirtualTagPreview: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [dateRange, setDateRange] = useState<DateRangeFilter>({
    start_date: subDays(new Date(), 30).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0]
  });

  const { data: virtualTag, isLoading: loadingTag } = useVirtualTag(id || '');
  const { preview, loading, error, getPreview } = useVirtualTagPreview();

  const handleRunPreview = async () => {
    if (!id) return;
    
    try {
      await getPreview(id, dateRange);
      toast.success('Preview gerado com sucesso!');
    } catch (error) {
      console.error('Erro ao gerar preview:', error);
    }
  };

  const calculateMetrics = () => {
    if (!preview || preview.length === 0) {
      return {
        totalResources: 0,
        totalCost: 0,
        coveredResources: 0,
        coveredCost: 0,
        coveragePercentage: 0
      };
    }

    const totalResources = preview.length;
    const totalCost = preview.reduce((sum, item) => sum + item.cost_amount, 0);
    const coveredResources = preview.filter(item => item.tag_value && item.tag_value !== 'untagged').length;
    const coveredCost = preview
      .filter(item => item.tag_value && item.tag_value !== 'untagged')
      .reduce((sum, item) => sum + item.cost_amount, 0);
    
    const coveragePercentage = totalCost > 0 ? (coveredCost / totalCost) * 100 : 0;

    return {
      totalResources,
      totalCost,
      coveredResources,
      coveredCost,
      coveragePercentage
    };
  };

  const groupByTagValue = () => {
    if (!preview) return [];

    const groups = preview.reduce((acc, item) => {
      const tagValue = item.tag_value || 'untagged';
      if (!acc[tagValue]) {
        acc[tagValue] = {
          tag_value: tagValue,
          resources: [],
          total_cost: 0,
          count: 0
        };
      }
      acc[tagValue].resources.push(item);
      acc[tagValue].total_cost += item.cost_amount;
      acc[tagValue].count += 1;
      return acc;
    }, {} as Record<string, any>);

    return Object.values(groups).sort((a: any, b: any) => b.total_cost - a.total_cost);
  };

  const metrics = calculateMetrics();
  const groupedPreview = groupByTagValue();

  if (loadingTag) {
    return (
      <Dashboard>
        <div className="flex-1 w-full">
          <div className="p-4">
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          </div>
        </div>
      </Dashboard>
    );
  }

  if (!virtualTag) {
    return (
      <Dashboard>
        <div className="flex-1 w-full">
          <div className="p-4">
            <Alert>
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>
                Virtual Tag não encontrada.
              </AlertDescription>
            </Alert>
          </div>
        </div>
      </Dashboard>
    );
  }

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <div className="p-4 space-y-6">
          <PageHeader 
            icon={Eye}
            title={`Preview: ${virtualTag.name}`}
            description="Visualize como a alocação será aplicada antes de processar"
          />

      <div className="flex items-center justify-between">
        <Button 
          variant="ghost" 
          onClick={() => navigate('/virtual-tags')}
          className="mb-4"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Voltar para Virtual Tags
        </Button>

        <div className="flex items-center gap-4">
          <DatePickerWithRange
            value={{
              from: new Date(dateRange.start_date),
              to: new Date(dateRange.end_date)
            }}
            onChange={(range) => {
              if (range?.from && range?.to) {
                setDateRange({
                  start_date: range.from.toISOString().split('T')[0],
                  end_date: range.to.toISOString().split('T')[0]
                });
              }
            }}
          />
          
          <Button 
            onClick={handleRunPreview}
            disabled={loading}
            className="min-w-[140px]"
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Gerando...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Gerar Preview
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Tag Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            Informações da Virtual Tag
            <Badge variant={virtualTag.is_active ? "default" : "secondary"}>
              {virtualTag.is_active ? 'Ativa' : 'Inativa'}
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Categoria</p>
              <p className="font-medium">{virtualTag.category}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Prioridade</p>
              <p className="font-medium">{virtualTag.priority}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Regras</p>
              <p className="font-medium">{virtualTag.rules.length} regras</p>
            </div>
          </div>
          {virtualTag.description && (
            <div className="mt-4">
              <p className="text-sm text-muted-foreground">Descrição</p>
              <p className="text-sm">{virtualTag.description}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {error && (
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {preview && (
        <>
          {/* Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <Database className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Total de Recursos</p>
                </div>
                <p className="text-2xl font-bold">{metrics.totalResources.toLocaleString()}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Custo Total</p>
                </div>
                <p className="text-2xl font-bold">{formatCurrency(metrics.totalCost)}</p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Recursos Cobertos</p>
                </div>
                <p className="text-2xl font-bold">{metrics.coveredResources.toLocaleString()}</p>
                <p className="text-xs text-muted-foreground">
                  de {metrics.totalResources.toLocaleString()} recursos
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-2">
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">Cobertura</p>
                </div>
                <p className="text-2xl font-bold">{metrics.coveragePercentage.toFixed(1)}%</p>
                <div className="mt-2">
                  <Progress value={metrics.coveragePercentage} className="h-2" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Results by Tag Value */}
          <Card>
            <CardHeader>
              <CardTitle>Alocação por Valor da Tag</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Valor da Tag</TableHead>
                    <TableHead className="text-right">Recursos</TableHead>
                    <TableHead className="text-right">Custo Total</TableHead>
                    <TableHead className="text-right">% do Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {groupedPreview.map((group: any, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {group.tag_value === 'untagged' ? (
                            <Badge variant="outline">Não Alocado</Badge>
                          ) : (
                            <Badge>{group.tag_value}</Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-right">{group.count.toLocaleString()}</TableCell>
                      <TableCell className="text-right">{formatCurrency(group.total_cost)}</TableCell>
                      <TableCell className="text-right">
                        {metrics.totalCost > 0 ? ((group.total_cost / metrics.totalCost) * 100).toFixed(1) : 0}%
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>

          {/* Detailed Results */}
          <Card>
            <CardHeader>
              <CardTitle>Detalhes da Alocação</CardTitle>
              <p className="text-sm text-muted-foreground">
                Mostrando os primeiros 100 recursos. Total: {preview.length} recursos.
              </p>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Recurso</TableHead>
                    <TableHead>Serviço</TableHead>
                    <TableHead>Valor da Tag</TableHead>
                    <TableHead>Regra Aplicada</TableHead>
                    <TableHead className="text-right">Custo</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {preview.slice(0, 100).map((item, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-mono text-xs">
                        {item.resource_id || 'N/A'}
                      </TableCell>
                      <TableCell>{item.service_name || 'N/A'}</TableCell>
                      <TableCell>
                        {item.tag_value ? (
                          item.tag_value === 'untagged' ? (
                            <Badge variant="outline">Não Alocado</Badge>
                          ) : (
                            <Badge variant="secondary">{item.tag_value}</Badge>
                          )
                        ) : (
                          <Badge variant="outline">Não Alocado</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {item.rule_applied ? (
                          <Badge variant="default" className="text-xs">
                            {item.rule_applied}
                          </Badge>
                        ) : (
                          <span className="text-muted-foreground text-xs">Nenhuma</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">{formatCurrency(item.cost_amount)}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </>
      )}

      {!preview && !loading && (
        <Card>
          <CardContent className="p-12 text-center">
            <div className="mx-auto w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-4">
              <Play className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Gerar Preview</h3>
            <p className="text-muted-foreground mb-4">
              Selecione um período e clique em "Gerar Preview" para visualizar como a alocação será aplicada.
            </p>
            <Button onClick={handleRunPreview} disabled={loading}>
              <Play className="h-4 w-4 mr-2" />
              Gerar Preview
            </Button>
          </CardContent>
        </Card>
      )}
        </div>
      </div>
    </Dashboard>
  );
};

export default VirtualTagPreview;
