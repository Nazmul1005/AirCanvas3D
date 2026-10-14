#!/usr/bin/env python3
"""
AirCanvas AR - Draw in the air and see it on your webcam feed!
Augmented Reality mode with drawing overlaid on camera.
"""

import cv2
import numpy as np
import sys
from collections import deque

sys.path.insert(0, 'backend')
from hand_tracker import HandTracker
import config

# Drawing settings
DRAW_COLOR = (0, 255, 255)  # Cyan
DRAW_THICKNESS = 5
ERASE_COLOR = (0, 0, 255)  # Red
ERASE_RADIUS = 50

# Colors for different modes
COLORS = {
    'cyan': (255, 255, 0),    # BGR format
    'yellow': (0, 255, 255),
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'purple': (255, 0, 255),
    'white': (255, 255, 255)
}

class ARCanvas:
    """Augmented Reality Canvas for drawing on webcam feed."""
    
    def __init__(self):
        # Initialize camera
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")
        
        # Set camera resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Read one frame to get actual size
        ret, test_frame = self.cap.read()
        if ret:
            self.frame_height, self.frame_width = test_frame.shape[:2]
            print(f"Camera resolution: {self.frame_width}x{self.frame_height}")
        else:
            self.frame_width, self.frame_height = 640, 480
        
        # Initialize hand tracker
        self.tracker = HandTracker()
        
        # Drawing canvas (transparent layer)
        self.canvas = None
        
        # Drawing state
        self.drawing = False
        self.prev_point = None
        self.current_color = COLORS['cyan']
        self.current_thickness = 5
        
        # Mode
        self.mode = 'draw'  # 'draw' or 'erase'
        
        # Points buffer for smooth lines
        self.points_buffer = deque(maxlen=5)
        
        # UI state
        self.show_ui = True
        
    def draw_smooth_line(self, canvas, p1, p2, color, thickness):
        """Draw a smooth line between two points."""
        if p1 and p2:
            cv2.line(canvas, p1, p2, color, thickness, cv2.LINE_AA)
    
    def process_frame(self):
        """Process one frame: detect hand, update drawing, display."""
        ret, frame = self.cap.read()
        if not ret:
            return False
        
        # Mirror frame
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]
        
        # Initialize canvas if needed
        if self.canvas is None:
            self.canvas = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Process hand tracking
        results = self.tracker.process(frame)
        hands_data = self.tracker.extract_landmarks(results, w, h)
        
        # Draw hand landmarks on frame
        frame_with_hands = self.tracker.draw_landmarks(frame.copy(), results)
        
        # Process gestures
        if hands_data:
            hand = hands_data[0]  # Use first hand
            landmarks = hand['landmarks']
            
            # Get index fingertip position (landmark 8)
            index_tip = landmarks[8]
            x = int(index_tip[0] * w)
            y = int(index_tip[1] * h)
            cursor_pos = (x, y)
            
            # Detect gesture
            gesture = self.detect_simple_gesture(landmarks)
            
            # Handle gesture
            if gesture == 'draw':
                # Draw mode - index finger extended
                self.mode = 'draw'
                
                if self.prev_point:
                    # Draw line from previous point
                    self.draw_smooth_line(self.canvas, self.prev_point, cursor_pos, 
                                         self.current_color, self.current_thickness)
                
                self.prev_point = cursor_pos
                self.drawing = True
                
                # Draw cursor
                cv2.circle(frame_with_hands, cursor_pos, 10, self.current_color, -1)
                cv2.circle(frame_with_hands, cursor_pos, 12, (255, 255, 255), 2)
                
            elif gesture == 'palm':
                # Erase mode - open palm
                self.mode = 'erase'
                
                # Get palm center (average of wrist and middle MCP)
                wrist = landmarks[0]
                middle_mcp = landmarks[9]
                palm_x = int((wrist[0] + middle_mcp[0]) / 2 * w)
                palm_y = int((wrist[1] + middle_mcp[1]) / 2 * h)
                palm_pos = (palm_x, palm_y)
                
                # Erase circle
                cv2.circle(self.canvas, palm_pos, ERASE_RADIUS, (0, 0, 0), -1)
                
                # Show erase cursor
                cv2.circle(frame_with_hands, palm_pos, ERASE_RADIUS, (0, 0, 255), 3)
                cv2.circle(frame_with_hands, palm_pos, 5, (0, 0, 255), -1)
                
                self.prev_point = None
                
            elif gesture == 'fist':
                # Idle - stop drawing
                self.prev_point = None
                self.drawing = False
                
                # Show idle cursor at index tip
                cv2.circle(frame_with_hands, cursor_pos, 8, (128, 128, 128), -1)
            
            elif gesture == 'peace':
                # Two fingers - change color
                self.prev_point = None
        else:
            # No hand detected
            self.prev_point = None
            self.drawing = False
        
        # Composite: frame + canvas
        # Make canvas semi-transparent
        mask = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        mask = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY)[1]
        
        # Blend canvas onto frame
        output = frame_with_hands.copy()
        output[mask > 0] = cv2.addWeighted(
            frame_with_hands[mask > 0], 0.3,
            self.canvas[mask > 0], 0.7,
            0
        )
        
        # Draw UI
        if self.show_ui:
            self.draw_ui(output, hands_data)
        
        return True, output
    
    def detect_simple_gesture(self, landmarks):
        """Simple gesture detection."""
        # Get fingertip positions
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Get wrist
        wrist = landmarks[0]
        
        # Calculate distances from wrist (simple extension detection)
        def is_extended(tip, pip_idx):
            tip_dist = ((tip[0] - wrist[0])**2 + (tip[1] - wrist[1])**2)**0.5
            pip_dist = ((landmarks[pip_idx][0] - wrist[0])**2 + 
                       (landmarks[pip_idx][1] - wrist[1])**2)**0.5
            return tip_dist > pip_dist * 0.8
        
        index_extended = is_extended(index_tip, 6)
        middle_extended = is_extended(middle_tip, 10)
        ring_extended = is_extended(ring_tip, 14)
        pinky_extended = is_extended(pinky_tip, 18)
        
        # PALM: all fingers extended
        if all([index_extended, middle_extended, ring_extended, pinky_extended]):
            return 'palm'
        
        # DRAW: only index extended
        if index_extended and not middle_extended and not ring_extended:
            return 'draw'
        
        # PEACE: index and middle extended
        if index_extended and middle_extended and not ring_extended:
            return 'peace'
        
        # Default: fist/idle
        return 'fist'
    
    def draw_ui(self, frame, hands_data):
        """Draw UI overlay."""
        h, w = frame.shape[:2]
        
        # Semi-transparent background for UI
        overlay = frame.copy()
        
        # Top bar
        cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
        frame[:80] = cv2.addWeighted(frame[:80], 0.3, overlay[:80], 0.7, 0)
        
        # Title
        cv2.putText(frame, "AirCanvas AR - Draw in the Air!", (20, 35),
                   cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)
        
        # Mode indicator
        mode_text = f"Mode: {self.mode.upper()}"
        mode_color = self.current_color if self.mode == 'draw' else (0, 0, 255)
        cv2.putText(frame, mode_text, (20, 65),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)
        
        # Hand status
        if hands_data:
            hand = hands_data[0]
            status = f"Hand: {hand['handedness']}"
            cv2.putText(frame, status, (w - 250, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No hand detected", (w - 250, 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Bottom bar - Instructions
        bar_height = 120
        cv2.rectangle(overlay, (0, h - bar_height), (w, h), (0, 0, 0), -1)
        frame[h - bar_height:] = cv2.addWeighted(
            frame[h - bar_height:], 0.3,
            overlay[h - bar_height:], 0.7, 0
        )
        
        # Instructions
        instructions = [
            "✏️  DRAW: Point index finger",
            "✋  ERASE: Open palm (all fingers)",
            "✊  PAUSE: Make a fist",
            "   [C] Clear | [1-7] Colors | [+/-] Size | [Q] Quit"
        ]
        
        y_offset = h - bar_height + 25
        for inst in instructions:
            cv2.putText(frame, inst, (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_offset += 25
        
        # Color palette
        colors_list = list(COLORS.items())
        x_offset = w - 400
        for i, (name, color) in enumerate(colors_list):
            cv2.rectangle(frame, (x_offset + i * 50, h - 100),
                         (x_offset + i * 50 + 40, h - 60), color, -1)
            cv2.rectangle(frame, (x_offset + i * 50, h - 100),
                         (x_offset + i * 50 + 40, h - 60), (255, 255, 255), 2)
            
            # Highlight current color
            if color == self.current_color:
                cv2.rectangle(frame, (x_offset + i * 50 - 3, h - 103),
                             (x_offset + i * 50 + 43, h - 57), (255, 255, 255), 3)
    
    def run(self):
        """Main loop."""
        print("=" * 60)
        print("AirCanvas AR - Augmented Reality Drawing")
        print("=" * 60)
        print("\nGestures:")
        print("  ✏️  DRAW: Point with index finger (others curled)")
        print("  ✋  ERASE: Open palm with all fingers spread")
        print("  ✊  PAUSE: Make a fist")
        print("\nKeyboard:")
        print("  C - Clear canvas")
        print("  1-7 - Change color")
        print("  +/- - Change thickness")
        print("  H - Toggle UI")
        print("  Q - Quit")
        print("=" * 60)
        print("\nStarting... Show your hand to the camera!")
        print()
        
        # Create named window with proper size
        window_name = "AirCanvas AR - Draw in the Air!"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(window_name, self.frame_width, self.frame_height)
        
        while True:
            success, frame = self.process_frame()
            if not success:
                break
            
            # Ensure frame is correct size
            if frame.shape[0] != self.frame_height or frame.shape[1] != self.frame_width:
                frame = cv2.resize(frame, (self.frame_width, self.frame_height))
            
            # Display
            cv2.imshow(window_name, frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                print("\nQuitting...")
                break
            elif key == ord('c'):
                # Clear canvas
                self.canvas = np.zeros_like(self.canvas)
                print("Canvas cleared!")
            elif key == ord('h'):
                # Toggle UI
                self.show_ui = not self.show_ui
            elif key == ord('=') or key == ord('+'):
                # Increase thickness
                self.current_thickness = min(20, self.current_thickness + 2)
                print(f"Thickness: {self.current_thickness}")
            elif key == ord('-') or key == ord('_'):
                # Decrease thickness
                self.current_thickness = max(2, self.current_thickness - 2)
                print(f"Thickness: {self.current_thickness}")
            elif ord('1') <= key <= ord('7'):
                # Change color
                color_idx = key - ord('1')
                color_name = list(COLORS.keys())[color_idx]
                self.current_color = COLORS[color_name]
                print(f"Color: {color_name}")
            elif key == ord('s'):
                # Save frame
                filename = f"aircanvas_ar_{int(cv2.getTickCount())}.png"
                cv2.imwrite(filename, frame)
                print(f"Saved: {filename}")
        
        # Cleanup
        self.cap.release()
        self.tracker.close()
        cv2.destroyAllWindows()
        
        print("\nThank you for using AirCanvas AR!")


if __name__ == "__main__":
    try:
        app = ARCanvas()
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
