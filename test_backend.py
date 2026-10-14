#!/usr/bin/env python3
"""
Test script to verify backend imports and basic functionality.
"""

import sys

print("Testing AirCanvas 3D backend...")
print("=" * 60)

# Test imports
print("\n1. Testing imports...")
try:
    import cv2
    print("   ✓ opencv-python imported")
except ImportError as e:
    print(f"   ✗ opencv-python failed: {e}")
    sys.exit(1)

try:
    import mediapipe
    print("   ✓ mediapipe imported")
except ImportError as e:
    print(f"   ✗ mediapipe failed: {e}")
    sys.exit(1)

try:
    import websockets
    print("   ✓ websockets imported")
except ImportError as e:
    print(f"   ✗ websockets failed: {e}")
    sys.exit(1)

try:
    import numpy
    print("   ✓ numpy imported")
except ImportError as e:
    print(f"   ✗ numpy failed: {e}")
    sys.exit(1)

# Test backend modules
print("\n2. Testing backend modules...")
try:
    sys.path.insert(0, 'backend')
    import config
    print("   ✓ config module loaded")
except ImportError as e:
    print(f"   ✗ config failed: {e}")
    sys.exit(1)

try:
    import filters
    print("   ✓ filters module loaded")
except ImportError as e:
    print(f"   ✗ filters failed: {e}")
    sys.exit(1)

try:
    import hand_tracker
    print("   ✓ hand_tracker module loaded")
except ImportError as e:
    print(f"   ✗ hand_tracker failed: {e}")
    sys.exit(1)

try:
    import gesture_engine
    print("   ✓ gesture_engine module loaded")
except ImportError as e:
    print(f"   ✗ gesture_engine failed: {e}")
    sys.exit(1)

try:
    import camera
    print("   ✓ camera module loaded")
except ImportError as e:
    print(f"   ✗ camera failed: {e}")
    sys.exit(1)

# Test configuration
print("\n3. Testing configuration...")
print(f"   Camera: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.CAMERA_FPS} FPS")
print(f"   MediaPipe complexity: {config.MP_MODEL_COMPLEXITY}")
print(f"   WebSocket: ws://{config.WS_HOST}:{config.WS_PORT}")
print(f"   Pinch threshold: {config.PINCH_THRESHOLD_START} / {config.PINCH_THRESHOLD_END}")
print(f"   Gesture debounce: {config.GESTURE_DEBOUNCE_START} frames")

# Test filter initialization
print("\n4. Testing filter initialization...")
try:
    from filters import OneEuroFilter, LandmarkFilter
    f = OneEuroFilter()
    print("   ✓ OneEuroFilter initialized")
    
    lf = LandmarkFilter(dimensions=3)
    print("   ✓ LandmarkFilter initialized")
except Exception as e:
    print(f"   ✗ Filter initialization failed: {e}")
    sys.exit(1)

# Test gesture engine initialization
print("\n5. Testing gesture engine...")
try:
    from gesture_engine import GestureEngine
    ge = GestureEngine()
    print("   ✓ GestureEngine initialized")
except Exception as e:
    print(f"   ✗ GestureEngine initialization failed: {e}")
    sys.exit(1)

# Test hand tracker initialization
print("\n6. Testing hand tracker...")
try:
    from hand_tracker import HandTracker
    ht = HandTracker()
    print("   ✓ HandTracker initialized")
    ht.close()
    print("   ✓ HandTracker cleaned up")
except Exception as e:
    print(f"   ✗ HandTracker initialization failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All backend tests passed!")
print("\nTo run the full application:")
print("  1. python backend/main.py")
print("  2. cd frontend && python -m http.server 8000")
print("  3. Open http://localhost:8000 in your browser")
print("\nNote: Make sure your webcam is connected and not in use.")
