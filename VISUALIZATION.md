# 🎨 AirCanvas 3D - Visual Guide

## 📸 Demo Screenshots

> **Note**: Add your own screenshots here by running the application and capturing images.

### Main Interface
![Main Interface](docs/images/main-interface.png)
*The 3D canvas with gesture controls and live webcam preview*

### Gesture Recognition
![Hand Tracking](docs/images/hand-tracking.png)
*Real-time hand tracking with 21 landmarks*

### Creating Strokes
![Drawing Demo](docs/images/drawing-demo.png)
*Drawing glowing 3D strokes in mid-air*

### Building with Blocks
![Block Building](docs/images/block-building.png)
*Placing and manipulating colorful 3D blocks*

---

## 🖐️ Gesture Visual Guide

### Draw Gesture
```
     ☝️ Index Finger Extended
    
    👆
   |  |
   |  |     ✅ Draw Mode
   |__|     Create 3D strokes
    /\
   /  \
  /____\
```

### Pinch Gesture
```
    👌 Thumb + Index Touch
    
     ⭕
    /  \    ✅ Pinch Mode
   |    |   Grab & place blocks
    \  /
     \/
```

### Palm Gesture
```
    🖐️ All Fingers Spread
    
   | | | |
   | | | |  ✅ Erase Mode
   | | | |  Remove objects in radius
    \___/
```

### Fist Gesture
```
    ✊ All Fingers Closed
    
    ___
   |   |   ✅ Idle Mode
   |___|   Pause & finalize
```

### Two-Hand Scale
```
    🙌 Both Hands Pinching
    
   👌     👌
    \     /   ✅ Scale Mode
     \   /    Zoom in/out
      \ /
```

---

## 🔄 System Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│                     (Hand Gestures)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   Webcam Camera  │
              │   (OpenCV)       │
              │   640×480 @ 30fps │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  MediaPipe Hands │
              │  21 Landmarks    │
              │  Per Hand (×2)   │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │ Gesture Engine   │
              │ • Normalize      │
              │ • Classify       │
              │ • Debounce       │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  One Euro Filter │
              │  (Smoothing)     │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   WebSocket      │
              │   Server         │
              │   Port 8765      │
              └────────┬─────────┘
                       │
                       │ JSON @ 30Hz
                       ▼
              ┌──────────────────┐
              │   Browser        │
              │   WebSocket      │
              │   Client         │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │   Three.js       │
              │   3D Scene       │
              │   Rendering      │
              └────────┬─────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                       OUTPUT                                 │
│              3D Objects & Visual Feedback                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

### WebSocket Message Structure

```json
{
  "t": 1712345678.123,
  "hands": [
    {
      "handedness": "Right",
      "gesture": "draw",
      "confidence": 0.93,
      "cursor": {
        "x": 0.42,
        "y": 0.31,
        "z": 0.18
      },
      "palm": {
        "x": 0.50,
        "y": 0.60
      },
      "pinch": 0.21,
      "landmarks": [
        [0.5, 0.6, 0.0],
        [0.52, 0.58, -0.02],
        // ... 21 landmarks total
      ]
    }
  ]
}
```

---

## 🎯 Coordinate Mapping

### Screen Space → World Space

```
Screen Coordinates          World Coordinates
(0,0) ─────────── (1,0)     (-5,8) ───────── (5,8)
  │                │           │                │
  │    Camera      │           │    3D Scene    │
  │    View        │     →     │                │
  │                │           │                │
(0,1) ─────────── (1,1)     (-5,-2) ──────── (5,-2)

X: [0→1]  maps to  [-5→5]
Y: [0→1]  maps to  [8→-2] (inverted + offset)
Z: Derived from hand size (proxy depth)
```

---

## 🧮 Gesture Recognition Algorithm

### Pinch Detection with Hysteresis

```
Distance Between Thumb & Index

High ┤
     │     ╭─────────╮ Active
     │     │         │
0.45 ├─────┤         ├─────  End Threshold
     │ Gap │         │ Gap
0.30 ├─────┤         ├─────  Start Threshold
     │     │         │
Low  └─────┴─────────┴─────▶ Time
          ^         ^
       Trigger    Release
       
This prevents flickering when distance hovers near threshold!
```

### Debouncing Timeline

```
Frame:  1  2  3  4  5  6  7  8  9  10
        ───────────────────────────▶
        
Detect: D  D  D  D  P  P  P  P  D  D
        │  │  │  └──┬──┘  │  │  │  │
        └──┴──┴─────┘     └──┴──┴──┘
                 │             │
        [HOLD 4 FRAMES]  [HOLD 3 FRAMES]
                 │             │
Output: DRAW────────PINCH──────────DRAW

Result: Stable gesture recognition!
```

---

## 🎨 3D Scene Layout

```
                    ☀️ Directional Light
                    │
                    ▼
        ┌───────────────────────┐
        │                       │
        │   🎯 Cursor Sphere    │   ← User's hand position
        │        │              │
        │        │ Shadow Line  │
        │        ▼              │
        │   🟦🟥🟨 Blocks       │   ← Placed objects
        │   ╱│╲                │
        │  ╱ │ ╲               │
        │ ▓▓▓▓▓▓▓ Strokes      │   ← Drawn lines
        │                       │
        └───────────────────────┘
        ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓  ← Grid Floor
        
Camera Position: (0, 5, 10)
Looking At: (0, 3, 0)
FOV: 60°
```

---

## ⚡ Performance Metrics

