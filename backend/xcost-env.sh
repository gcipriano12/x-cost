#!/bin/bash

# X-Cost Environment Manager
# Usage: ./xcost-env.sh [start|stop]

PROJECT_DIR="/Users/gcipriano/Repositories/x-cost"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[X-Cost]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[X-Cost]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[X-Cost]${NC} $1"
}

print_error() {
    echo -e "${RED}[X-Cost]${NC} $1"
}

# Function to start the environment
start_environment() {
    print_status "🚀 Iniciando ambiente X-Cost..."
    
    # Start Podman machine first
    print_status "🖥️  Verificando Podman machine..."
    if command -v podman &> /dev/null; then
        MACHINE_STATUS=$(podman machine list --format "{{.Running}}" 2>/dev/null | head -1)
        if [ "$MACHINE_STATUS" != "true" ]; then
            print_status "Iniciando Podman machine..."
            podman machine start
            if [ $? -eq 0 ]; then
                print_success "✅ Podman machine iniciada"
                # Wait for machine to be ready
                sleep 5
            else
                print_error "❌ Falha ao iniciar Podman machine"
                exit 1
            fi
        else
            print_success "✅ Podman machine já está rodando"
        fi
    else
        print_error "❌ Podman não encontrado"
        exit 1
    fi
    
    # Start Podman containers
    print_status "🐳 Iniciando containers Podman..."
    cd "$BACKEND_DIR"
    
    if ! command -v podman-compose &> /dev/null; then
        print_warning "⚠️  podman-compose não encontrado, tentando com podman compose..."
        podman compose -f podman-compose.yml up -d 2>/dev/null || { print_error "❌ Falha ao iniciar containers"; exit 1; }
    else
        podman-compose -f podman-compose.yml up -d 2>/dev/null || { print_error "❌ Falha ao iniciar containers"; exit 1; }
    fi
    
    print_success "✅ Containers Podman iniciados"
    # Wait for services to be ready
    print_status "⏳ Aguardando containers ficarem prontos..."
    sleep 10
    
    # Start backend
    print_status "Iniciando backend (FastAPI)..."
    cd "$BACKEND_DIR"
    
    # Kill any existing backend process
    pkill -f "uvicorn app.main:app" 2>/dev/null
    
    # Start backend in background
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/xcost-backend.log 2>&1 &
    BACKEND_PID=$!
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend is running
    if ps -p $BACKEND_PID > /dev/null; then
        print_success "✅ Backend iniciado (PID: $BACKEND_PID, Port: 8000)"
        echo $BACKEND_PID > /tmp/xcost-backend.pid
    else
        print_error "❌ Falha ao iniciar backend"
        print_error "Verifique o log: tail -f /tmp/xcost-backend.log"
        exit 1
    fi
    
    # Start frontend
    print_status "Iniciando frontend (React/Vite)..."
    cd "$FRONTEND_DIR"
    
    # Kill any existing frontend process
    pkill -f "vite" 2>/dev/null
    
    # Start frontend in background
    npm run dev > /tmp/xcost-frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait a moment for frontend to start
    sleep 5
    
    # Check if frontend is running
    if ps -p $FRONTEND_PID > /dev/null; then
        # Try to determine the port from the log
        FRONTEND_PORT=$(grep -o "http://localhost:[0-9]*" /tmp/xcost-frontend.log | head -1 | grep -o "[0-9]*")
        if [ -z "$FRONTEND_PORT" ]; then
            FRONTEND_PORT="8080"
        fi
        print_success "✅ Frontend iniciado (PID: $FRONTEND_PID, Port: $FRONTEND_PORT)"
        echo $FRONTEND_PID > /tmp/xcost-frontend.pid
    else
        print_error "❌ Falha ao iniciar frontend"
        print_error "Verifique o log: tail -f /tmp/xcost-frontend.log"
        exit 1
    fi
    
    print_success "🎉 Ambiente X-Cost iniciado com sucesso!"
    print_status ""
    print_status "🌐 URLs disponíveis:"
    print_status "  📱 Frontend: http://localhost:$FRONTEND_PORT"
    print_status "  🔧 Backend API: http://localhost:8000"
    print_status "  📊 API Docs: http://localhost:8000/docs"
    print_status ""
    print_status "🖥️  Podman Machine: Ativa (4 CPUs, 2GB RAM)"
    print_status "🐳 Containers Podman ativos:"
    print_status "  - PostgreSQL (porta 5432)"
    print_status "  - Redis (porta 6379)" 
    print_status "  - LocalStack (porta 4566)"
    print_status ""
    print_status "🔧 Comandos úteis:"
    print_status "  Para parar: ./xcost-env.sh stop"
    print_status "  Ver status: ./xcost-env.sh status"
    print_status "  Reiniciar: ./xcost-env.sh restart"
    print_status ""
    print_status "📋 Logs:"
    print_status "  Backend:  tail -f /tmp/xcost-backend.log"
    print_status "  Frontend: tail -f /tmp/xcost-frontend.log"
    print_status "  Containers: podman logs [finops_postgres|finops_redis|finops_localstack]"
}

