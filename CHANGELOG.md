# Changelog

All notable changes to AirCanvas 3D will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-15

### 🎉 Initial Release

#### Added
- **Hand Tracking**: Real-time hand detection using MediaPipe
- **Gesture Recognition**: 5 core gestures (Draw, Pinch, Palm, Fist, Two-Hand Scale)
- **3D Drawing**: Create glowing 3D strokes in mid-air
- **Block Placement**: Place and manipulate colorful 3D blocks
- **Grab System**: Pinch to grab and move objects
- **Erase Tool**: Palm gesture to remove objects in radius
- **Two-Hand Scale**: Zoom scene using both hands
- **Undo/Redo**: Full action history (up to 50 actions)
- **Save/Load**: Export and import scenes as JSON
- **Color Picker**: Choose any color for strokes
- **Brush Size**: Adjustable stroke thickness
- **Live Preview**: Picture-in-picture webcam feed
- **Auto-Reconnect**: Automatic WebSocket reconnection
- **Debouncing**: Stable gesture recognition
- **Smoothing**: One Euro filter for fluid motion
- **Keyboard Shortcuts**: Ctrl+Z/Y for undo/redo

#### Backend Features
- Threaded camera capture at 30 FPS
- MediaPipe Hands integration
- Gesture engine with hysteresis
- Distance normalization by hand size
- One Euro filter implementation
- WebSocket server (asyncio)
- Configurable thresholds
- Debug window with landmarks

#### Frontend Features
- Three.js 3D rendering
- WebSocket client with reconnection
- State management system
- Tool system (Draw, Blocks)
- Material system with lighting
- Shadow rendering
- Grid floor with ground plane
- Orbit controls
- Tutorial overlay
- Responsive design
- Status indicators
- FPS counter
- Gesture indicator

#### Documentation
- Comprehensive README
- Technical deep dive (HOW_IT_WORKS.md)
- Project structure guide
- Visual documentation
- Contributing guidelines
- Issue templates
- MIT License

### Performance
- 30 FPS backend processing
- 60 FPS frontend rendering
- < 50ms end-to-end latency
- Optimized stroke points
- Efficient memory management

---

## [Unreleased]

### Planned Features
- [ ] Multi-user collaboration
- [ ] Physics simulation
- [ ] Additional shapes (cylinder, sphere, pyramid)
- [ ] Texture mapping
- [ ] Voice commands
- [ ] VR/AR support
- [ ] GLB/OBJ export
- [ ] Animation timeline
- [ ] Particle effects
- [ ] Mobile app

### Ideas Under Consideration
- Custom gesture shortcuts
- Gesture recording/playback
- Scene templates
- Collaborative drawing
- Real-time chat
- User avatars
- Material presets
- Procedural generation

---

## Version History Format

### [Version] - YYYY-MM-DD

#### Added
- New features

#### Changed
- Changes to existing functionality

#### Deprecated
- Soon-to-be removed features

#### Removed
- Removed features

#### Fixed
- Bug fixes

#### Security
- Security improvements

---

[1.0.0]: https://github.com/yourusername/aircanvas3d/releases/tag/v1.0.0
