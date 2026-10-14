#!/bin/bash
# Quick start script for AR Canvas

cd "/Users/nazmul/Desktop/Project/practice project/3D – Gesture-Controlled Virtual Construction/aircanvas3d"

echo "=========================================="
echo "  AirCanvas AR - Starting..."
echo "=========================================="
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo "Starting AR Canvas..."
echo ""
echo "A window will open showing your webcam."
echo ""
echo "Gestures:"
echo "  ✏️  Point index finger to DRAW"
echo "  ✋  Open palm to ERASE"
echo "  ✊  Make fist to PAUSE"
echo ""
echo "Keyboard:"
echo "  1-7: Change colors"
echo "  +/-: Change brush size"
echo "  C: Clear canvas"
echo "  Q: Quit"
echo ""
echo "=========================================="
echo ""

python ar_canvas.py
