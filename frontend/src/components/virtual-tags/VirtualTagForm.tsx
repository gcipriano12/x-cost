import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeft, 
  ArrowRight, 
  Save, 
  Plus, 
  Trash2, 
  Info,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { useVirtualTag, useVirtualTagMutations, useVirtualTagForm } from '@/hooks/useVirtualTags';
import { VirtualTagCategory } from '@/types/virtualTags';
import RuleBuilder from './RuleBuilder';

const categoryOptions: { value: VirtualTagCategory; label: string }[] = [
  { value: 'business_unit', label: 'Unidade de Negócio' },
  { value: 'project', label: 'Projeto' },
  { value: 'environment', label: 'Ambiente' },
  { value: 'cost_center', label: 'Centro de Custo' },
  { value: 'department', label: 'Departamento' },
  { value: 'team', label: 'Time' },
  { value: 'application', label: 'Aplicação' },
  { value: 'owner', label: 'Proprietário' },
  { value: 'custom', label: 'Personalizado' }
];

const VirtualTagForm: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditing = !!id;

  // Fetch existing data if editing
  const { data: existingTag, isLoading: loadingTag } = useVirtualTag(id || '');

  // Form state management
  const {
    formData,
    currentStep,
    errors,
    updateField,
    validateStep,
    nextStep,
    prevStep,
    resetForm,
    setCurrentStep
  } = useVirtualTagForm(existingTag);

  // Mutations
  const { create, update } = useVirtualTagMutations();

  const steps = [
    { title: 'Informações Básicas', description: 'Nome, categoria e configurações gerais' },
    { title: 'Regras', description: 'Definir condições e ações de alocação' },
    { title: 'Revisão', description: 'Revisar e confirmar a configuração' }
  ];

  const handleSave = async () => {
    if (!validateStep(currentStep)) return;

    try {
      const payload = {
        name: formData.name,
        description: formData.description || undefined,
        category: formData.category,
        priority: formData.priority,
        default_value: formData.default_value || undefined,
        is_active: formData.is_active,
        rules: formData.rules.map(rule => ({
          name: rule.name,
          description: rule.description,
          conditions: rule.conditions,
          action: rule.action,
          priority: rule.priority,
          logical_operator: rule.logical_operator,
          is_active: rule.is_active
        }))
      };

      if (isEditing && id) {
        await update.mutateAsync({ id, data: payload });
      } else {
        await create.mutateAsync(payload);
      }

      navigate('/virtual-tags');
    } catch (error) {
      console.error('Erro ao salvar Virtual Tag:', error);
    }
  };

  const handleCancel = () => {
    navigate('/virtual-tags');
  };

  if (loadingTag) {
    return (
      <div className="container mx-auto py-6">
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900 mx-auto"></div>
              <p className="mt-4">Carregando Virtual Tag...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">
            {isEditing ? 'Editar Virtual Tag' : 'Nova Virtual Tag'}
          </h1>
          <p className="text-muted-foreground">
            {isEditing ? 'Modifique as configurações da Virtual Tag' : 'Configure regras de alocação automática de custos'}
          </p>
        </div>
        <Button variant="outline" onClick={handleCancel}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Voltar
        </Button>
      </div>

      {/* Progress */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-4">
            {steps.map((step, index) => (
              <div 
                key={index}
                className={`flex items-center ${index < steps.length - 1 ? 'flex-1' : ''}`}
              >
                <div className="flex flex-col items-center">
                  <div className={`
                    w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                    ${index <= currentStep 
                      ? 'bg-primary text-primary-foreground' 
                      : 'bg-muted text-muted-foreground'
                    }
                  `}>
                    {index < currentStep ? (
                      <CheckCircle2 className="h-4 w-4" />
                    ) : (
                      index + 1
                    )}
                  </div>
                  <div className="mt-2 text-center">
                    <p className="text-sm font-medium">{step.title}</p>
                    <p className="text-xs text-muted-foreground hidden sm:block">
                      {step.description}
                    </p>
                  </div>
                </div>
                {index < steps.length - 1 && (
                  <div className={`
                    flex-1 h-px mx-4 
                    ${index < currentStep ? 'bg-primary' : 'bg-muted'}
                  `} />
                )}
              </div>
            ))}
          </div>
          <Progress value={(currentStep / (steps.length - 1)) * 100} className="h-2" />
        </CardContent>
      </Card>

      {/* Step Content */}
      <Card>
        <CardContent className="p-6">
          {currentStep === 0 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Informações Básicas</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome *</Label>
                    <Input
                      id="name"
                      placeholder="Ex: Recursos do Time de Engenharia"
                      value={formData.name}
                      onChange={(e) => updateField('name', e.target.value)}
                      className={errors.name ? 'border-red-500' : ''}
                    />
                    {errors.name && (
                      <p className="text-sm text-red-500">{errors.name}</p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="category">Categoria *</Label>
                    <Select 
                      value={formData.category} 
                      onValueChange={(value) => updateField('category', value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                      <SelectContent>
                        {categoryOptions.map((option) => (
                          <SelectItem key={option.value} value={option.value}>
                            {option.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="priority">Prioridade *</Label>
                    <Input
                      id="priority"
                      type="number"
                      min="1"
                      max="1000"
                      placeholder="100"
                      value={formData.priority}
                      onChange={(e) => updateField('priority', parseInt(e.target.value) || 100)}
                      className={errors.priority ? 'border-red-500' : ''}
                    />
                    {errors.priority && (
                      <p className="text-sm text-red-500">{errors.priority}</p>
                    )}
                    <p className="text-sm text-muted-foreground">
                      Prioridade de execução (1-1000). Menor valor = maior prioridade.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="default_value">Valor Padrão</Label>
                    <Input
                      id="default_value"
                      placeholder="Ex: Não Classificado"
                      value={formData.default_value}
                      onChange={(e) => updateField('default_value', e.target.value)}
                    />
                    <p className="text-sm text-muted-foreground">
                      Valor usado quando nenhuma regra for aplicada.
                    </p>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="description">Descrição</Label>
                  <Textarea
                    id="description"
                    placeholder="Descreva o propósito desta Virtual Tag..."
                    value={formData.description}
                    onChange={(e) => updateField('description', e.target.value)}
                    rows={3}
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_active"
                    checked={formData.is_active}
                    onCheckedChange={(checked) => updateField('is_active', checked)}
                  />
                  <Label htmlFor="is_active">Ativar Virtual Tag imediatamente</Label>
                </div>
              </div>
            </div>
          )}

          {currentStep === 1 && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-medium">Regras de Alocação</h3>
                  <p className="text-sm text-muted-foreground">
                    Defina condições para identificar recursos e ações para alocá-los
                  </p>
                </div>
                <Badge variant="secondary">
                  {formData.rules.length} regra(s)
                </Badge>
              </div>

              {errors.rules && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{errors.rules}</AlertDescription>
                </Alert>
              )}

              <RuleBuilder
                rules={formData.rules}
                onChange={(rules) => updateField('rules', rules)}
              />
            </div>
          )}

          {currentStep === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-medium mb-4">Revisar Configuração</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <Card>
                    <CardHeader className="pb-4">
                      <CardTitle className="text-base">Informações Gerais</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div>
                        <p className="text-sm text-muted-foreground">Nome</p>
                        <p className="font-medium">{formData.name}</p>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Categoria</p>
                        <Badge variant="outline">
                          {categoryOptions.find(c => c.value === formData.category)?.label}
                        </Badge>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Prioridade</p>
                        <p className="font-medium">{formData.priority}</p>
                      </div>
                      {formData.default_value && (
                        <div>
                          <p className="text-sm text-muted-foreground">Valor Padrão</p>
                          <p className="font-medium">{formData.default_value}</p>
                        </div>
                      )}
                      <div>
                        <p className="text-sm text-muted-foreground">Status</p>
                        <Badge variant={formData.is_active ? 'default' : 'secondary'}>
                          {formData.is_active ? 'Ativa' : 'Inativa'}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader className="pb-4">
                      <CardTitle className="text-base">Regras Configuradas</CardTitle>
                    </CardHeader>
                    <CardContent>
                      {formData.rules.length === 0 ? (
                        <p className="text-muted-foreground">Nenhuma regra configurada</p>
                      ) : (
                        <div className="space-y-3">
                          {formData.rules.map((rule, index) => (
                            <div key={index} className="p-3 border rounded-lg">
                              <div className="flex items-center justify-between mb-2">
                                <p className="font-medium">{rule.name}</p>
                                <Badge variant="outline">
                                  Prioridade {rule.priority}
                                </Badge>
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {rule.conditions.length} condição(ões) • {rule.logical_operator}
                              </p>
                              <p className="text-sm">
                                Ação: {rule.action.type} → {rule.action.value}
                              </p>
                            </div>
                          ))}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>

                {formData.description && (
                  <Card>
                    <CardHeader className="pb-4">
                      <CardTitle className="text-base">Descrição</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-muted-foreground">{formData.description}</p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Actions */}
      <Card>
        <CardContent className="p-4">
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={prevStep}
              disabled={currentStep === 0}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Anterior
            </Button>

            <div className="flex gap-2">
              <Button variant="outline" onClick={handleCancel}>
                Cancelar
              </Button>
              
              {currentStep < steps.length - 1 ? (
                <Button onClick={nextStep}>
                  Próximo
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button 
                  onClick={handleSave}
                  disabled={create.isPending || update.isPending}
                >
                  <Save className="mr-2 h-4 w-4" />
                  {(create.isPending || update.isPending) 
                    ? 'Salvando...' 
                    : isEditing ? 'Atualizar' : 'Criar Virtual Tag'
                  }
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VirtualTagForm;
