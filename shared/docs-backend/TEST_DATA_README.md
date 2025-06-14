# 🎯 Dados de Teste - X Cost API

Script simples e direto para criar dados fictícios realistas para testar sua API FinOps.

## 🚀 Uso Rápido

```bash
# Certifique-se que PostgreSQL está rodando
docker-compose up -d postgres redis localstack

# Criar dados de teste
python create_test_data.py

# Iniciar API e testar
uvicorn app.main:app --reload
```

## 📊 Dados Criados

### **👤 Usuários de Teste**
| Username | Senha | Role | Propósito |
|----------|-------|------|-----------|
| admin | ChangeMe123! | admin | Administrador completo |
| finops_manager | Password123! | finops_admin | Gerente FinOps |
| cloud_operator | Password123! | operator | Operador de cloud |
| cost_viewer | Password123! | viewer | Visualizador de custos |
| data_analyst | Password123! | viewer | Analista de dados |

### **💰 Dados de Custo**
- **~3.000 registros** realísticos
- **4 provedores**: AWS, Azure, GCP, Oracle Cloud
- **60 dias** de dados históricos
- **Padrões realistas**: crescimento, sazonalidade, variações
- **Cenários especiais**: picos de custo, recursos ociosos

### **💳 Orçamentos**
- 4 orçamentos de exemplo
- Diferentes períodos (mensal, trimestral, anual)
- Alertas configurados (75-90%)

## 🔧 Comandos Disponíveis

```bash
# Criar dados (padrão)
python create_test_data.py

# Limpar dados existentes antes de criar
python create_test_data.py --clean

# Apenas verificar dados existentes
python create_test_data.py --verify
```

## 🧪 Testando a API

### **1. Login**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"ChangeMe123!"}'
```

### **2. Endpoints Úteis**
```bash
# Salvar token
export TOKEN="seu_token_aqui"

# Listar custos
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/costs?limit=10"

# Análise de tendências
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/analytics/trend?provider_name=AWS"

# Verificar orçamentos
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/budgets"

# Status do sistema
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/system/status"
```

### **3. URLs Importantes**
- **📖 API Docs**: http://localhost:8000/docs
- **🏥 Health Check**: http://localhost:8000/api/v1/health
- **📊 PostgreSQL Admin**: http://localhost:8080

## 📈 Cenários de Teste Incluídos

### **🚨 Detecção de Anomalias**
- Picos de custo 5x maiores que o normal
- Localizados nos últimos 3 dias
- Útil para testar alertas de anomalia

### **💡 Oportunidades de Otimização**
- Recursos com alta utilização (>80%)
- Recursos ociosos (utilização <10%)
- Recomendações de otimização

### **📊 Análises Multi-Cloud**
- Distribuição realística entre provedores
- Diferentes padrões de custo por provedor
- Dados para comparações e benchmarks

## ⚠️ Troubleshooting

### **Erro de Conexão**
```bash
# Verificar PostgreSQL
docker-compose ps postgres
docker-compose logs postgres

# Reiniciar se necessário
docker-compose restart postgres
```

### **Dados Já Existem**
```bash
# Limpar e recriar
python create_test_data.py --clean
```

### **Erro de Permissões**
```bash
# Verificar conexão manual
psql postgresql://finops_user:finops_password@localhost:5432/finops_db
```

---

## ✅ Resumo

**Uma única comando cria tudo que você precisa:**

```bash
python create_test_data.py
```

**Resultado:**
- ✅ 5 usuários com diferentes roles
- ✅ 3.000+ registros de custo realísticos  
- ✅ 4 orçamentos configurados
- ✅ Cenários de anomalias e otimização
- ✅ Dados prontos para testar toda a API

**🚀 Sua aplicação FinOps está pronta para desenvolvimento!**