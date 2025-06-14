import React from 'react';
import { useTranslation } from 'react-i18next';
import { TrendingUp, TrendingDown, BarChart2, ArrowUpRight } from 'lucide-react';
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
import { Badge } from '@/components/ui/badge';
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
}

export function TopServicesCard({ services, currency }: TopServicesCardProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  
  const formatCurrency = (value: number) => {
    if (value >= 1000000) {
      return `${currency} ${(value / 1000000).toFixed(2)}M`;
    } else if (value >= 1000) {
      return `${currency} ${(value / 1000).toFixed(2)}K`;
    }
    return `${currency} ${value.toLocaleString('pt-BR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    })}`;
  };

  const getProviderColor = (provider: string) => {
    switch(provider.toLowerCase()) {
      case 'aws': 
        return isDark 
          ? 'bg-amber-900/50 text-amber-100 border-amber-800' 
          : 'bg-amber-50 text-amber-700 border-amber-200';
      case 'azure': 
        return isDark 
          ? 'bg-blue-900/50 text-blue-100 border-blue-800' 
          : 'bg-blue-50 text-blue-700 border-blue-200';
      case 'gcp': 
        return isDark 
          ? 'bg-emerald-900/50 text-emerald-100 border-emerald-800' 
          : 'bg-emerald-50 text-emerald-700 border-emerald-200';
      default: 
        return isDark 
          ? 'bg-slate-800 text-slate-300 border-slate-700' 
          : 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center text-lg font-medium">
          <BarChart2 className={cn("mr-2 h-5 w-5", isDark ? "text-blue-400" : "text-XCost-blue")} />
          {t('topServices.title')}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="h-[358px] overflow-y-auto">
        <Table>
            <TableHeader className={cn(
              "sticky top-0 z-10",
              isDark ? "bg-slate-800" : "bg-gray-50"
            )}>
            <TableRow>
                <TableHead className="font-medium text-xs">{t('topServices.service')}</TableHead>
                <TableHead className="font-medium text-xs">{t('topServices.provider')}</TableHead>
                <TableHead className="text-right font-medium text-xs">{t('topServices.currentSpend')}</TableHead>
                <TableHead className="text-right font-medium text-xs">{t('topServices.variation')}</TableHead>
                <TableHead className="w-24"></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {services.map((service) => {
              const isIncrease = service.trend > 0;
              
              return (
                  <TableRow key={service.id} className={cn(
                    isDark ? "hover:bg-slate-800/70" : "hover:bg-gray-50"
                  )}>
                    <TableCell className="font-medium py-3 text-sm">{service.name}</TableCell>
                    <TableCell>
                      <Badge 
                        variant="outline" 
                        className={`font-normal text-xs ${getProviderColor(service.provider)}`}
                      >
                        {service.provider}
                      </Badge>
                    </TableCell>
                  <TableCell className="text-right">
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
                            <p>{currency} {service.currentSpend.toLocaleString('pt-BR', {
                              minimumFractionDigits: 2,
                              maximumFractionDigits: 2
                            })}</p>
                          </TooltipContent>
                        </Tooltip>
                      </TooltipProvider>
                  </TableCell>
                  <TableCell className="text-right">
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
      </CardContent>
    </Card>
  );
}
