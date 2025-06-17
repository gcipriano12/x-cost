import React from 'react';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import { useSearchParams } from 'react-router-dom';
import { DollarSign, RefreshCw, Download, TrendingUp, Zap, Target } from 'lucide-react';
import { useSavingsOpportunities } from '@/hooks/useOptimization';
import { SavingsFilters } from '@/components/savings/SavingsFilters';
import { SavingsTable } from '@/components/savings/SavingsTable';
import { SavingsOpportunityCard } from '@/components/savings/SavingsOpportunityCard';
import { SavingsDetailModal } from '@/components/savings/SavingsDetailModal';
import { SavingsOpportunity, SavingsFilters as SavingsFiltersType } from '@/types/optimization';
import { formatCurrency } from '@/utils/optimizationUtils';
import { useToast } from '@/hooks/use-toast';
import { Toggle } from '@/components/ui/toggle';
import { Grid, List } from 'lucide-react';

const SavingsOpportunities = () => {
  const { toast } = useToast();
  const [searchParams, setSearchParams] = useSearchParams();
  
  // State management
  const [filters, setFilters] = React.useState<SavingsFiltersType>({
    days: 30,
    page: 1,
    per_page: 20
  });
  const [selectedOpportunity, setSelectedOpportunity] = React.useState<SavingsOpportunity | null>(null);
  const [selectedItems, setSelectedItems] = React.useState<string[]>([]);
  const [sortColumn, setSortColumn] = React.useState<string>('monthly_savings');
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>('desc');
  const [viewMode, setViewMode] = React.useState<'grid' | 'table'>('grid');
  const [isInitialized, setIsInitialized] = React.useState(false);
  
  // Initialize filters from URL params (only once)
  React.useEffect(() => {
    if (isInitialized) return;
    
    const urlFilters: Partial<SavingsFiltersType> = {};
    
    if (searchParams.get('provider')) urlFilters.provider = searchParams.get('provider')!;
    if (searchParams.get('category')) urlFilters.category = searchParams.get('category')!;
    if (searchParams.get('confidence_level')) urlFilters.confidence_level = searchParams.get('confidence_level')!;
    if (searchParams.get('days')) urlFilters.days = parseInt(searchParams.get('days')!);
    if (searchParams.get('search')) urlFilters.search = searchParams.get('search')!;
    if (searchParams.get('page')) urlFilters.page = parseInt(searchParams.get('page')!);
    if (searchParams.get('min_savings')) urlFilters.min_savings = parseFloat(searchParams.get('min_savings')!);
    if (searchParams.get('max_savings')) urlFilters.max_savings = parseFloat(searchParams.get('max_savings')!);
    if (searchParams.get('view')) setViewMode(searchParams.get('view') as 'grid' | 'table');
    
    if (Object.keys(urlFilters).length > 0) {
      setFilters(prev => ({ ...prev, ...urlFilters }));
    }
    setIsInitialized(true);
  }, [searchParams, isInitialized]);
  
  // Fetch savings opportunities data
  const { 
    data: opportunities = [], 
    total,
    loading, 
    error, 
    refetch,
    pagination
  } = useSavingsOpportunities({
    ...filters,
    sort_by: sortColumn,
    sort_order: sortDirection
  });
  
  // Calculate summary statistics
  const totalMonthlySavings = opportunities.reduce((sum, opp) => sum + opp.monthly_savings, 0);
  const totalAnnualSavings = totalMonthlySavings * 12;
  const highROICount = opportunities.filter(opp => {
    const roi = ((opp.monthly_savings * 12) / (opp.implementation_effort_hours * 100)) * 100;
    return roi > 300;
  }).length;
  const quickWinsCount = opportunities.filter(opp => 
    opp.implementation_effort === 'low' && opp.risk_level === 'low'
  ).length;
  
  const confidenceCounts = opportunities.reduce((counts, opp) => {
    counts[opp.confidence_level] = (counts[opp.confidence_level] || 0) + 1;
    return counts;
  }, {} as Record<string, number>);

  // Handlers
  const handleFiltersChange = React.useCallback((newFilters: Partial<SavingsFiltersType>) => {
    const updatedFilters = { ...filters, ...newFilters, page: 1 };
    setFilters(updatedFilters);
    
    if (isInitialized) {
      const newSearchParams = new URLSearchParams();
      Object.entries(updatedFilters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          newSearchParams.set(key, value.toString());
        }
      });
      newSearchParams.set('view', viewMode);
      setSearchParams(newSearchParams, { replace: true });
    }
  }, [filters, isInitialized, setSearchParams, viewMode]);
  
  const handleResetFilters = React.useCallback(() => {
    const resetFilters = { days: 30, page: 1, per_page: 20 };
    setFilters(resetFilters);
    if (isInitialized) {
      setSearchParams({ view: viewMode }, { replace: true });
    }
  }, [isInitialized, setSearchParams, viewMode]);
  
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
  
  const handleViewDetails = React.useCallback((opportunity: SavingsOpportunity) => {
    setSelectedOpportunity(opportunity);
  }, []);
  
  const handleCloseModal = React.useCallback(() => {
    setSelectedOpportunity(null);
  }, []);
  
  const handleViewModeChange = React.useCallback((mode: 'grid' | 'table') => {
    setViewMode(mode);
    if (isInitialized) {
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set('view', mode);
      setSearchParams(newSearchParams, { replace: true });
    }
  }, [isInitialized, searchParams, setSearchParams]);
  
  const handleExport = React.useCallback(() => {
    const csvData = opportunities.map(opp => ({
      id: opp.id,
      title: opp.title,
      provider: opp.provider,
      category: opp.category,
      monthly_savings: opp.monthly_savings,
      annual_savings: opp.monthly_savings * 12,
      confidence_level: opp.confidence_level,
      implementation_effort: opp.implementation_effort,
      risk_level: opp.risk_level,
      currency: opp.currency,
      description: opp.description,
      affected_resources: opp.affected_resources.length,
      detected_at: opp.detected_at
    }));
    
    const headers = Object.keys(csvData[0] || {});
    const csvContent = [
      headers.join(','),
      ...csvData.map(row => headers.map(header => 
        JSON.stringify(row[header as keyof typeof row] || '')
      ).join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `savings-opportunities-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: "Export completed",
      description: "Savings opportunities exported to CSV",
    });
  }, [opportunities, toast]);
  
  const handleBulkAction = React.useCallback((action: string, items: string[]) => {
    toast({
      title: `Bulk action: ${action}`,
      description: `Applied to ${items.length} opportunities`,
    });
    setSelectedItems([]);
  }, [toast]);

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={DollarSign} 
          title="Savings Opportunities" 
          color="text-green-500"
        />
        
        <div className="p-6 space-y-6">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-green-500" />
                  <span className="text-sm font-medium">Total Opportunities</span>
                </div>
                <div className="text-2xl font-bold">{total || 0}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-medium">Monthly Savings</span>
                </div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(totalMonthlySavings, 'USD', 'en-US', true)}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4 text-orange-500" />
                  <span className="text-sm font-medium">High ROI</span>
                </div>
                <div className="text-2xl font-bold">{highROICount}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-purple-500" />
                  <span className="text-sm font-medium">Quick Wins</span>
                </div>
                <div className="text-2xl font-bold">{quickWinsCount}</div>
              </CardContent>
            </Card>
          </div>
          
          {/* Annual Savings Card */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-green-500" />
                  <span className="font-medium">Total Annual Savings Potential</span>
                </div>
                <div className="text-2xl font-bold text-green-600">
                  {formatCurrency(totalAnnualSavings, 'USD', 'en-US', true)}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Filters */}
          <SavingsFilters
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onReset={handleResetFilters}
            totalCount={total}
            isLoading={loading}
          />

          {/* Header Actions */}
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Opportunities</h2>
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1 border rounded-md p-1">
                <Toggle
                  pressed={viewMode === 'grid'}
                  onPressedChange={() => handleViewModeChange('grid')}
                  aria-label="Grid view"
                  size="sm"
                >
                  <Grid className="h-4 w-4" />
                </Toggle>
                <Toggle
                  pressed={viewMode === 'table'}
                  onPressedChange={() => handleViewModeChange('table')}
                  aria-label="Table view"
                  size="sm"
                >
                  <List className="h-4 w-4" />
                </Toggle>
              </div>
              <Button variant="outline" onClick={refetch} disabled={loading}>
                <RefreshCw className={cn("h-4 w-4 mr-2", loading && "animate-spin")} />
                Refresh
              </Button>
              <Button variant="outline" onClick={handleExport} disabled={loading || !opportunities.length}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>

          {/* Content based on view mode */}
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {loading ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <Card key={i} className="animate-pulse">
                    <CardContent className="p-4">
                      <div className="h-4 bg-gray-200 rounded mb-2"></div>
                      <div className="h-8 bg-gray-200 rounded mb-4"></div>
                      <div className="h-3 bg-gray-200 rounded mb-2"></div>
                      <div className="h-3 bg-gray-200 rounded"></div>
                    </CardContent>
                  </Card>
                ))
              ) : error ? (
                <div className="col-span-full text-center py-8">
                  <p className="text-red-600">Error loading opportunities: {error}</p>
                  <Button onClick={refetch} className="mt-2">
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Retry
                  </Button>
                </div>
              ) : opportunities.length === 0 ? (
                <div className="col-span-full text-center py-8">
                  <DollarSign className="h-12 w-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600">No savings opportunities found</p>
                  <p className="text-sm text-gray-500">Try adjusting your filters</p>
                </div>
              ) : (
                opportunities.map((opportunity) => (
                  <SavingsOpportunityCard
                    key={opportunity.id}
                    opportunity={opportunity}
                    onViewDetails={handleViewDetails}
                    onAddToPlan={(id) => toast({ title: "Added to plan", description: `Opportunity ${id} added to implementation plan` })}
                    onImplement={(id) => toast({ title: "Implementation started", description: `Started implementing opportunity ${id}` })}
                  />
                ))
              )}
            </div>
          ) : (
            <SavingsTable
              data={opportunities}
              loading={loading}
              error={error}
              totalCount={total || 0}
              currentPage={pagination?.page || 1}
              pageSize={pagination?.per_page || 20}
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
          )}
          
          {/* Pagination for grid view */}
          {viewMode === 'grid' && opportunities.length > 0 && (
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-600">
                Showing {((pagination?.page || 1) - 1) * (pagination?.per_page || 20) + 1} to{' '}
                {Math.min((pagination?.page || 1) * (pagination?.per_page || 20), total || 0)} of {total || 0} opportunities
              </p>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange((pagination?.page || 1) - 1)}
                  disabled={!pagination?.page || pagination.page <= 1}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange((pagination?.page || 1) + 1)}
                  disabled={!pagination?.page || pagination.page >= (pagination?.total_pages || 1)}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
        
        {/* Details Modal */}
        <SavingsDetailModal
          opportunity={selectedOpportunity}
          open={!!selectedOpportunity}
          onClose={handleCloseModal}
          onAddToPlan={(id) => {
            toast({
              title: "Added to plan",
              description: `Opportunity ${id} has been added to implementation plan`,
            });
          }}
          onImplement={(id) => {
            toast({
              title: "Implementation started",
              description: `Started implementing opportunity ${id}`,
            });
          }}
        />
      </div>
    </Dashboard>
  );
};

export default SavingsOpportunities;