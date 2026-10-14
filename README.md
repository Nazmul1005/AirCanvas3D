<div align="center">

# 🎨 AirCanvas 3D

### Gesture-Controlled Virtual Construction

*Build stunning 3D structures using just your hands and a webcam*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Three.js](https://img.shields.io/badge/Three.js-r160-green?logo=three.js&logoColor=white)](https://threejs.org/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.35-orange?logo=google&logoColor=white)](https://google.github.io/mediapipe/)
[![License](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [Documentation](#-documentation)

</div>

---

## 🌟 Overview

AirCanvas 3D transforms your webcam into a powerful 3D creation tool. Using advanced hand tracking and gesture recognition, you can draw glowing strokes, place and manipulate blocks, and build complex structures—all without touching a mouse or keyboard.

Perfect for:
- 🎓 **Education**: Interactive 3D geometry and spatial reasoning
- 🎮 **Creative Expression**: Digital art and sculpture
- 🏗️ **Prototyping**: Quick 3D mockups and concept visualization
- 🔬 **Research**: Computer vision and HCI experimentation

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🖐️ Intuitive Gestures
- **Draw Mode**: Create flowing 3D strokes in mid-air
- **Block Mode**: Place and stack colorful cubes
- **Grab & Move**: Manipulate objects naturally
- **Erase**: Remove objects with palm gesture
- **Two-Hand Scale**: Zoom with both hands

</td>
<td width="50%">

### 🚀 Advanced Technology
- **Real-time tracking** at 30 FPS
- **Adaptive smoothing** for fluid motion
- **Debounced gestures** for reliability
- **Distance-invariant** recognition
- **WebSocket** communication
- **Full undo/redo** system

</td>
</tr>
</table>

### 🎯 Core Features

| Feature | Description |
|---------|-------------|
| 🎨 **Color Picker** | Choose from any color for your strokes |
| 📏 **Brush Size** | Adjustable stroke thickness |
| 💾 **Save/Load** | Export and import creations as JSON |
| 📹 **Live Preview** | Picture-in-picture webcam feed with landmarks |
| ⌨️ **Keyboard Shortcuts** | Ctrl+Z undo, Ctrl+Y redo |
| 🔄 **Auto-Reconnect** | Seamless recovery from disconnections |

---

## 🎬 Demo

### Gesture Controls

```
✏️ DRAW          🤏 PINCH         ✋ PALM          ✊ FIST
Index extended   Thumb + Index    All fingers      All fingers
Others curled    touching         spread wide      curled
→ Draw stroke    → Grab object    → Erase radius   → Idle mode
```

### System Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Webcam    │ ───> │   MediaPipe  │ ───> │   Gesture   │
│   Camera    │      │  Hand Track  │      │   Engine    │
└─────────────┘      └──────────────┘      └─────────────┘
                                                    │
                                                    ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Three.js   │ <─── │   WebSocket  │ <─── │  Smoothing  │
│  3D Scene   │      │   (30 FPS)   │      │   Filters   │
└─────────────┘      └──────────────┘      └─────────────┘
```

---

## 🚀 Installation

### Prerequisites

- **Python** 3.10 or 3.11
- **Webcam** (built-in or USB)
- **Modern Browser** (Chrome, Firefox, Safari, or Edge)
- **Operating System**: macOS, Linux, or Windows

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/aircanvas3d.git
   cd aircanvas3d
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

That's it! You're ready to run AirCanvas 3D.

---

## 🎮 Usage

### Starting the Application

#### **Terminal 1: Backend Server**
```bash
# Activate virtual environment
source venv/bin/activate

# Start the hand tracking backend
python backend/main.py
```

Expected output:
```
AirCanvas 3D - Gesture-Controlled Virtual Construction
============================================================
Camera started: 640x480 @ 30 FPS
WebSocket server will start on ws://localhost:8765
Processing loop started
```

#### **Terminal 2: Frontend Server**
```bash
# Navigate to frontend directory
cd frontend

# Start HTTP server
python -m http.server 8000
```

#### **Browser**
Open your browser and navigate to:
```
http://localhost:8000
```

### First-Time Setup

1. **Grant camera permissions** when prompted
2. **Dismiss the tutorial** overlay by clicking "Start Creating!"
3. **Show your hand** to the camera
4. **Look for green landmarks** in the debug window
5. **See the glowing cursor** appear in the 3D scene

---

## 🖐️ Gesture Guide

### Drawing

1. Select the **Draw** tool (✏️ button)
2. Make **draw gesture** (extend index finger)
3. Move your hand to create strokes
4. Make **fist gesture** to finish

### Building with Blocks

1. Select the **Block** tool (🧱 button)
2. Make **pinch gesture** in empty space
3. Block appears at cursor position
4. Release and repeat to place more

### Moving Objects

1. Position cursor near an object
2. Make **pinch gesture**
3. Object highlights (yellow)
4. Move hand while pinching
5. Release to drop

### Erasing

1. Position hand near objects
2. Make **palm gesture** (spread all fingers)
3. Red sphere indicates erase radius
4. Objects inside fade away

### Zooming

1. Show both hands to camera
2. Make **pinch gesture** with both hands
3. Move hands apart to zoom in
4. Move hands together to zoom out

---

## ⚙️ Configuration

All settings are in `backend/config.py`. Adjust these to fine-tune your experience:

### Camera Settings
```python
CAMERA_INDEX = 0           # Try 1, 2, etc. for other cameras
CAMERA_WIDTH = 640         # Resolution width
CAMERA_HEIGHT = 480        # Resolution height
CAMERA_FPS = 30           # Target frame rate
```

### Gesture Sensitivity
```python
PINCH_THRESHOLD_START = 0.30   # Lower = easier to trigger
PINCH_THRESHOLD_END = 0.45     # Higher = stays active longer
FINGER_EXTEND_THRESHOLD = 0.6  # Finger extension detection
```

### Smoothing (reduce jitter)
```python
ONE_EURO_MIN_CUTOFF = 1.0   # Lower = smoother, more lag
ONE_EURO_BETA = 0.007       # Higher = faster response
```

### Performance
```python
MP_MODEL_COMPLEXITY = 1   # 0 = fast, 1 = accurate
```

---

## 🛠️ Troubleshooting

<details>
<summary><b>Camera not detected</b></summary>

**Error**: `ERROR: Could not open camera 0`

**Solutions**:
- Verify webcam is connected
- Try different `CAMERA_INDEX` (1, 2, 3...)
- Check camera permissions in system settings
- Close other apps using the camera
</details>

<details>
<summary><b>Hand not tracking properly</b></summary>

**Symptoms**: No green landmarks, jittery tracking

**Solutions**:
- **Improve lighting**: Face a window or use a desk lamp
- **Plain background**: Avoid cluttered/patterned backgrounds
- **Distance**: Keep hand 1-3 feet (30-90cm) from camera
- **Position**: Ensure entire hand is visible in frame
- **Increase confidence**: Raise `MP_MIN_DETECTION_CONFIDENCE` to 0.8
</details>

<details>
<summary><b>Gestures not triggering</b></summary>

**Symptoms**: Making gestures but nothing happens

**Solutions**:
- Check debug window for landmarks
- Lower thresholds in `config.py`
- Hold gestures clearly for at least 0.5 seconds
- Reduce `GESTURE_DEBOUNCE_START` for faster triggering
- Verify connection status shows "Connected"
</details>

<details>
<summary><b>Low FPS / laggy performance</b></summary>

**Solutions**:
- Set `MP_MODEL_COMPLEXITY = 0` for faster processing
- Lower camera resolution (e.g., 320×240)
- Close other resource-intensive applications
- Update graphics drivers
</details>

<details>
<summary><b>WebSocket connection failed</b></summary>

**Error**: "Disconnected" badge in browser

**Solutions**:
- Ensure backend is running (`python backend/main.py`)
- Check port 8765 isn't blocked by firewall
- Verify no other service is using port 8765
- Try restarting both backend and frontend
</details>

---

## 📁 Project Structure

```
aircanvas3d/
├── backend/                    # Python backend
│   ├── main.py                # WebSocket server & main loop
│   ├── camera.py              # Threaded webcam capture
│   ├── hand_tracker.py        # MediaPipe wrapper
│   ├── gesture_engine.py      # Gesture classification
│   ├── filters.py             # Smoothing algorithms
│   ├── config.py              # Configuration settings
│   └── hand_landmarker.task   # MediaPipe AI model
│
├── frontend/                   # Web frontend
│   ├── index.html             # Main HTML page
│   ├── style.css              # Styles and layout
│   └── js/
│       ├── main.js            # Application bootstrap
│       ├── scene.js           # Three.js 3D scene
│       ├── socket.js          # WebSocket client
│       ├── tools.js           # Drawing & block tools
│       ├── state.js           # State management
│       └── ui.js              # User interface
│
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── HOW_IT_WORKS.md           # Technical deep dive
└── PROJECT_STRUCTURE.md      # Architecture details
```

---

## 📚 Documentation

- **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** - Technical implementation details
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - Architecture and file organization
- **Inline Code Comments** - Detailed explanations throughout the codebase

---

## 🎯 Tips for Best Results

### ✅ DO
- Use **bright, even lighting** from the front
- Use a **plain, uncluttered background**
- Keep hand **1-3 feet** from camera
- Hold gestures **clearly and deliberately**
- Keep **entire hand visible** in frame

### ❌ DON'T
- Use backlighting (window behind you)
- Use busy or patterned backgrounds
- Move hand too fast or erratically
- Let fingers go off-screen
- Use in very dim lighting

---

## 🔮 Future Enhancements

- [ ] **Multi-user collaboration** with real-time sync
- [ ] **Physics simulation** for realistic block stacking
- [ ] **Additional shapes** (cylinders, spheres, pyramids)
- [ ] **Texture mapping** and materials
- [ ] **Voice commands** for tool switching
- [ ] **VR/AR support** for immersive building
- [ ] **Export to GLB/OBJ** for 3D printing
- [ ] **Animation timeline** for creating motion
- [ ] **Particle effects** and advanced brushes
- [ ] **Mobile app** with touch controls

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow existing code style
- Add comments for complex logic
- Test thoroughly before submitting
- Update documentation as needed

---

## 🙏 Acknowledgments

- **[MediaPipe Hands](https://google.github.io/mediapipe/solutions/hands.html)** - Google's hand tracking solution
- **[Three.js](https://threejs.org/)** - 3D graphics library
- **[One Euro Filter](http://cristal.univ-lille.fr/~casiez/1euro/)** - Smoothing algorithm by Géry Casiez et al.
- **OpenCV** - Computer vision library

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📧 Contact

**Project Maintainer**: [Your Name]

- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

**Project Link**: [https://github.com/yourusername/aircanvas3d](https://github.com/yourusername/aircanvas3d)

---

<div align="center">

### ⭐ Star this repo if you find it useful!

**Built with ❤️ using Python, Three.js, and MediaPipe**

[Report Bug](https://github.com/yourusername/aircanvas3d/issues) • [Request Feature](https://github.com/yourusername/aircanvas3d/issues)

</div>
