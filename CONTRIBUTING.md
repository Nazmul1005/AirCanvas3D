# Contributing to AirCanvas 3D

Thank you for your interest in contributing to AirCanvas 3D! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
- Check the [README](README.md) troubleshooting section
- Search existing [issues](https://github.com/yourusername/aircanvas3d/issues) to avoid duplicates

When reporting bugs, include:
- **Operating System**: macOS, Linux, or Windows (with version)
- **Python Version**: Output of `python --version`
- **Browser**: Name and version
- **Steps to Reproduce**: Clear steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Screenshots/Videos**: If applicable
- **Console Logs**: Backend terminal output and browser console errors

### Suggesting Enhancements

We love feature ideas! When suggesting enhancements:
- Provide a clear description of the feature
- Explain why it would be useful
- Include mockups or examples if possible
- Consider implementation complexity

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test thoroughly**:
   - Test all gestures
   - Check performance
   - Verify on different browsers
   - Test edge cases
5. **Commit** with clear messages:
   ```bash
   git commit -m "Add: Description of your changes"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** with:
   - Clear title and description
   - Reference any related issues
   - Screenshots/videos of changes
   - Test results

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/aircanvas3d.git
cd aircanvas3d

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests (if available)
python -m pytest

# Start development
python backend/main.py
```

## Code Style

### Python
- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable names
- Add docstrings for functions and classes
- Keep functions focused and small

### JavaScript
- Use ES6+ features
- Use `const` and `let`, avoid `var`
- Use descriptive function and variable names
- Add JSDoc comments for functions

### Comments
- Explain **why**, not **what** (code shows what)
- Document complex algorithms
- Add TODO comments for future improvements

## Project Areas

### Backend (Python)
- `backend/camera.py` - Webcam capture
- `backend/hand_tracker.py` - MediaPipe integration
- `backend/gesture_engine.py` - Gesture recognition
- `backend/filters.py` - Smoothing algorithms
- `backend/config.py` - Configuration

### Frontend (JavaScript)
- `frontend/js/scene.js` - Three.js 3D rendering
- `frontend/js/tools.js` - Drawing and block tools
- `frontend/js/state.js` - State management
- `frontend/js/socket.js` - WebSocket communication
- `frontend/js/ui.js` - User interface

## Testing

Before submitting:
- [ ] Test all gestures (draw, pinch, palm, fist)
- [ ] Verify camera tracking works
- [ ] Check WebSocket connection
- [ ] Test undo/redo functionality
- [ ] Verify save/load works
- [ ] Test on multiple browsers
- [ ] Check performance (30 FPS target)
- [ ] Verify no console errors

## Good First Issues

Look for issues labeled:
- `good first issue` - Simple changes, great for beginners
- `help wanted` - We need community help
- `documentation` - Improve docs
- `enhancement` - New features

## Questions?

- Open an issue for questions
- Check [HOW_IT_WORKS.md](HOW_IT_WORKS.md) for technical details
- Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for architecture

## Code of Conduct

Be respectful and inclusive. We're all here to learn and build together!

---

Thank you for contributing! 🎉