# Function to stop the environment
stop_environment() {
    print_status "🛑 Parando ambiente X-Cost..."
    
    # Stop frontend first
    print_status "Parando frontend..."
    if [ -f /tmp/xcost-frontend.pid ]; then
        FRONTEND_PID=$(cat /tmp/xcost-frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null; then
            kill $FRONTEND_PID
            print_success "✅ Frontend parado (PID: $FRONTEND_PID)"
        fi
        rm -f /tmp/xcost-frontend.pid
    fi
    
    # Kill any remaining vite processes
    pkill -f "vite" 2>/dev/null && print_status "Matou processos vite restantes"
    
    # Stop backend
    print_status "Parando backend..."
    if [ -f /tmp/xcost-backend.pid ]; then
        BACKEND_PID=$(cat /tmp/xcost-backend.pid)
        if ps -p $BACKEND_PID > /dev/null; then
            kill $BACKEND_PID
            print_success "✅ Backend parado (PID: $BACKEND_PID)"
        fi
        rm -f /tmp/xcost-backend.pid
    fi
    
    # Kill any remaining uvicorn processes
    pkill -f "uvicorn app.main:app" 2>/dev/null && print_status "Matou processos uvicorn restantes"
    
    # Stop Podman containers
    print_status "🐳 Parando containers Podman..."
    cd "$BACKEND_DIR"
    
    if ! command -v podman-compose &> /dev/null; then
        print_warning "⚠️  podman-compose não encontrado, tentando com podman compose..."
        podman compose -f podman-compose.yml down 2>/dev/null || true
    else
        podman-compose -f podman-compose.yml down 2>/dev/null || true
    fi
    
    # Always report success since we're using || true and suppressing errors
    print_success "✅ Containers Podman parados"
    
    # Additional cleanup: try to stop any remaining containers individually (silently)
    podman stop finops_postgres finops_redis finops_localstack 2>/dev/null || true
    
    # Stop Podman machine to free maximum resources
    print_status "🖥️  Parando Podman machine para liberar recursos..."
    if command -v podman &> /dev/null; then
        MACHINE_STATUS=$(podman machine list --format "{{.Running}}" 2>/dev/null | head -1)
        if [ "$MACHINE_STATUS" = "true" ]; then
            podman machine stop
            if [ $? -eq 0 ]; then
                print_success "✅ Podman machine parada (CPUs e RAM liberados)"
            else
                print_warning "⚠️  Falha ao parar Podman machine"
            fi
        else
            print_status "Podman machine já estava parada"
        fi
    fi
    
    # Clean up log files
    rm -f /tmp/xcost-backend.log /tmp/xcost-frontend.log
    
    print_success "🎉 Ambiente X-Cost parado com sucesso!"
    print_status "💻 Recursos máximos liberados:"
    print_status "  - Podman machine parada (4 CPUs + 2GB RAM liberados)"
    print_status "  - Todos os containers parados"
    print_status "  - Backend e frontend finalizados"
    print_status "  - Sua máquina está livre! 🚀"
}

# Function to show status
show_status() {
    print_status "📊 Status do ambiente X-Cost:"
    print_status ""
    
    # Check Podman machine
    print_status "🖥️  Podman Machine:"
    if command -v podman &> /dev/null; then
        MACHINE_INFO=$(podman machine list --format "table {{.Name}}\t{{.VMType}}\t{{.Running}}\t{{.CPUs}}\t{{.Memory}}" | tail -n +2)
        if [ -n "$MACHINE_INFO" ]; then
            echo "$MACHINE_INFO" | while read -r line; do
                MACHINE_NAME=$(echo "$line" | awk '{print $1}')
                VM_TYPE=$(echo "$line" | awk '{print $2}')
                RUNNING=$(echo "$line" | awk '{print $3}')
                CPUS=$(echo "$line" | awk '{print $4}')
                MEMORY=$(echo "$line" | awk '{print $5}')
                
                if [ "$RUNNING" = "true" ]; then
                    print_success "✅ $MACHINE_NAME ($VM_TYPE): Rodando - $CPUS CPUs, $MEMORY RAM"
                else
                    print_error "❌ $MACHINE_NAME ($VM_TYPE): Parada"
                fi
            done
        else
            print_error "❌ Nenhuma máquina Podman encontrada"
        fi
    else
        print_error "❌ Podman não encontrado"
    fi
    
    print_status ""
    
    # Check Podman containers
    print_status "🐳 Containers Podman:"
    if command -v podman &> /dev/null; then
        MACHINE_STATUS=$(podman machine list --format "{{.Running}}" 2>/dev/null | head -1)
        if [ "$MACHINE_STATUS" = "true" ]; then
            CONTAINERS=$(podman ps --filter "name=finops_" --format "table {{.Names}}\t{{.Status}}" 2>/dev/null | tail -n +2)
            if [ -n "$CONTAINERS" ]; then
                echo "$CONTAINERS" | while read -r line; do
                    CONTAINER_NAME=$(echo "$line" | awk '{print $1}')
                    STATUS=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ *//')
                    if echo "$STATUS" | grep -q "Up"; then
                        print_success "✅ $CONTAINER_NAME: $STATUS"
                    else
                        print_error "❌ $CONTAINER_NAME: $STATUS"
                    fi
                done
            else
                print_warning "⚠️  Nenhum container X-Cost rodando (machine ativa)"
            fi
        else
            print_error "❌ Podman machine parada - containers indisponíveis"
        fi
    else
        print_error "❌ Podman não encontrado"
    fi
    
    print_status ""
    
    # Check backend
    print_status "🔧 Backend (FastAPI):"
    if [ -f /tmp/xcost-backend.pid ]; then
        BACKEND_PID=$(cat /tmp/xcost-backend.pid)
        if ps -p $BACKEND_PID > /dev/null; then
            print_success "✅ Backend rodando (PID: $BACKEND_PID, Port: 8000)"
        else
            print_warning "⚠️  Backend PID file existe mas processo não está rodando"
        fi
    else
        if pgrep -f "uvicorn app.main:app" > /dev/null; then
            BACKEND_PID=$(pgrep -f "uvicorn app.main:app")
            print_warning "⚠️  Backend rodando sem PID file (PID: $BACKEND_PID)"
        else
            print_error "❌ Backend não está rodando"
        fi
    fi
    
    # Check frontend
    print_status "📱 Frontend (React/Vite):"
    if [ -f /tmp/xcost-frontend.pid ]; then
        FRONTEND_PID=$(cat /tmp/xcost-frontend.pid)
        if ps -p $FRONTEND_PID > /dev/null; then
            print_success "✅ Frontend rodando (PID: $FRONTEND_PID)"
        else
            print_warning "⚠️  Frontend PID file existe mas processo não está rodando"
        fi
    else
        if pgrep -f "vite" > /dev/null; then
            FRONTEND_PID=$(pgrep -f "vite")
            print_warning "⚠️  Frontend rodando sem PID file (PID: $FRONTEND_PID)"
        else
            print_error "❌ Frontend não está rodando"
        fi
    fi
}

# Main script logic
case "$1" in
    start)
        start_environment
        ;;
    stop)
        stop_environment
        ;;
    status)
        show_status
        ;;
    restart)
        print_status "🔄 Reiniciando ambiente X-Cost..."
        stop_environment
        sleep 2
        start_environment
        ;;
    *)
        echo "Usage: $0 {start|stop|status|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Inicia o ambiente X-Cost completo (Podman + backend + frontend)"
        echo "  stop    - Para o ambiente X-Cost e libera TODOS os recursos"
        echo "  status  - Mostra o status de todos os serviços"
        echo "  restart - Para e inicia novamente o ambiente completo"
        echo ""
        echo "🖥️  Inclui gerenciamento completo do Podman:"
        echo "  - Podman machine (4 CPUs + 2GB RAM)"
        echo "  - Containers: PostgreSQL, Redis, LocalStack"
        echo ""
        echo "Exemplos:"
        echo "  $0 start     # Inicia containers + backend + frontend"
        echo "  $0 stop      # Para tudo e libera recursos"
        echo "  $0 status    # Ver status completo"
        echo ""
        exit 1
        ;;
esac