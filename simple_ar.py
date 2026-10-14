#!/usr/bin/env python3
"""
Simple AR Canvas - Minimal version with full camera view guaranteed.
"""

import cv2
import numpy as np
import sys

sys.path.insert(0, 'backend')
from hand_tracker import HandTracker
import config

print("=" * 60)
print("Simple AR Canvas - Draw in the Air!")
print("=" * 60)
print("\nGestures:")
print("  ✏️  Point index finger = DRAW")
print("  ✋  Open palm = ERASE")
print("  ✊  Make fist = PAUSE")
print("\nKeyboard:")
print("  C = Clear, Q = Quit, 1-5 = Colors")
print("=" * 60)

# Initialize camera
print("\nOpening camera...")
cap = cv2.VideoCapture(config.CAMERA_INDEX)

if not cap.isOpened():
    print("ERROR: Could not open camera!")
    sys.exit(1)

# Set resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Read test frame
ret, frame = cap.read()
if not ret:
    print("ERROR: Could not read from camera!")
    sys.exit(1)

frame = cv2.flip(frame, 1)
h, w = frame.shape[:2]
print(f"Camera: {w}x{h}")

# Initialize hand tracker
print("Initializing hand tracker...")
try:
    tracker = HandTracker()
    print("✓ Ready!")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)

# Create canvas
canvas = np.zeros((h, w, 3), dtype=np.uint8)

# Colors
colors = {
    '1': (255, 255, 0),    # Cyan
    '2': (0, 255, 255),    # Yellow
    '3': (0, 0, 255),      # Red
    '4': (0, 255, 0),      # Green
    '5': (255, 0, 255),    # Magenta
}
current_color = colors['1']

# Drawing state
prev_point = None
drawing = False

print("\nShow your hand to the camera!")
print("Window opening...")

# Create window
window_name = "Simple AR Canvas"
cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

while True:
    # Read frame
    ret, frame = cap.read()
    if not ret:
        print("Lost camera connection")
        break
    
    # Mirror
    frame = cv2.flip(frame, 1)
    
    # Process hand
    results = tracker.process(frame)
    hands_data = tracker.extract_landmarks(results, w, h)
    
    # Draw landmarks
    frame_display = tracker.draw_landmarks(frame.copy(), results)
    
    # Process gesture
    if hands_data:
        hand = hands_data[0]
        landmarks = hand['landmarks']
        
        # Get index tip
        index_tip = landmarks[8]
        x = int(index_tip[0] * w)
        y = int(index_tip[1] * h)
        
        # Simple gesture detection
        index_extended = landmarks[8][1] < landmarks[6][1]
        middle_extended = landmarks[12][1] < landmarks[10][1]
        ring_extended = landmarks[16][1] < landmarks[14][1]
        
        if index_extended and not middle_extended and not ring_extended:
            # DRAW mode
            if prev_point:
                cv2.line(canvas, prev_point, (x, y), current_color, 5)
            prev_point = (x, y)
            drawing = True
            
            # Show cursor
            cv2.circle(frame_display, (x, y), 10, current_color, -1)
            cv2.circle(frame_display, (x, y), 12, (255, 255, 255), 2)
            
        elif index_extended and middle_extended and ring_extended:
            # ERASE mode (all fingers up)
            wrist = landmarks[0]
            palm_x = int(wrist[0] * w)
            palm_y = int(wrist[1] * h)
            
            cv2.circle(canvas, (palm_x, palm_y), 50, (0, 0, 0), -1)
            cv2.circle(frame_display, (palm_x, palm_y), 50, (0, 0, 255), 3)
            
            prev_point = None
        else:
            # IDLE
            prev_point = None
    else:
        prev_point = None
    
    # Combine canvas with frame
    mask = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]
    
    output = frame_display.copy()
    if np.any(mask):
        output[mask > 0] = cv2.addWeighted(
            frame_display[mask > 0], 0.4,
            canvas[mask > 0], 0.6, 0
        )
    
    # Add simple UI
    cv2.putText(output, "Simple AR Canvas", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    
    if hands_data:
        cv2.putText(output, "Hand Detected!", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        cv2.putText(output, "Show your hand", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    cv2.putText(output, "C=Clear, Q=Quit, 1-5=Colors", (10, h-10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Show
    cv2.imshow(window_name, output)
    
    # Handle keys
    key = cv2.waitKey(1) & 0xFF
    
    if key == ord('q'):
        break
    elif key == ord('c'):
        canvas = np.zeros((h, w, 3), dtype=np.uint8)
        print("Canvas cleared!")
    elif chr(key) in colors:
        current_color = colors[chr(key)]
        print(f"Color changed to: {chr(key)}")

# Cleanup
cap.release()
tracker.close()
cv2.destroyAllWindows()

print("\nThank you!")
