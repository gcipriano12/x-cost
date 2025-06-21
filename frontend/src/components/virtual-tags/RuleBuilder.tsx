import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { 
  Plus, 
  Trash2, 
  GripVertical, 
  Info,
  Settings
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAvailableFields } from '@/hooks/useVirtualTags';
import {
  VirtualTagRule,
  RuleCondition,
  RuleAction,
  RuleOperator,
  LogicalOperator,
  RuleActionType,
  AvailableField
} from '@/types/virtualTags';

interface RuleBuilderProps {
  rules: VirtualTagRule[];
  onChange: (rules: VirtualTagRule[]) => void;
  className?: string;
}

const operatorOptions: { value: RuleOperator; label: string; description: string }[] = [
  { value: 'equals', label: 'Igual a', description: 'Valor deve ser exatamente igual' },
  { value: 'not_equals', label: 'Diferente de', description: 'Valor deve ser diferente' },
  { value: 'contains', label: 'Contém', description: 'Valor deve conter o texto' },
  { value: 'not_contains', label: 'Não contém', description: 'Valor não deve conter o texto' },
  { value: 'starts_with', label: 'Inicia com', description: 'Valor deve iniciar com o texto' },
  { value: 'ends_with', label: 'Termina com', description: 'Valor deve terminar com o texto' },
  { value: 'regex', label: 'Expressão regular', description: 'Valor deve corresponder ao padrão' },
  { value: 'in', label: 'Está em', description: 'Valor deve estar na lista' },
  { value: 'not_in', label: 'Não está em', description: 'Valor não deve estar na lista' },
  { value: 'greater_than', label: 'Maior que', description: 'Valor numérico maior que' },
  { value: 'less_than', label: 'Menor que', description: 'Valor numérico menor que' },
  { value: 'greater_equal', label: 'Maior ou igual', description: 'Valor numérico maior ou igual' },
  { value: 'less_equal', label: 'Menor ou igual', description: 'Valor numérico menor ou igual' }
];

const actionTypeOptions: { value: RuleActionType; label: string; description: string }[] = [
  { value: 'set_value', label: 'Definir valor', description: 'Define um valor fixo para a tag' },
  { value: 'extract_from_field', label: 'Extrair de campo', description: 'Extrai valor de outro campo' },
  { value: 'map_value', label: 'Mapear valor', description: 'Mapeia valor usando dicionário' },
  { value: 'calculate', label: 'Calcular', description: 'Calcula valor usando expressão' },
  { value: 'default', label: 'Valor padrão', description: 'Usa valor padrão quando não há match' }
];

