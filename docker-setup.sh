#!/bin/bash

# Docker Setup Script for Attention App
# This script sets up and runs the Attention App using Docker

set -e

echo "🚀 Setting up Attention App with Docker..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p backend/uploads backend/output backend/recordings backend/reports

# Build and start the services
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."
docker-compose ps

# Display access information
echo ""
echo "✅ Attention App is now running!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend: http://localhost"
echo "   Backend API: http://localhost:8000"
echo "   Health Check: http://localhost:8000/api/health"
echo ""
echo "📊 To view logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart the application:"
echo "   docker-compose restart"
echo ""

# Test the health endpoint
echo "🏥 Testing backend health..."
if curl -f http://localhost:8000/api/health &> /dev/null; then
    echo "✅ Backend is healthy and ready!"
else
    echo "⚠️  Backend might still be starting up. Please wait a moment and try accessing http://localhost"
fi
