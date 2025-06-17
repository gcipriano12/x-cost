import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import {
  DollarSign,
  TrendingUp,
  Clock,
  Shield,
  Server,
  Calendar,
  FileText,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  Info,
  ExternalLink,
  Copy,
  Plus,
  Play,
  X,
  Target,
  BarChart3,
  Zap
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { SavingsOpportunity } from '@/types/optimization';
import { formatCurrency, formatRelativeTime } from '@/utils/optimizationUtils';
import { useToast } from '@/hooks/use-toast';

interface SavingsDetailModalProps {
  opportunity: SavingsOpportunity | null;
  open: boolean;
  onClose: () => void;
  onAddToPlan?: (opportunityId: string) => void;
  onImplement?: (opportunityId: string) => void;
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

const calculateROI = (monthlySavings: number, implementationHours: number) => {
  const annualSavings = monthlySavings * 12;
  const implementationCost = implementationHours * 100;
  if (implementationCost === 0) return 0;
  return ((annualSavings - implementationCost) / implementationCost) * 100;
};

const getPaybackMonths = (monthlySavings: number, implementationHours: number) => {
  const implementationCost = implementationHours * 100;
  if (monthlySavings === 0) return Infinity;
  return implementationCost / monthlySavings;
};

const getConfidenceIcon = (level: string) => {
  switch (level) {
    case 'high': return <CheckCircle className="h-4 w-4" />;
    case 'medium': return <Info className="h-4 w-4" />;
    case 'low': return <AlertTriangle className="h-4 w-4" />;
    default: return <Info className="h-4 w-4" />;
  }
};

const getImplementationSteps = (category: string, title: string) => {
  const steps: Record<string, string[]> = {
    compute: [
      "Analyze current resource utilization over the past 30 days",
      "Identify right-sized instance types based on usage patterns",
      "Schedule maintenance window for instance modifications",
      "Apply changes during low-traffic periods",
      "Monitor performance for 48 hours after changes",
      "Validate savings and performance metrics"
    ],
    storage: [
      "Review storage access patterns and frequency",
      "Identify data suitable for different storage tiers",
      "Set up lifecycle policies for automatic tiering",
      "Test backup and recovery procedures",
      "Monitor storage costs and access patterns",
      "Optimize based on usage analytics"
    ],
    network: [
      "Analyze network traffic patterns and bandwidth usage",
      "Identify opportunities for traffic optimization",
      "Configure CDN or edge locations if applicable",
      "Implement network compression and caching",
      "Test network performance and latency",
      "Monitor network costs and performance metrics"
    ],
    reserved_instances: [
      "Analyze historical usage patterns for the past 12 months",
      "Calculate optimal reservation mix and terms",
      "Purchase Reserved Instances or Savings Plans",
      "Monitor utilization and coverage rates",
      "Adjust reservations based on usage changes",
      "Track savings against on-demand pricing"
    ]
  };

  return steps[category] || [
    "Review current configuration and usage patterns",
    "Plan implementation approach and timeline",
    "Execute changes during maintenance window",
    "Monitor performance and validate results",
    "Document changes and update procedures"
  ];
};

const getRiskAssessment = (riskLevel: string, category: string) => {
  const assessments: Record<string, Record<string, string[]>> = {
    low: {
      compute: [
        "Changes can be easily reverted if issues occur",
        "Based on conservative 90-day usage patterns",
        "No impact on application functionality expected"
      ],
      storage: [
        "Data integrity maintained during tier transitions",
        "Access patterns well understood from historical data",
        "Rollback procedures well-defined and tested"
      ],
      network: [
        "Network changes tested in staging environment",
        "Fallback routes available if performance degrades",
        "Minimal impact on user experience expected"
      ]
    },
    medium: {
      compute: [
        "Some performance impact possible during peak hours",
        "Requires careful monitoring during initial period",
        "May need fine-tuning based on application behavior"
      ],
      storage: [
        "Initial access latency may increase for some data",
        "Monitoring required to ensure SLA compliance",
        "May require adjustment of access patterns"
      ],
      network: [
        "Some regions may experience temporary latency changes",
        "Requires comprehensive testing before full rollout",
        "May need configuration adjustments"
      ]
    },
    high: {
      compute: [
        "Significant performance impact possible",
        "Requires extensive testing and gradual rollout",
        "Strong monitoring and alerting essential"
      ],
      storage: [
        "Potential for extended access times during migration",
        "Requires careful planning and phased approach",
        "May impact dependent applications"
      ],
      network: [
        "Could affect user experience during implementation",
        "Requires detailed rollback plan",
        "May need coordination with multiple teams"
      ]
    }
  };

  return assessments[riskLevel]?.[category] || [
    "Risk assessment based on historical implementation data",
    "Comprehensive monitoring recommended during implementation",
    "Rollback procedures should be prepared and tested"
  ];
};

export function SavingsDetailModal({
  opportunity,
  open,
  onClose,
  onAddToPlan,
  onImplement
}: SavingsDetailModalProps) {
  const { isDark } = useTheme();
  const { toast } = useToast();

  if (!opportunity) return null;

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
    currency = 'USD',
    detected_at
  } = opportunity;

  const annualSavings = monthly_savings * 12;
  const roi = calculateROI(monthly_savings, implementation_effort_hours);
  const paybackMonths = getPaybackMonths(monthly_savings, implementation_effort_hours);

  const categoryColor = categoryColors[category as keyof typeof categoryColors] || 'bg-gray-500';
  const providerColor = providerColors[provider as keyof typeof providerColors] || 'bg-gray-500 text-white';
  const confidenceColor = confidenceColors[confidence_level as keyof typeof confidenceColors];
  const effortColor = effortColors[implementation_effort as keyof typeof effortColors];
  const riskColor = riskColors[risk_level as keyof typeof riskColors];

  const implementationSteps = getImplementationSteps(category, title);
  const riskAssessment = getRiskAssessment(risk_level, category);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: `${label} copied to clipboard`,
    });
  };

  const handleAddToPlan = () => {
    if (onAddToPlan) {
      onAddToPlan(id);
    }
    onClose();
  };

  const handleImplement = () => {
    if (onImplement) {
      onImplement(id);
    }
    onClose();
  };

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh]">
        <DialogHeader className="space-y-4">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <DialogTitle className="text-xl font-semibold leading-tight pr-4">
                {title}
              </DialogTitle>
              <div className="flex items-center gap-2 mt-2">
                <Badge className={cn("text-xs", providerColor)}>
                  {provider}
                </Badge>
                <Badge variant="outline" className="text-xs">
                  <div className={cn("h-2 w-2 rounded-full mr-1", categoryColor)} />
                  {category.replace('_', ' ')}
                </Badge>
                <Badge className={cn("text-xs", confidenceColor)}>
                  {getConfidenceIcon(confidence_level)}
                  <span className="ml-1">{confidence_level} confidence</span>
                </Badge>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="shrink-0"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <ScrollArea className="max-h-[70vh]">
          <div className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <DollarSign className="h-4 w-4" />
                    Monthly Savings
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(monthly_savings, currency, 'en-US', true)}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <TrendingUp className="h-4 w-4" />
                    Annual Savings
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(annualSavings, currency, 'en-US', true)}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Target className="h-4 w-4" />
                    ROI
                  </div>
                  <div className={cn(
                    "text-2xl font-bold",
                    roi > 300 ? "text-green-600" : roi > 100 ? "text-yellow-600" : "text-red-600"
                  )}>
                    {roi > 1000 ? '1000%+' : `${Math.round(roi)}%`}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 text-sm text-muted-foreground mb-1">
                    <Clock className="h-4 w-4" />
                    Payback Period
                  </div>
                  <div className="text-2xl font-bold">
                    {paybackMonths < 1 ? '<1 mo' : paybackMonths > 24 ? '24+ mo' : `${Math.round(paybackMonths)} mo`}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Tabs for detailed information */}
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="implementation">Implementation</TabsTrigger>
                <TabsTrigger value="resources">Resources</TabsTrigger>
                <TabsTrigger value="analysis">Analysis</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Description
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{description}</p>
                  </CardContent>
                </Card>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <CheckCircle className="h-4 w-4" />
                        Confidence Score
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className={cn("text-sm font-medium", confidenceColor)}>
                            {confidence_level.toUpperCase()}
                          </span>
                          <span className="text-sm font-medium">
                            {Math.round(confidence_score)}%
                          </span>
                        </div>
                        <Progress value={confidence_score} className="h-2" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Clock className="h-4 w-4" />
                        Implementation Effort
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge className={cn("text-sm", effortColor)}>
                        {implementation_effort.toUpperCase()}
                      </Badge>
                      <p className="text-sm text-muted-foreground mt-2">
                        ~{implementation_effort_hours} hours estimated
                      </p>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-base">
                        <Shield className="h-4 w-4" />
                        Risk Level
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Badge className={cn("text-sm", riskColor)}>
                        {risk_level.toUpperCase()}
                      </Badge>
                      <p className="text-sm text-muted-foreground mt-2">
                        Based on historical implementation data
                      </p>
                    </CardContent>
                  </Card>
                </div>

                {/* Quick Win / High ROI Indicators */}
                {(implementation_effort === 'low' && risk_level === 'low') || roi > 300 ? (
                  <Card className="border-green-200 bg-green-50 dark:bg-green-900/20">
                    <CardContent className="p-4">
                      <div className="flex items-center gap-2">
                        {implementation_effort === 'low' && risk_level === 'low' && (
                          <div className="flex items-center gap-1 text-green-600">
                            <Zap className="h-4 w-4" />
                            <span className="font-medium">Quick Win Opportunity</span>
                          </div>
                        )}
                        {roi > 300 && (
                          <div className="flex items-center gap-1 text-blue-600">
                            <TrendingUp className="h-4 w-4" />
                            <span className="font-medium">High ROI Opportunity</span>
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ) : null}
              </TabsContent>

              <TabsContent value="implementation" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Lightbulb className="h-5 w-5" />
                      Implementation Plan
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {implementationSteps.map((step, index) => (
                        <div key={index} className="flex items-start gap-3">
                          <div className="flex items-center justify-center w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-sm font-medium shrink-0">
                            {index + 1}
                          </div>
                          <p className="text-sm text-muted-foreground">{step}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5" />
                      Risk Assessment
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {riskAssessment.map((risk, index) => (
                        <div key={index} className="flex items-start gap-2">
                          <div className="w-1 h-1 rounded-full bg-muted-foreground mt-2 shrink-0" />
                          <p className="text-sm text-muted-foreground">{risk}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="resources" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Server className="h-5 w-5" />
                      Affected Resources ({affected_resources.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {affected_resources.slice(0, 10).map((resource, index) => (
                        <div key={index} className="flex items-center justify-between p-2 border rounded">
                          <span className="text-sm font-mono">{resource}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => copyToClipboard(resource, 'Resource ID')}
                            className="h-6 w-6 p-0"
                          >
                            <Copy className="h-3 w-3" />
                          </Button>
                        </div>
                      ))}
                      {affected_resources.length > 10 && (
                        <p className="text-sm text-muted-foreground text-center py-2">
                          ... and {affected_resources.length - 10} more resources
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="analysis" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      Cost Impact Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm font-medium">Current Monthly Cost</p>
                          <p className="text-lg text-muted-foreground">
                            {formatCurrency(monthly_savings * 1.5, currency, 'en-US', true)}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm font-medium">Optimized Monthly Cost</p>
                          <p className="text-lg text-green-600">
                            {formatCurrency(monthly_savings * 0.5, currency, 'en-US', true)}
                          </p>
                        </div>
                      </div>
                      <Separator />
                      <div>
                        <p className="text-sm font-medium">Implementation Cost</p>
                        <p className="text-lg text-muted-foreground">
                          {formatCurrency(implementation_effort_hours * 100, currency, 'en-US', true)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          Based on {implementation_effort_hours} hours @ $100/hour
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Calendar className="h-5 w-5" />
                      Timeline Information
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Detected:</span>
                        <span className="text-sm text-muted-foreground">
                          {formatRelativeTime(detected_at)}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Estimated Implementation:</span>
                        <span className="text-sm text-muted-foreground">
                          {implementation_effort_hours} hours
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Payback Period:</span>
                        <span className="text-sm text-muted-foreground">
                          {paybackMonths < 1 ? 'Less than 1 month' : `${Math.round(paybackMonths)} months`}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </ScrollArea>

        <DialogFooter className="flex items-center gap-2">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
          <Button variant="outline" onClick={handleAddToPlan}>
            <Plus className="h-4 w-4 mr-2" />
            Add to Plan
          </Button>
          <Button onClick={handleImplement} className="bg-green-600 hover:bg-green-700">
            <Play className="h-4 w-4 mr-2" />
            Implement Now
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}