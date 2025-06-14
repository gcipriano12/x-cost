import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { AlertCircle, DollarSign } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '@/hooks/useTheme';
import { BudgetCreate, BudgetUpdate, BudgetResponse } from '@/hooks/useBudgets';

interface BudgetFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: BudgetCreate | BudgetUpdate) => Promise<void>;
  budget?: BudgetResponse; // Para edição
  mode: 'create' | 'edit';
}

export function BudgetFormDialog({
  open,
  onOpenChange,
  onSubmit,
  budget,
  mode
}: BudgetFormDialogProps) {
  const { t } = useTranslation();
  const { isDark } = useTheme();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    budget_name: '',
    provider_name: null,
    service_name: '',
    budget_amount: '',
    budget_period: 'monthly',
    alert_threshold: '80.00',
    is_active: true,
    tags: {}
  });

  const [tagsText, setTagsText] = useState('');
  const [displayBudgetAmount, setDisplayBudgetAmount] = useState('');

  // Atualizar o estado do formulário quando o budget mudar ou o diálogo for aberto
  useEffect(() => {
    if (mode === 'edit' && budget && open) {
      const budgetAmount = budget.budget_amount || '';
      setFormData({
        budget_name: budget.budget_name || '',
        provider_name: budget.provider_name || null,
        service_name: budget.service_name || '',
        budget_amount: budgetAmount,
        budget_period: budget.budget_period || 'monthly',
        alert_threshold: budget.alert_threshold || '80.00',
        is_active: budget.is_active ?? true,
        tags: budget.tags || {}
      });
      
      // Formatar valor para exibição
      if (budgetAmount) {
        const numericValue = parseFloat(budgetAmount);
        if (!isNaN(numericValue)) {
          setDisplayBudgetAmount(numericValue.toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
          }));
        } else {
          setDisplayBudgetAmount('');
        }
      } else {
        setDisplayBudgetAmount('');
      }
      
      setTagsText(budget.tags ? JSON.stringify(budget.tags, null, 2) : '');
      setError(null);
    } else if (mode === 'create' && open) {
      // Reset form for create mode
      setFormData({
        budget_name: '',
        provider_name: null,
        service_name: '',
        budget_amount: '',
        budget_period: 'monthly',
        alert_threshold: '80.00',
        is_active: true,
        tags: {}
      });
      setDisplayBudgetAmount('');
      setTagsText('');
      setError(null);
    }
  }, [budget, mode, open]);

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    setError(null);
  };

  // Funções utilitárias para formatação monetária
  const formatCurrency = (value: string): string => {
    // Remove tudo que não for dígito
    const cleanValue = value.replace(/\D/g, '');
    
    if (!cleanValue) return '';
    
    // Não dividir por 100 - tratar o valor como já sendo em unidades completas
    const numberValue = parseInt(cleanValue);
    
    // Formatar no padrão americano (separador de milhares com vírgula, decimal com ponto)
    return numberValue.toLocaleString('en-US', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    });
  };

  const parseFormattedCurrency = (formattedValue: string): string => {
    // Remove vírgulas de separação de milhares e retorna só os dígitos
    const cleanValue = formattedValue.replace(/,/g, '');
    return cleanValue || '';
  };

  const handleBudgetAmountChange = (value: string) => {
    // Atualizar valor formatado para exibição
    const formatted = formatCurrency(value);
    setDisplayBudgetAmount(formatted);
    
    // Atualizar valor limpo no state para envio ao backend
    const cleanValue = parseFormattedCurrency(formatted);
    setFormData(prev => ({
      ...prev,
      budget_amount: cleanValue
    }));
    setError(null);
  };

  const validateForm = (): string | null => {
    if (!formData.budget_name.trim()) {
      return t('budgets.form.validation.budgetNameRequired');
    }
    
    if (!formData.budget_amount || parseFloat(formData.budget_amount) <= 0) {
      return t('budgets.form.validation.budgetAmountInvalid');
    }

    const threshold = parseFloat(formData.alert_threshold);
    if (isNaN(threshold) || threshold < 0 || threshold > 100) {
      return t('budgets.form.validation.alertThresholdInvalid');
    }

    if (tagsText.trim()) {
      try {
        JSON.parse(tagsText);
      } catch {
        return t('budgets.form.validation.tagsInvalidJson');
      }
    }

    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let tags = {};
      if (tagsText.trim()) {
        tags = JSON.parse(tagsText);
      }

      const submitData = {
        ...formData,
        budget_amount: parseFloat(formData.budget_amount).toFixed(4),
        alert_threshold: parseFloat(formData.alert_threshold).toFixed(2),
        tags: Object.keys(tags).length > 0 ? tags : undefined,
        // Tratamento correto para provider_name
        provider_name: formData.provider_name && formData.provider_name !== "all_providers" ? formData.provider_name : undefined,
        service_name: formData.service_name.trim() || undefined,
      };

      await onSubmit(submitData);
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setError(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <DollarSign className="h-5 w-5 text-blue-600" />
            {mode === 'create' ? t('budgets.form.createTitle') : t('budgets.form.editTitle')}
          </DialogTitle>
          <DialogDescription>
            {mode === 'create' 
              ? t('budgets.form.createDescription')
              : t('budgets.form.editDescription')
            }
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <Card className="border-red-200 bg-red-50">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-red-700">
                  <AlertCircle className="h-4 w-4" />
                  <span className="text-sm">{error}</span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">{t('budgets.form.sections.basicInfo')}</h3>
            
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="budget_name">{t('budgets.form.fields.budgetName')} *</Label>
                <Input
                  id="budget_name"
                  value={formData.budget_name}
                  onChange={(e) => handleInputChange('budget_name', e.target.value)}
                  placeholder={t('budgets.form.fields.budgetNamePlaceholder')}
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="budget_amount">{t('budgets.form.fields.budgetAmount')} *</Label>
                  <div className="relative">
                    <span className="absolute left-3 top-2.5 text-muted-foreground">$</span>
                    <Input
                      id="budget_amount"
                      type="text"
                      value={displayBudgetAmount}
                      onChange={(e) => handleBudgetAmountChange(e.target.value)}
                      placeholder="1,000,000"
                      className="pl-8"
                      required
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {t('budgets.form.fields.budgetAmountHelp')}
                  </p>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="budget_period">{t('budgets.form.fields.period')}</Label>
                  <Select
                    value={formData.budget_period}
                    onValueChange={(value) => handleInputChange('budget_period', value)}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="monthly">{t('budgets.form.periods.monthly')}</SelectItem>
                      <SelectItem value="annual">{t('budgets.form.periods.annual')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="alert_threshold">{t('budgets.form.fields.alertThreshold')}</Label>
                <Input
                  id="alert_threshold"
                  type="number"
                  step="0.01"
                  min="0"
                  max="100"
                  value={formData.alert_threshold}
                  onChange={(e) => handleInputChange('alert_threshold', e.target.value)}
                  placeholder="80.00"
                />
                <p className="text-xs text-muted-foreground">
                  {t('budgets.form.fields.alertThresholdHelp')}
                </p>
              </div>
            </div>
          </div>

          {/* Scope Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">{t('budgets.form.sections.scopeConfig')}</h3>              
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="provider_name">{t('budgets.form.fields.cloudProvider')}</Label>
                <Select
                  value={formData.provider_name || "all_providers"}
                  onValueChange={(value) => handleInputChange('provider_name', value === "all_providers" ? "" : value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder={t('budgets.form.fields.allProviders')} />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all_providers">{t('budgets.form.fields.allProviders')}</SelectItem>
                    <SelectItem value="AWS">{t('budgets.form.providers.aws')}</SelectItem>
                    <SelectItem value="Azure">{t('budgets.form.providers.azure')}</SelectItem>
                    <SelectItem value="GCP">{t('budgets.form.providers.gcp')}</SelectItem>
                    <SelectItem value="Oracle Cloud">{t('budgets.form.providers.oracleCloud')}</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="service_name">{t('budgets.form.fields.service')}</Label>
                <Input
                  id="service_name"
                  value={formData.service_name}
                  onChange={(e) => handleInputChange('service_name', e.target.value)}
                  placeholder={t('budgets.form.fields.servicePlaceholder')}
                />
              </div>
            </div>
          </div>

          {/* Advanced Settings */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">{t('budgets.form.sections.advancedSettings')}</h3>
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label htmlFor="is_active">{t('budgets.form.fields.activeBudget')}</Label>
                <p className="text-sm text-muted-foreground">
                  {t('budgets.form.fields.activeBudgetHelp')}
                </p>
              </div>
              <Switch
                id="is_active"
                checked={formData.is_active}
                onCheckedChange={(checked) => handleInputChange('is_active', checked)}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="tags">{t('budgets.form.fields.tags')}</Label>
              <Textarea
                id="tags"
                value={tagsText}
                onChange={(e) => setTagsText(e.target.value)}
                placeholder={t('budgets.form.fields.tagsPlaceholder')}
                rows={4}
                className="font-mono text-sm"
              />
              <p className="text-xs text-muted-foreground">
                {t('budgets.form.fields.tagsHelp')}
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button 
              type="button" 
              variant="outline" 
              onClick={handleCancel}
              disabled={loading}
            >
              {t('budgets.form.buttons.cancel')}
            </Button>
            <Button 
              type="submit" 
              disabled={loading}
              className="flex items-center gap-2"
            >
              {loading && <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>}
              {mode === 'create' ? t('budgets.form.buttons.create') : t('budgets.form.buttons.update')}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
