# CLAUDE AI - Instruções para Frontend (X-Cost)

## Visão Geral
Este é um projeto monorepo X-Cost com frontend em React/TypeScript e backend em FastAPI/Python. Como Claude, você é responsável exclusivamente pelo **frontend** e deve seguir rigorosamente estas diretrizes.

## Responsabilidades
- ✅ Desenvolvimento e manutenção do frontend (`/frontend`)
- ✅ Documentação frontend (`/shared/docs-frontend`)
- ✅ Integração com APIs do backend (sem modificar o backend)
- ❌ **NUNCA** modificar arquivos do backend (`/backend`)
- ❌ **NUNCA** modificar configurações do backend

## Stack Tecnológica Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React Query (@tanstack/react-query)
- **Routing**: React Router DOM
- **HTTP Client**: Axios
- **UI Components**: Radix UI (via shadcn/ui)
- **Charts**: Recharts
- **Internacionalização**: i18next
- **Themes**: next-themes

## Comandos Disponíveis
```bash
cd frontend
npm run dev          # Desenvolvimento
npm run build        # Build produção
npm run build:dev    # Build desenvolvimento
npm run lint         # Lint/verificação
npm run preview      # Preview build
```

## Regras de Desenvolvimento

### 1. Preservação de Funcionalidades
- **CRÍTICO**: Novas implementações NÃO podem quebrar funcionalidades existentes
- Sempre testar funcionalidades relacionadas antes de finalizar
- Manter compatibilidade com APIs existentes

### 2. Convenções de Código
- Seguir padrões existentes do projeto
- Usar TypeScript com tipagem estrita
- Componentes funcionais com hooks
- Organização: `components/`, `hooks/`, `pages/`, `utils/`

### 3. Integração com Backend
- Backend roda em: `http://localhost:8000` (desenvolvimento)
- API base configurada em: `src/api/client.ts`
- Usar hooks existentes: `useAuth`, `useDashboard`, `useCredentials`, etc.
- **NUNCA** modificar endpoints do backend

### 4. Componentização
- Usar shadcn/ui para componentes base
- Componentes personalizados em `components/`
- Manter consistência visual com design system

### 5. Internacionalização
- Textos em `src/i18n/locales/en.json` e `pt.json`
- Usar hook `useTranslation` para textos
- Suporte a PT-BR e EN-US

## Arquivos Importantes
- `src/api/client.ts` - Cliente HTTP configurado
- `src/hooks/` - Hooks personalizados para integração
- `src/types/api.ts` - Tipagens da API
- `src/components/dashboard/` - Componentes do dashboard
- `src/utils/` - Utilitários e helpers

## Integração com Backend
O backend fornece:
- Autenticação JWT
- APIs de credenciais cloud
- Dados de custos e analytics
- Gestão de budgets e alertas

## Documentação Compartilhada
- Consulte `/shared/docs-frontend/` para integrações específicas
- Documentação backend está em `/shared/docs-backend/` (apenas consulta)

## Testes e Qualidade
- Executar `npm run lint` antes de finalizar
- Testar em desenvolvimento com `npm run dev`
- Verificar build com `npm run build`

## Colaboração com Copilot
- Copilot trabalha exclusivamente no backend
- Comunicação via documentação em `/shared/`
- Não modificar estruturas de dados do backend
- Reportar necessidades de API via documentação

## Fluxo de Trabalho
1. Analisar requisitos
2. Verificar funcionalidades existentes
3. Implementar sem quebrar o que funciona
4. Testar integração com backend
5. Executar lint e build
6. Documentar se necessário
7. **GERAR PROMPT DE INTEGRAÇÃO** para o usuário em formato markdown

## Sistema de Prompts de Integração

### OBRIGATÓRIO: Ao final de cada tarefa, você DEVE gerar um prompt para integração em formato markdown

Quando você completar uma tarefa que requer integração com o backend, você DEVE fornecer ao usuário um prompt estruturado para ser usado com o Copilot no backend.

### Formato do Prompt de Integração:

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

### Exemplos de Situações que Requerem Prompts:

1. **Nova funcionalidade frontend** que consome API inexistente
2. **Modificação de interface** que requer mudança no backend
3. **Novo formulário** que precisa de endpoint de submissão
4. **Integração com novo cloud provider**
5. **Alteração de modelo de dados**

### Regras para Geração de Prompts:

1. **SEMPRE gerar** quando há necessidade de integração
2. **Ser específico** sobre o que foi implementado
3. **Incluir exemplos** de estruturas de dados
4. **Documentar validações** necessárias
5. **Sugerir testes** para o backend
6. **Referenciar arquivos** relevantes