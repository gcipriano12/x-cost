import React, { useRef, useEffect } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import { Skeleton } from '@/components/ui/skeleton';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  ArrowUpDown,
  ArrowUp,
  ArrowDown,
  Eye,
  Search,
  FileText,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  Download,
  MoreHorizontal,
  Plus,
  Play,
  DollarSign,
  TrendingUp,
  Clock,
  Shield,
  Target
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { SavingsOpportunity } from '@/types/optimization';
import { formatCurrency, formatRelativeTime } from '@/utils/optimizationUtils';

interface SavingsTableProps {
  data: SavingsOpportunity[];
  loading?: boolean;
  error?: string | null;
  totalCount: number;
  currentPage: number;
  pageSize: number;
  onPageChange: (page: number) => void;
  onPageSizeChange: (size: number) => void;
  onSort: (column: string, direction: 'asc' | 'desc') => void;
  sortColumn?: string;
  sortDirection?: 'asc' | 'desc';
  selectedItems: string[];
  onSelectionChange: (selected: string[]) => void;
  onViewDetails: (opportunity: SavingsOpportunity) => void;
  onExport?: () => void;
  onBulkAction?: (action: string, items: string[]) => void;
}

type SortableColumn = 'title' | 'provider' | 'category' | 'monthly_savings' | 'annual_savings' | 'confidence_level' | 'implementation_effort' | 'risk_level' | 'detected_at';

const COLUMNS: { 
  key: SortableColumn; 
  label: string; 
  sortable: boolean; 
  width?: string;
}[] = [
  { key: 'title', label: 'Opportunity', sortable: true },
  { key: 'provider', label: 'Provider', sortable: true, width: 'w-24' },
  { key: 'category', label: 'Category', sortable: true, width: 'w-32' },
  { key: 'monthly_savings', label: 'Monthly', sortable: true, width: 'w-32' },
  { key: 'annual_savings', label: 'Annual', sortable: true, width: 'w-32' },
  { key: 'confidence_level', label: 'Confidence', sortable: true, width: 'w-24' },
  { key: 'implementation_effort', label: 'Effort', sortable: true, width: 'w-24' },
  { key: 'risk_level', label: 'Risk', sortable: true, width: 'w-24' },
];

const categoryColors = {
  compute: 'bg-blue-500',
  storage: 'bg-green-500', 
  network: 'bg-purple-500',
  database: 'bg-orange-500',
  security: 'bg-red-500',
  monitoring: 'bg-yellow-500',
  reserved_instances: 'bg-indigo-500'
} as const;

const providerColors = {
  AWS: 'bg-orange-400',
  Azure: 'bg-blue-500',
  GCP: 'bg-green-500',
  Oracle: 'bg-red-500'
} as const;

const confidenceColors = {
  high: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200', 
  low: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
} as const;

const effortColors = {
  low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
} as const;

const riskColors = {
  low: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
  high: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
} as const;

const PAGE_SIZES = [10, 20, 50, 100];

const calculateROI = (monthlySavings: number, implementationHours: number) => {
  const annualSavings = monthlySavings * 12;
  const implementationCost = implementationHours * 100;
  if (implementationCost === 0) return 0;
  return ((annualSavings - implementationCost) / implementationCost) * 100;
};

