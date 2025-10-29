#!/bin/bash

# Development Mode Switcher
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    echo "🔄 Development Mode Switcher"
    echo ""
    echo "Usage: $0 [MODE]"
    echo ""
    echo "Modes:"
    echo "  local     - Start local development (no Docker)"
    echo "  docker    - Start Docker development environment"
    echo "  stop      - Stop all services"
    echo "  status    - Show current status"
    echo "  setup     - Setup development environment"
    echo ""
    echo "Examples:"
    echo "  $0 local     # Start local development"
    echo "  $0 docker    # Start Docker environment"
    echo "  $0 stop      # Stop all services"
    echo "  $0 status    # Check what's running"
}

check_status() {
    print_status "Checking current status..."
    
    # Check Docker containers
    if docker ps --format "{{.Names}}" | grep -q stock_control_backend; then
        print_status "🐳 Docker containers are running:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep stock_control_backend
    else
        print_status "🐳 No Docker containers running"
    fi
    
    # Check local processes
    if pgrep -f "python.*manage.py runserver" > /dev/null; then
        print_status "🐍 Django server is running locally"
    else
        print_status "🐍 Django server not running locally"
    fi
    
    if pgrep -f "npm.*dev" > /dev/null; then
        print_status "⚛️  Vue.js dev server is running locally"
    else
        print_status "⚛️  Vue.js dev server not running locally"
    fi
    
    # Check ports
    if lsof -i :8000 >/dev/null 2>&1; then
        print_status "🔌 Port 8000 is in use"
    fi
    
    if lsof -i :3000 >/dev/null 2>&1; then
        print_status "🔌 Port 3000 is in use"
    fi
}

case "${1:-help}" in
    "local")
        print_status "Starting local development mode..."
        ./stop-containers.sh
        ./start-local-dev.sh
        ;;
    "docker")
        print_status "Starting Docker development mode..."
        cd stock_control_backend
        docker compose -f docker-compose.alt.yml up -d
        print_success "Docker environment started!"
        print_status "Frontend: http://localhost:3000"
        print_status "Backend: http://localhost:8000"
        print_status "Admin: http://localhost:8000/admin/"
        ;;
    "stop")
        print_status "Stopping all services..."
        ./stop-containers.sh
        pkill -f "python.*manage.py runserver" 2>/dev/null || true
        pkill -f "npm.*dev" 2>/dev/null || true
        print_success "All services stopped!"
        ;;
    "status")
        check_status
        ;;
    "setup")
        print_status "Setting up development environment..."
        ./setup-dev-environment.sh
        ;;
    "help"|*)
        show_help
        ;;
esac
