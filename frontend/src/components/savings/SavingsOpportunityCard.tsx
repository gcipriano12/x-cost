import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  DollarSign, 
  TrendingUp, 
  Clock, 
  Shield, 
  Eye, 
  Plus, 
  Play,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { SavingsOpportunity } from '@/types/optimization';
import { formatCurrency } from '@/utils/optimizationUtils';

interface SavingsOpportunityCardProps {
  opportunity: SavingsOpportunity;
  onViewDetails: (opportunity: SavingsOpportunity) => void;
  onAddToPlan: (id: string) => void;
  onImplement: (id: string) => void;
  className?: string;
}

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
  AWS: 'bg-orange-400 text-white',
  Azure: 'bg-blue-500 text-white',
  GCP: 'bg-green-500 text-white',
  Oracle: 'bg-red-500 text-white'
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

const getConfidenceIcon = (level: string) => {
  switch (level) {
    case 'high': return <CheckCircle className="h-3 w-3" />;
    case 'medium': return <Info className="h-3 w-3" />;
    case 'low': return <AlertTriangle className="h-3 w-3" />;
    default: return <Info className="h-3 w-3" />;
  }
};

const calculateROI = (monthlySavings: number, implementationHours: number) => {
  const annualSavings = monthlySavings * 12;
  const implementationCost = implementationHours * 100; // Assuming $100/hour
  if (implementationCost === 0) return 0;
  return ((annualSavings - implementationCost) / implementationCost) * 100;
};

const getPaybackMonths = (monthlySavings: number, implementationHours: number) => {
  const implementationCost = implementationHours * 100;
  if (monthlySavings === 0) return Infinity;
  return implementationCost / monthlySavings;
};

export function SavingsOpportunityCard({
  opportunity,
  onViewDetails,
  onAddToPlan,
  onImplement,
  className
}: SavingsOpportunityCardProps) {
  const {
    id,
    title,
    description,
    provider,
    category,
    monthly_savings,
    confidence_level,
    confidence_score,
    implementation_effort,
    implementation_effort_hours,
    risk_level,
    affected_resources,
    currency = 'USD'
  } = opportunity;

  const annualSavings = monthly_savings * 12;
  const roi = calculateROI(monthly_savings, implementation_effort_hours);
  const paybackMonths = getPaybackMonths(monthly_savings, implementation_effort_hours);

  const categoryColor = categoryColors[category as keyof typeof categoryColors] || 'bg-gray-500';
  const providerColor = providerColors[provider as keyof typeof providerColors] || 'bg-gray-500 text-white';

  return (
    <Card className={cn("hover:shadow-lg transition-shadow duration-200", className)}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="font-semibold text-lg leading-tight truncate" title={title}>
              {title}
            </h3>
            <div className="flex items-center gap-2 mt-2">
              <Badge className={cn("text-xs", providerColor)}>
                {provider}
              </Badge>
              <Badge variant="outline" className="text-xs">
                <div className={cn("h-2 w-2 rounded-full mr-1", categoryColor)} />
                {category.replace('_', ' ')}
              </Badge>
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Savings Metrics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <DollarSign className="h-3 w-3" />
              Monthly Savings
            </div>
            <div className="text-xl font-bold text-green-600">
              {formatCurrency(monthly_savings, currency, 'en-US', true)}
            </div>
          </div>
          <div className="space-y-1">
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <TrendingUp className="h-3 w-3" />
              Annual Savings
            </div>
            <div className="text-xl font-bold text-green-600">
              {formatCurrency(annualSavings, currency, 'en-US', true)}
            </div>
          </div>
        </div>

        {/* Confidence and Risk Indicators */}
        <div className="grid grid-cols-3 gap-2">
          <div className="text-center">
            <Badge className={cn("text-xs mb-1", confidenceColors[confidence_level as keyof typeof confidenceColors])}>
              <div className="flex items-center gap-1">
                {getConfidenceIcon(confidence_level)}
                Confidence
              </div>
            </Badge>
            <div className="text-sm font-medium">
              {Math.round(confidence_score)}%
            </div>
          </div>
          <div className="text-center">
            <Badge className={cn("text-xs mb-1", effortColors[implementation_effort as keyof typeof effortColors])}>
              <Clock className="h-3 w-3 mr-1" />
              Effort
            </Badge>
            <div className="text-sm font-medium capitalize">
              {implementation_effort}
            </div>
          </div>
          <div className="text-center">
            <Badge className={cn("text-xs mb-1", riskColors[risk_level as keyof typeof riskColors])}>
              <Shield className="h-3 w-3 mr-1" />
              Risk
            </Badge>
            <div className="text-sm font-medium capitalize">
              {risk_level}
            </div>
          </div>
        </div>

        {/* Progress bar for confidence */}
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Confidence Score</span>
            <span>{Math.round(confidence_score)}%</span>
          </div>
          <Progress 
            value={confidence_score} 
            className="h-2"
            aria-label={`Confidence score: ${Math.round(confidence_score)}%`}
          />
        </div>

        {/* Description */}
        <div className="space-y-1">
          <p className="text-sm text-muted-foreground line-clamp-2" title={description}>
            {description}
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4 pt-2 border-t">
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">ROI</div>
            <div className={cn(
              "text-sm font-medium",
              roi > 300 ? "text-green-600" : roi > 100 ? "text-yellow-600" : "text-red-600"
            )}>
              {roi > 1000 ? '1000%+' : `${Math.round(roi)}%`}
            </div>
          </div>
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Payback</div>
            <div className="text-sm font-medium">
              {paybackMonths < 1 ? '<1 mo' : paybackMonths > 24 ? '24+ mo' : `${Math.round(paybackMonths)} mo`}
            </div>
          </div>
        </div>

        {/* Affected Resources */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Affected Resources</span>
            <Badge variant="secondary" className="text-xs">
              {affected_resources.length} resources
            </Badge>
          </div>
          {affected_resources.length > 0 && (
            <div className="text-xs text-muted-foreground truncate">
              {affected_resources.slice(0, 2).join(', ')}
              {affected_resources.length > 2 && ` +${affected_resources.length - 2} more`}
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-2 pt-2 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewDetails(opportunity)}
            className="flex-1"
          >
            <Eye className="h-3 w-3 mr-1" />
            Details
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => onAddToPlan(id)}
            className="flex-1"
          >
            <Plus className="h-3 w-3 mr-1" />
            Add to Plan
          </Button>
          <Button
            size="sm"
            onClick={() => onImplement(id)}
            className="flex-1 bg-green-600 hover:bg-green-700"
          >
            <Play className="h-3 w-3 mr-1" />
            Implement
          </Button>
        </div>

        {/* Quick Win Indicator */}
        {implementation_effort === 'low' && risk_level === 'low' && (
          <div className="flex items-center gap-1 text-xs text-green-600 bg-green-50 dark:bg-green-900/20 px-2 py-1 rounded">
            <CheckCircle className="h-3 w-3" />
            Quick Win Opportunity
          </div>
        )}

        {/* High ROI Indicator */}
        {roi > 300 && (
          <div className="flex items-center gap-1 text-xs text-blue-600 bg-blue-50 dark:bg-blue-900/20 px-2 py-1 rounded">
            <TrendingUp className="h-3 w-3" />
            High ROI Opportunity
          </div>
        )}
      </CardContent>
    </Card>
  );
}