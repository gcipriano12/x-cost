import { useTranslation } from 'react-i18next';
import { TrendingUp, TrendingDown, BarChart2, ArrowUpRight, ChevronLeft, ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Button } from '@/components/ui/button';
import { MockDataBadge } from '@/components/ui/mock-data-badge';
import { ProviderBadge } from '@/components/ui/provider-badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';
import { useState, useMemo } from 'react';

interface ServiceData {
  id: string;
  name: string;
  provider: string;
  currentSpend: number;
  previousSpend: number;
  trend: number;
}

type SortField = 'name' | 'provider' | 'currentSpend' | 'trend';
type SortDirection = 'asc' | 'desc' | null;

interface TopServicesCardProps {
  services: ServiceData[];
  currency: string;
  isUsingMockData?: boolean;
  totalServices?: number;
  currentPage?: number;
  pageSize?: number;
  totalPages?: number;
  hasNext?: boolean;
  hasPrevious?: boolean;
  onPageChange?: (page: number) => void;
  sortBy?: string;
  sortOrder?: string;
  onSortChange?: (sortBy: string, sortOrder: string) => void;
}


export function TopServicesCard({ 
  services, 
  currency, 
  isUsingMockData = false,
  totalServices = 0,
  currentPage = 1,
  pageSize = 10,
  totalPages = 1,
  hasNext = false,
  hasPrevious = false,
  onPageChange,
  sortBy = 'cost',
  sortOrder = 'desc',
  onSortChange
}: TopServicesCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Mapeamento de campos para backend
  const backendFieldMapping: Record<SortField, string> = {
    'name': 'service_name',
    'provider': 'provider',
    'currentSpend': 'cost',
    'trend': 'change_from_previous'
  };
  
  // Função para alterar ordenação (notifica o componente pai)
  const handleSort = (field: SortField) => {
    const backendField = backendFieldMapping[field];
    
    if (sortBy === backendField) {
      // Se já está ordenando por este campo, alternar direção
      const newOrder = sortOrder === 'desc' ? 'asc' : 'desc';
      onSortChange?.(backendField, newOrder);
    } else {
      // Novo campo, começar com desc para custo/trend, asc para nome/provider
      const newOrder = (field === 'currentSpend' || field === 'trend') ? 'desc' : 'asc';
      onSortChange?.(backendField, newOrder);
    }
  };
  
  // Função para obter ícone de ordenação
  const getSortIcon = (field: SortField) => {
    const backendField = backendFieldMapping[field];
    
    if (sortBy !== backendField) {
      return <ArrowUpDown className="h-3 w-3 opacity-50" />;
    }
    if (sortOrder === 'desc') {
      return <ArrowDown className="h-3 w-3" />;
    }
    if (sortOrder === 'asc') {
      return <ArrowUp className="h-3 w-3" />;
    }
    return <ArrowUpDown className="h-3 w-3 opacity-50" />;
  };
  
  // Para compatibilidade com ordenação local (quando não há callback)
  const [localSortField, setLocalSortField] = useState<SortField>('currentSpend');
  const [localSortDirection, setLocalSortDirection] = useState<SortDirection>('desc');
  
  const handleLocalSort = (field: SortField) => {
    if (localSortField === field) {
      setLocalSortDirection(prev => {
        if (prev === 'desc') return 'asc';
        if (prev === 'asc') return null;
        return 'desc';
      });
    } else {
      setLocalSortField(field);
      setLocalSortDirection(field === 'currentSpend' || field === 'trend' ? 'desc' : 'asc');
    }
  };
  
  const getLocalSortIcon = (field: SortField) => {
    if (localSortField !== field) {
      return <ArrowUpDown className="h-3 w-3 opacity-50" />;
    }
    if (localSortDirection === 'desc') {
      return <ArrowDown className="h-3 w-3" />;
    }
    if (localSortDirection === 'asc') {
      return <ArrowUp className="h-3 w-3" />;
    }
    return <ArrowUpDown className="h-3 w-3 opacity-50" />;
  };
  
  // Serviços ordenados localmente (quando não há backend sorting)
  const localSortedServices = useMemo(() => {
    if (onSortChange || !localSortDirection || !localSortField) {
      return services; // Use backend sorting ou dados originais
    }
    
    return [...services].sort((a, b) => {
      let aValue: string | number;
      let bValue: string | number;
      
      switch (localSortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'provider':
          aValue = a.provider.toLowerCase();
          bValue = b.provider.toLowerCase();
          break;
        case 'currentSpend':
          aValue = a.currentSpend;
          bValue = b.currentSpend;
          break;
        case 'trend':
          aValue = a.trend;
          bValue = b.trend;
          break;
        default:
          return 0;
      }
      
      if (localSortDirection === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });
  }, [services, localSortField, localSortDirection, onSortChange]);
  
  // Usar serviços do backend (se disponível) ou ordenação local
  const displayServices = onSortChange ? services : localSortedServices;
  const currentSortHandler = onSortChange ? handleSort : handleLocalSort;
  const currentIconGetter = onSortChange ? getSortIcon : getLocalSortIcon;
  
  // Enable pagination now that backend supports it
  const shouldShowPagination = totalPages > 1 && onPageChange;
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency}${(value / 1000000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}M`;
    } else if (value >= 1000) {
      return `${currency}${(value / 1000).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })}K`;
    }
    return `${currency}${value.toLocaleString('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };


  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center text-lg font-medium">
            <BarChart2 className={cn("mr-2 h-5 w-5", isDark ? "text-blue-400" : "text-XCost-blue")} />
            {t('topServices.title')}
          </CardTitle>
          {isUsingMockData && <MockDataBadge />}
        </div>
      </CardHeader>
      <CardContent className="p-0">
        {services.length === 0 && !isUsingMockData && (
          <div className="flex items-center justify-center h-48 text-center p-4">
            <div className="text-muted-foreground">
              <p className="text-sm">No services data available.</p>
              <p className="text-xs mt-1">Configure AWS credentials to view real cost data.</p>
            </div>
          </div>
        )}
        
        {services.length === 0 && isUsingMockData && (
          <div className="flex items-center justify-center h-48 text-center p-4">
            <div className="text-muted-foreground">
              <p className="text-sm">Loading services data...</p>
              <p className="text-xs mt-1">Please configure AWS credentials in Settings.</p>
            </div>
          </div>
        )}
        
        {services.length > 0 && (
        <>
        <Table>
            <TableHeader className={cn(
              "sticky top-0 z-10",
              isDark ? "bg-slate-800" : "bg-gray-50"
            )}>
            <TableRow>
                <TableHead className="text-center font-medium text-xs h-10 py-2 px-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-1 font-medium text-xs hover:bg-transparent"
                    onClick={() => currentSortHandler('name')}
                  >
                    <span className="flex items-center gap-1">
                      {t('topServices.service')}
                      {currentIconGetter('name')}
                    </span>
                  </Button>
                </TableHead>
                <TableHead className="text-center font-medium text-xs h-10 py-2 px-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-1 font-medium text-xs hover:bg-transparent"
                    onClick={() => currentSortHandler('provider')}
                  >
                    <span className="flex items-center gap-1">
                      {t('topServices.provider')}
                      {currentIconGetter('provider')}
                    </span>
                  </Button>
                </TableHead>
                <TableHead className="text-center font-medium text-xs h-10 py-2 px-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-1 font-medium text-xs hover:bg-transparent"
                    onClick={() => currentSortHandler('currentSpend')}
                  >
                    <span className="flex items-center gap-1">
                      {t('topServices.currentSpend')}
                      {currentIconGetter('currentSpend')}
                    </span>
                  </Button>
                </TableHead>
                <TableHead className="text-center font-medium text-xs h-10 py-2 px-3">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-auto p-1 font-medium text-xs hover:bg-transparent"
                    onClick={() => currentSortHandler('trend')}
                  >
                    <span className="flex items-center gap-1">
                      {t('topServices.variation')}
                      {currentIconGetter('trend')}
                    </span>
                  </Button>
                </TableHead>
                <TableHead className="text-center font-medium text-xs w-24 h-10 py-2 px-3">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayServices.map((service) => {
              const isIncrease = service.trend > 0;
              
              return (
                  <TableRow key={service.id} className={cn(
                    "h-12",
                    isDark ? "hover:bg-slate-800/70" : "hover:bg-gray-50"
                  )}>
                    <TableCell className="text-center font-medium text-sm">{service.name}</TableCell>
                    <TableCell className="text-center">
                      <ProviderBadge 
                        provider={service.provider}
                        size="xs"
                      />
                    </TableCell>
                  <TableCell className="text-center">
                      <TooltipProvider>
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <span className="font-medium cursor-help">
                              {formatCurrency(service.currentSpend)}
                            </span>
                          </TooltipTrigger>
                          <TooltipContent className={cn(
                            isDark ? "bg-slate-800 border-slate-700 text-white" : "bg-white border-gray-200 text-slate-900"
                          )}>
                            <p>{currency}{service.currentSpend.toLocaleString('en-US', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            })}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                  </TableCell>
                  <TableCell className="text-center">
                      <span className={cn(
                        "inline-flex items-center px-2 py-1 rounded-full text-xs font-medium",
                        isIncrease 
                          ? isDark 
                            ? "bg-red-900/50 border border-red-800 text-red-400" 
                            : "bg-red-50 text-XCost-red" 
                          : isDark 
                            ? "bg-green-900/50 border border-green-800 text-green-400" 
                            : "bg-green-50 text-XCost-green"
                      )}>
                        {isIncrease ? (
                          <TrendingUp className="h-3 w-3 mr-1 flex-shrink-0" />
                        ) : (
                          <TrendingDown className="h-3 w-3 mr-1 flex-shrink-0" />
                        )}
                        {Math.abs(service.trend)}%
                    </span>
                  </TableCell>
                  <TableCell className="py-2 px-3">
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className={cn(
                          "h-7 text-xs w-full flex items-center justify-center",
                          isDark ? "text-blue-400" : "text-XCost-blue"
                        )}
                      >
                        <span className="mr-1">{t('topServices.details')}</span>
                        <ArrowUpRight className="h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
        
        {/* Pagination Section - Complete implementation */}
        {shouldShowPagination && (
          <div className="flex items-center justify-between p-4 border-t">
            {/* Page info */}
            <div className="text-sm text-muted-foreground">
              Showing {((currentPage - 1) * pageSize) + 1}-{Math.min(currentPage * pageSize, totalServices)} of {totalServices} services
            </div>
            
            {/* Pagination controls */}
            <div className="flex items-center gap-2">
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onPageChange?.(currentPage - 1)} 
                disabled={!hasPrevious}
                className="h-8"
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              
              <span className="text-sm text-muted-foreground px-3">
                Page {currentPage} of {totalPages}
              </span>
              
              <Button 
                variant="outline" 
                size="sm" 
                onClick={() => onPageChange?.(currentPage + 1)} 
                disabled={!hasNext}
                className="h-8"
              >
                Next
                <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            </div>
          </div>
        )}
        </>
        )}
      </CardContent>
    </Card>
  );
}
