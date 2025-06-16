# 📋 Plano de Execução - Integração Frontend para Anomalias e Oportunidades

## 🎯 **Objetivo**
Integrar todas as novas funcionalidades de **Cloud Native Optimization** (Anomalias e Oportunidades de Economia) no frontend React, criando uma experiência completa de monitoramento e otimização de custos cloud.

---

## 📊 **Contexto - APIs Disponíveis**

### **Endpoints Implementados:**
```http
GET /api/v1/optimization/anomalies          # Buscar anomalias
GET /api/v1/optimization/savings             # Buscar oportunidades  
GET /api/v1/optimization/recommendations     # Buscar recomendações
GET /api/v1/optimization/summary            # Resumo completo
POST /api/v1/optimization/cache/invalidate  # Invalidar cache
GET /api/v1/optimization/providers          # Provedores suportados
GET /api/v1/optimization/types              # Tipos de otimização
```

### **Parâmetros de Query Suportados:**
- `provider_name: Optional[str]` (AWS, Azure, GCP, Oracle)
- `days: int = 30` (período de análise)
- `severity: Optional[str]` (high, medium, low)
- `min_savings: Optional[float]` (economia mínima)
- `category: Optional[str]` (compute, storage, network, etc.)

---

## 🏗️ **Plano de Execução - 8 Fases**

---

### **📱 FASE 1: Criação de Componentes Base (3-4 horas)**

#### **1.1 - Criar Hooks de API**
**Arquivo:** `frontend/src/hooks/useOptimization.ts`

```typescript
// Implementar hooks para consumir as APIs:
- useAnomalies(provider?, days?, severity?)
- useSavingsOpportunities(provider?, minSavings?, category?)
- useOptimizationSummary(provider?)
- useOptimizationRecommendations(provider?)
- useInvalidateCache()
```

**Funcionalidades:**
- ✅ React Query para cache automático
- ✅ Loading states e error handling
- ✅ Refetch automático a cada 5 minutos
- ✅ Tipos TypeScript completos

#### **1.2 - Definir Tipos TypeScript**
**Arquivo:** `frontend/src/types/optimization.ts`

```typescript
// Definir interfaces para:
- CloudAnomaly (id, provider, severity, cost_impact, etc.)
- SavingsOpportunity (id, potential_savings, effort_level, etc.)
- OptimizationSummary (optimization_score, health_status, etc.)
- OptimizationRecommendation (priority, category, impact, etc.)
```

#### **1.3 - Utilitários de Formatação**
**Arquivo:** `frontend/src/utils/optimizationUtils.ts`

```typescript
// Implementar funções:
- formatCurrency(amount)
- formatSeverity(severity) → badge color
- formatEffortLevel(effort) → badge style
- calculateROI(savings, effort)
- groupByCategory(items)
- sortByPriority(items)
```

---

### **🎨 FASE 2: Cards de Resumo no Dashboard (2-3 horas)**

#### **2.1 - Card de Anomalias Detectadas**
**Arquivo:** `frontend/src/components/dashboard/AnomaliesCard.tsx`

**Layout:**
```
┌─────────────────────────────────────┐
│ 🔍 Anomalies Detected    [7] HIGH  │
├─────────────────────────────────────┤
│ • AWS EC2 Spike: $2,340            │
│ • Azure Storage: $890               │
│ • GCP Compute: $567                 │
├─────────────────────────────────────┤
│ Total Impact: $3,797                │
│ [View All Anomalies] →              │
└─────────────────────────────────────┘
```

**Funcionalidades:**
- ✅ Top 3 anomalias por impacto
- ✅ Contadores por severidade (badges coloridos)
- ✅ Link para página detalhada
- ✅ Refresh automático

#### **2.2 - Card de Oportunidades de Economia**
**Arquivo:** `frontend/src/components/dashboard/SavingsCard.tsx`

