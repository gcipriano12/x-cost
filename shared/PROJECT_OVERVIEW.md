# X-Cost - Monorepo Overview

## Estrutura do Projeto

Este é um monorepo para o projeto X-Cost, uma plataforma de análise de custos em cloud. O projeto está dividido em duas partes principais:

### Frontend (`/frontend`)
- **Responsável**: Claude AI
- **Tecnologia**: React + TypeScript + Vite
- **UI**: Tailwind CSS + shadcn/ui
- **Documentação**: CLAUDE.md na raiz

### Backend (`/backend`) 
- **Responsável**: GitHub Copilot
- **Tecnologia**: FastAPI + Python
- **Database**: PostgreSQL + SQLAlchemy
- **Documentação**: COPILOT.md na raiz

## Colaboração Entre Agentes

### Regras Fundamentais
1. **Separação de Responsabilidades**: Cada agente trabalha exclusivamente em sua área
2. **Preservação de Funcionalidades**: Novas implementações não podem quebrar o que já funciona
3. **Comunicação via Documentação**: Use `/shared` para documentar necessidades entre frontend/backend

### Fluxo de Comunicação
```
Claude (Frontend) ←→ /shared/ ←→ Copilot (Backend)
```

### Pasta `/shared`
- **docs-frontend/**: Documentação específica do frontend
- **docs-backend/**: Documentação específica do backend  
- **FRONTEND_README.md**: README do frontend
- **BACKEND_README.md**: README do backend (a ser criado pelo Copilot)

## Comandos Principais

### Frontend
```bash
cd frontend
npm run dev     # Desenvolvimento
npm run build   # Build
npm run lint    # Linting
```

### Backend  
```bash
cd backend
source venv/bin/activate
python app/main.py  # Desenvolvimento
pytest             # Testes
```

## Integração
- Backend serve APIs em `http://localhost:8000`
- Frontend consome APIs via axios client configurado
- Autenticação via JWT tokens
- Dados de custos de múltiplos cloud providers

## Monitoramento de Qualidade
- Frontend: ESLint + TypeScript
- Backend: pytest + type checking
- Ambos devem executar verificações antes de finalizar tarefas