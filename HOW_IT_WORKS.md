# How AirCanvas 3D Works

## System Architecture

AirCanvas 3D is divided into two main components that communicate over WebSocket:

### Backend (Python)
- **Camera Thread**: Captures frames from webcam at 30 FPS using OpenCV
- **MediaPipe Hands**: Detects up to 2 hands and extracts 21 3D landmarks per hand
- **Gesture Engine**: Classifies gestures based on normalized finger positions
- **WebSocket Server**: Broadcasts hand data to all connected browsers in real-time

### Frontend (JavaScript + Three.js)
- **WebSocket Client**: Receives hand tracking data with auto-reconnect
- **3D Scene**: Renders objects, cursor, grid, and lighting with Three.js
- **Tools System**: Handles drawing, block placement, grabbing, and erasing
- **State Manager**: Tracks all objects and implements undo/redo
- **UI Layer**: Displays HUD, toolbar, webcam preview, and tutorial

---

## Gesture Recognition Deep Dive

### Why Normalize by Hand Size?

The key insight is that hand positions change dramatically with distance from the camera:
- Close hand: large on screen, landmarks far apart
- Far hand: small on screen, landmarks close together

To make gestures work at any distance, we calculate:

```python
hand_size = distance(wrist[0], middle_mcp[9])
normalized_distance = raw_distance / hand_size
```

Now a "pinch" gesture has the same normalized thumb-index distance whether you're 1 foot or 3 feet from the camera.

### Pinch Detection with Hysteresis

Simple threshold:
```
if distance < 0.30: pinching = True
```

Problem: Noise causes flickering when distance hovers around 0.30.

Solution: Use two thresholds (hysteresis):
```python
if not pinching:
    if distance < 0.30:  # Start threshold
        pinching = True
else:  # Already pinching
    if distance > 0.45:  # End threshold (wider)
        pinching = False
```

This creates a "dead zone" between 0.30 and 0.45 where the state doesn't change, preventing flicker.

### Debouncing for Reliability

Raw gesture classifications can flicker frame-to-frame due to:
- Temporary occlusions
- Lighting changes
- Transient hand positions during movement

Debouncing requires a gesture to **hold steady** for N frames before triggering:

```python
history = [draw, draw, draw, draw]  # Last 4 frames
if all gestures are "draw" and current != "draw":
    current_gesture = "draw"  # Now trigger
```

Similarly, a gesture must be **absent** for M frames before ending.

Configuration:
- `GESTURE_DEBOUNCE_START = 4`: New gesture must hold 4 frames (~133ms at 30 FPS)
- `GESTURE_DEBOUNCE_END = 3`: Must be gone 3 frames to end

### Finger Extension Detection

Challenge: Detect if a finger is extended, even when the hand is rotated.

Bad approach: Compare Y-coordinates
```python
# Fails when hand is tilted
extended = finger_tip.y < finger_pip.y
```

Good approach: Compare distances from wrist
```python
wrist = landmarks[0]
tip_distance = distance(wrist, finger_tip)
pip_distance = distance(wrist, finger_pip)
ratio = tip_distance / pip_distance

extended = ratio > 0.6  # Extended fingers have higher ratio
```

This works regardless of hand rotation because it uses relative distances within the hand skeleton.

---

## 2D to 3D Mapping

### X and Y Mapping

MediaPipe gives us normalized coordinates (0 to 1):
```
x = 0.0 (left edge) to 1.0 (right edge)
y = 0.0 (top edge) to 1.0 (bottom edge)
```

We map to world space centered at origin:
```javascript
worldX = (x - 0.5) × 10  // -5 to +5 range
worldY = (0.5 - y) × 10 + 3  // Inverted (screen Y goes down, world Y goes up), offset up
```

The offset (+3) raises the drawing plane to a comfortable height.

### Z Depth Estimation

MediaPipe's z-coordinate is relative and unreliable. Instead, we derive depth from hand size:

```javascript
// Smaller hand = farther away = larger Z (moves away from camera)
z = 0.5 + (1.0 / (hand_size × 10 + 0.1)) × 2.0
```

This is a proxy depth that feels natural because:
- When you move hand closer (hand_size increases), z decreases (comes forward)
- When you move hand farther (hand_size decreases), z increases (goes back)

