#!/bin/bash

# Start Local Development Environment (without Docker)
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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

echo "🚀 Starting local development environment..."

# Check if required commands exist
if ! command_exists python3; then
    print_error "Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

if ! command_exists npm; then
    print_error "npm is not installed. Please install npm"
    exit 1
fi

# Check if PostgreSQL is running
if ! command_exists psql; then
    print_warning "PostgreSQL client not found. Make sure PostgreSQL is installed and running."
    print_status "You can install PostgreSQL with: sudo apt-get install postgresql postgresql-contrib"
fi

# Check if Redis is running
if ! command_exists redis-cli; then
    print_warning "Redis client not found. Make sure Redis is installed and running."
    print_status "You can install Redis with: sudo apt-get install redis-server"
fi

# Check if ports are available
if port_in_use 8000; then
    print_error "Port 8000 is already in use. Please stop the service using this port."
    exit 1
fi

if port_in_use 3000; then
    print_error "Port 3000 is already in use. Please stop the service using this port."
    exit 1
fi

# Start Redis if not running
print_status "Starting Redis..."
if ! pgrep redis-server > /dev/null; then
    if command_exists redis-server; then
        redis-server --daemonize yes
        print_success "Redis started"
    else
        print_warning "Redis not found. Please start Redis manually or install it."
    fi
else
    print_status "Redis is already running"
fi

# Start PostgreSQL if not running
print_status "Starting PostgreSQL..."
if ! pgrep postgres > /dev/null; then
    if command_exists pg_ctl; then
        print_warning "PostgreSQL not running. Please start PostgreSQL manually."
        print_status "You can start PostgreSQL with: sudo systemctl start postgresql"
    else
        print_warning "PostgreSQL not found. Please install and start PostgreSQL manually."
    fi
else
    print_status "PostgreSQL is already running"
fi

# Backend setup
print_status "Setting up backend..."
cd stock_control_backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Set up environment variables
if [ ! -f ".env" ]; then
    print_status "Creating .env file from example..."
    cp env.example .env
    print_warning "Please edit .env file with your database settings"
fi

# Run migrations
print_status "Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist
print_status "Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Start backend in background
print_status "Starting Django backend server..."
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Frontend setup
print_status "Setting up frontend..."
cd ../stock_control_frontend

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install

# Start frontend
print_status "Starting Vue.js frontend server..."
npm run dev &
FRONTEND_PID=$!

# Wait for services to start
sleep 5

print_success "Development environment started successfully!"
echo ""
echo "🌐 URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:8000/api/v1/"
echo "  Django Admin: http://localhost:8000/admin/"
echo ""
echo "🔐 Credentials:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "📝 To stop the development servers:"
echo "  Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "🔄 Hot reload is enabled - your changes will be reflected automatically!"

# Keep script running and handle Ctrl+C
trap "echo ''; print_status 'Stopping development servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; print_success 'Development servers stopped'; exit 0" INT

# Wait for background processes
wait
