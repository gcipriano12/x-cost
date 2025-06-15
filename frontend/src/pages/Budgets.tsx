import React, { useState, useMemo, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import Dashboard from '@/components/dashboard/Dashboard';
import { PageHeader } from '@/components/layout/PageHeader';
import { LineChart, Plus, Search, AlertTriangle, CheckCircle, AlertCircle, Edit, Trash2, Eye, Power, PowerOff, RefreshCw, Filter, Target, DollarSign, TrendingUp, BarChart3, ArrowUpDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  AlertDialog, 
  AlertDialogAction, 
  AlertDialogCancel, 
  AlertDialogContent, 
  AlertDialogDescription, 
  AlertDialogFooter, 
  AlertDialogHeader, 
  AlertDialogTitle, 
  AlertDialogTrigger 
} from '@/components/ui/alert-dialog';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { useBudgets, BudgetResponse, BudgetCreate, BudgetUpdate } from '@/hooks/useBudgets';
import { BudgetFormDialog } from '@/components/dashboard/BudgetFormDialog';
import { BudgetDetailsDialog } from '@/components/dashboard/BudgetDetailsDialog';
import { getProviderColor } from '@/utils/providerColors';

const formatCurrency = (amount: string | number) => {
  const value = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

const getStatusInfo = (budget: BudgetResponse, isActive: boolean = true) => {
  if (!isActive) {
    return {
      status: 'inactive',
      color: 'text-red-600 dark:text-red-400',
      bgColor: 'bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800',
      icon: <AlertCircle className="h-4 w-4" />
    };
  }

  // For active budgets, we'll show based on basic info
  // Real consumption status will be shown in details dialog
  return {
    status: 'active',
    color: 'text-green-600 dark:text-green-400',
    bgColor: 'bg-green-50 dark:bg-green-950/20 border-green-200 dark:border-green-800',
    icon: <CheckCircle className="h-4 w-4" />
  };
};

const BudgetStatusBadge = ({ budget }: { budget: BudgetResponse }) => {
  const { t } = useTranslation();
  const statusInfo = getStatusInfo(budget, budget.is_active);
  
  return (
    <Badge 
      variant="outline" 
      className={cn("text-xs", statusInfo.color, statusInfo.bgColor)}
    >
      {statusInfo.icon}
      <span className="ml-1">
        {budget.is_active ? t('budgets.status.active') : t('budgets.status.inactive')}
      </span>
    </Badge>
  );
};

const ProviderDisplay = ({ provider }: { provider: string | null }) => {
  const { t } = useTranslation();
  const displayProvider = provider || t('common.all');
  const providerColor = getProviderColor(displayProvider);
  
  return (
    <Badge 
      className="text-white border-0 font-medium"
      style={{ backgroundColor: providerColor }}
    >
      {displayProvider}
    </Badge>
  );
};

const Budgets = () => {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // API Integration
  const [filters, setFilters] = useState({
    provider_name: '',
    service_name: '',
    is_active: undefined as boolean | undefined
  });
  
  const {
    budgets,
    totalCount,
    totalBudgetAmount,
    totalConsumption,
    overallConsumptionPercentage,
    // Active budget summaries
    activeBudgetCount,
    activeBudgetAmount,
    activeBudgetConsumption,
    activeBudgetConsumptionPercentage,
    loading,
    error,
    createBudget,
    updateBudget,
    deleteBudget,
    getBudgetConsumption,
    getBudgetAlerts,
    activateBudget,
    deactivateBudget,
    refreshBudgets
  } = useBudgets(filters);

  // UI State
  const [searchQuery, setSearchQuery] = useState('');
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedBudget, setSelectedBudget] = useState<BudgetResponse | null>(null);
  const [budgetToDelete, setBudgetToDelete] = useState<BudgetResponse | null>(null);
  
  // Sorting state
  const [sortField, setSortField] = useState<keyof BudgetResponse | ''>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Filter, search and sort budgets
  const filteredBudgets = useMemo(() => {
    let filtered = budgets.filter(budget => {
      const matchesSearch = searchQuery === '' || 
        budget.budget_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        budget.provider_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
        budget.service_name?.toLowerCase().includes(searchQuery.toLowerCase());
      
      return matchesSearch;
    });

    // Apply sorting
    if (sortField) {
      filtered = [...filtered].sort((a, b) => {
        let aValue = a[sortField];
        let bValue = b[sortField];
        
        // Handle null/undefined values
        if (aValue == null) aValue = '';
        if (bValue == null) bValue = '';
        
        // Special handling for numeric fields
        if (sortField === 'budget_amount' || sortField === 'alert_threshold') {
          const aNum = parseFloat(aValue.toString());
          const bNum = parseFloat(bValue.toString());
          const aNumValue = isNaN(aNum) ? 0 : aNum;
          const bNumValue = isNaN(bNum) ? 0 : bNum;
          
          if (aNumValue < bNumValue) return sortDirection === 'asc' ? -1 : 1;
          if (aNumValue > bNumValue) return sortDirection === 'asc' ? 1 : -1;
          return 0;
        }
        
        // Special handling for date fields
        if (sortField === 'created_at') {
          const aDate = new Date(aValue.toString());
          const bDate = new Date(bValue.toString());
          
          if (aDate < bDate) return sortDirection === 'asc' ? -1 : 1;
          if (aDate > bDate) return sortDirection === 'asc' ? 1 : -1;
          return 0;
        }
        
        // Special handling for boolean fields
        if (sortField === 'is_active') {
          const aBool = aValue === true ? 1 : 0;
          const bBool = bValue === true ? 1 : 0;
          
          if (aBool < bBool) return sortDirection === 'asc' ? -1 : 1;
          if (aBool > bBool) return sortDirection === 'asc' ? 1 : -1;
          return 0;
        }
        
        // Convert to string for comparison (for text fields)
        if (typeof aValue === 'string' && typeof bValue === 'string') {
          aValue = aValue.toLowerCase();
          bValue = bValue.toLowerCase();
        }
        
        if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
        return 0;
      });
    }

    return filtered;
  }, [budgets, searchQuery, sortField, sortDirection]);

  const handleCreateBudget = async (data: BudgetCreate) => {
    await createBudget(data);
  };

  const handleUpdateBudget = async (data: BudgetUpdate) => {
    if (selectedBudget) {
      await updateBudget(selectedBudget.id, data);
      setSelectedBudget(null);
    }
  };

  const handleDeleteBudget = (budget: BudgetResponse) => {
    setBudgetToDelete(budget);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteBudget = async () => {
    if (budgetToDelete) {
      await deleteBudget(budgetToDelete.id);
      setBudgetToDelete(null);
      setDeleteDialogOpen(false);
    }
  };

  const cancelDeleteBudget = () => {
    setBudgetToDelete(null);
    setDeleteDialogOpen(false);
  };

  const handleToggleBudgetStatus = async (budget: BudgetResponse) => {
    if (budget.is_active) {
      await deactivateBudget(budget.id);
    } else {
      await activateBudget(budget.id);
    }
  };

  const handleViewDetails = (budget: BudgetResponse) => {
    setSelectedBudget(budget);
    setDetailsDialogOpen(true);
  };

  const handleEditBudget = (budget: BudgetResponse) => {
    setSelectedBudget(budget);
    setEditDialogOpen(true);
  };

  const handleFilterChange = (key: string, value: string | boolean | undefined) => {
    setFilters(prev => ({
      ...prev,
      [key]: value === 'all' ? undefined : value
    }));
  };

  const handleSort = (field: keyof BudgetResponse) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const SortableTableHead = ({ field, children }: { field?: keyof BudgetResponse; children: React.ReactNode }) => {
    if (!field) {
      return <TableHead className="text-center">{children}</TableHead>;
    }
    
    return (
      <TableHead 
        className="text-center cursor-pointer hover:bg-muted/50 select-none"
        onClick={() => handleSort(field)}
      >
        <div className="flex items-center justify-center gap-1">
          {children}
          <ArrowUpDown className={cn(
            "h-3 w-3 transition-colors",
            sortField === field ? "text-blue-600" : "text-muted-foreground"
          )} />
        </div>
      </TableHead>
    );
  };

  // Update selectedBudget when budgets list changes (after activate/deactivate)
  useEffect(() => {
    if (selectedBudget && budgets.length > 0) {
      const updatedBudget = budgets.find(b => b.id === selectedBudget.id);
      if (updatedBudget) {
        setSelectedBudget(updatedBudget);
      }
    }
  }, [budgets, selectedBudget]);

  const overallProgress = parseFloat(activeBudgetConsumptionPercentage) || 0;

  // Debug: verificar estado de autenticação
  console.log('🔍 [Budgets] Debug auth state:', {
    loading,
    error,
    budgetsCount: budgets.length,
    totalCount,
    activeBudgetCount,
    activeBudgetAmount,
    activeBudgetConsumption,
    activeBudgetConsumptionPercentage,
    token: localStorage.getItem('access_token') ? 'Present' : 'Missing'
  });

  if (loading) {
    return (
      <Dashboard>
        <div className="flex-1 w-full">
          <PageHeader 
            icon={LineChart} 
            title="Budgets" 
            color="text-[#0080af]"
            showTimeFilter={false}
          />
          <div className="p-4 flex items-center justify-center h-64">
            <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        </div>
      </Dashboard>
    );
  }

  return (
    <Dashboard>
      <div className="flex-1 w-full">
        <PageHeader 
          icon={LineChart} 
          title={t('budgets.page.title')}
          color="text-[#0080af]"
          showTimeFilter={false}
          actions={
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={refreshBudgets}
                disabled={loading}
              >
                <RefreshCw className={cn("mr-2 h-4 w-4", loading && "animate-spin")} />
                {t('budgets.page.refresh')}
              </Button>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                {t('budgets.page.newBudget')}
              </Button>
            </div>
          }
        />
        
        {error && (
          <div className="p-4">
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          </div>
        )}
        
        <div className="p-4 space-y-6">
          {/* Overall Budget Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="border-l-4 border-l-blue-500 bg-gradient-to-r from-blue-50 to-white dark:from-blue-950/50 dark:to-background">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <Target className="h-4 w-4 text-blue-500" />
                  {t('budgets.summary.totalBudgets')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{activeBudgetCount}</div>
              </CardContent>
            </Card>
            <Card className="border-l-4 border-l-green-500 bg-gradient-to-r from-green-50 to-white dark:from-green-950/50 dark:to-background">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-green-500" />
                  {t('budgets.summary.totalBudgetAmount')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">{formatCurrency(activeBudgetAmount)}</div>
              </CardContent>
            </Card>
            <Card className="border-l-4 border-l-amber-500 bg-gradient-to-r from-amber-50 to-white dark:from-amber-950/50 dark:to-background">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-amber-500" />
                  {t('budgets.summary.totalConsumption')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-amber-600 dark:text-amber-400">{formatCurrency(activeBudgetConsumption)}</div>
              </CardContent>
            </Card>
            <Card className={cn(
              "border-l-4 bg-gradient-to-r to-white dark:to-background",
              overallProgress > 90 
                ? "border-l-red-500 from-red-50 dark:from-red-950/50" 
                : overallProgress > 70 
                  ? "border-l-orange-500 from-orange-50 dark:from-orange-950/50"
                  : "border-l-purple-500 from-purple-50 dark:from-purple-950/50"
            )}>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                  <BarChart3 className={cn(
                    "h-4 w-4",
                    overallProgress > 90 
                      ? "text-red-500" 
                      : overallProgress > 70 
                        ? "text-orange-500"
                        : "text-purple-500"
                  )} />
                  {t('budgets.summary.overallProgress')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className={cn(
                    "text-2xl font-bold",
                    overallProgress > 90 
                      ? "text-red-600 dark:text-red-400" 
                      : overallProgress > 70 
                        ? "text-orange-600 dark:text-orange-400"
                        : "text-purple-600 dark:text-purple-400"
                  )}>{overallProgress.toFixed(1)}%</div>
                  <Progress 
                    value={overallProgress} 
                    className="h-2"
                    progressColor={cn(
                      overallProgress > 90 
                        ? "bg-red-500" 
                        : overallProgress > 70 
                          ? "bg-orange-500"
                          : "bg-purple-500"
                    )}
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Budgets Table */}
          <Card>
            <CardHeader className="pb-2">
              <div className="flex flex-wrap justify-between items-center gap-4">
                <CardTitle className="text-lg font-medium">{t('budgets.table.title')}</CardTitle>
                <div className="flex gap-2">
                  <div className="relative">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder={t('budgets.table.search')}
                      className="w-[250px] pl-9"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                  <Select 
                    value={filters.provider_name || 'all'} 
                    onValueChange={(value) => handleFilterChange('provider_name', value)}
                  >
                    <SelectTrigger className="w-[200px]">
                      <SelectValue placeholder="Provider" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">{t('budgets.table.filters.allProviders')}</SelectItem>
                      <SelectItem value="AWS">AWS</SelectItem>
                      <SelectItem value="Azure">Azure</SelectItem>
                      <SelectItem value="GCP">GCP</SelectItem>
                      <SelectItem value="Oracle Cloud">Oracle Cloud</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select 
                    value={filters.is_active === undefined ? 'all' : filters.is_active.toString()} 
                    onValueChange={(value) => handleFilterChange('is_active', value === 'all' ? undefined : value === 'true')}
                  >
                    <SelectTrigger className="w-[160px]">
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">{t('budgets.table.filters.allStatus')}</SelectItem>
                      <SelectItem value="true">{t('budgets.table.filters.active')}</SelectItem>
                      <SelectItem value="false">{t('budgets.table.filters.inactive')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <SortableTableHead field="is_active">{t('budgets.table.columns.status')}</SortableTableHead>
                      <SortableTableHead field="budget_name">{t('budgets.table.columns.budgetName')}</SortableTableHead>
                      <SortableTableHead field="provider_name">{t('budgets.table.columns.provider')}</SortableTableHead>
                      <SortableTableHead field="service_name">{t('budgets.table.columns.service')}</SortableTableHead>
                      <SortableTableHead field="budget_amount">{t('budgets.table.columns.budgetAmount')}</SortableTableHead>
                      <SortableTableHead field="budget_period">{t('budgets.table.columns.period')}</SortableTableHead>
                      <SortableTableHead field="created_at">{t('budgets.table.columns.created')}</SortableTableHead>
                      <SortableTableHead>{t('budgets.table.columns.actions')}</SortableTableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredBudgets.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                          {searchQuery || filters.provider_name || filters.service_name || filters.is_active !== undefined
                            ? t('budgets.table.noResults')
                            : t('budgets.table.noData')
                          }
                        </TableCell>
                      </TableRow>
                    ) : (
                      filteredBudgets.map((budget) => (
                        <TableRow key={budget.id}>
                          <TableCell className="text-center">
                            <BudgetStatusBadge budget={budget} />
                          </TableCell>
                          <TableCell className="text-center font-medium">{budget.budget_name}</TableCell>
                          <TableCell className="text-center">
                            <ProviderDisplay provider={budget.provider_name} />
                          </TableCell>
                          <TableCell className="text-center">{budget.service_name || t('common.all')}</TableCell>
                          <TableCell className="text-center">{formatCurrency(budget.budget_amount)}</TableCell>
                          <TableCell className="text-center">{t(`budgets.table.periods.${budget.budget_period}`)}</TableCell>
                          <TableCell className="text-center">{formatDate(budget.created_at)}</TableCell>
                          <TableCell className="text-center">
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button 
                                  variant="default" 
                                  size="sm"
                                  className="bg-blue-600 hover:bg-blue-700 text-white shadow-md"
                                >
                                  <Edit className="mr-1 h-3 w-3" />
                                  {t('budgets.table.manageButton')}
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => handleViewDetails(budget)}>
                                  <Eye className="mr-2 h-4 w-4" />
                                  {t('budgets.table.actions.viewDetails')}
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleEditBudget(budget)}>
                                  <Edit className="mr-2 h-4 w-4" />
                                  {t('budgets.table.actions.edit')}
                                </DropdownMenuItem>
                                <DropdownMenuItem onClick={() => handleToggleBudgetStatus(budget)}>
                                  {budget.is_active ? (
                                    <>
                                      <PowerOff className="mr-2 h-4 w-4" />
                                      {t('budgets.table.actions.deactivate')}
                                    </>
                                  ) : (
                                    <>
                                      <Power className="mr-2 h-4 w-4" />
                                      {t('budgets.table.actions.activate')}
                                    </>
                                  )}
                                </DropdownMenuItem>
                                <DropdownMenuItem 
                                  onClick={() => handleDeleteBudget(budget)}
                                  className="text-destructive"
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  {t('budgets.table.actions.delete')}
                                </DropdownMenuItem>
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Dialog Components */}
        <BudgetFormDialog
          open={createDialogOpen}
          onOpenChange={setCreateDialogOpen}
          onSubmit={handleCreateBudget}
          mode="create"
        />

        <BudgetFormDialog
          open={editDialogOpen}
          onOpenChange={setEditDialogOpen}
          onSubmit={handleUpdateBudget}
          mode="edit"
          budget={selectedBudget || undefined}
        />

        <BudgetDetailsDialog
          open={detailsDialogOpen}
          onOpenChange={setDetailsDialogOpen}
          budget={selectedBudget}
          onGetConsumption={getBudgetConsumption}
          onGetAlerts={getBudgetAlerts}
          onActivate={activateBudget}
          onDeactivate={deactivateBudget}
        />

        {/* Delete Confirmation Dialog */}
        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle className="flex items-center gap-2">
                <Trash2 className="h-5 w-5 text-destructive" />
                {t('budgets.deleteDialog.title')}
              </AlertDialogTitle>
              <AlertDialogDescription>
                {budgetToDelete && (
                  <>
                    <div className="mb-3">
                      {t('budgets.deleteDialog.description').split('{budgetName}').join(budgetToDelete.budget_name)}
                    </div>
                    <div className="mt-3 p-3 bg-muted rounded-lg">
                      <div className="text-sm font-medium">{budgetToDelete.budget_name}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {budgetToDelete.provider_name && (
                          <span>{t('budgets.form.fields.cloudProvider')}: {budgetToDelete.provider_name} • </span>
                        )}
                        {budgetToDelete.service_name && (
                          <span>{t('budgets.form.fields.service')}: {budgetToDelete.service_name} • </span>
                        )}
                        <span>{t('budgets.form.fields.budgetAmount')}: {formatCurrency(budgetToDelete.budget_amount)}</span>
                      </div>
                    </div>
                  </>
                )}
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel onClick={cancelDeleteBudget}>
                {t('budgets.deleteDialog.cancelButton')}
              </AlertDialogCancel>
              <AlertDialogAction 
                onClick={confirmDeleteBudget}
                className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                {t('budgets.deleteDialog.confirmButton')}
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </Dashboard>
  );
};

export default Budgets;
