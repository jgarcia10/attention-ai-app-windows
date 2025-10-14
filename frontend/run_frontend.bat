@echo off
REM Frontend startup script for Windows

echo 🚀 Starting Attention App Frontend...

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found.
    echo 💡 Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found.
    echo 💡 Please install npm (usually comes with Node.js)
    pause
    exit /b 1
)

echo ✅ npm found

REM Install dependencies if node_modules doesn't exist
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
) else (
    echo ✅ Dependencies already installed
)

REM Set environment variables
echo 🔧 Setting environment variables...
set VITE_API_URL=http://localhost:8000

echo 🌐 Starting Vite development server...
echo 📍 Frontend will be available at: http://localhost:5173
echo 📍 Backend API: http://localhost:8000
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

npm run dev
