# Templates de Prompts de Integração

Este documento contém templates padronizados para comunicação entre Claude (frontend) e Copilot (backend).

## Template: Claude → Copilot (Frontend para Backend)

```
=== PROMPT PARA COPILOT (BACKEND) ===

**Tarefa**: [Descrição da tarefa realizada no frontend]

**Contexto**: 
- Implementei [X] no frontend
- Localização: [arquivos modificados]
- Funcionalidade: [descrição da funcionalidade]

**Necessidades do Backend**:
1. [Endpoint/API necessário]
2. [Modelo de dados esperado]
3. [Validações necessárias]
4. [Integrações cloud se aplicável]

**Estrutura de Dados Esperada**:
```typescript
// Exemplo da interface/tipo esperado
interface ExampleData {
  field1: string;
  field2: number;
}
```

**Endpoint Esperado**:
- Método: [GET/POST/PUT/DELETE]
- URL: `/api/exemplo`
- Request Body: [estrutura esperada]
- Response: [estrutura esperada]

**Validações**:
- [Lista de validações necessárias]

**Testes Sugeridos**:
- [Casos de teste que o backend deve implementar]

**Arquivos para Consulta**:
- Frontend: [arquivos relevantes que o Copilot pode consultar]
- Documentação: [documentos em /shared/ relevantes]

===================================
```

## Template: Copilot → Claude (Backend para Frontend)

```
=== PROMPT PARA CLAUDE (FRONTEND) ===

**Tarefa Completada**: [Descrição do que foi implementado no backend]

**Endpoint Implementado**:
- URL: `/api/exemplo`
- Método: [GET/POST/PUT/DELETE]
- Autenticação: [Bearer token/None]

**Request Body** (se aplicável):
```json
{
  "field1": "string",
  "field2": 123
}
```

**Response Body**:
```json
{
  "data": {
    "field1": "string",
    "field2": 123
  },
  "status": "success"
}
```

**Códigos de Status**:
- 200: Sucesso
- 400: Erro de validação
- 401: Não autorizado
- 404: Não encontrado
- 500: Erro interno

**Headers Necessários**:
- Content-Type: application/json
- Authorization: Bearer {token} (se aplicável)

**Validações Implementadas**:
- [Lista de validações ativas]

**Casos de Erro**:
- [Estrutura de resposta de erro]

**Testes Disponíveis**:
- [Endpoints de teste disponíveis]

**Arquivos Modificados**:
- [Lista de arquivos do backend modificados]

**Próximos Passos para Frontend**:
1. [Atualizar client HTTP se necessário]
2. [Atualizar tipos TypeScript]
3. [Implementar chamadas da API]
4. [Atualizar hooks se necessário]

===================================
```

## Exemplos Práticos

### Exemplo 1: Nova Funcionalidade de Relatórios

**Claude → Copilot**:
```
=== PROMPT PARA COPILOT (BACKEND) ===

**Tarefa**: Implementei interface de geração de relatórios personalizados no frontend

**Contexto**: 
- Implementei formulário de configuração de relatórios no frontend
- Localização: src/components/reports/ReportBuilder.tsx
- Funcionalidade: Usuário pode selecionar métricas, período e formato de exportação

**Necessidades do Backend**:
1. Endpoint para gerar relatórios personalizados
2. Modelo de dados para configuração de relatórios
3. Validações de período e métricas
4. Integração com cloud providers para coleta de dados

**Estrutura de Dados Esperada**:
```typescript
interface ReportConfig {
  name: string;
  metrics: string[];
  dateRange: {
    start: string;
    end: string;
  };
  format: 'pdf' | 'excel' | 'csv';
  cloudProviders: string[];
}
```

**Endpoint Esperado**:
- Método: POST
- URL: `/api/reports/generate`
- Request Body: ReportConfig
- Response: { reportId: string, downloadUrl: string }

**Validações**:
- Período não pode ser maior que 1 ano
- Pelo menos uma métrica deve ser selecionada
- Usuário deve ter permissão para os cloud providers selecionados

**Testes Sugeridos**:
- Teste de geração de relatório válido
- Teste de validação de período inválido
- Teste de permissões de cloud provider

**Arquivos para Consulta**:
- Frontend: src/components/reports/ReportBuilder.tsx
- Documentação: /shared/docs-frontend/REPORTS_INTEGRATION.md

===================================
```

### Exemplo 2: Resposta do Backend

**Copilot → Claude**:
```
=== PROMPT PARA CLAUDE (FRONTEND) ===

**Tarefa Completada**: Implementei API de geração de relatórios personalizados

**Endpoint Implementado**:
- URL: `/api/reports/generate`
- Método: POST
- Autenticação: Bearer token

**Request Body**:
```json
{
  "name": "string",
  "metrics": ["cost", "usage", "efficiency"],
  "dateRange": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "format": "pdf",
  "cloudProviders": ["aws", "azure"]
}
```

**Response Body**:
```json
{
  "data": {
    "reportId": "uuid-string",
    "downloadUrl": "/api/reports/download/uuid-string",
    "status": "processing",
    "estimatedTime": 300
  },
  "status": "success"
}
```

**Códigos de Status**:
- 200: Relatório iniciado com sucesso
- 400: Configuração inválida
- 401: Token inválido
- 403: Sem permissão para cloud providers
- 500: Erro interno

**Headers Necessários**:
- Content-Type: application/json
- Authorization: Bearer {token}

**Validações Implementadas**:
- Período máximo de 365 dias
- Métricas válidas: cost, usage, efficiency, savings
- Formatos válidos: pdf, excel, csv
- Verificação de permissões por cloud provider

**Casos de Erro**:
```json
{
  "error": {
    "code": "INVALID_DATE_RANGE",
    "message": "Date range cannot exceed 365 days",
    "details": {"maxDays": 365, "requestedDays": 400}
  },
  "status": "error"
}
```

**Testes Disponíveis**:
- GET /api/reports/test/generate - Endpoint de teste
- Logs disponíveis em /api/logs/reports

**Arquivos Modificados**:
- app/reports_api.py (novo)
- app/models.py (adicionado ReportConfig)
- tests/test_reports.py (novo)

**Próximos Passos para Frontend**:
1. Atualizar tipos em src/types/api.ts
2. Criar hook useReports para gerenciar estado
3. Implementar polling para status do relatório
4. Adicionar tratamento de erros específicos

===================================
```

## Diretrizes de Uso

### Para Claude (Frontend):
1. **Sempre gerar** prompt ao implementar funcionalidade que precisa do backend
2. **Ser específico** sobre estruturas de dados TypeScript
3. **Incluir contexto** completo da implementação
4. **Documentar casos de uso** e fluxos esperados

### Para Copilot (Backend):
1. **Processar prompts** do Claude como especificação técnica
2. **Implementar completamente** antes de responder
3. **Testar todas** as funcionalidades
4. **Documentar APIs** no formato OpenAPI quando possível

### Para o Usuário:
1. **Copiar e colar** prompts entre os agentes
2. **Aguardar implementação** completa antes de solicitar próximo passo
3. **Verificar integração** funcionando antes de prosseguir
4. **Manter histórico** de prompts para referência futura