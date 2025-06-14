import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, CheckCircle, AlertCircle, Calendar, DollarSign, TrendingUp, TrendingDown, Clock, Power, PowerOff } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { BudgetResponse, BudgetConsumption, BudgetAlertsResponse } from '@/hooks/useBudgets';

interface BudgetDetailsDialogProps {
  budget: BudgetResponse | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onGetConsumption: (id: number, periodDays?: number) => Promise<BudgetConsumption>;
  onGetAlerts: (id: number) => Promise<BudgetAlertsResponse>;
  onActivate: (id: number) => Promise<void>;
  onDeactivate: (id: number) => Promise<void>;
}

export function BudgetDetailsDialog({
  budget,
  open,
  onOpenChange,
  onGetConsumption,
  onGetAlerts,
  onActivate,
  onDeactivate
}: BudgetDetailsDialogProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const [consumption, setConsumption] = useState<BudgetConsumption | null>(null);
  const [alerts, setAlerts] = useState<BudgetAlertsResponse | null>(null);
  const [loadingConsumption, setLoadingConsumption] = useState(false);
  const [loadingAlerts, setLoadingAlerts] = useState(false);
  const [loadingAction, setLoadingAction] = useState(false);

  useEffect(() => {
    if (open && budget) {
      loadConsumptionData();
      loadAlertsData();
    }
  }, [open, budget]);

  const loadConsumptionData = async () => {
    setLoadingConsumption(true);
    try {
      const data = await onGetConsumption(budget.id);
      setConsumption(data);
    } catch (error) {
      console.error('Error loading consumption data:', error);
    } finally {
      setLoadingConsumption(false);
    }
  };

  const loadAlertsData = async () => {
    setLoadingAlerts(true);
    try {
      const data = await onGetAlerts(budget.id);
      setAlerts(data);
    } catch (error) {
      console.error('Error loading alerts data:', error);
    } finally {
      setLoadingAlerts(false);
    }
  };

  const handleToggleActive = async () => {
    setLoadingAction(true);
    try {
      if (budget.is_active) {
        await onDeactivate(budget.id);
      } else {
        await onActivate(budget.id);
      }
      // Budget data will be refreshed by parent component
    } catch (error) {
      console.error('Error toggling budget status:', error);
    } finally {
      setLoadingAction(false);
    }
  };

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
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status?: string) => {
    switch (status) {
      case 'under_budget':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'warning':
        return 'text-amber-600 bg-amber-50 border-amber-200';
      case 'over_budget':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'under_budget':
        return <CheckCircle className="h-4 w-4" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4" />;
      case 'over_budget':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getProgressColor = (status?: string) => {
    switch (status) {
      case 'under_budget':
        return 'bg-green-500';
      case 'warning':
        return 'bg-amber-500';
      case 'over_budget':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (!budget) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-blue-600" />
            {budget.budget_name}
          </DialogTitle>
          <DialogDescription>
            {t('budgets.details.title')}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6">
          {/* Budget Info Header */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{t('budgets.details.budgetAmount')}</p>
                    <p className="text-2xl font-bold">{formatCurrency(budget.budget_amount)}</p>
                  </div>
                  <DollarSign className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{t('budgets.details.period')}</p>
                    <p className="text-lg font-semibold capitalize">{t(`budgets.table.periods.${budget.budget_period}`)}</p>
                  </div>
                  <Calendar className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{t('budgets.details.alertThreshold')}</p>
                    <p className="text-lg font-semibold">{budget.alert_threshold}%</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-amber-600" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Budget Status and Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{t('budgets.details.budgetStatus')}</span>
                <div className="flex items-center gap-2">
                  <Badge variant={budget.is_active ? "default" : "secondary"}>
                    {budget.is_active ? t('budgets.status.active') : t('budgets.status.inactive')}
                  </Badge>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleToggleActive}
                    disabled={loadingAction}
                    className="flex items-center gap-1"
                  >
                    {budget.is_active ? (
                      <>
                        <PowerOff className="h-4 w-4" />
                        {t('budgets.details.buttons.deactivate')}
                      </>
                    ) : (
                      <>
                        <Power className="h-4 w-4" />
                        {t('budgets.details.buttons.activate')}
                      </>
                    )}
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t('budgets.details.provider')}</p>
                  <p className="font-medium">{budget.provider_name || t('budgets.details.allProviders')}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t('budgets.details.service')}</p>
                  <p className="font-medium">{budget.service_name || t('budgets.details.allServices')}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t('budgets.details.created')}</p>
                  <p className="font-medium">{formatDate(budget.created_at)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">{t('budgets.details.budgetId')}</p>
                  <p className="font-medium">#{budget.id}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Consumption Data */}
          {loadingConsumption ? (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="text-sm text-muted-foreground mt-2">{t('budgets.details.loading.consumption')}</p>
              </CardContent>
            </Card>
          ) : consumption ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {t('budgets.details.currentConsumption')}
                  <Badge className={cn("text-xs", getStatusColor(consumption.status))}>
                    {getStatusIcon(consumption.status)}
                    <span className="ml-1 capitalize">
                      {consumption.status === 'under_budget' && t('budgets.details.status.underBudget')}
                      {consumption.status === 'warning' && t('budgets.details.status.warning')}
                      {consumption.status === 'over_budget' && t('budgets.details.status.overBudget')}
                      {consumption.status && !['under_budget', 'warning', 'over_budget'].includes(consumption.status) && consumption.status.replace('_', ' ')}
                      {!consumption.status && 'Unknown Status'}
                    </span>
                  </Badge>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Progress Bar */}
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm font-medium">{t('budgets.details.budgetProgress')}</span>
                      <span className="text-sm text-muted-foreground">
                        {consumption.consumption_percentage ? parseFloat(consumption.consumption_percentage).toFixed(1) : '0.0'}%
                      </span>
                    </div>
                    <Progress 
                      value={consumption.consumption_percentage ? parseFloat(consumption.consumption_percentage) : 0} 
                      className="h-3"
                      progressColor={getProgressColor(consumption.status)}
                    />
                  </div>

                  {/* Consumption Details */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">{t('budgets.details.currentSpend')}</p>
                      <p className="text-lg font-bold text-blue-600">
                        {formatCurrency(consumption.current_consumption || 0)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">{t('budgets.details.remainingBudget')}</p>
                      <p className="text-lg font-bold text-green-600">
                        {formatCurrency(consumption.remaining_budget || 0)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">{t('budgets.details.daysRemaining')}</p>
                      <p className="text-lg font-bold">{consumption.days_remaining || 0}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">{t('budgets.details.projectedTotal')}</p>
                      <p className="text-lg font-bold text-amber-600">
                        {consumption.projected_consumption 
                          ? formatCurrency(consumption.projected_consumption)
                          : 'N/A'
                        }
                      </p>
                    </div>
                  </div>

                  {/* Period Info */}
                  <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                    <p className="text-sm font-medium mb-2">{t('budgets.details.currentPeriod')}</p>
                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>{t('budgets.details.from')}: {consumption.period_start ? formatDate(consumption.period_start) : 'N/A'}</span>
                      <span>{t('budgets.details.to')}: {consumption.period_end ? formatDate(consumption.period_end) : 'N/A'}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <AlertCircle className="h-8 w-8 text-amber-500 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">{t('budgets.details.noData.consumption')}</p>
              </CardContent>
            </Card>
          )}

          {/* Alerts */}
          {loadingAlerts ? (
            <Card>
              <CardContent className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="text-sm text-muted-foreground mt-2">{t('budgets.details.loading.alerts')}</p>
              </CardContent>
            </Card>
          ) : alerts && alerts.alert_count > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-amber-600" />
                  {t('budgets.details.alerts.title')} ({alerts.alert_count})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {alerts.alerts.filter(alert => alert && (alert.type || alert.message)).map((alert, index) => (
                    <div 
                      key={index}
                      className={cn(
                        "p-3 rounded-lg border",
                        alert.severity === 'critical' 
                          ? "bg-red-50 border-red-200 text-red-800"
                          : "bg-amber-50 border-amber-200 text-amber-800"
                      )}
                    >
                      <div className="flex items-start gap-2">
                        {alert.severity === 'critical' ? (
                          <AlertTriangle className="h-4 w-4 mt-0.5 text-red-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 mt-0.5 text-amber-600" />
                        )}
                        <div className="flex-1">
                          <p className="font-medium capitalize">
                            {alert.type ? (t(`budgets.details.alerts.types.${alert.type}`) || alert.type.replace('_', ' ')) : 'Unknown Type'} - {alert.severity ? t(`budgets.details.alerts.severity.${alert.severity}`) : 'Unknown Severity'}
                          </p>
                          <p className="text-sm mt-1">{alert.message || 'No message available'}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <p className="text-xs text-muted-foreground mt-3">
                  {t('budgets.details.alerts.lastChecked')}: {formatDate(alerts.last_check)}
                </p>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="p-8 text-center">
                <CheckCircle className="h-8 w-8 text-green-500 mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">{t('budgets.details.noData.alerts')}</p>
              </CardContent>
            </Card>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