export function SavingsTable({
  data,
  loading = false,
  error,
  totalCount,
  currentPage,
  pageSize,
  onPageChange,
  onPageSizeChange,
  onSort,
  sortColumn,
  sortDirection,
  selectedItems,
  onSelectionChange,
  onViewDetails,
  onExport,
  onBulkAction
}: SavingsTableProps) {
  const { isDark } = useTheme();
  const selectAllCheckboxRef = useRef<HTMLButtonElement>(null);

  const totalPages = Math.ceil(totalCount / pageSize);
  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalCount);

  const handleSort = (column: SortableColumn) => {
    if (sortColumn === column) {
      const newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      onSort(column, newDirection);
    } else {
      const newDirection = ['monthly_savings', 'annual_savings'].includes(column) ? 'desc' : 'asc';
      onSort(column, newDirection);
    }
  };

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      onSelectionChange(data.map(item => item.id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelectItem = (itemId: string, checked: boolean) => {
    if (checked) {
      onSelectionChange([...selectedItems, itemId]);
    } else {
      onSelectionChange(selectedItems.filter(id => id !== itemId));
    }
  };

  const getSortIcon = (column: SortableColumn) => {
    if (sortColumn !== column) {
      return <ArrowUpDown className="ml-2 h-4 w-4 text-muted-foreground" />;
    }
    return sortDirection === 'asc' 
      ? <ArrowUp className="ml-2 h-4 w-4" />
      : <ArrowDown className="ml-2 h-4 w-4" />;
  };

  const isAllSelected = data.length > 0 && selectedItems.length === data.length;
  const isPartiallySelected = selectedItems.length > 0 && selectedItems.length < data.length;

  useEffect(() => {
    if (selectAllCheckboxRef.current) {
      const checkbox = selectAllCheckboxRef.current.querySelector('input[type="checkbox"]') as HTMLInputElement;
      if (checkbox) {
        checkbox.indeterminate = isPartiallySelected;
      }
    }
  }, [isPartiallySelected]);

  // Loading state
  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-8 w-32" />
        </div>
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Skeleton className="h-4 w-4" />
                </TableHead>
                {COLUMNS.map((column) => (
                  <TableHead key={column.key}>
                    <Skeleton className="h-4 w-20" />
                  </TableHead>
                ))}
                <TableHead className="w-20">
                  <Skeleton className="h-4 w-16" />
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {[...Array(5)].map((_, i) => (
                <TableRow key={i}>
                  <TableCell>
                    <Skeleton className="h-4 w-4" />
                  </TableCell>
                  {COLUMNS.map((column) => (
                    <TableCell key={column.key}>
                      <Skeleton className="h-4 w-full" />
                    </TableCell>
                  ))}
                  <TableCell>
                    <Skeleton className="h-4 w-16" />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="border rounded-lg p-8 text-center">
        <div className="text-muted-foreground mb-4">
          <FileText className="h-12 w-12 mx-auto mb-2" />
          <p>Error loading opportunities</p>
          <p className="text-sm">{error}</p>
        </div>
      </div>
    );
  }

  // Empty state
  if (!data.length) {
    return (
      <div className="border rounded-lg p-8 text-center">
        <div className="text-muted-foreground mb-4">
          <DollarSign className="h-12 w-12 mx-auto mb-2" />
          <p className="text-lg font-medium">No savings opportunities found</p>
          <p className="text-sm">Try adjusting your filters or check back later</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header with bulk actions and export */}
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          {selectedItems.length > 0 && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                {selectedItems.length} selected
              </span>
              {onBulkAction && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      Actions
                      <MoreHorizontal className="ml-2 h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem 
                      onClick={() => onBulkAction('add_to_plan', selectedItems)}
                    >
                      <Plus className="mr-2 h-4 w-4" />
                      Add to Plan
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => onBulkAction('implement', selectedItems)}
                    >
                      <Play className="mr-2 h-4 w-4" />
                      Start Implementation
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => onBulkAction('export', selectedItems)}
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Export Selected
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            {startItem}-{endItem} of {totalCount}
          </span>
          {onExport && (
            <Button variant="outline" size="sm" onClick={onExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className={isDark ? "border-slate-700" : "border-slate-200"}>
                <TableHead className="w-12">
                  <Checkbox
                    ref={selectAllCheckboxRef}
                    checked={isAllSelected}
                    onCheckedChange={handleSelectAll}
                    aria-label="Select all opportunities"
                  />
                </TableHead>
                {COLUMNS.map((column) => (
                  <TableHead 
                    key={column.key} 
                    className={cn(column.width, column.sortable && "cursor-pointer select-none")}
                    onClick={column.sortable ? () => handleSort(column.key) : undefined}
                  >
                    <div className="flex items-center">
                      {column.label}
                      {column.sortable && getSortIcon(column.key)}
                    </div>
                  </TableHead>
                ))}
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((opportunity) => {
                const isSelected = selectedItems.includes(opportunity.id);
                const annualSavings = opportunity.monthly_savings * 12;
                const roi = calculateROI(opportunity.monthly_savings, opportunity.implementation_effort_hours);
                
                const categoryColor = categoryColors[opportunity.category as keyof typeof categoryColors] || 'bg-gray-500';
                const providerColor = providerColors[opportunity.provider as keyof typeof providerColors] || 'bg-gray-500';
                const confidenceColor = confidenceColors[opportunity.confidence_level as keyof typeof confidenceColors];
                const effortColor = effortColors[opportunity.implementation_effort as keyof typeof effortColors];
                const riskColor = riskColors[opportunity.risk_level as keyof typeof riskColors];

                return (
                  <TableRow 
                    key={opportunity.id}
                    className={cn(
                      "cursor-pointer",
                      isSelected && (isDark ? "bg-slate-800" : "bg-slate-50"),
                      isDark ? "border-slate-700 hover:bg-slate-800/50" : "border-slate-200 hover:bg-slate-50"
                    )}
                    onClick={() => onViewDetails(opportunity)}
                  >
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={(checked) => handleSelectItem(opportunity.id, checked as boolean)}
                        aria-label={`Select opportunity ${opportunity.id}`}
                      />
                    </TableCell>
                    
                    {/* Opportunity Title */}
                    <TableCell>
                      <div className="max-w-md">
                        <p className="font-medium text-sm line-clamp-1">
                          {opportunity.title}
                        </p>
                        <p className="text-xs text-muted-foreground line-clamp-1">
                          {opportunity.description}
                        </p>
                        <div className="flex items-center gap-1 mt-1">
                          {opportunity.implementation_effort === 'low' && opportunity.risk_level === 'low' && (
                            <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                              Quick Win
                            </Badge>
                          )}
                          {roi > 300 && (
                            <Badge variant="secondary" className="text-xs bg-blue-100 text-blue-800">
                              High ROI
                            </Badge>
                          )}
                        </div>
                      </div>
                    </TableCell>

                    {/* Provider */}
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className={cn("h-2 w-2 rounded-full", providerColor)} />
                        <span className="font-medium text-sm">{opportunity.provider}</span>
                      </div>
                    </TableCell>

                    {/* Category */}
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className={cn("h-2 w-2 rounded-full", categoryColor)} />
                        <span className="font-medium text-sm capitalize">
                          {opportunity.category.replace('_', ' ')}
                        </span>
                      </div>
                    </TableCell>

                    {/* Monthly Savings */}
                    <TableCell>
                      <div className="text-right">
                        <div className="font-medium text-sm">
                          {formatCurrency(opportunity.monthly_savings, opportunity.currency, 'en-US', true)}
                        </div>
                      </div>
                    </TableCell>

                    {/* Annual Savings */}
                    <TableCell>
                      <div className="text-right">
                        <div className="font-medium text-sm text-green-600">
                          {formatCurrency(annualSavings, opportunity.currency, 'en-US', true)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          ROI: {roi > 1000 ? '1000%+' : `${Math.round(roi)}%`}
                        </div>
                      </div>
                    </TableCell>

                    {/* Confidence */}
                    <TableCell>
                      <Badge className={cn("text-xs", confidenceColor)}>
                        {opportunity.confidence_level}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {Math.round(opportunity.confidence_score)}%
                      </div>
                    </TableCell>

                    {/* Effort */}
                    <TableCell>
                      <Badge className={cn("text-xs", effortColor)}>
                        <Clock className="h-3 w-3 mr-1" />
                        {opportunity.implementation_effort}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {opportunity.implementation_effort_hours}h
                      </div>
                    </TableCell>

                    {/* Risk */}
                    <TableCell>
                      <Badge className={cn("text-xs", riskColor)}>
                        <Shield className="h-3 w-3 mr-1" />
                        {opportunity.risk_level}
                      </Badge>
                    </TableCell>

                    {/* Actions */}
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onViewDetails(opportunity)}
                          className="h-8 w-8 p-0"
                          title="View details"
                        >
                          <Eye className="h-4 w-4" />
                          <span className="sr-only">View details</span>
                        </Button>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-8 w-8 p-0"
                            >
                              <MoreHorizontal className="h-4 w-4" />
                              <span className="sr-only">More actions</span>
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => onBulkAction?.('add_to_plan', [opportunity.id])}>
                              <Plus className="mr-2 h-4 w-4" />
                              Add to Plan
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => onBulkAction?.('implement', [opportunity.id])}>
                              <Play className="mr-2 h-4 w-4" />
                              Implement
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </div>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Rows per page:</span>
          <Select value={pageSize.toString()} onValueChange={(value) => onPageSizeChange(parseInt(value))}>
            <SelectTrigger className="w-20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {PAGE_SIZES.map((size) => (
                <SelectItem key={size} value={size.toString()}>
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(1)}
            disabled={currentPage === 1}
          >
            <ChevronsLeft className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage === 1}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          <span className="text-sm text-muted-foreground px-2">
            Page {currentPage} of {totalPages}
          </span>
          
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage === totalPages}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onPageChange(totalPages)}
            disabled={currentPage === totalPages}
          >
            <ChevronsRight className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}