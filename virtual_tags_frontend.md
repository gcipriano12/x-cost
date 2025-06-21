# 🏷️ Implementação de Virtual Tags - X Cost

## 📋 RESUMO EXECUTIVO

Implementar funcionalidade **Virtual Tags** no X Cost baseada na solução da FinOut. Virtual Tags são regras dinâmicas de alocação de custos que funcionam como uma camada de abstração sobre dados de billing, permitindo 100% de alocação de custos sem modificar infraestrutura existente.

---

## 🎯 PROMPT PARA FRONTEND (CLAUDE AI)

### CONTEXTO
Você precisa implementar a interface completa de Virtual Tags no frontend React/TypeScript do X Cost. Esta funcionalidade permitirá aos usuários criar, gerenciar e visualizar regras de alocação de custos de forma intuitiva.

### REQUISITOS FUNCIONAIS

#### 1. **CRUD de Virtual Tags**
```typescript
interface VirtualTag {
  id: string;
  name: string;
  description?: string;
  category: 'Project' | 'Team' | 'Environment' | 'Feature' | 'Cost Center';
  rules: VirtualTagRule[];
  isActive: boolean;
  priority: number;
  defaultValue?: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
}

interface VirtualTagRule {
  id: string;
  conditions: RuleCondition[];
  action: RuleAction;
  priority: number;
  logicalOperator: 'AND' | 'OR';
}

interface RuleCondition {
  field: string; // Ex: provider, service, resourceId, tags.team
  operator: 'equals' | 'contains' | 'startsWith' | 'oneOf' | 'exists' | 'notExists';
  value: string | string[];
}

interface RuleAction {
  type: 'setValue' | 'copyFromField' | 'calculate';
  value: string;
  sourceField?: string;
}
```

#### 2. **Componentes UI Necessários**

**A. Listagem de Virtual Tags (VirtualTagsList)**
- Tabela com filtros e busca
- Colunas: Nome, Categoria, Status, Prioridade, Ações
- Ações: Editar, Duplicar, Ativar/Desativar, Excluir

**B. Formulário de Criação/Edição (VirtualTagForm)**
- Step 1: Informações básicas (nome, descrição, categoria)
- Step 2: Configuração de regras (WHERE/THEN logic)
- Step 3: Preview e validação
- Componente de regras com drag-and-drop para prioridade

**C. Editor de Regras (RuleBuilder)**
- Interface visual para construir condições IF/THEN
- Dropdowns para campos disponíveis
- Operadores dinâmicos baseados no tipo de campo
- Preview em tempo real das regras

**D. Dashboard de Virtual Tags (VirtualTagsDashboard)**
- Métricas: % cobertura de custos, regras ativas, top categorias
- Gráficos de alocação por categoria
- Lista de custos não alocados
- Alertas de regras com conflito

#### 3. **Páginas e Rotas**
```typescript
// Adicionar ao router existente
/virtual-tags                    // Lista principal
/virtual-tags/new               // Criar nova
/virtual-tags/:id/edit          // Editar existente
/virtual-tags/:id/preview       // Preview de alocação
/virtual-tags/dashboard         // Dashboard e analytics
```

#### 4. **Integração com API**
```typescript
// Hooks customizados necessários
const useVirtualTags = () => { /* CRUD operations */ }
const useVirtualTagRules = () => { /* Rule operations */ }
const useVirtualTagPreview = (tagId: string) => { /* Preview allocation */ }
const useVirtualTagMetrics = () => { /* Dashboard metrics */ }

// API endpoints esperados (backend deve implementar)
GET    /api/v1/virtual-tags
POST   /api/v1/virtual-tags
PUT    /api/v1/virtual-tags/:id
DELETE /api/v1/virtual-tags/:id
POST   /api/v1/virtual-tags/:id/preview
GET    /api/v1/virtual-tags/fields    // Campos disponíveis
GET    /api/v1/virtual-tags/metrics   // Métricas dashboard
```

#### 5. **UX/UI Guidelines**
- Usar componentes shadcn/ui existentes
- Seguir padrão de cores e design system atual
- Interface intuitiva tipo "no-code" para usuários de negócio
- Validação em tempo real
- Feedback visual para regras com conflito
- Tooltips explicativos para conceitos complexos

#### 6. **Estados e Validações**
- Form validation com zod
- Estados de loading/error em todas as operações
- Confirmação para operações destrutivas
- Validação de prioridades duplicadas
- Preview antes de salvar regras

### DELIVERABLES
1. Componentes React completos e funcionais
2. Hooks customizados para API integration
3. Páginas com roteamento configurado
4. Testes unitários dos componentes principais
5. Documentação em `/shared/docs-frontend/virtual-tags.md`

---

## 🔄 INTEGRAÇÃO ENTRE FRONTEND E BACKEND

### Fluxo de Dados
1. **Frontend** cria/edita Virtual Tags via formulário
2. **Backend** valida regras e armazena no banco
3. **Backend** processa alocação em background
4. **Frontend** exibe resultados e métricas

### Comunicação
- Usar axios client existente configurado
- Manter padrões de error handling atuais
- Implementar WebSocket para updates em tempo real (opcional)

### Validações
- **Frontend**: Validação de formulário em tempo real
- **Backend**: Validação de regras e conflitos
- **Ambos**: Validação de permissões por role

---

## 🎯 CRITÉRIOS DE SUCESSO

1. ✅ Interface intuitiva para usuários não-técnicos
2. ✅ Processamento eficiente de grandes volumes de dados
3. ✅ Alocação 100% dos custos (sem untagged)
4. ✅ Performance: <3s para preview, <30s para processamento completo
5. ✅ Retroatividade: aplicar regras a dados históricos
6. ✅ Escalabilidade: suportar centenas de regras
7. ✅ Auditoria: rastrear todas as mudanças
8. ✅ Testes: cobertura >90%

---

## 📚 REFERÊNCIAS TÉCNICAS

- **Especificação FOCUS**: Para padronização de dados de custo
- **FinOut Virtual Tags**: Referência funcional (análise anexa)
- **X Cost atual**: Manter compatibilidade e padrões existentes

Implementem esta funcionalidade mantendo a qualidade e padrões atuais do projeto X Cost!