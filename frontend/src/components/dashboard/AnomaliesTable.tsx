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
  MoreHorizontal
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { CloudAnomaly } from '@/types/optimization';
import { 
  formatSeverity, 
  formatCloudProvider, 
  formatCurrency, 
  formatRelativeTime 
} from '@/utils/optimizationUtils';

interface AnomaliesTableProps {
  data: CloudAnomaly[];
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
  onViewDetails: (anomaly: CloudAnomaly) => void;
  onExport?: () => void;
  onBulkAction?: (action: string, items: string[]) => void;
}

type SortableColumn = 'severity' | 'provider' | 'service' | 'cost_impact' | 'detected_at';

const COLUMNS: { 
  key: SortableColumn; 
  label: string; 
  sortable: boolean; 
  width?: string;
}[] = [
  { key: 'severity', label: 'Status', sortable: true, width: 'w-24' },
  { key: 'provider', label: 'Provider', sortable: true, width: 'w-32' },
  { key: 'service', label: 'Service', sortable: true, width: 'w-32' },
  { key: 'cost_impact', label: 'Cost Impact', sortable: true, width: 'w-32' },
  { key: 'detected_at', label: 'Detected', sortable: true, width: 'w-32' },
];

const PAGE_SIZES = [10, 25, 50, 100];

export function AnomaliesTable({
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
}: AnomaliesTableProps) {
  const { isDark } = useTheme();
  const selectAllCheckboxRef = useRef<HTMLButtonElement>(null);

  const totalPages = Math.ceil(totalCount / pageSize);
  const startItem = (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalCount);

  const handleSort = (column: SortableColumn) => {
    if (sortColumn === column) {
      // Toggle direction
      const newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      onSort(column, newDirection);
    } else {
      // New column, start with desc for cost_impact, asc for others
      const newDirection = column === 'cost_impact' ? 'desc' : 'asc';
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

  // Set indeterminate state for select all checkbox
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
          <p>Error loading anomalies</p>
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
          <Search className="h-12 w-12 mx-auto mb-2" />
          <p className="text-lg font-medium">No anomalies found</p>
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
                      onClick={() => onBulkAction('mark_reviewed', selectedItems)}
                    >
                      Mark as Reviewed
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => onBulkAction('dismiss', selectedItems)}
                    >
                      Dismiss Selected
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => onBulkAction('export', selectedItems)}
                    >
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
                    aria-label="Select all anomalies"
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
                <TableHead>Description</TableHead>
                <TableHead className="w-20">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((anomaly) => {
                const severityStyle = formatSeverity(anomaly.severity);
                const providerStyle = formatCloudProvider(anomaly.provider);
                const isSelected = selectedItems.includes(anomaly.id);

                return (
                  <TableRow 
                    key={anomaly.id}
                    className={cn(
                      "cursor-pointer",
                      isSelected && (isDark ? "bg-slate-800" : "bg-slate-50"),
                      isDark ? "border-slate-700 hover:bg-slate-800/50" : "border-slate-200 hover:bg-slate-50"
                    )}
                    onClick={() => onViewDetails(anomaly)}
                  >
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        checked={isSelected}
                        onCheckedChange={(checked) => handleSelectItem(anomaly.id, checked as boolean)}
                        aria-label={`Select anomaly ${anomaly.id}`}
                      />
                    </TableCell>
                    
                    {/* Status */}
                    <TableCell>
                      <Badge className={cn("text-xs", severityStyle.color)}>
                        {severityStyle.icon} {severityStyle.label}
                      </Badge>
                    </TableCell>

                    {/* Provider */}
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className={cn("h-2 w-2 rounded-full", providerStyle.color)} />
                        <span className="font-medium">{anomaly.provider}</span>
                      </div>
                    </TableCell>

                    {/* Service */}
                    <TableCell>
                      <span className="font-medium">{anomaly.service}</span>
                      {anomaly.region && (
                        <div className="text-xs text-muted-foreground">{anomaly.region}</div>
                      )}
                    </TableCell>

                    {/* Cost Impact */}
                    <TableCell>
                      <div className="text-right">
                        <div className="font-medium">
                          {formatCurrency(anomaly.cost_impact, anomaly.currency, 'en-US', true)}
                        </div>
                      </div>
                    </TableCell>

                    {/* Detected Date */}
                    <TableCell>
                      <div className="text-sm">
                        {formatRelativeTime(anomaly.detected_at)}
                      </div>
                    </TableCell>

                    {/* Description */}
                    <TableCell>
                      <div className="max-w-md">
                        <p className="font-medium text-sm line-clamp-1">
                          {anomaly.anomaly_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </p>
                        <p className="text-xs text-muted-foreground line-clamp-2">
                          {anomaly.description}
                        </p>
                      </div>
                    </TableCell>

                    {/* Actions */}
                    <TableCell onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onViewDetails(anomaly)}
                          className="h-8 w-8 p-0"
                        >
                          <Eye className="h-4 w-4" />
                          <span className="sr-only">View details</span>
                        </Button>
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