**Layout:**
```
┌─────────────────────────────────────┐
│ 💰 Savings Opportunities  $152.57K  │
├─────────────────────────────────────┤
│ • Reserved Instances: $67.8K        │
│ • Right-sizing: $45.2K              │
│ • Unused Resources: $39.5K          │
├─────────────────────────────────────┤
│ Potential Annual Savings            │
│ [Explore Opportunities] →           │
└─────────────────────────────────────┘
```

**Funcionalidades:**
- ✅ Top 3 oportunidades por valor
- ✅ Total de economia potencial
- ✅ Breakdown por categoria
- ✅ Progress bar de implementação

#### **2.3 - Card de Optimization Score**
**Arquivo:** `frontend/src/components/dashboard/OptimizationScoreCard.tsx`

**Layout:**
```
┌─────────────────────────────────────┐
│ 📊 Optimization Score               │
├─────────────────────────────────────┤
│        ●●●●●○○○○○                   │
│           67/100                    │
├─────────────────────────────────────┤
│ Status: Needs Attention             │
│ Recommendations: 23 pending         │
│ [View Details] →                    │
└─────────────────────────────────────┘
```

**Funcionalidades:**
- ✅ Score visual (0-100) com cores
- ✅ Health status badge
- ✅ Contadores de recomendações
- ✅ Drill-down para detalhes

---

### **📄 FASE 3: Página de Anomalias (4-5 horas)**

#### **3.1 - Layout Principal**
**Arquivo:** `frontend/src/pages/AnomaliesPage.tsx`

**Estrutura:**
```
┌─ Header ─────────────────────────────────────────┐
│ Anomalies Detection │ [Filters] [Refresh] [Export]│
├─ Filters Bar ───────────────────────────────────────┤
│ Provider: [All▼] Period: [30d▼] Severity: [All▼] │
├─ Summary Stats ─────────────────────────────────────┤
│ [7 Total] [4 High] [2 Medium] [1 Low] [$15.2K Impact]│
├─ Anomalies Table ───────────────────────────────────┤
│ [Tabela com paginação e ordenação]                │
└─────────────────────────────────────────────────────┘
```

#### **3.2 - Filtros Avançados**
**Componente:** `AnomaliesFilters.tsx`

```typescript
// Filtros implementados:
- Provider dropdown (AWS, Azure, GCP, Oracle, All)
- Period selector (7d, 30d, 90d, custom)
- Severity multi-select (High, Medium, Low)
- Service filter (EC2, Storage, etc.)
- Cost impact range slider
- Date range picker
```

#### **3.3 - Tabela de Anomalias**
**Componente:** `AnomaliesTable.tsx`

**Colunas:**
- Status (🔴 High, 🟡 Medium, 🟢 Low)
- Provider + Service (badges coloridos)
- Description (título + contexto)
- Cost Impact ($value + % change)
- Detected Date (relative time)
- Actions (View Details, Investigate)

**Funcionalidades:**
- ✅ Ordenação por qualquer coluna
- ✅ Paginação (10/25/50 por página)
- ✅ Busca em tempo real
- ✅ Seleção múltipla para ações em lote
- ✅ Export para CSV/Excel

#### **3.4 - Modal de Detalhes**
**Componente:** `AnomalyDetailsModal.tsx`

**Seções:**
- Overview (provider, service, timeline)
- Cost Impact (gráfico de trend)
- Root Cause Analysis
- Affected Resources (lista expandível)
- Recommended Actions
- Investigation Notes (comentários)

---

### **💰 FASE 4: Página de Oportunidades (4-5 horas)**

#### **4.1 - Layout Principal**
**Arquivo:** `frontend/src/pages/SavingsOpportunitiesPage.tsx`

**Estrutura:**
```
┌─ Header ─────────────────────────────────────────┐
│ Savings Opportunities │ [Filters] [Plan] [Export]│
├─ ROI Summary ───────────────────────────────────────┤
│ Total: $152K │ High ROI: $89K │ Quick Wins: $23K │
├─ Category Breakdown ────────────────────────────────┤
│ [Compute: 45%] [Storage: 30%] [Network: 25%]     │
├─ Opportunities Grid ────────────────────────────────┤
│ [Cards em grid com paginação]                    │
└─────────────────────────────────────────────────────┘
```

