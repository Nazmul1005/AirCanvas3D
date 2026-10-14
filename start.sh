#!/bin/bash
# AirCanvas 3D - Quick start script

echo "======================================"
echo "  AirCanvas 3D - Quick Start"
echo "======================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found."
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    echo "Installing dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo ""
echo "✅ Virtual environment activated"
echo ""
echo "Starting backend server..."
echo "Press Ctrl+C to stop"
echo ""
echo "After backend starts, open a new terminal and run:"
echo "  cd frontend && python -m http.server 8000"
echo ""
echo "Then open http://localhost:8000 in your browser"
echo ""
echo "======================================"
echo ""

# Start the backend
python backend/main.py
