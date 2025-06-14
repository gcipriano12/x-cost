# 🐳 Guia Podman - X Cost API

Este guia fornece instruções específicas para usar Podman com a API FinOps, incluindo configurações, troubleshooting e comandos úteis.

## 🔧 Configuração Inicial do Podman

### **1. Verificar Instalação**

```bash
# Verificar se Podman está instalado
podman --version

# Verificar se podman-compose está disponível
podman-compose --version
# OU
docker-compose --version  # Se usando compatibilidade Docker
```

### **2. Configuração do Podman Machine (macOS/Windows)**

```bash
# Listar machines
podman machine list

# Criar nova machine se necessário
podman machine init --memory 4096 --disk-size 50

# Iniciar machine
podman machine start

# Verificar status
podman machine list
```

### **3. Configuração de Conexões**

```bash
# Listar conexões
podman system connection list

# Definir conexão padrão se necessário
podman system connection default <connection-name>

# Testar conectividade
podman info
```

## 🚀 Executando a X Cost API com Podman

### **Método 1: Script Automático (Recomendado)**

```bash
# O script quick_start.sh detecta automaticamente Podman
chmod +x quick_start.sh
./quick_start.sh
```

### **Método 2: Comandos Manuais**

```bash
# 1. Subir serviços essenciais
podman-compose up -d postgres redis localstack
# OU
docker-compose up -d postgres redis localstack

# 2. Verificar status
podman-compose ps
# OU
docker-compose ps

# 3. Inicializar banco
source venv/bin/activate
PYTHONPATH=. python scripts/init_db.py

# 4. Iniciar API
PYTHONPATH=. uvicorn app.main:app --reload
```

## 🔍 Comandos Úteis com Podman

### **Gerenciamento de Containers**

```bash
# Listar containers rodando
podman ps

# Listar todos os containers
podman ps -a

# Ver logs de um container
podman logs finops_postgres
podman logs -f finops_redis  # Follow logs

# Conectar a um container
podman exec -it finops_postgres bash
podman exec -it finops_redis redis-cli

# Parar containers
podman stop finops_postgres finops_redis finops_localstack

# Remover containers
podman rm finops_postgres finops_redis finops_localstack
```

### **Gerenciamento de Volumes**

```bash
# Listar volumes
podman volume ls

# Inspecionar volume
podman volume inspect finops-api_postgres_data

# Remover volumes (CUIDADO: apaga dados!)
podman volume rm finops-api_postgres_data
```

### **Gerenciamento de Networks**

```bash
# Listar networks
podman network ls

# Inspecionar network
podman network inspect finops-api_finops_network

# Conectar container a network
podman network connect finops-api_finops_network container_name
```

### **Gerenciamento de Images**

```bash
# Listar images
podman images

# Remover images não usadas
podman image prune

# Build de imagem local
podman build -t finops-api:dev -f Dockerfile.dev .

# Pull de imagens
podman pull postgres:15-alpine
podman pull redis:7-alpine
```

## 🔧 Usando Podman Compose

### **Comandos Básicos**

```bash
# Subir todos os serviços
podman-compose up

# Subir em background
podman-compose up -d

# Subir serviços específicos
podman-compose up -d postgres redis

# Ver logs
podman-compose logs
podman-compose logs -f postgres

# Parar serviços
podman-compose stop

# Parar e remover
podman-compose down

# Parar, remover e limpar volumes
podman-compose down -v
```

### **Troubleshooting Compose**

```bash
# Recriar containers
podman-compose up --force-recreate

# Rebuild images
podman-compose build --no-cache

# Validar compose file
podman-compose config

# Ver status detalhado
podman-compose ps
```

## 🛠️ Configurações Específicas do Podman

### **1. SELinux (Linux)**

Se estiver usando SELinux, pode ser necessário ajustar permissões:

```bash
# Verificar status do SELinux
sestatus

# Para volumes, usar :Z ou :z
# :Z = private label
# :z = shared label
podman run -v ./data:/data:Z postgres:15-alpine

# Ou desabilitar SELinux para containers específicos
podman run --security-opt label:disable postgres:15-alpine
```

### **2. User Namespaces**

```bash
# Verificar configuração de user namespaces
podman unshare cat /proc/self/uid_map

# Executar como root se necessário
podman run --privileged image_name

# Ou mapear usuários específicos
podman run --uidmap 0:1000:1000 image_name
```

### **3. Networking**

```bash
# Criar network personalizada
podman network create --driver bridge finops-network

# Listar configurações de rede
podman network inspect finops-network

# Para problemas de DNS
podman run --dns 8.8.8.8 image_name
```

## 🔍 Troubleshooting Comum

### **Problema 1: "Permission denied" ao acessar volumes**

