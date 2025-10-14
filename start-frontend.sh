#!/bin/bash

# Frontend startup script for local development

echo "🎨 Starting Attention Detection Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Node modules not found. Please run setup.sh first."
    exit 1
fi

# Set environment variables
export VITE_API_URL=http://localhost:8000

echo "🔧 Environment configured"
echo "🌐 Starting Vite dev server on http://localhost:5173"

# Start the frontend
npm run dev

