#!/bin/bash
# AirCanvas 3D - Safe Cleanup Script
# Removes unnecessary files while keeping essentials

echo "============================================================"
echo "  AirCanvas 3D - Safe Cleanup Script"
echo "============================================================"
echo ""
echo "This script will:"
echo "  1. Create a backup of all files"
echo "  2. Show you what will be deleted"
echo "  3. Ask for confirmation before deleting"
echo "  4. Keep all essential files for AR mode"
echo ""
echo "What will be KEPT:"
echo "  ✅ simple_ar.py (your working AR canvas)"
echo "  ✅ debug_camera.py (testing tool)"
echo "  ✅ backend/ folder (all hand tracking files)"
echo "  ✅ venv/ folder (Python environment)"
echo "  ✅ requirements.txt"
echo "  ✅ START_HERE.md (quick guide)"
echo "  ✅ TROUBLESHOOTING.md (help)"
echo "  ✅ FILE_GUIDE.md (this guide)"
echo ""
echo "What will be REMOVED:"
echo "  🗑️  frontend/ folder (3D browser mode - not used)"
echo "  🗑️  ar_canvas.py (alternative version)"
echo "  🗑️  backend/main.py (WebSocket server for 3D)"
echo "  🗑️  Extra documentation files"
echo "  🗑️  Test scripts (except debug_camera.py)"
echo "  🗑️  Launcher scripts"
echo "  🗑️  Cache files"
echo ""
echo "Space saved: ~30-40 MB"
echo ""
echo "============================================================"
echo ""
read -p "Do you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled. No changes made."
    exit 0
fi

echo ""
echo "Step 1: Creating backup..."
backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$backup_dir"

# List of files to backup before deleting
files_to_backup=(
    "frontend"
    "ar_canvas.py"
    "backend/main.py"
    "HOW_IT_WORKS.md"
    "PROJECT_STRUCTURE.md"
    "QUICK_REFERENCE.md"
    "README.md"
    "RUN_AR_MODE.md"
    "TEST_CHECKLIST.md"
    "test_backend.py"
    "test_window.py"
    "start.sh"
    "run_ar.sh"
)

for item in "${files_to_backup[@]}"; do
    if [ -e "$item" ]; then
        cp -r "$item" "$backup_dir/" 2>/dev/null
    fi
done

echo "✓ Backup created in: $backup_dir/"
echo ""
echo "Step 2: Removing unnecessary files..."
echo ""

# Remove frontend (3D browser mode)
if [ -d "frontend" ]; then
    echo "  🗑️  Removing frontend/ folder..."
    rm -rf frontend/
    echo "     ✓ Removed"
fi

# Remove alternative AR version
if [ -f "ar_canvas.py" ]; then
    echo "  🗑️  Removing ar_canvas.py..."
    rm ar_canvas.py
    echo "     ✓ Removed"
fi

# Remove WebSocket server (only for 3D mode)
if [ -f "backend/main.py" ]; then
    echo "  🗑️  Removing backend/main.py (WebSocket server)..."
    rm backend/main.py
    echo "     ✓ Removed"
fi

# Remove extra documentation
docs_to_remove=(
    "HOW_IT_WORKS.md"
    "PROJECT_STRUCTURE.md"
    "QUICK_REFERENCE.md"
    "RUN_AR_MODE.md"
    "TEST_CHECKLIST.md"
)

for doc in "${docs_to_remove[@]}"; do
    if [ -f "$doc" ]; then
        echo "  🗑️  Removing $doc..."
        rm "$doc"
        echo "     ✓ Removed"
    fi
done

# Remove test scripts (keep debug_camera.py)
if [ -f "test_backend.py" ]; then
    echo "  🗑️  Removing test_backend.py..."
    rm test_backend.py
    echo "     ✓ Removed"
fi

if [ -f "test_window.py" ]; then
    echo "  🗑️  Removing test_window.py..."
    rm test_window.py
    echo "     ✓ Removed"
fi

# Remove launcher scripts
if [ -f "start.sh" ]; then
    echo "  🗑️  Removing start.sh..."
    rm start.sh
    echo "     ✓ Removed"
fi

if [ -f "run_ar.sh" ]; then
    echo "  🗑️  Removing run_ar.sh..."
    rm run_ar.sh
    echo "     ✓ Removed"
fi

# Remove cache files
if [ -d "backend/__pycache__" ]; then
    echo "  🗑️  Removing backend/__pycache__/..."
    rm -rf backend/__pycache__/
    echo "     ✓ Removed"
fi

echo ""
echo "============================================================"
echo "✅ Cleanup Complete!"
echo "============================================================"
echo ""
echo "What was removed:"
echo "  • Frontend folder (3D browser mode)"
echo "  • Alternative AR version"
echo "  • Extra documentation files"
echo "  • Test scripts"
echo "  • Launcher scripts"
echo "  • Cache files"
echo ""
echo "What remains (all you need!):"
echo "  ✅ simple_ar.py - Your working AR canvas"
echo "  ✅ debug_camera.py - Testing tool"
echo "  ✅ backend/ - Hand tracking engine"
echo "  ✅ venv/ - Python environment"
echo "  ✅ requirements.txt - Dependencies"
echo "  ✅ README.md - Main documentation"
echo "  ✅ START_HERE.md - Quick start"
echo "  ✅ TROUBLESHOOTING.md - Help guide"
echo "  ✅ FILE_GUIDE.md - File information"
echo ""
echo "Backup location: $backup_dir/"
echo "  (You can delete this backup folder anytime)"
echo ""
echo "Space saved: ~30-40 MB"
echo ""
echo "To run AR Canvas:"
echo "  python simple_ar.py"
echo ""
echo "============================================================"