### Smoothing for Fluid Motion

Raw landmark positions are noisy. We apply two levels of smoothing:

1. **One Euro Filter**: Adaptive low-pass filter that reduces lag during fast movement
   - Low cutoff frequency for slow movements (more smoothing)
   - High cutoff frequency for fast movements (less lag)

2. **Lerp on Cursor**: Additional interpolation in the 3D scene
   ```javascript
   cursor.position.lerp(targetPosition, 0.3)
   ```

Result: Cursor follows hand smoothly without jitter or lag.

---

## Stroke Creation

Strokes are built incrementally as you draw:

1. **Point Collection**: Each frame, add cursor position to `activeStrokePoints` array
2. **Distance Check**: Only add if distance from last point > 0.1 units (avoids redundant points)
3. **Live Preview**: Create a temporary `TubeGeometry` mesh that updates in real-time
4. **Finalization**: When gesture ends, optimize points and create final mesh

```javascript
// Optimize by removing close points
optimized = points.filter((p, i) => 
    i === 0 || p.distanceTo(points[i-1]) >= 0.15
)

// Create tube from curve
curve = new THREE.CatmullRomCurve3(optimized)
geometry = new THREE.TubeGeometry(curve, segments, radius, radialSegments)
```

The `CatmullRomCurve3` creates smooth curves through the points, resulting in organic-looking strokes.

---

## WebSocket Message Flow

### Backend to Frontend (30 Hz)

```json
{
  "t": 1712345678.123,
  "hands": [
    {
      "handedness": "Right",
      "gesture": "draw",
      "confidence": 0.93,
      "cursor": {"x": 0.42, "y": 0.31, "z": 0.18},
      "palm": {"x": 0.50, "y": 0.60},
      "pinch": 0.21,
      "landmarks": [[x,y,z], ... 21 items]
    }
  ]
}
```

Key fields:
- **cursor**: Smoothed index fingertip position (used for drawing/interaction)
- **palm**: Center of palm (used for erase radius)
- **pinch**: Normalized thumb-index distance (for hysteresis)
- **gesture**: Classified gesture after debouncing
- **landmarks**: Full 21-point hand skeleton (for visualization)

### Automatic Reconnection

If connection drops:
1. Frontend detects `onclose` event
2. Updates status badge to "Disconnected"
3. Schedules reconnect after 2 seconds
4. Attempts to reconnect automatically
5. On success, resumes normal operation

No user intervention required—backend can restart without requiring page reload.

---

## Memory Management

Three.js requires explicit cleanup to prevent memory leaks:

```javascript
function disposeMesh(mesh) {
    if (mesh.geometry) {
        mesh.geometry.dispose()  // Free GPU buffers
    }
    if (mesh.material) {
        mesh.material.dispose()  // Free textures and shaders
    }
}
```

We call this:
- When undoing object creation
- When erasing objects
- When clearing the scene
- When replacing temporary stroke preview

Without this, the GPU would accumulate orphaned buffers over time.

---

## Performance Optimizations

1. **Thread Separation**: Camera capture runs in background thread, doesn't block WebSocket
2. **Latest Frame Only**: No queue buildup; we always process the newest frame
3. **Async I/O**: WebSocket uses asyncio for non-blocking communication
4. **Point Optimization**: Remove redundant stroke points before creating mesh
5. **MediaPipe Lite**: Use `model_complexity=0` for faster tracking on slower machines
6. **Shadow Map Caching**: Shadows computed once per object, not per frame
7. **Fog**: Reduces distant geometry rendering cost

Target: 30 FPS end-to-end (camera → detection → classification → broadcast → render)

---

## Why This Approach Works

1. **Normalized distances** make gestures distance-invariant
2. **Hysteresis** prevents flickering at threshold boundaries
3. **Debouncing** requires intentional, stable gestures
4. **One Euro filter** adapts to movement speed for optimal smoothing
5. **Mirrored camera** makes interaction feel natural (move right, cursor moves right)
6. **Depth from size** gives usable Z-axis without stereo cameras
7. **WebSocket** enables real-time communication with minimal latency
8. **No build step** means instant iteration and easy deployment

The result is a responsive, intuitive 3D creation experience using only webcam and hands!