const RuleBuilder: React.FC<RuleBuilderProps> = ({ rules, onChange, className }) => {
  const { data: availableFields = [], isLoading: loadingFields } = useAvailableFields();

  const addRule = () => {
    const newRule: VirtualTagRule = {
      name: `Regra ${rules.length + 1}`,
      description: '',
      conditions: [{
        field: '',
        operator: 'equals',
        value: ''
      }],
      action: {
        type: 'set_value',
        value: ''
      },
      priority: rules.length + 1,
      logical_operator: 'AND',
      is_active: true
    };
    onChange([...rules, newRule]);
  };

  const updateRule = (index: number, updates: Partial<VirtualTagRule>) => {
    const newRules = [...rules];
    newRules[index] = { ...newRules[index], ...updates };
    onChange(newRules);
  };

  const removeRule = (index: number) => {
    const newRules = rules.filter((_, i) => i !== index);
    // Reorder priorities
    newRules.forEach((rule, i) => {
      rule.priority = i + 1;
    });
    onChange(newRules);
  };

  const moveRule = (fromIndex: number, toIndex: number) => {
    const newRules = [...rules];
    const [movedRule] = newRules.splice(fromIndex, 1);
    newRules.splice(toIndex, 0, movedRule);
    
    // Update priorities
    newRules.forEach((rule, i) => {
      rule.priority = i + 1;
    });
    onChange(newRules);
  };

  const addCondition = (ruleIndex: number) => {
    const newCondition: RuleCondition = {
      field: '',
      operator: 'equals',
      value: ''
    };
    const newRules = [...rules];
    newRules[ruleIndex].conditions.push(newCondition);
    onChange(newRules);
  };

  const updateCondition = (ruleIndex: number, conditionIndex: number, updates: Partial<RuleCondition>) => {
    const newRules = [...rules];
    newRules[ruleIndex].conditions[conditionIndex] = {
      ...newRules[ruleIndex].conditions[conditionIndex],
      ...updates
    };
    onChange(newRules);
  };

  const removeCondition = (ruleIndex: number, conditionIndex: number) => {
    const newRules = [...rules];
    newRules[ruleIndex].conditions = newRules[ruleIndex].conditions.filter((_, i) => i !== conditionIndex);
    onChange(newRules);
  };

  const updateAction = (ruleIndex: number, updates: Partial<RuleAction>) => {
    const newRules = [...rules];
    newRules[ruleIndex].action = { ...newRules[ruleIndex].action, ...updates };
    onChange(newRules);
  };

  const getFieldType = (fieldName: string): string => {
    const field = availableFields.find(f => f.field_name === fieldName);
    return field?.field_type || 'string';
  };

  const getOperatorsForField = (fieldName: string): typeof operatorOptions => {
    const fieldType = getFieldType(fieldName);
    
    if (fieldType === 'number') {
      return operatorOptions.filter(op => 
        ['equals', 'not_equals', 'greater_than', 'less_than', 'greater_equal', 'less_equal', 'in', 'not_in'].includes(op.value)
      );
    }
    
    if (fieldType === 'boolean') {
      return operatorOptions.filter(op => ['equals', 'not_equals'].includes(op.value));
    }
    
    // String fields support all operators
    return operatorOptions;
  };

  const renderConditionValue = (condition: RuleCondition, ruleIndex: number, conditionIndex: number) => {
    const fieldType = getFieldType(condition.field);
    const isListOperator = ['in', 'not_in'].includes(condition.operator);

    if (isListOperator) {
      const values = Array.isArray(condition.value) ? condition.value : [condition.value].filter(Boolean);
      return (
        <div className="space-y-2">
          <Label>Valores (um por linha)</Label>
          <textarea
            className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            placeholder="Digite os valores, um por linha"
            value={values.join('\n')}
            onChange={(e) => {
              const newValues = e.target.value.split('\n').filter(v => v.trim());
              updateCondition(ruleIndex, conditionIndex, { value: newValues });
            }}
          />
        </div>
      );
    }

    return (
      <div className="space-y-2">
        <Label>Valor</Label>
        <Input
          type={fieldType === 'number' ? 'number' : 'text'}
          placeholder={fieldType === 'number' ? 'Digite um número' : 'Digite o valor'}
          value={condition.value as string}
          onChange={(e) => updateCondition(ruleIndex, conditionIndex, { value: e.target.value })}
        />
      </div>
    );
  };

  const renderActionConfig = (action: RuleAction, ruleIndex: number) => {
    switch (action.type) {
      case 'set_value':
        return (
          <div className="space-y-2">
            <Label>Valor da Tag</Label>
            <Input
              placeholder="Digite o valor que será atribuído à tag"
              value={action.value || ''}
              onChange={(e) => updateAction(ruleIndex, { value: e.target.value })}
            />
          </div>
        );

      case 'extract_from_field':
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Campo de Origem</Label>
              <Select
                value={action.field || ''}
                onValueChange={(value) => updateAction(ruleIndex, { field: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o campo" />
                </SelectTrigger>
                <SelectContent>
                  {availableFields.map((field) => (
                    <SelectItem key={field.field_name} value={field.field_name}>
                      {field.field_label} ({field.field_name})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            {action.pattern && (
              <div className="space-y-2">
                <Label>Padrão de Extração (Regex)</Label>
                <Input
                  placeholder="Exemplo: team-(\w+)-.*"
                  value={action.pattern || ''}
                  onChange={(e) => updateAction(ruleIndex, { pattern: e.target.value })}
                />
              </div>
            )}
          </div>
        );

      case 'map_value':
        return (
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Campo de Origem</Label>
              <Select
                value={action.field || ''}
                onValueChange={(value) => updateAction(ruleIndex, { field: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o campo" />
                </SelectTrigger>
                <SelectContent>
                  {availableFields.map((field) => (
                    <SelectItem key={field.field_name} value={field.field_name}>
                      {field.field_label} ({field.field_name})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Mapeamento (JSON)</Label>
              <textarea
                className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder='{"dev": "Desenvolvimento", "prod": "Produção"}'
                value={action.mapping ? JSON.stringify(action.mapping, null, 2) : ''}
                onChange={(e) => {
                  try {
                    const mapping = JSON.parse(e.target.value);
                    updateAction(ruleIndex, { mapping });
                  } catch {
                    // Invalid JSON, ignore
                  }
                }}
              />
            </div>
          </div>
        );

      case 'default':
        return (
          <div className="space-y-2">
            <Label>Valor Padrão</Label>
            <Input
              placeholder="Valor usado quando nenhuma regra anterior fez match"
              value={action.default_value || ''}
              onChange={(e) => updateAction(ruleIndex, { default_value: e.target.value })}
            />
          </div>
        );

      default:
        return (
          <div className="space-y-2">
            <Label>Configuração</Label>
            <Input
              placeholder="Digite a configuração"
              value={action.value || ''}
              onChange={(e) => updateAction(ruleIndex, { value: e.target.value })}
            />
          </div>
        );
    }
  };

  if (loadingFields) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Construtor de Regras</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Settings className="h-5 w-5" />
          Construtor de Regras
        </CardTitle>
        <Alert>
          <Info className="h-4 w-4" />
          <AlertDescription>
            As regras são processadas em ordem de prioridade. A primeira regra que encontrar uma correspondência será aplicada.
          </AlertDescription>
        </Alert>
      </CardHeader>
      <CardContent className="space-y-6">
        {rules.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">Nenhuma regra definida</p>
            <Button onClick={addRule} variant="outline">
              <Plus className="h-4 w-4 mr-2" />
              Adicionar Primeira Regra
            </Button>
          </div>
        ) : (
          <>
            {rules.map((rule, ruleIndex) => (
              <Card key={ruleIndex} className="border-l-4 border-l-primary">
                <CardHeader className="pb-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <GripVertical className="h-4 w-4 text-muted-foreground cursor-move" />
                      <Badge variant="secondary">Prioridade {rule.priority}</Badge>
                      <Input
                        placeholder="Nome da regra"
                        value={rule.name}
                        onChange={(e) => updateRule(ruleIndex, { name: e.target.value })}
                        className="max-w-xs"
                      />
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeRule(ruleIndex)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                  {rule.description && (
                    <Input
                      placeholder="Descrição da regra (opcional)"
                      value={rule.description}
                      onChange={(e) => updateRule(ruleIndex, { description: e.target.value })}
                      className="mt-2"
                    />
                  )}
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Conditions Section */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <Label className="text-base font-medium">Condições (SE)</Label>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => addCondition(ruleIndex)}
                      >
                        <Plus className="h-4 w-4 mr-2" />
                        Adicionar Condição
                      </Button>
                    </div>

                    {rule.conditions.length > 1 && (
                      <div className="mb-4">
                        <Label>Operador Lógico</Label>
                        <Select
                          value={rule.logical_operator}
                          onValueChange={(value: LogicalOperator) => 
                            updateRule(ruleIndex, { logical_operator: value })
                          }
                        >
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="AND">E (AND)</SelectItem>
                            <SelectItem value="OR">OU (OR)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    <div className="space-y-4">
                      {rule.conditions.map((condition, conditionIndex) => (
                        <Card key={conditionIndex} className="border-dashed">
                          <CardContent className="pt-4">
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                              <div className="space-y-2">
                                <Label>Campo</Label>                  <Select
                    value={condition.field}
                    onValueChange={(value) => 
                      updateCondition(ruleIndex, conditionIndex, { field: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione o campo" />
                    </SelectTrigger>
                    <SelectContent>
                      {availableFields.map((field) => (
                        <SelectItem key={field.field_name} value={field.field_name}>
                          {field.field_label} ({field.field_name})
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                              </div>

                              <div className="space-y-2">
                                <Label>Operador</Label>
                                <Select
                                  value={condition.operator}
                                  onValueChange={(value: RuleOperator) => 
                                    updateCondition(ruleIndex, conditionIndex, { operator: value })
                                  }
                                >
                                  <SelectTrigger>
                                    <SelectValue placeholder="Selecione o operador" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {getOperatorsForField(condition.field).map((op) => (
                                      <SelectItem key={op.value} value={op.value}>
                                        {op.label}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>

                              <div className="space-y-2">
                                {renderConditionValue(condition, ruleIndex, conditionIndex)}
                              </div>
                            </div>

                            {rule.conditions.length > 1 && (
                              <div className="flex justify-end mt-4">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() => removeCondition(ruleIndex, conditionIndex)}
                                  className="text-destructive"
                                >
                                  <Trash2 className="h-4 w-4 mr-2" />
                                  Remover
                                </Button>
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>

                  <Separator />

                  {/* Action Section */}
                  <div>
                    <Label className="text-base font-medium mb-4 block">Ação (ENTÃO)</Label>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label>Tipo de Ação</Label>
                        <Select
                          value={rule.action.type}
                          onValueChange={(value: RuleActionType) => 
                            updateAction(ruleIndex, { type: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione a ação" />
                          </SelectTrigger>
                          <SelectContent>
                            {actionTypeOptions.map((action) => (
                              <SelectItem key={action.value} value={action.value}>
                                {action.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        {renderActionConfig(rule.action, ruleIndex)}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            <div className="flex justify-center">
              <Button onClick={addRule} variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Adicionar Nova Regra
              </Button>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};

export default RuleBuilder;