#### **4.2 - Filtros e Agrupamento**
**Componente:** `SavingsFilters.tsx`

```typescript
// Filtros implementados:
- Provider selector
- Category multi-select (Compute, Storage, Network, etc.)
- Effort level (Low, Medium, High)
- Minimum savings threshold
- ROI range
- Implementation complexity
- Sort by (Savings, ROI, Effort, Date)
```

#### **4.3 - Cards de Oportunidades**
**Componente:** `SavingOpportunityCard.tsx`

**Layout do Card:**
```
┌─────────────────────────────────────┐
│ 💾 Reserved Instances       [AWS]   │
├─────────────────────────────────────┤
│ Current: $2,340/mo                  │
│ Savings: $670/mo (29%)              │
│ Effort: ●●○ Medium                  │
├─────────────────────────────────────┤
│ ROI: 4.2x │ Confidence: 92%         │
│ [Implement] [Details] [Dismiss]     │
└─────────────────────────────────────┘
```

**Estados:**
- Default (pode implementar)
- In Progress (sendo implementado)
- Implemented (concluído)
- Dismissed (dispensado)

#### **4.4 - Modal de Implementação**
**Componente:** `ImplementationModal.tsx`

**Seções:**
- Implementation Steps (checklist)
- Estimated Timeline
- Required Permissions
- Risk Assessment
- Cost-Benefit Analysis
- Progress Tracking

---

### **📊 FASE 5: Dashboard de Otimização (3-4 horas)**

#### **5.1 - Página Principal**
**Arquivo:** `frontend/src/pages/OptimizationDashboard.tsx`

**Layout:**
```
┌─ KPIs Row ──────────────────────────────────────┐
│ [Score Card] [Anomalies] [Savings] [Health]    │
├─ Charts Row ────────────────────────────────────┤
│ [Trend Chart - 8 cols] [Category Pie - 4 cols] │
├─ Recommendations ───────────────────────────────┤
│ [Priority List - 6 cols] [Action Plan - 6 cols]│
├─ Recent Activity ───────────────────────────────┤
│ [Timeline of recent optimizations]             │
└─────────────────────────────────────────────────┘
```

#### **5.2 - Gráfico de Tendências**
**Componente:** `OptimizationTrendChart.tsx`

**Métricas:**
- Cost savings over time
- Anomalies detected per week
- Optimization score evolution
- Implementation rate

**Funcionalidades:**
- ✅ Multi-line chart com Recharts
- ✅ Toggle de métricas
- ✅ Zoom e pan
- ✅ Export de dados

#### **5.3 - Lista de Recomendações Prioritárias**
**Componente:** `PriorityRecommendations.tsx`

**Itens:**
- Top 5 recomendações por ROI
- Action buttons diretos
- Progress indicators
- Expected completion dates

---

### **🔔 FASE 6: Sistema de Notificações (2-3 horas)**

#### **6.1 - Alertas em Tempo Real**
**Componente:** `OptimizationAlerts.tsx`

**Tipos de Alertas:**
```typescript
- "New critical anomaly detected: $5,200 impact"
- "High-ROI opportunity identified: $12,000 potential"
- "Implementation completed: $3,400/month saved"
- "Optimization score improved: 67 → 73"
```

#### **6.2 - Centro de Notificações**
**Componente:** `NotificationCenter.tsx`

**Funcionalidades:**
- ✅ Lista de notificações não lidas
- ✅ Filtros por tipo e prioridade
- ✅ Ações rápidas (mark read, dismiss, act)
- ✅ Configurações de preferência

#### **6.3 - Toast Notifications**
**Integração:** Hook personalizado `useOptimizationToasts.ts`

**Trigger automático quando:**
- Nova anomalia crítica
- Oportunidade de alto valor
- Implementação concluída
- Score de otimização muda significativamente

---

