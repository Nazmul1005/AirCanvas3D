#!/bin/bash

# AirCanvas 3D - Setup Script
# This script sets up the project environment

set -e

echo "🎨 AirCanvas 3D Setup"
echo "===================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Found Python $python_version"

# Check if Python version is 3.10 or higher
required_version="3.10"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.10+ is required"
    exit 1
fi

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✓ Virtual environment recreated"
    else
        echo "✓ Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check if MediaPipe model exists
echo ""
echo "🤖 Checking MediaPipe model..."
if [ -f "backend/hand_landmarker.task" ]; then
    echo "✓ MediaPipe model found"
else
    echo "⚠️  MediaPipe model not found"
    echo "   It will be downloaded automatically on first run"
fi

# Display success message
echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start AirCanvas 3D:"
echo ""
echo "   Terminal 1 (Backend):"
echo "   $ source venv/bin/activate"
echo "   $ python backend/main.py"
echo ""
echo "   Terminal 2 (Frontend):"
echo "   $ cd frontend"
echo "   $ python -m http.server 8000"
echo ""
echo "   Browser:"
echo "   → http://localhost:8000"
echo ""
echo "📚 Read README.md for more information"
echo ""
