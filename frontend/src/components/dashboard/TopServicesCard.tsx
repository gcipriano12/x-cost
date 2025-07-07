import { useTranslation } from 'react-i18next';
import { TrendingUp, TrendingDown, BarChart2, ArrowUpRight, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';
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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ProviderBadge } from '@/components/ui/provider-badge';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

interface ServiceData {
  id: string;
  name: string;
  provider: string;
  currentSpend: number;
  previousSpend: number;
  trend: number;
}

interface TopServicesCardProps {
  services: ServiceData[];
  currency: string;
  isUsingMockData?: boolean;
  totalServices?: number;
  currentPage?: number;
  pageSize?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  onPageSizeChange?: (size: number) => void;
}

// Page size options following the same pattern as Anomalies and Savings
const PAGE_SIZES = [5, 10, 25, 50];

export function TopServicesCard({ 
  services, 
  currency, 
  isUsingMockData = false,
  totalServices = 0,
  currentPage = 1,
  pageSize = 5,
  totalPages = 1,
  onPageChange,
  onPageSizeChange
}: TopServicesCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  // Show pagination only if there are more services than page size
  const shouldShowPagination = totalServices > pageSize;
  
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
        <div>
        <Table>
            <TableHeader className={cn(
              "sticky top-0 z-10",
              isDark ? "bg-slate-800" : "bg-gray-50"
            )}>
            <TableRow>
                <TableHead className="text-center font-medium text-xs">{t('topServices.service')}</TableHead>
                <TableHead className="text-center font-medium text-xs">{t('topServices.provider')}</TableHead>
                <TableHead className="text-center font-medium text-xs">{t('topServices.currentSpend')}</TableHead>
                <TableHead className="text-center font-medium text-xs">{t('topServices.variation')}</TableHead>
                <TableHead className="text-center font-medium text-xs w-24">Action</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {services.map((service) => {
              const isIncrease = service.trend > 0;
              
              return (
                  <TableRow key={service.id} className={cn(
                    isDark ? "hover:bg-slate-800/70" : "hover:bg-gray-50"
                  )}>
                    <TableCell className="text-center font-medium py-3 text-sm">{service.name}</TableCell>
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
                  <TableCell>
                      <Button 
                        variant="ghost" 
                        size="sm" 
                        className={cn(
                          "h-8 text-xs w-full flex items-center justify-center",
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
        </div>
        
        {/* Pagination Section */}
        {shouldShowPagination && onPageChange && onPageSizeChange && (
          <div className="flex items-center justify-between p-4 border-t">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Rows per page:</span>
              <Select 
                value={pageSize.toString()} 
                onValueChange={(value) => onPageSizeChange(parseInt(value))}
              >
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
        )}
      </CardContent>
    </Card>
  );
}