### **🚀 FASE 7: Funcionalidades Avançadas (3-4 horas)**

#### **7.1 - Planos de Otimização**
**Arquivo:** `frontend/src/pages/OptimizationPlansPage.tsx`

**Funcionalidades:**
```typescript
// Criar planos customizados:
- Select múltiplas oportunidades
- Priorizar por ROI/impacto/esforço
- Timeline de implementação
- Budget allocation
- Risk assessment
- Progress tracking
```

#### **7.2 - Comparador de Cenários**
**Componente:** `ScenarioComparator.tsx`

**Cenários:**
- Current state vs optimized state
- Conservative vs aggressive optimization
- Provider-specific optimizations
- Timeline comparisons (3mo, 6mo, 1yr)

#### **7.3 - Export e Relatórios**
**Componente:** `OptimizationReports.tsx`

**Formatos:**
- PDF executive summary
- Excel detailed report
- PowerPoint presentation
- CSV raw data

**Conteúdo:**
- Executive summary
- Detailed findings
- Implementation roadmap
- ROI projections

#### **7.4 - Configurações Avançadas**
**Componente:** `OptimizationSettings.tsx`

**Configurações:**
```typescript
- Thresholds de alertas
- Preferências de notificação
- Auto-implementation rules
- Provider priorities
- Cost allocation tags
- Refresh intervals
```

---

### **🧪 FASE 8: Testes e Refinamentos (2-3 horas)**

#### **8.1 - Testes de Componentes**
**Arquivo:** `frontend/src/components/__tests__/`

```typescript
// Testes para cada componente:
- AnomaliesCard.test.tsx
- SavingsCard.test.tsx
- AnomaliesTable.test.tsx
- etc.

// Cobertura de teste:
- Loading states
- Error handling
- User interactions
- Data formatting
```

#### **8.2 - Testes de Integração**
**Arquivo:** `frontend/src/pages/__tests__/`

```typescript
// Testes E2E com React Testing Library:
- Full page rendering
- API integration
- Filter functionality
- Navigation flows
```

#### **8.3 - Performance Testing**
**Verificações:**
- Bundle size optimization
- React Query cache effectiveness
- Table virtualization para grandes datasets
- Lazy loading de componentes

#### **8.4 - Acessibilidade e UX**
**Melhorias:**
- ARIA labels completos
- Keyboard navigation
- Screen reader compatibility
- Color contrast validation
- Mobile responsiveness

---

## 📋 **Checklist de Deliverables**

### **🎯 Componentes Core (Obrigatório)**
- [ ] `useOptimization.ts` - Hooks de API
- [ ] `optimization.ts` - Tipos TypeScript
- [ ] `AnomaliesCard.tsx` - Card do dashboard
- [ ] `SavingsCard.tsx` - Card do dashboard
- [ ] `AnomaliesPage.tsx` - Página de anomalias
- [ ] `SavingsOpportunitiesPage.tsx` - Página de oportunidades
- [ ] `OptimizationDashboard.tsx` - Dashboard principal

### **🔧 Funcionalidades Avançadas (Opcional)**
- [ ] `OptimizationPlansPage.tsx` - Planos de otimização
- [ ] `NotificationCenter.tsx` - Centro de notificações
- [ ] `OptimizationReports.tsx` - Relatórios e exports
- [ ] `OptimizationSettings.tsx` - Configurações

### **📊 Integração com Sistema Existente**
- [ ] Adicionar rota no `App.tsx`
- [ ] Adicionar item no menu de navegação
- [ ] Integrar com sistema de autenticação
- [ ] Adicionar ao dashboard principal existente

### **🧪 Testes e Qualidade**
- [ ] Testes unitários (>80% cobertura)
- [ ] Testes de integração
- [ ] Validação de acessibilidade
- [ ] Performance audit

---

## ⏱️ **Estimativa de Tempo Total: 25-35 horas**