```bash
# Solução 1: Usar labels SELinux
podman-compose up -d  # Já configurado no podman-compose.yml

# Solução 2: Verificar ownership
sudo chown -R $USER:$USER ./data

# Solução 3: Usar podman unshare
podman unshare chown -R 0:0 ./data
```

### **Problema 2: Containers não conseguem se comunicar**

```bash
# Verificar se estão na mesma network
podman inspect finops_postgres | grep NetworkMode
podman inspect finops_redis | grep NetworkMode

# Recriar network se necessário
podman network rm finops-api_finops_network
podman network create finops-api_finops_network
```

### **Problema 3: LocalStack não funciona**

```bash
# Para Podman, LocalStack pode precisar de configuração especial
# Editar podman-compose.yml:
environment:
  - DOCKER_HOST=tcp://host.containers.internal:2375

# Ou usar modo host
network_mode: host
```

### **Problema 4: Podman Machine não inicia (macOS/Windows)**

```bash
# Remover machine atual
podman machine stop
podman machine rm

# Criar nova machine com mais recursos
podman machine init --memory 6144 --disk-size 100 --cpus 4

# Iniciar machine
podman machine start
```

### **Problema 5: Problemas de performance**

```bash
# Aumentar recursos da machine
podman machine stop
podman machine set --memory 8192 --cpus 4

# Verificar uso de recursos
podman machine info

# Limpar caches
podman system prune -a
```

## 📊 Monitoramento com Podman

### **Stats em Tempo Real**

```bash
# Ver uso de recursos de todos os containers
podman stats

# Ver stats de container específico
podman stats finops_postgres

# Exportar stats
podman stats --format json > container_stats.json
```

### **Health Checks**

```bash
# Ver status de health checks
podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Health}}"

# Executar health check manualmente
podman healthcheck run finops_postgres
```

### **Logs Centralizados**

```bash
# Ver todos os logs do compose
podman-compose logs --timestamps

# Filtrar logs por serviço
podman-compose logs postgres | grep ERROR

# Exportar logs
podman-compose logs > finops_logs.txt
```

## 🔄 Backup e Restore com Podman

### **Backup do Banco PostgreSQL**

```bash
# Backup usando pg_dump
podman exec finops_postgres pg_dump -U finops_user finops_db > backup.sql

# Backup do volume
podman run --rm -v finops-api_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz /data
```

### **Restore do Banco**

```bash
# Restore usando psql
cat backup.sql | podman exec -i finops_postgres psql -U finops_user finops_db

# Restore do volume
podman run --rm -v finops-api_postgres_data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres_backup.tar.gz -C /
```

## 🚀 Performance Tips

### **1. Otimizações de Sistema**

```bash
# Aumentar ulimits
ulimit -n 65536

# Para Linux, otimizar cgroups v2
echo 'memory.high 4G' > /sys/fs/cgroup/memory.high
```

### **2. Configurações de Container**

```bash
# Usar shared memory para PostgreSQL
podman run --shm-size=256m postgres:15-alpine

# Configurar CPU limits
podman run --cpus="2.0" --memory="4g" image_name
```

### **3. Otimizações de Rede**

```bash
# Usar host networking para melhor performance (quando possível)
podman run --network host image_name

# Configurar MTU específico
podman network create --opt com.docker.network.driver.mtu=1450 custom_network
```

## 📱 Integração com IDEs

### **VS Code com Podman**

```json
// .vscode/settings.json
{
    "dev.containers.dockerPath": "podman",
    "dev.containers.dockerComposePath": "podman-compose"
}
```

### **PyCharm com Podman**

1. Ir em **Settings** → **Build, Execution, Deployment** → **Docker**
2. Configurar **Docker daemon** para usar Podman socket
3. Adicionar interpretador Python do container

## 🔒 Segurança com Podman

### **Execução Rootless**

```bash
# Verificar se rodando rootless
podman info | grep rootless

# Configurar registries para rootless
echo 'unqualified-search-registries = ["docker.io"]' > ~/.config/containers/registries.conf
```

### **Políticas de Segurança**

```bash
# Verificar políticas
podman info | grep -A5 -B5 policies

# Configurar política customizada
sudo cp /etc/containers/policy.json /etc/containers/policy.json.bak
```

## ✅ Checklist Podman

- [ ] Podman instalado e funcionando
- [ ] Podman Machine iniciada (macOS/Windows)
- [ ] podman-compose ou docker-compose disponível
- [ ] Conexões configuradas corretamente
- [ ] Volumes com permissões adequadas
- [ ] Network criada e funcional
- [ ] Containers de infra rodando
- [ ] API conectando aos serviços
- [ ] Health checks passando

---

**🐳 Com este guia, sua API FinOps funcionará perfeitamente com Podman!**