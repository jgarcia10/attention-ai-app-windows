@echo off
REM Backend startup script for Windows

echo 🚀 Starting Attention App Backend...

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Trying python3...
    python3 --version >nul 2>&1
    if errorlevel 1 (
        echo ❌ Neither python nor python3 found.
        echo 💡 Please install Python or add it to your PATH
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo ✅ Python found: %PYTHON_CMD%

REM Test imports first
echo 🔍 Testing imports...
%PYTHON_CMD% test_imports.py
if errorlevel 1 (
    echo ❌ Import test failed. Please check the error messages above.
    pause
    exit /b 1
)

echo ✅ Imports successful!

REM Set environment variables
echo 🔧 Setting environment variables...
set YOLO_MODEL_PATH=./models/yolov8n.pt
set CONF_THRESHOLD=0.4
set YAW_T=20
set PITCH_T=15
set STREAM_WIDTH=1280
set STREAM_HEIGHT=720
set STREAM_FPS=20

echo 🌐 Starting Flask server...
echo 📍 Backend will be available at: http://localhost:8000
echo 📍 Health check: http://localhost:8000/api/health
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

%PYTHON_CMD% app.py
