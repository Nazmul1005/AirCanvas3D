#!/usr/bin/env python3
"""
Debug script to test camera and hand detection.
Shows exactly what MediaPipe sees and detects.
"""

import cv2
import sys
import time

# Add backend to path
sys.path.insert(0, 'backend')

from hand_tracker import HandTracker
import config

print("=" * 60)
print("AirCanvas 3D - Camera & Hand Detection Debug")
print("=" * 60)

# Test camera
print("\n1. Testing camera...")
cap = cv2.VideoCapture(config.CAMERA_INDEX)

if not cap.isOpened():
    print(f"✗ ERROR: Could not open camera {config.CAMERA_INDEX}")
    print("\nTry these:")
    print("  1. Check if webcam is connected")
    print("  2. Close other apps using webcam (Zoom, Skype, etc.)")
    print("  3. Try different camera index in backend/config.py:")
    print("     CAMERA_INDEX = 1  # or 2, 3...")
    sys.exit(1)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

ret, frame = cap.read()
if not ret:
    print("✗ ERROR: Could not read from camera")
    sys.exit(1)

print(f"✓ Camera opened successfully")
print(f"  Resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")

# Mirror frame
frame = cv2.flip(frame, 1)

# Show raw camera feed
print("\n2. Testing raw camera feed...")
print("  Close this window to continue...")
cv2.imshow("Raw Camera Feed (Close this window)", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Initialize hand tracker
print("\n3. Initializing hand tracker...")
try:
    tracker = HandTracker()
    print("✓ Hand tracker initialized")
except Exception as e:
    print(f"✗ ERROR: Failed to initialize hand tracker: {e}")
    sys.exit(1)

# Test hand detection
print("\n4. Testing hand detection...")
print("=" * 60)
print("INSTRUCTIONS:")
print("  1. Show your hand to the camera")
print("  2. Try different distances (1-3 feet works best)")
print("  3. Make sure room is well-lit")
print("  4. Use a plain background (solid wall)")
print("  5. Press 'q' to quit, 'c' to see current config")
print("=" * 60)

frame_count = 0
hands_detected_count = 0
last_status_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    frame_count += 1
    
    # Mirror frame
    frame = cv2.flip(frame, 1)
    
    # Process with hand tracker
    results = tracker.process(frame)
    
    # Extract hands
    hands_data = tracker.extract_landmarks(results, frame.shape[1], frame.shape[0])
    
    if hands_data:
        hands_detected_count += 1
    
    # Draw landmarks
    debug_frame = tracker.draw_landmarks(frame.copy(), results)
    
    # Add status text
    h, w = debug_frame.shape[:2]
    
    # Detection status
    if hands_data:
        status = f"HANDS DETECTED: {len(hands_data)}"
        color = (0, 255, 0)  # Green
        
        # Show details for each hand
        y_offset = 60
        for i, hand in enumerate(hands_data):
            text = f"Hand {i+1}: {hand['handedness']} ({hand['confidence']:.2f})"
            cv2.putText(debug_frame, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            y_offset += 30
    else:
        status = "NO HANDS DETECTED"
        color = (0, 0, 255)  # Red
        
        # Show hints
        hints = [
            "Tips:",
            "- Improve lighting",
            "- Move hand closer (1-3 feet)",
            "- Use plain background",
            "- Show whole hand in frame",
            "- Try different hand positions"
        ]
        y_offset = 60
        for hint in hints:
            cv2.putText(debug_frame, hint, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
            y_offset += 25
    
    cv2.putText(debug_frame, status, (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Show FPS and detection rate
    if time.time() - last_status_time >= 2.0:
        fps = frame_count / 2.0
        detection_rate = (hands_detected_count / max(frame_count, 1)) * 100
        
        print(f"FPS: {fps:.1f} | Detection rate: {detection_rate:.1f}% | "
              f"Hands: {len(hands_data) if hands_data else 0}")
        
        frame_count = 0
        hands_detected_count = 0
        last_status_time = time.time()
    
    # Add instructions
    cv2.putText(debug_frame, "Press 'q' to quit, 'c' for config", 
               (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Show frame
    cv2.imshow("Hand Detection Debug - AirCanvas 3D", debug_frame)
    
    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        print("\nQuitting...")
        break
    elif key == ord('c'):
        print("\n" + "=" * 60)
        print("Current Configuration (backend/config.py):")
        print("=" * 60)
        print(f"Camera Index: {config.CAMERA_INDEX}")
        print(f"Resolution: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT}")
        print(f"MediaPipe Complexity: {config.MP_MODEL_COMPLEXITY}")
        print(f"Detection Confidence: {config.MP_MIN_DETECTION_CONFIDENCE}")
        print(f"Tracking Confidence: {config.MP_MIN_TRACKING_CONFIDENCE}")
        print("=" * 60)
        print()

# Cleanup
cap.release()
tracker.close()
cv2.destroyAllWindows()

print("\n" + "=" * 60)
print("Debug session complete!")
print("=" * 60)

if hands_detected_count == 0:
    print("\n⚠️  NO HANDS WERE DETECTED")
    print("\nTroubleshooting steps:")
    print("  1. LIGHTING: Add more light (face a window or lamp)")
    print("  2. BACKGROUND: Use a plain, solid-colored background")
    print("  3. DISTANCE: Keep hand 1-3 feet from camera")
    print("  4. POSITION: Keep entire hand visible in frame")
    print("  5. CONTRAST: Ensure good contrast between hand and background")
    print("\nIf still not working, try lowering detection threshold:")
    print("  Edit backend/config.py:")
    print("  MP_MIN_DETECTION_CONFIDENCE = 0.5  # (default is 0.7)")
    print("  MP_MIN_TRACKING_CONFIDENCE = 0.5   # (default is 0.6)")
else:
    print("\n✓ Hands were detected during this session!")
    print("  The hand tracking is working correctly.")
    print("  Make sure to maintain good lighting and positioning.")

print()
