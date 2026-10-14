# AirCanvas 3D - Project Structure

```
aircanvas3d/
│
├── backend/                          # Python backend
│   ├── main.py                       # Entry point: starts camera + WebSocket server
│   ├── camera.py                     # OpenCV webcam capture in background thread
│   ├── hand_tracker.py               # MediaPipe Hands wrapper
│   ├── gesture_engine.py             # Gesture classification with debouncing
│   ├── filters.py                    # One Euro filter for smoothing
│   └── config.py                     # All thresholds and constants
│
├── frontend/                         # Web frontend
│   ├── index.html                    # Main HTML page
│   ├── style.css                     # Styles and responsive layout
│   │
│   └── js/                           # JavaScript modules
│       ├── main.js                   # Application bootstrap and main loop
│       ├── scene.js                  # Three.js scene setup and rendering
│       ├── socket.js                 # WebSocket client with reconnection
│       ├── tools.js                  # Drawing, blocks, grab, erase logic
│       ├── state.js                  # State management and undo/redo
│       └── ui.js                     # UI elements and event handlers
│
├── requirements.txt                  # Python dependencies (pinned versions)
├── README.md                         # Full documentation and setup guide
├── HOW_IT_WORKS.md                   # Technical deep dive
├── PROJECT_STRUCTURE.md              # This file
└── start.sh                          # Quick start script for Unix systems

```

## File Descriptions

### Backend

#### `config.py`
Central configuration file containing all tunable parameters:
- Camera settings (resolution, FPS, device index)
- MediaPipe model parameters
- Gesture recognition thresholds
- Smoothing filter parameters
- Debouncing frame counts
- WebSocket server settings

#### `filters.py`
Implements signal smoothing algorithms:
- **OneEuroFilter**: Adaptive low-pass filter that reduces lag during fast movement
- **LandmarkFilter**: Applies One Euro filter to 2D or 3D coordinates
- **EMAFilter**: Simple exponential moving average (alternative)

#### `hand_tracker.py`
Wrapper around MediaPipe Hands:
- Initializes MediaPipe with configured parameters
- Processes frames and extracts landmarks
- Calculates hand size for normalization
- Draws debug visualization on frames

#### `gesture_engine.py`
Core gesture recognition logic:
- Classifies gestures: DRAW, PINCH, PALM, FIST, TWO_HAND_SCALE
- Normalizes all distances by hand size
- Implements hysteresis for pinch detection
- Applies debouncing to prevent flicker
- Smooths cursor and palm positions with One Euro filter
- Maintains per-hand state

#### `camera.py`
Threaded camera capture:
- Captures frames in background thread
- Mirrors frames horizontally
- Resizes to target resolution
- Calculates and reports FPS
- Thread-safe frame access

#### `main.py`
Application entry point:
- Initializes all components
- Starts camera capture thread
- Runs asyncio WebSocket server
- Processes frames in async loop
- Broadcasts data to all clients
- Shows debug window with landmarks
- Handles graceful shutdown (Ctrl+C)

### Frontend

#### `index.html`
Main page structure:
- Status badges (connection, FPS, gesture)
- Webcam picture-in-picture preview
- Toolbar with tool buttons and controls
- Tutorial overlay
- Canvas container for Three.js
- Imports Three.js via ES modules from CDN

#### `style.css`
Complete styling:
- Dark theme with gradient background
- Glassmorphism effects (backdrop blur)
- Responsive layout (desktop and mobile)
- Tool button states and animations
- Tutorial overlay and gesture cards
- Accessibility features (focus outlines, sr-only)

#### `js/main.js`
Application coordinator:
- Initializes all modules
- Handles WebSocket messages
- Implements gesture actions (draw, pinch, erase, scale)
- Manages active stroke and grabbed objects
- Implements undo/redo logic
- Handles save/load functionality
- Coordinates between scene, state, and UI

#### `js/scene.js`
Three.js scene management:
- Creates scene, camera, renderer
- Sets up lighting (ambient + directional + rim)
- Creates grid floor and ground plane
- Manages cursor sphere and shadow line
- Implements erase indicator
- Handles window resize
- Manages OrbitControls
- Provides methods to add/remove objects

#### `js/socket.js`
WebSocket client:
- Connects to backend server
- Automatic reconnection with exponential backoff
- Status change callbacks
- Message parsing and error handling
- Graceful disconnect

