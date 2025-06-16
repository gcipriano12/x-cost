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
import {
  AlertTriangle,
  Calendar,
  DollarSign,
  Server,
  MapPin,
  FileText,
  Lightbulb,
  ExternalLink,
  Copy,
  CheckCircle,
  X
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
import { useToast } from '@/hooks/use-toast';

interface AnomalyDetailsModalProps {
  anomaly: CloudAnomaly | null;
  open: boolean;
  onClose: () => void;
  onDismiss?: (anomalyId: string) => void;
  onMarkResolved?: (anomalyId: string) => void;
}

export function AnomalyDetailsModal({
  anomaly,
  open,
  onClose,
  onDismiss,
  onMarkResolved
}: AnomalyDetailsModalProps) {
  const { isDark } = useTheme();
  const { toast } = useToast();

  if (!anomaly) return null;

  const severityStyle = formatSeverity(anomaly.severity);
  const providerStyle = formatCloudProvider(anomaly.provider);

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    toast({
      title: "Copied to clipboard",
      description: `${label} copied to clipboard`,
    });
  };

  const handleDismiss = () => {
    if (onDismiss) {
      onDismiss(anomaly.id);
    }
    onClose();
  };

  const handleMarkResolved = () => {
    if (onMarkResolved) {
      onMarkResolved(anomaly.id);
    }
    onClose();
  };

  // Generate mock recommendations based on anomaly type
  const getRecommendations = (anomaly: CloudAnomaly) => {
    const baseRecommendations = {
      'spike': [
        'Monitor resource utilization patterns over the next 24-48 hours',
        'Check for any recent application deployments or configuration changes',
        'Consider implementing auto-scaling to handle traffic spikes',
        'Review alert thresholds for early spike detection'
      ],
      'drift': [
        'Investigate gradual cost increases over the past 30 days',
        'Review resource allocation and optimize underutilized instances',
        'Check for data growth patterns that might affect storage costs',
        'Implement cost allocation tags for better tracking'
      ],
      'unusual_pattern': [
        'Analyze usage patterns during the anomalous period',
        'Compare with historical baselines from similar time periods',
        'Check for external factors affecting resource usage',
        'Review scheduled jobs and automated processes'
      ],
      'cost_increase': [
        'Review billing details for the affected service',
        'Check for price changes or new charges introduced',
        'Analyze resource usage to identify cost drivers',
        'Consider reserved instances for predictable workloads'
      ]
    };

    return baseRecommendations[anomaly.anomaly_type] || [
      'Review the affected resources and their usage patterns',
      'Check for any configuration changes in the specified time period',
      'Monitor the situation for further developments',
      'Consider implementing automated alerts for similar patterns'
    ];
  };

  const recommendations = getRecommendations(anomaly);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className={cn("max-w-4xl max-h-[90vh] flex flex-col", isDark ? "bg-slate-900" : "bg-white")}>
        <DialogHeader className="flex-shrink-0">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <AlertTriangle className={cn("h-6 w-6 mt-1", severityStyle.textColor)} />
              <div>
                <DialogTitle className="text-xl font-semibold">
                  {anomaly.anomaly_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} Detected
                </DialogTitle>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={cn("text-xs", severityStyle.color)}>
                    {severityStyle.icon} {severityStyle.label}
                  </Badge>
                  <div className="flex items-center gap-1 text-sm text-muted-foreground">
                    <div className={cn("h-2 w-2 rounded-full", providerStyle.color)} />
                    {anomaly.provider}
                  </div>
                  <span className="text-sm text-muted-foreground">•</span>
                  <span className="text-sm text-muted-foreground">{anomaly.service}</span>
                  {anomaly.region && (
                    <>
                      <span className="text-sm text-muted-foreground">•</span>
                      <span className="text-sm text-muted-foreground">{anomaly.region}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </DialogHeader>

        <ScrollArea className="flex-grow overflow-hidden">
          <div className="space-y-6 pr-4">
            {/* Overview Section */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign className="h-4 w-4 text-green-600" />
                    <span className="font-medium text-sm">Cost Impact</span>
                  </div>
                  <div className="text-2xl font-bold">
                    {formatCurrency(anomaly.cost_impact, anomaly.currency)}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Calendar className="h-4 w-4 text-blue-600" />
                    <span className="font-medium text-sm">Detected</span>
                  </div>
                  <div className="text-sm">
                    {formatRelativeTime(anomaly.detected_at)}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {new Date(anomaly.detected_at).toLocaleDateString()}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Server className="h-4 w-4 text-purple-600" />
                    <span className="font-medium text-sm">Resources</span>
                  </div>
                  <div className="text-sm font-medium">
                    {anomaly.affected_resources.length} affected
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {anomaly.affected_resources.length > 1 ? 'Multiple resources' : 'Single resource'}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Detailed Information */}
            <Tabs defaultValue="details" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="details">Details</TabsTrigger>
                <TabsTrigger value="resources">Resources</TabsTrigger>
                <TabsTrigger value="recommendations">Actions</TabsTrigger>
                <TabsTrigger value="timeline">Timeline</TabsTrigger>
              </TabsList>

              <TabsContent value="details" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <FileText className="h-5 w-5" />
                      Description
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm leading-relaxed">{anomaly.description}</p>
                    
                    {anomaly.root_cause && (
                      <div className="mt-4">
                        <h4 className="font-medium text-sm mb-2">Root Cause Analysis</h4>
                        <p className="text-sm text-muted-foreground bg-muted p-3 rounded-lg">
                          {anomaly.root_cause}
                        </p>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4 mt-4">
                      <div>
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">Anomaly Type</span>
                        <p className="font-medium capitalize">
                          {anomaly.anomaly_type.replace(/_/g, ' ')}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs text-muted-foreground uppercase tracking-wide">Severity Level</span>
                        <p className="font-medium capitalize">{anomaly.severity}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="resources" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Server className="h-5 w-5" />
                      Affected Resources ({anomaly.affected_resources.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      {anomaly.affected_resources.length > 0 ? (
                        anomaly.affected_resources.map((resource, index) => (
                          <div 
                            key={index} 
                            className="flex items-center justify-between p-3 bg-muted rounded-lg"
                          >
                            <div className="flex items-center gap-3">
                              <div className={cn("h-2 w-2 rounded-full", providerStyle.color)} />
                              <span className="font-mono text-sm">{resource}</span>
                            </div>
                            <div className="flex items-center gap-2">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => copyToClipboard(resource, 'Resource ID')}
                                className="h-8 w-8 p-0"
                              >
                                <Copy className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-8 w-8 p-0"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-muted-foreground">
                          <Server className="h-8 w-8 mx-auto mb-2 opacity-50" />
                          <p>No specific resources identified</p>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="recommendations" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Lightbulb className="h-5 w-5" />
                      Recommended Actions
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {recommendations.map((recommendation, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 bg-muted rounded-lg">
                          <div className="h-6 w-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium mt-0.5">
                            {index + 1}
                          </div>
                          <p className="text-sm flex-1">{recommendation}</p>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="timeline" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg flex items-center gap-2">
                      <Calendar className="h-5 w-5" />
                      Investigation Timeline
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <div className="h-2 w-2 bg-red-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">Anomaly Detected</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(anomaly.detected_at).toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Automated monitoring system flagged unusual cost pattern
                          </p>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <div className="h-2 w-2 bg-yellow-500 rounded-full mt-2"></div>
                        <div className="flex-1">
                          <p className="font-medium text-sm">Under Investigation</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date().toLocaleString()}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Reviewing affected resources and impact analysis
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>
        </ScrollArea>

        <DialogFooter className="flex-shrink-0 pt-4 border-t">
          <div className="flex items-center gap-2 w-full">
            <Button variant="outline" onClick={onClose}>
              Close
            </Button>
            {onDismiss && (
              <Button variant="outline" onClick={handleDismiss}>
                Dismiss
              </Button>
            )}
            {onMarkResolved && (
              <Button onClick={handleMarkResolved} className="ml-auto">
                <CheckCircle className="h-4 w-4 mr-2" />
                Mark as Resolved
              </Button>
            )}
          </div>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}