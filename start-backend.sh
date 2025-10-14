#!/bin/bash

# Backend startup script for local development

echo "🚀 Starting Attention Detection Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export YOLO_MODEL_PATH=./models/yolov8n.pt
export CONF_THRESHOLD=0.4
export YAW_T=60
export PITCH_T=45
export STREAM_WIDTH=1280
export STREAM_HEIGHT=720
export STREAM_FPS=20
export FLASK_ENV=development
export FLASK_DEBUG=True

echo "🔧 Environment configured"
echo "📊 Starting Flask server on http://localhost:8000"

# Start the backend
python3 app.py

