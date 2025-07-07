# Práticas de Segurança - Tokens e Credenciais

## Visão Geral

Este documento descreve as práticas recomendadas para lidar com tokens e credenciais neste projeto.

## Diretrizes de Segurança

1. **NUNCA armazene tokens ou credenciais em arquivos de código-fonte**
   - Tokens e senhas devem ser gerenciados através de variáveis de ambiente ou serviços de gestão de segredos

2. **Use variáveis de ambiente para credenciais**
   ```bash
   # Configure variáveis de ambiente antes de executar scripts
   export X_COST_API_TOKEN="seu-token-aqui"
   ```

3. **Para desenvolvimento local**
   - Use um arquivo .env que esteja no .gitignore
   - Ferramentas como python-dotenv ou dotenv para Node.js podem carregar essas variáveis automaticamente

4. **Arquivos de token temporários**
   - Arquivos como `current-token.txt` devem ser adicionados ao .gitignore
   - Nunca faça commit de arquivos temporários contendo tokens

## Configuração da Autenticação

### Backend (Python)
```python
import os

# Obtenha tokens de variáveis de ambiente
TOKEN = os.environ.get("X_COST_API_TOKEN")
```

### Frontend (JavaScript)
```javascript
// Utilize o mecanismo de autenticação da aplicação
// Não armazene tokens em arquivos estáticos
```

## Gestão de Tokens para Testes

1. Gere tokens temporários com curto período de validade para testes
2. Utilize um arquivo `.env.test` para variáveis de ambiente em testes
3. Configure CI/CD para fornecer tokens seguros durante a pipeline

## Exemplo de .gitignore

```
# Arquivos de token e credenciais
*token*.txt
*token*.js
*.env
*.env.*
!.env.example
```

## Relatório de Segurança

Se encontrar credenciais ou tokens expostos no código, relate imediatamente para que sejam invalidados e substituídos por métodos seguros.
