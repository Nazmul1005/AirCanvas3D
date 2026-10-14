"""
Configuration for AirCanvas 3D gesture recognition and tracking.

All thresholds, constants, and tunable parameters in one place.
"""

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# MediaPipe Hands settings
MP_MODEL_COMPLEXITY = 1  # 0 (lite) or 1 (full)
MP_MIN_DETECTION_CONFIDENCE = 0.7
MP_MIN_TRACKING_CONFIDENCE = 0.6
MP_MAX_NUM_HANDS = 2

# Gesture recognition thresholds (normalized by hand size)
# Pinch: hysteresis prevents flickering
PINCH_THRESHOLD_START = 0.30  # thumb-index distance to trigger pinch
PINCH_THRESHOLD_END = 0.45    # must open wider to release

# Palm detection: all fingers extended and spread
PALM_FINGER_EXTEND_THRESHOLD = 0.6  # tip-to-wrist / pip-to-wrist ratio
PALM_SPREAD_THRESHOLD = 0.15        # min distance between adjacent fingertips (normalized)

# Draw gesture: index extended, others curled
FINGER_EXTEND_THRESHOLD = 0.6  # for per-finger extension test
FINGER_CURL_THRESHOLD = 0.4    # below this = curled

# Gesture debouncing (frames)
GESTURE_DEBOUNCE_START = 4  # gesture must hold for N frames to start
GESTURE_DEBOUNCE_END = 3    # gesture must be absent for N frames to end

# One Euro filter parameters for landmark smoothing
ONE_EURO_MIN_CUTOFF = 1.0   # lower = smoother but more lag
ONE_EURO_BETA = 0.007       # higher = reacts faster to velocity changes
ONE_EURO_DERIVATE_CUTOFF = 1.0

# Depth estimation (z-coordinate proxy from hand size)
DEPTH_SCALE = 2.0  # multiplier for z derived from hand size
DEPTH_OFFSET = 0.5 # base offset

# WebSocket settings
WS_HOST = "localhost"
WS_PORT = 8765

# Debug visualization
SHOW_DEBUG_WINDOW = True  # Show OpenCV window with landmarks
DEBUG_WINDOW_NAME = "AirCanvas 3D - Hand Tracking"
