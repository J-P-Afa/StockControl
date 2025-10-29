#!/bin/bash

# Stop and Remove Docker Containers for Development
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

echo "🛑 Stopping Docker containers for development..."

# Navigate to backend directory
cd stock_control_backend

# Stop and remove containers
print_status "Stopping containers..."
docker compose -f docker-compose.alt.yml down

# Optional: Remove volumes (uncomment if you want to reset database)
# print_warning "Removing volumes (this will delete all data)..."
# docker compose -f docker-compose.alt.yml down -v

# Optional: Remove images (uncomment if you want to clean up images)
# print_warning "Removing images..."
# docker rmi stock_control_backend-web stock_control_backend-frontend || true

print_success "Docker containers stopped successfully!"
print_status "You can now run the project locally for development."
print_status "Use './start-local-dev.sh' to start the project locally."