```
Target Performance Goals:

┌────────────────────────────────┐
│ Component        │ Target │ FPS │
├──────────────────┼────────┼─────┤
│ Camera Capture   │   30   │  ██ │
│ MediaPipe Track  │   30   │  ██ │
│ Gesture Engine   │   30   │  ██ │
│ WebSocket Send   │   30   │  ██ │
│ Three.js Render  │   60   │  ██ │
└──────────────────┴────────┴─────┘

Latency Budget:
• Camera to Detection: < 10ms
• Detection to Gesture: < 5ms
• Gesture to WebSocket: < 2ms
• WebSocket to Render: < 15ms
───────────────────────────────
  Total End-to-End: < 35ms ✅
```

---

## 🎬 Usage Workflow

### Creating a 3D Sculpture

```
Step 1: Start System
   [Backend] + [Frontend] → [Browser]
      │          │            │
      └──────────┴────────────┘
         Connection Made ✅

Step 2: Show Hand
   Camera → Detection → Green Landmarks
                  ↓
            Cursor Appears 🎯

Step 3: Select Draw Tool
   Click [✏️] Button → Tool Active

Step 4: Make Draw Gesture
   Index Finger ☝️ → Start Drawing
        │
        ▼
   Move Hand → Create Stroke 〰️

Step 5: Finalize
   Make Fist ✊ → Stroke Complete ✅

Step 6: Add Blocks
   Click [🧱] → Switch to Blocks
        │
        ▼
   Pinch 👌 → Place Block 🟦

Step 7: Save Work
   Click [💾] → Download JSON
        │
        ▼
   aircanvas3d_20241015_143022.json ✅
```

---

## 🔧 Configuration Visualization

### Sensitivity Settings Impact

```
PINCH_THRESHOLD_START
────────────────────────────────
0.20 ─┤ Very Sensitive
      │ + Easy to trigger
      │ - May trigger accidentally
      │
0.30 ─┤ ✅ RECOMMENDED
      │ Balanced sensitivity
      │
0.40 ─┤ Less Sensitive
      │ - Harder to trigger
      │ + Fewer false positives


ONE_EURO_MIN_CUTOFF
────────────────────────────────
0.5 ──┤ Very Smooth
      │ + No jitter
      │ - Noticeable lag
      │
1.0 ──┤ ✅ RECOMMENDED
      │ Good balance
      │
2.0 ──┤ Fast Response
      │ + Minimal lag
      │ - Some jitter
```

---

## 📈 State Machine Diagram

```
┌─────────────────────────────────────────────────┐
│              GESTURE STATE MACHINE               │
└─────────────────────────────────────────────────┘

          ┌──────────┐
    ╔═════│  IDLE    │═════╗
    ║     │ (Fist)   │     ║
    ║     └──────────┘     ║
    ║                      ║
    ▼                      ▼
┌─────────┐          ┌─────────┐
│  DRAW   │          │  PINCH  │
│  Mode   │          │  Mode   │
│ ☝️ Index│          │👌 Touch │
└────┬────┘          └────┬────┘
     │                    │
     ├─→ Creating Stroke  │
     │                    ├─→ Grabbing Object
     │                    ├─→ Placing Block
     │                    │
     ▼                    ▼
┌─────────┐          ┌─────────┐
│  PALM   │          │  SCALE  │
│  Mode   │          │  Mode   │
│ 🖐️ Open │          │🙌 Both  │
└────┬────┘          └────┬────┘
     │                    │
     ├─→ Erasing Objects  │
     │                    ├─→ Zooming Scene
     │                    │
     ▼                    ▼
     ╚════════════════════╝
          Back to IDLE
```

---

## 🎨 Color Scheme

### UI Colors
```css
Primary:    #00D9FF (Cyan)     ████
Secondary:  #FFD700 (Gold)     ████
Error:      #FF4444 (Red)      ████
Success:    #00FF88 (Green)    ████
Background: #1a1a2e (Dark)     ████
Surface:    #16213e (Navy)     ████
```

### Gesture Colors
```css
Draw:       #00FFFF (Cyan)     ████ ✏️
Pinch:      #FFFF00 (Yellow)   ████ 🤏
Erase:      #FF0000 (Red)      ████ ✋
Scale:      #FF00FF (Magenta)  ████ 🙌
Idle:       #FFFFFF (White)    ████ ✊
```

---

## 📱 Responsive Design

```
Desktop (1920×1080)          Laptop (1366×768)
┌────────────────────┐      ┌─────────────────┐
│   Status    FPS    │      │  Status   FPS   │
│   ┌──────────────┐ │      │ ┌─────────────┐ │
│   │              │ │      │ │             │ │
│   │   3D Scene   │ │      │ │  3D Scene   │ │
│   │              │ │      │ │             │ │
│   └──────────────┘ │      │ └─────────────┘ │
│   [━━━━━━━━━━━━━] │      │ [━━━━━━━━━━━] │
│   Toolbar     📹   │      │ Toolbar    📹  │
└────────────────────┘      └─────────────────┘

Mobile/Tablet (768×1024)
┌──────────────┐
│ Status  FPS  │
│┌────────────┐│
││            ││
││  3D Scene  ││
││            ││
│└────────────┘│
│ [━━━━━━━━━] │
│ Toolbar  📹  │
└──────────────┘
```

---

## 🎓 Learning Resources

### Recommended Reading Order

```
1. README.md
   └─→ Quick start and overview

2. VISUALIZATION.md (This file!)
   └─→ Visual understanding

3. HOW_IT_WORKS.md
   └─→ Technical details

4. PROJECT_STRUCTURE.md
   └─→ Code organization

5. Source Code
   └─→ Implementation details
```

---

*Add your own screenshots to the `docs/images/` directory to complete this visual guide!*
