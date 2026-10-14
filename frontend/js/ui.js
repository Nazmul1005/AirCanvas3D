/**
 * UI management: HUD, toolbar, tutorial, webcam preview.
 */

export class UI {
    constructor(state) {
        this.state = state;
        
        // Elements
        this.connectionStatus = document.getElementById('connection-status');
        this.fpsCounter = document.getElementById('fps-counter');
        this.gestureIndicator = document.getElementById('gesture-indicator');
        this.webcamPreview = document.getElementById('webcam-preview');
        this.webcamCanvas = document.getElementById('webcam-canvas');
        this.tutorialOverlay = document.getElementById('tutorial-overlay');
        
        // Toolbar
        this.toolDraw = document.getElementById('tool-draw');
        this.toolBlocks = document.getElementById('tool-blocks');
        this.colorPicker = document.getElementById('color-picker');
        this.brushSize = document.getElementById('brush-size');
        this.undoBtn = document.getElementById('undo-btn');
        this.redoBtn = document.getElementById('redo-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.saveBtn = document.getElementById('save-btn');
        this.loadBtn = document.getElementById('load-btn');
        this.loadInput = document.getElementById('load-input');
        
        // Tutorial
        this.startBtn = document.getElementById('start-btn');
        this.toggleWebcamBtn = document.getElementById('toggle-webcam');
        
        // Webcam context
        this.webcamCtx = this.webcamCanvas.getContext('2d');
        this.webcamVisible = true;
        
        // FPS tracking
        this.frameCount = 0;
        this.lastFpsTime = performance.now();
        this.fps = 0;
        
        this.setupEventListeners();
    }
    
    /**
     * Setup UI event listeners.
     */
    setupEventListeners() {
        // Tutorial
        this.startBtn.addEventListener('click', () => {
            this.tutorialOverlay.classList.add('hidden');
        });
        
        // Tool selection
        this.toolDraw.addEventListener('click', () => {
            this.setActiveTool('draw');
            this.state.setTool('draw');
        });
        
        this.toolBlocks.addEventListener('click', () => {
            this.setActiveTool('blocks');
            this.state.setTool('blocks');
        });
        
        // Color and size
        this.colorPicker.addEventListener('input', (e) => {
            this.state.setColor(e.target.value);
        });
        
        this.brushSize.addEventListener('input', (e) => {
            this.state.setSize(e.target.value);
        });
        
        // Load button
        this.loadBtn.addEventListener('click', () => {
            this.loadInput.click();
        });
        
        // Webcam toggle
        this.toggleWebcamBtn.addEventListener('click', () => {
            this.webcamVisible = !this.webcamVisible;
            if (this.webcamVisible) {
                this.webcamPreview.classList.remove('hidden');
            } else {
                this.webcamPreview.classList.add('hidden');
            }
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Undo: Ctrl+Z or Cmd+Z
            if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
                e.preventDefault();
                this.undoBtn.click();
            }
            
            // Redo: Ctrl+Y or Ctrl+Shift+Z or Cmd+Shift+Z
            if (((e.ctrlKey || e.metaKey) && e.key === 'y') ||
                ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'z')) {
                e.preventDefault();
                this.redoBtn.click();
            }
        });
    }
    
    /**
     * Set active tool in UI.
     * @param {string} tool - 'draw' or 'blocks'
     */
    setActiveTool(tool) {
        this.toolDraw.classList.remove('active');
        this.toolBlocks.classList.remove('active');
        
        if (tool === 'draw') {
            this.toolDraw.classList.add('active');
        } else if (tool === 'blocks') {
            this.toolBlocks.classList.add('active');
        }
    }
    
    /**
     * Update connection status.
     * @param {string} status - 'connected', 'connecting', or 'disconnected'
     */
    updateConnectionStatus(status) {
        this.connectionStatus.className = `status-badge ${status}`;
        
        const statusText = this.connectionStatus.querySelector('.status-text');
        statusText.textContent = status.charAt(0).toUpperCase() + status.slice(1);
    }
    
    /**
     * Update gesture indicator.
     * @param {string} gesture - Gesture name
     * @param {string} handedness - 'Left' or 'Right'
     */
    updateGestureIndicator(gesture, handedness = '') {
        const icon = this.gestureIndicator.querySelector('.gesture-icon');
        const label = this.gestureIndicator.querySelector('.gesture-label');
        
        const gestureInfo = {
            'draw': { icon: '✏️', label: 'Draw' },
            'pinch': { icon: '🤏', label: 'Pinch' },
            'palm': { icon: '✋', label: 'Erase' },
            'fist': { icon: '✊', label: 'Idle' },
            'two_hand_scale': { icon: '🙌', label: 'Scale' },
            'none': { icon: '👋', label: 'No Hand' }
        };
        
        const info = gestureInfo[gesture] || gestureInfo['none'];
        icon.textContent = info.icon;
        label.textContent = handedness ? `${info.label} (${handedness})` : info.label;
    }
    
    /**
     * Update FPS counter.
     */
    updateFPS() {
        this.frameCount++;
        const now = performance.now();
        const elapsed = now - this.lastFpsTime;
        
        if (elapsed >= 1000) {
            this.fps = Math.round(this.frameCount / (elapsed / 1000));
            this.fpsCounter.textContent = `FPS: ${this.fps}`;
            this.frameCount = 0;
            this.lastFpsTime = now;
        }
    }
    
    /**
     * Draw webcam feed with landmarks on preview canvas.
     * @param {ImageData|HTMLCanvasElement|HTMLVideoElement} source - Video source
     * @param {Array} hands - Array of hand data with landmarks
     */
    drawWebcamPreview(source, hands = []) {
        if (!this.webcamVisible) return;
        
        const canvas = this.webcamCanvas;
        const ctx = this.webcamCtx;
        
        // Set canvas size if needed
        if (source.width && (canvas.width !== source.width || canvas.height !== source.height)) {
            canvas.width = source.width;
            canvas.height = source.height;
        }
        
        // Draw video frame
        if (source instanceof HTMLCanvasElement || source instanceof HTMLVideoElement) {
            ctx.drawImage(source, 0, 0, canvas.width, canvas.height);
        } else if (source instanceof ImageData) {
            ctx.putImageData(source, 0, 0);
        }
        
        // Draw landmarks
        for (const hand of hands) {
            if (!hand.landmarks) continue;
            
            // Draw hand skeleton
            ctx.strokeStyle = hand.gesture === 'draw' ? '#00ffff' :
                             hand.gesture === 'pinch' ? '#ffff00' :
                             hand.gesture === 'palm' ? '#ff4444' : '#ffffff';
            ctx.lineWidth = 2;
            
            // Draw connections (simplified)
            const connections = [
                [0, 1], [1, 2], [2, 3], [3, 4],  // Thumb
                [0, 5], [5, 6], [6, 7], [7, 8],  // Index
                [0, 9], [9, 10], [10, 11], [11, 12],  // Middle
                [0, 13], [13, 14], [14, 15], [15, 16],  // Ring
                [0, 17], [17, 18], [18, 19], [19, 20],  // Pinky
                [5, 9], [9, 13], [13, 17]  // Palm
            ];
            
            for (const [i, j] of connections) {
                const p1 = hand.landmarks[i];
                const p2 = hand.landmarks[j];
                
                ctx.beginPath();
                ctx.moveTo(p1[0] * canvas.width, p1[1] * canvas.height);
                ctx.lineTo(p2[0] * canvas.width, p2[1] * canvas.height);
                ctx.stroke();
            }
            
            // Draw landmarks as circles
            ctx.fillStyle = ctx.strokeStyle;
            for (const lm of hand.landmarks) {
                ctx.beginPath();
                ctx.arc(lm[0] * canvas.width, lm[1] * canvas.height, 3, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
    
    /**
     * Register undo button callback.
     * @param {Function} callback
     */
    onUndo(callback) {
        this.undoBtn.addEventListener('click', callback);
    }
    
    /**
     * Register redo button callback.
     * @param {Function} callback
     */
    onRedo(callback) {
        this.redoBtn.addEventListener('click', callback);
    }
    
    /**
     * Register clear button callback.
     * @param {Function} callback
     */
    onClear(callback) {
        this.clearBtn.addEventListener('click', () => {
            if (confirm('Clear all objects? This cannot be undone.')) {
                callback();
            }
        });
    }
    
    /**
     * Register save button callback.
     * @param {Function} callback
     */
    onSave(callback) {
        this.saveBtn.addEventListener('click', callback);
    }
    
    /**
     * Register load button callback.
     * @param {Function} callback
     */
    onLoad(callback) {
        this.loadInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    try {
                        const data = JSON.parse(event.target.result);
                        callback(data);
                        e.target.value = ''; // Reset input
                    } catch (error) {
                        alert('Failed to load file: ' + error.message);
                    }
                };
                reader.readAsText(file);
            }
        });
    }
    
    /**
     * Show tutorial overlay.
     */
    showTutorial() {
        this.tutorialOverlay.classList.remove('hidden');
    }
    
    /**
     * Hide tutorial overlay.
     */
    hideTutorial() {
        this.tutorialOverlay.classList.add('hidden');
    }
}
