#!/usr/bin/env python3
"""
Simple test to check if OpenCV window can open.
"""

import cv2
import numpy as np

print("Testing OpenCV window capability...")
print()

# Create a test image
img = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(img, "OpenCV Window Test", (150, 200), 
           cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 2)
cv2.putText(img, "If you see this, windows work!", (120, 250),
           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 1)
cv2.putText(img, "Press any key to continue...", (150, 300),
           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 1)

# Try to open window
try:
    cv2.imshow("Test Window", img)
    print("✓ Window opened successfully!")
    print("  Press any key in the window to close it...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print("✓ Window closed successfully!")
    print()
    print("AR Canvas should work. Run: python ar_canvas.py")
except Exception as e:
    print(f"✗ Error opening window: {e}")
    print()
    print("This might mean:")
    print("  1. No display available (running over SSH?)")
    print("  2. OpenCV not properly installed")
    print("  3. Permission issues")