### **Timeline Recomendada:**
- **Semana 1**: Fases 1-3 (Componentes base + Anomalias)
- **Semana 2**: Fases 4-5 (Oportunidades + Dashboard)
- **Semana 3**: Fases 6-8 (Notificações + Avançado + Testes)

### **Dependências Críticas:**
1. **APIs Backend**: Todas funcionando (✅ CONCLUÍDO)
2. **Autenticação JWT**: Sistema existente
3. **UI Library**: Shadcn/ui (assumindo que já está)
4. **State Management**: React Query recomendado

---

## 🎯 **Resultado Final Esperado**

Uma **suite completa de otimização cloud** integrada ao frontend existente, oferecendo:

- 🔍 **Detecção proativa** de anomalias de custo
- 💰 **Identificação automática** de oportunidades de economia  
- 📊 **Dashboard executivo** com KPIs de otimização
- 🚀 **Planos de implementação** estruturados
- 📈 **ROI tracking** e análise de impacto
- 🔔 **Alertas inteligentes** em tempo real
- 📋 **Relatórios executivos** exportáveis

**Valor de negócio**: Interface completa para gestão proativa de custos cloud com potencial de economia significativa e melhoria contínua da eficiência operacional.

---

## 📚 **Referências Técnicas**

### **APIs Backend Disponíveis:**
- Base URL: `http://localhost:8000/api/v1/optimization/`
- Autenticação: JWT Bearer Token
- Rate Limiting: 100 requests/minute
- Cache TTL: 1-6 horas dependendo do endpoint

### **Modelos de Dados:**

```typescript
interface CloudAnomaly {
  id: string;
  provider: string;
  service: string;
  region?: string;
  anomaly_type: 'spike' | 'drift' | 'unusual_pattern' | 'cost_increase';
  severity: 'low' | 'medium' | 'high' | 'critical';
  detected_at: string;
  cost_impact: number;
  currency: string;
  description: string;
  root_cause?: string;
  affected_resources: string[];
}

interface SavingsOpportunity {
  id: string;
  provider: string;
  service: string;
  region?: string;
  opportunity_type: 'rightsizing' | 'reserved_instances' | 'spot_instances' | 
                   'storage_optimization' | 'network_optimization' | 
                   'idle_resources' | 'scheduling';
  estimated_savings: number;
  currency: string;
  confidence_level: number;
  implementation_effort: 'Baixo' | 'Médio' | 'Alto';
  description: string;
  resources_affected: string[];
  action_required: string;
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
}

interface OptimizationSummary {
  total_anomalies: number;
  total_opportunities: number;
  total_recommendations: number;
  total_estimated_savings: number;
  optimization_score: number;
  health_status: 'excellent' | 'good' | 'needs_attention' | 'critical';
  currency: string;
  last_updated: string;
  providers_summary: Record<string, any>;
}
```

### **Guias de Estilo:**

1. **Cores para Severidade:**
   - Critical: `bg-red-500`
   - High: `bg-orange-500`
   - Medium: `bg-yellow-500`
   - Low: `bg-green-500`

2. **Cores para Providers:**
   - AWS: `bg-orange-400`
   - Azure: `bg-blue-500`
   - GCP: `bg-green-500`
   - Oracle: `bg-red-500`

3. **Formatação de Moeda:**
   - Use `Intl.NumberFormat` para localização
   - Sempre mostrar currency symbol
   - Abreviar valores grandes (K, M, B)

---

## 🚀 **Como Executar este Plano**

### **Para o Agente Frontend:**

1. **Execute fase por fase** seguindo a numeração
2. **Complete todos os itens** de uma fase antes de avançar
3. **Teste cada componente** individualmente antes da integração
4. **Mantenha consistência** com o design system existente
5. **Documente** todas as decisões técnicas importantes

### **Comandos Úteis:**

```bash
# Testar APIs backend
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/optimization/summary

# Verificar tipos TypeScript
npm run type-check

# Executar testes
npm run test

# Build para produção
npm run build
```

**Status**: 📋 **Pronto para execução** - Todas as APIs backend estão funcionais e testadas.
