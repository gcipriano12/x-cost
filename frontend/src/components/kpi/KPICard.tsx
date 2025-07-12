import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Info,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Circle
} from 'lucide-react';
import { KPIValue } from '@/types/kpi.types';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';

interface KPICardProps {
  kpi: KPIValue;
  onClick?: () => void;
  compact?: boolean;
}

export const KPICard: React.FC<KPICardProps> = ({ kpi, onClick, compact = false }) => {
  const { isDark } = useTheme();
  
  // Ícone de status
  const StatusIcon = {
    good: CheckCircle,
    warning: AlertTriangle,
    critical: XCircle,
    neutral: Circle
  }[kpi.status];
  
  // Cor do status
  const statusColor = {
    good: 'text-green-500',
    warning: 'text-yellow-500',
    critical: 'text-red-500',
    neutral: 'text-gray-500'
  }[kpi.status];
  
  // Ícone de tendência
  const TrendIcon = (kpi.trend && typeof kpi.trend === 'number' && kpi.trend > 0) ? TrendingUp : 
                   (kpi.trend && typeof kpi.trend === 'number' && kpi.trend < 0) ? TrendingDown : Minus;
  
  // Cor da tendência baseada em is_good_when_higher
  const getTrendColor = () => {
    if (!kpi.trend || typeof kpi.trend !== 'number' || kpi.trend === 0) return 'text-gray-500';
    
    const isPositiveTrend = kpi.trend > 0;
    const isGoodTrend = kpi.is_good_when_higher ? isPositiveTrend : !isPositiveTrend;
    
    return isGoodTrend ? 'text-green-500' : 'text-red-500';
  };
  
  // Calcular progresso em relação ao target
  const progress = (kpi.target && typeof kpi.value === 'number' && typeof kpi.target === 'number') 
    ? (kpi.value / kpi.target) * 100 
    : 0;
  const progressCapped = Math.min(Math.max(progress, 0), 100);
  
  if (compact) {
    return (
      <div 
        className={cn(
          "flex items-center justify-between p-3 rounded-lg cursor-pointer transition-colors",
          isDark ? "hover:bg-gray-800" : "hover:bg-gray-100"
        )}
        onClick={onClick}
      >
        <div className="flex items-center gap-3">
          <StatusIcon className={cn("h-4 w-4", statusColor)} />
          <span className="text-sm font-medium">{kpi.name}</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm font-mono">
            {typeof kpi.value === 'number' ? kpi.value.toFixed(kpi.unit === '%' ? 1 : 2) : kpi.value}{kpi.unit}
          </span>
          <TrendIcon className={cn("h-4 w-4", getTrendColor())} />
        </div>
      </div>
    );
  }
  
  return (
    <Card 
      className={cn(
        "cursor-pointer transition-all hover:shadow-lg",
        isDark ? "hover:border-gray-600" : "hover:border-gray-300"
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <StatusIcon className={cn("h-5 w-5", statusColor)} />
            <h3 className="font-medium text-sm line-clamp-1">{kpi.name}</h3>
          </div>
          <Info className="h-4 w-4 text-gray-400" />
        </div>
        
        <div className="space-y-3">
          {/* Valor principal */}
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold">
              {typeof kpi.value === 'number' ? kpi.value.toFixed(kpi.unit === '%' ? 1 : 2) : kpi.value}
            </span>
            <span className="text-sm text-gray-500">{kpi.unit}</span>
          </div>
          
          {/* Tendência */}
          <div className="flex items-center gap-2">
            <TrendIcon className={cn("h-4 w-4", getTrendColor())} />
            <span className={cn("text-sm", getTrendColor())}>
              {(kpi.trend && typeof kpi.trend === 'number' && kpi.trend > 0) ? '+' : ''}{typeof kpi.trend === 'number' ? kpi.trend.toFixed(1) : (kpi.trend || '0')}%
            </span>
          </div>
          
          {/* Progresso em relação ao target */}
          {kpi.target && (
            <div className="space-y-1">
              <div className="flex justify-between text-xs text-gray-500">
                <span>Target: {typeof kpi.target === 'number' ? kpi.target.toFixed(kpi.unit === '%' ? 1 : 2) : kpi.target}{kpi.unit}</span>
                <span>{progressCapped.toFixed(0)}%</span>
              </div>
              <Progress 
                value={progressCapped} 
                className="h-2"
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};