#### `js/tools.js`
Object creation and manipulation:
- **createStroke()**: TubeGeometry from points with emissive material
- **createBlock()**: BoxGeometry with random pastel color
- **findNearestObject()**: Spatial search for grabbing
- **findObjectsInRadius()**: Spatial search for erasing
- **highlightObject()**: Visual feedback for selected objects
- **animateRemoval()**: Fade and scale animation
- **optimizeStrokePoints()**: Remove redundant points
- **snapToGrid()**: Align blocks to grid

#### `js/state.js`
Global state manager:
- Tracks all strokes and blocks
- Maintains undo/redo stacks
- Records actions (create, delete, move, clear)
- Current tool and brush settings
- Active stroke and grabbed object state
- Export/import to/from JSON

#### `js/ui.js`
User interface controller:
- Updates connection status badge
- Updates gesture indicator icon and label
- Draws webcam preview with landmarks
- Handles toolbar button clicks
- Manages tutorial overlay
- Registers keyboard shortcuts (Ctrl+Z, Ctrl+Y)
- FPS counter updates
- Save/load file dialogs

## Data Flow

### Capture → Broadcast

```
Camera Thread          Main Thread              WebSocket
     |                      |                       |
  [Capture]                 |                       |
     |                      |                       |
  [Mirror]                  |                       |
     |                      |                       |
     v                      |                       |
[Thread-safe             [Get latest              |
   frame buffer]    ----> frame]                   |
                           |                       |
                      [MediaPipe                   |
                       detection]                  |
                           |                       |
                      [Extract                     |
                       landmarks]                  |
                           |                       |
                      [Gesture                     |
                       classify]                   |
                           |                       |
                      [Apply                       |
                       filters]                    |
                           |                       |
                      [Build JSON]                 |
                           |                       |
                           +-------------------> [Broadcast]
                                                    |
                                                    v
                                              [All clients]
```

### Frontend Render Loop

```
WebSocket Message
       |
       v
  [Parse JSON]
       |
       v
[Update cursor position]
       |
       +----> [Update cursor mesh]
       |
       +----> [Handle gesture action]
                |
                +----> DRAW: [Add stroke points]
                |
                +----> PINCH: [Grab/move/place block]
                |
                +----> PALM: [Erase in radius]
                |
                +----> TWO_HAND_SCALE: [Scale scene]
                |
                v
       [State updated]
       |
       v
  [Render frame]
```

## Extension Points

### Add New Gesture

1. Define in `gesture_engine.py`:
   ```python
   def _is_my_gesture(self, landmarks, hand_size):
       # Your logic here
       return True/False
   ```

2. Add to `_classify_gesture()` method

3. Handle in `frontend/js/main.js` in `onSocketMessage()`

### Add New Tool

1. Create tool logic in `frontend/js/tools.js`
2. Add button to `index.html` toolbar
3. Handle in `js/main.js` gesture handlers
4. Update `js/state.js` to track tool state

### Add Physics

1. Import physics engine (e.g., Cannon.js) in `index.html`
2. Create physics world in `js/scene.js`
3. Add rigid bodies when creating blocks
4. Update physics world in render loop
5. Sync Three.js mesh positions with physics bodies

### Multi-user Support

1. Backend: Track client IDs, broadcast user metadata
2. Frontend: Render other users' cursors with labels
3. State: Sync object creation/deletion across clients
4. Conflict resolution: Last-write-wins or operational transforms

## Performance Considerations

### Backend
- Camera capture in separate thread (doesn't block processing)
- MediaPipe model_complexity=0 for speed vs. 1 for accuracy
- Process at 640×480 (not full HD) for real-time performance
- No frame queue—always process latest frame

### Frontend
- Dispose geometries/materials explicitly to prevent memory leaks
- Optimize stroke points (remove close points) before creating mesh
- Use fog to reduce distant geometry rendering
- Shadow map size: 2048×2048 (balance quality vs. performance)
- Lerp cursor position for extra smoothing without CPU cost

## Security Notes

- WebSocket runs on localhost by default (not exposed to network)
- No authentication required (trusted local environment)
- No sensitive data transmitted (only hand coordinates)
- Frontend served via simple HTTP server (no HTTPS needed for localhost)

For production deployment:
- Add WSS (WebSocket Secure) with SSL certificates
- Implement authentication and authorization
- Add rate limiting on WebSocket messages
- Sanitize any user-provided data (file uploads, etc.)
