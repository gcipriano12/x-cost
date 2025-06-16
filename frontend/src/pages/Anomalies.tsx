import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { useSearchParams } from 'react-router-dom';
import { AlertTriangle, RefreshCw, Download, BarChart3 } from 'lucide-react';
import { useAnomalies } from '@/hooks/useOptimization';
import { AnomaliesFilters } from '@/components/dashboard/AnomaliesFilters';
import { AnomaliesTable } from '@/components/dashboard/AnomaliesTable';
import { AnomalyDetailsModal } from '@/components/dashboard/AnomalyDetailsModal';
import { CloudAnomaly, AnomaliesFilters as AnomaliesFiltersType, SeverityLevel } from '@/types/optimization';
import { formatCurrency } from '@/utils/optimizationUtils';
import { useToast } from '@/hooks/use-toast';

const Anomalies = () => {
  const { toast } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State management
  const [filters, setFilters] = React.useState<AnomaliesFiltersType>({
    days: 30,
    page: 1,
    per_page: 25
  });
  const [selectedAnomaly, setSelectedAnomaly] = React.useState<CloudAnomaly | null>(null);
  const [selectedItems, setSelectedItems] = React.useState<string[]>([]);
  const [sortColumn, setSortColumn] = React.useState<string>('detected_at');
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('desc');
  const [isInitialized, setIsInitialized] = React.useState(false);
  
  // Initialize filters from URL params (only once)
  React.useEffect(() => {
    if (isInitialized) return;
    
    const urlFilters: Partial<AnomaliesFiltersType> = {};
    
    if (searchParams.get('provider')) urlFilters.provider = searchParams.get('provider')!;
    if (searchParams.get('severity')) urlFilters.severity = searchParams.get('severity') as SeverityLevel;
    if (searchParams.get('service')) urlFilters.service_name = searchParams.get('service')!;
    if (searchParams.get('days')) urlFilters.days = parseInt(searchParams.get('days')!);
    if (searchParams.get('search')) urlFilters.search = searchParams.get('search')!;
    if (searchParams.get('page')) urlFilters.page = parseInt(searchParams.get('page')!);
    
    if (Object.keys(urlFilters).length > 0) {
      setFilters(prev => ({ ...prev, ...urlFilters }));
    }
    setIsInitialized(true);
  }, [searchParams, isInitialized]);
  
  // Fetch anomalies data
  const { 
    data: anomalies = [], 
    total,
    loading, 
    error, 
    refetch,
    pagination
  } = useAnomalies({
    ...filters,
    // Add sorting to the filters
    sort_by: sortColumn,
    sort_order: sortDirection
  });
  
  // Calculate summary statistics
  const totalImpact = anomalies.reduce((sum, anomaly) => sum + anomaly.cost_impact, 0);
  const severityCounts = anomalies.reduce((counts, anomaly) => {
    counts[anomaly.severity] = (counts[anomaly.severity] || 0) + 1;
    return counts;
  }, {} as Record<string, number>);

  // Handlers
  const handleFiltersChange = React.useCallback((newFilters: Partial<AnomaliesFiltersType>) => {
    const updatedFilters = { ...filters, ...newFilters, page: 1 }; // Reset to page 1 when filters change
    setFilters(updatedFilters);
    
    // Update URL params only if initialized to prevent loops
    if (isInitialized) {
      const newSearchParams = new URLSearchParams();
      Object.entries(updatedFilters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          newSearchParams.set(key, value.toString());
        }
      });
      setSearchParams(newSearchParams, { replace: true });
    }
  }, [filters, isInitialized, setSearchParams]);
  
  const handleResetFilters = React.useCallback(() => {
    const resetFilters = { days: 30, page: 1, per_page: 25 };
    setFilters(resetFilters);
    if (isInitialized) {
      setSearchParams({}, { replace: true });
    }
  }, [isInitialized, setSearchParams]);
  
  const handleSort = React.useCallback((column: string, direction: 'asc' | 'desc') => {
    setSortColumn(column);
    setSortDirection(direction);
  }, []);
  
  const handlePageChange = React.useCallback((page: number) => {
    handleFiltersChange({ page });
  }, [handleFiltersChange]);
  
  const handlePageSizeChange = React.useCallback((pageSize: number) => {
    handleFiltersChange({ per_page: pageSize, page: 1 });
  }, [handleFiltersChange]);
  
  const handleViewDetails = React.useCallback((anomaly: CloudAnomaly) => {
    setSelectedAnomaly(anomaly);
  }, []);
  
  const handleCloseModal = React.useCallback(() => {
    setSelectedAnomaly(null);
  }, []);
  
  const handleExport = React.useCallback(() => {
    // Generate CSV data
    const csvData = anomalies.map(anomaly => ({
      id: anomaly.id,
      provider: anomaly.provider,
      service: anomaly.service,
      region: anomaly.region || '',
      severity: anomaly.severity,
      type: anomaly.anomaly_type,
      description: anomaly.description,
      cost_impact: anomaly.cost_impact,
      currency: anomaly.currency,
      detected_at: anomaly.detected_at,
      root_cause: anomaly.root_cause || '',
      affected_resources: anomaly.affected_resources.join(';')
    }));
    
    // Convert to CSV
    const headers = Object.keys(csvData[0] || {});
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => headers.map(header => 
        JSON.stringify(row[header as keyof typeof row] || '')
      ).join(','))
    ].join('\n');
    
    // Download
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `anomalies-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Export completed",
      description: "Anomalies data exported to CSV",
    });
  }, [anomalies, toast]);
  
  const handleBulkAction = React.useCallback((action: string, items: string[]) => {
    // Placeholder for bulk actions
    toast({
      title: `Bulk action: ${action}`,
      description: `Applied to ${items.length} anomalies`,
    });
    setSelectedItems([]);
  }, [toast]);

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={AlertTriangle} 
          title="Anomalies Detection" 
          color="text-amber-500"
        />
        
        <div className="p-6 space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                  <span className="text-sm font-medium">Total</span>
                </div>
                <div className="text-2xl font-bold">{total || 0}</div>
              </CardContent>
            </Card>
            
            {['critical', 'high', 'medium', 'low'].map((severity) => (
              <Card key={severity}>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2">
                    <div className={cn(
                      "h-2 w-2 rounded-full",
                      severity === 'critical' ? 'bg-red-500' :
                      severity === 'high' ? 'bg-orange-500' :
                      severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    )} />
                    <span className="text-sm font-medium capitalize">{severity}</span>
                  </div>
                  <div className="text-2xl font-bold">{severityCounts[severity] || 0}</div>
                </CardContent>
              </Card>
            ))}
          </div>
          
          {/* Total Impact */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5 text-red-500" />
                  <span className="font-medium">Total Cost Impact</span>
                </div>
                <div className="text-2xl font-bold text-red-600">
                  {formatCurrency(totalImpact, 'USD', 'en-US', true)}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Filters */}
          <AnomaliesFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onReset={handleResetFilters}
            totalCount={total}
            isLoading={loading}
          />

          {/* Header Actions */}
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Anomalies List</h2>
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={refetch} disabled={loading}>
                <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
                Refresh
              </Button>
              <Button variant="outline" onClick={handleExport} disabled={loading || !anomalies.length}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Table */}
          <AnomaliesTable
            data={anomalies}
            loading={loading}
            error={error}
            totalCount={total || 0}
            currentPage={pagination?.page || 1}
            pageSize={pagination?.per_page || 25}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
            onSort={handleSort}
            sortColumn={sortColumn}
            sortDirection={sortDirection}
            selectedItems={selectedItems}
            onSelectionChange={setSelectedItems}
            onViewDetails={handleViewDetails}
            onExport={handleExport}
            onBulkAction={handleBulkAction}
          />
        </div>
        
        {/* Details Modal */}
        <AnomalyDetailsModal
          anomaly={selectedAnomaly}
          open={!!selectedAnomaly}
          onClose={handleCloseModal}
          onDismiss={(id) => {
            toast({
              title: "Anomaly dismissed",
              description: `Anomaly ${id} has been dismissed`,
            });
          }}
          onMarkResolved={(id) => {
            toast({
              title: "Anomaly resolved",
              description: `Anomaly ${id} has been marked as resolved`,
            });
          }}
        />
      </div>
    </Dashboard>
  );
};

export default Anomalies;