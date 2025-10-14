@echo off
REM Docker Setup Script for Attention App (Windows)
REM This script sets up and runs the Attention App using Docker

echo 🚀 Setting up Attention App with Docker...

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    echo    Visit: https://docs.docker.com/desktop/windows/install/
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    echo    Visit: https://docs.docker.com/compose/install/
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "backend\uploads" mkdir "backend\uploads"
if not exist "backend\output" mkdir "backend\output"
if not exist "backend\recordings" mkdir "backend\recordings"
if not exist "backend\reports" mkdir "backend\reports"

REM Build and start the services
echo 🔨 Building Docker images...
docker-compose build

echo 🚀 Starting services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if services are running
echo 🔍 Checking service status...
docker-compose ps

REM Display access information
echo.
echo ✅ Attention App is now running!
echo.
echo 🌐 Access the application:
echo    Frontend: http://localhost
echo    Backend API: http://localhost:8000
echo    Health Check: http://localhost:8000/api/health
echo.
echo 📊 To view logs:
echo    docker-compose logs -f
echo.
echo 🛑 To stop the application:
echo    docker-compose down
echo.
echo 🔄 To restart the application:
echo    docker-compose restart
echo.

REM Test the health endpoint
echo 🏥 Testing backend health...
curl -f http://localhost:8000/api/health >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend might still be starting up. Please wait a moment and try accessing http://localhost
) else (
    echo ✅ Backend is healthy and ready!
)

pause
