#!/bin/bash

# Attention Detection System Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Setting up Attention Detection System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/{models,uploads,output}
mkdir -p frontend/dist

# Set permissions for directories
chmod 755 backend/{models,uploads,output}

echo "✅ Directory structure created"

# Option 1: Docker setup
read -p "Do you want to start with Docker? (y/N): " use_docker

if [[ $use_docker =~ ^[Yy]$ ]]; then
    echo "🐳 Starting with Docker..."
    docker-compose up --build -d
    
    echo "✅ Application started successfully!"
    echo "🌐 Frontend: http://localhost:5173"
    echo "🔧 Backend API: http://localhost:8000"
    echo "📊 Health Check: http://localhost:8000/api/health"
    
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f"
    echo ""
    echo "To stop the application:"
    echo "  docker-compose down"
    
else
    # Option 2: Local development setup
    echo "💻 Setting up for local development..."
    
    # Check Python version
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.11+"
        exit 1
    fi
    
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo "🐍 Python version: $python_version"
    
    # Check Node.js version
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 20+"
        exit 1
    fi
    
    node_version=$(node --version)
    echo "📦 Node.js version: $node_version"
    
    # Backend setup
    echo "🔧 Setting up backend..."
    cd backend
    
    if [ ! -d ".venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv .venv
    fi
    
    echo "Activating virtual environment and installing dependencies..."
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "✅ Backend setup complete"
    cd ..
    
    # Frontend setup
    echo "🎨 Setting up frontend..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install
    fi
    
    echo "✅ Frontend setup complete"
    cd ..
    
    echo "🎯 Setup complete!"
    echo ""
    echo "To start the application:"
    echo "  1. Backend: cd backend && source .venv/bin/activate && python3 app.py"
    echo "  2. Frontend: cd frontend && npm run dev"
    echo ""
    echo "Or use the provided start scripts:"
    echo "  ./start-backend.sh"
    echo "  ./start-frontend.sh"
fi

echo ""
echo "📖 For detailed documentation, see README.md"
echo "🧪 To run demo: cd backend && python3 -m _samples.run_demo --mode webcam"

