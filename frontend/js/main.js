/**
 * AirCanvas 3D - Main application entry point.
 * Coordinates scene, socket, state, tools, and UI.
 */

import * as THREE from 'three';
import { Scene3D } from './scene.js';
import { SocketClient } from './socket.js';
import { State } from './state.js';
import { UI } from './ui.js';
import {
    createStroke,
    createBlock,
    findNearestObject,
    findObjectsInRadius,
    highlightObject,
    animateRemoval,
    optimizeStrokePoints,
    snapToGrid
} from './tools.js';

class AirCanvas3D {
    constructor() {
        // Initialize components
        this.state = new State();
        this.scene = new Scene3D(document.getElementById('canvas-container'));
        this.ui = new UI(this.state);
        
        // Socket client
        this.socket = new SocketClient(
            'ws://localhost:8765',
            (data) => this.onSocketMessage(data),
            (status) => this.onSocketStatus(status)
        );
        
        // Active stroke tracking
        this.activeStrokePoints = [];
        this.lastDrawPoint = null;
        
        // Two-hand scale tracking
        this.lastTwoHandDistance = null;
        this.lastTwoHandAngle = null;
        
        this.setupUI();
        this.start();
    }
    
    /**
     * Setup UI callbacks.
     */
    setupUI() {
        this.ui.onUndo(() => this.undo());
        this.ui.onRedo(() => this.redo());
        this.ui.onClear(() => this.clearAll());
        this.ui.onSave(() => this.save());
        this.ui.onLoad((data) => this.load(data));
    }
    
    /**
     * Start the application.
     */
    start() {
        console.log('AirCanvas 3D starting...');
        
        // Connect to WebSocket
        this.socket.connect();
        
        // Start render loop
        this.animate();
    }
    
    /**
     * Main animation loop.
     */
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Update UI
        this.ui.updateFPS();
        
        // Render scene
        this.scene.render();
    }
    
    /**
     * Handle WebSocket message (hand data).
     * @param {Object} data - Hand tracking data
     */
    onSocketMessage(data) {
        if (!data.hands || data.hands.length === 0) {
            // No hands detected
            this.ui.updateGestureIndicator('none');
            this.scene.updateCursor(null, 'fist', false);
            
            // Finalize any active stroke
            this.finalizeStroke();
            
            // Clear grabbed object
            if (this.state.grabbedObject) {
                highlightObject(this.state.grabbedObject, false);
                this.state.grabbedObject = null;
                this.state.grabbedOffset = null;
            }
            
            // Re-enable orbit controls
            this.scene.setControlsEnabled(true);
            
            return;
        }
        
        // Get primary hand (first hand in array)
        const primaryHand = data.hands[0];
        const gesture = primaryHand.gesture;
        
        // Update UI
        this.ui.updateGestureIndicator(gesture, primaryHand.handedness);
        
        // Update cursor
        this.scene.updateCursor(primaryHand.cursor, gesture, true);
        
        // Draw webcam preview
        this.ui.drawWebcamPreview(
            this.createDummyCanvas(),  // We don't have raw video, so skip
            data.hands
        );
        
        // Disable orbit controls when hand is active
        this.scene.setControlsEnabled(false);
        
        // Handle gestures
        switch (gesture) {
            case 'draw':
                this.handleDraw(primaryHand);
                break;
            
            case 'pinch':
                this.handlePinch(primaryHand);
                break;
            
            case 'palm':
                this.handleErase(primaryHand);
                break;
            
            case 'two_hand_scale':
                if (data.hands.length >= 2) {
                    this.handleTwoHandScale(data.hands[0], data.hands[1]);
                }
                break;
            
            case 'fist':
            default:
                this.finalizeStroke();
                if (this.state.grabbedObject) {
                    this.releaseGrabbedObject();
                }
                break;
        }
        
        // Store last hand data
        this.state.lastHandData = data;
    }
    
    /**
     * Handle draw gesture.
     * @param {Object} hand - Hand data
     */
    handleDraw(hand) {
        if (this.state.currentTool !== 'draw') {
            this.finalizeStroke();
            return;
        }
        
        const cursorPos = this.scene.getCursorPosition();
        
        // Start new stroke or continue existing
        if (this.activeStrokePoints.length === 0) {
            this.activeStrokePoints.push(cursorPos.clone());
            this.lastDrawPoint = cursorPos.clone();
        } else {
            // Only add point if it's far enough from last point
            if (this.lastDrawPoint.distanceTo(cursorPos) > 0.1) {
                this.activeStrokePoints.push(cursorPos.clone());
                this.lastDrawPoint = cursorPos.clone();
                
                // Update or create stroke mesh
                this.updateActiveStroke();
            }
        }
    }
    
    /**
     * Update the active stroke mesh as it's being drawn.
     */
    updateActiveStroke() {
        if (this.activeStrokePoints.length < 2) return;
        
        // Remove old active stroke mesh if it exists
        if (this.state.activeStroke) {
            this.scene.remove(this.state.activeStroke.mesh);
            this.scene.disposeMesh(this.state.activeStroke.mesh);
        }
        
        // Create new stroke mesh
        const stroke = createStroke(
            this.activeStrokePoints,
            this.state.brushColor,
            this.state.brushSize
        );
        
        if (stroke) {
            this.scene.add(stroke.mesh);
            this.state.activeStroke = stroke;
        }
    }
    
    /**
     * Finalize the active stroke.
     */
    finalizeStroke() {
        if (this.activeStrokePoints.length >= 2 && this.state.activeStroke) {
            // Optimize points
            const optimized = optimizeStrokePoints(this.activeStrokePoints, 0.15);
            
            if (optimized.length >= 2) {
                // Remove temporary stroke
                this.scene.remove(this.state.activeStroke.mesh);
                this.scene.disposeMesh(this.state.activeStroke.mesh);
                
                // Create final stroke
                const finalStroke = createStroke(
                    optimized,
                    this.state.brushColor,
                    this.state.brushSize
                );
                
                if (finalStroke) {
                    this.scene.add(finalStroke.mesh);
                    this.state.addStroke(finalStroke);
                }
            }
        }
        
        // Reset
        this.activeStrokePoints = [];
        this.lastDrawPoint = null;
        this.state.activeStroke = null;
    }
    
    /**
     * Handle pinch gesture (grab or place block).
     * @param {Object} hand - Hand data
     */
    handlePinch(hand) {
        const cursorPos = this.scene.getCursorPosition();
        
        // If already grabbing, move the object
        if (this.state.grabbedObject) {
            this.moveGrabbedObject(cursorPos);
            return;
        }
        
        // Try to grab an object
        const allObjects = this.state.getAllObjects();
        const nearest = findNearestObject(cursorPos, allObjects, 2.0);
        
        if (nearest) {
            // Grab the object
            this.state.grabbedObject = nearest;
            this.state.grabbedOffset = nearest.mesh.position.clone().sub(cursorPos);
            highlightObject(nearest, true);
        } else if (this.state.currentTool === 'blocks') {
            // Place a new block (only once per pinch)
            if (!this.state.lastHandData || 
                this.state.lastHandData.hands[0].gesture !== 'pinch') {
                
                const block = createBlock(cursorPos);
                this.scene.add(block.mesh);
                this.state.addBlock(block);
            }
        }
    }
    
    /**
     * Move the grabbed object.
     * @param {THREE.Vector3} cursorPos - Current cursor position
     */
    moveGrabbedObject(cursorPos) {
        if (!this.state.grabbedObject) return;
        
        const targetPos = cursorPos.clone().add(this.state.grabbedOffset);
        
        // Smooth movement
        this.state.grabbedObject.mesh.position.lerp(targetPos, 0.3);
    }
    
    /**
     * Release the grabbed object and snap to grid.
     */
    releaseGrabbedObject() {
        if (!this.state.grabbedObject) return;
        
        // Snap to grid
        if (this.state.grabbedObject.type === 'block') {
            const snapped = snapToGrid(this.state.grabbedObject.mesh.position, 0.5);
            this.state.grabbedObject.mesh.position.copy(snapped);
        }
        
        // Remove highlight
        highlightObject(this.state.grabbedObject, false);
        
        // Record move action
        this.state.recordAction({
            type: 'move',
            object: this.state.grabbedObject,
            position: this.state.grabbedObject.mesh.position.clone()
        });
        
        this.state.grabbedObject = null;
        this.state.grabbedOffset = null;
    }
    
    /**
     * Handle erase gesture.
     * @param {Object} hand - Hand data
     */
    handleErase(hand) {
        const cursorPos = this.scene.getCursorPosition();
        const allObjects = this.state.getAllObjects();
        
        // Find objects within erase radius
        const toErase = findObjectsInRadius(cursorPos, allObjects, 1.5);
        
        for (const obj of toErase) {
            // Animate removal
            animateRemoval(obj.mesh, () => {
                this.scene.remove(obj.mesh);
                this.scene.disposeMesh(obj.mesh);
            });
            
            // Remove from state
            this.state.removeObject(obj);
        }
    }
    
    /**
     * Handle two-hand scale gesture.
     * @param {Object} hand1 - First hand data
     * @param {Object} hand2 - Second hand data
     */
    handleTwoHandScale(hand1, hand2) {
        const pos1 = new THREE.Vector3(hand1.cursor.x, hand1.cursor.y, hand1.cursor.z);
        const pos2 = new THREE.Vector3(hand2.cursor.x, hand2.cursor.y, hand2.cursor.z);
        
        const distance = pos1.distanceTo(pos2);
        const angle = Math.atan2(pos2.y - pos1.y, pos2.x - pos1.x);
        
        if (this.lastTwoHandDistance !== null) {
            // Scale based on distance change
            const scale = distance / this.lastTwoHandDistance;
            const clampedScale = Math.max(0.9, Math.min(1.1, scale));
            
            this.scene.getCamera().position.multiplyScalar(1 / clampedScale);
        }
        
        this.lastTwoHandDistance = distance;
        this.lastTwoHandAngle = angle;
    }
    
    /**
     * Undo last action.
     */
    undo() {
        const action = this.state.popUndo();
        if (!action) return;
        
        switch (action.type) {
            case 'create':
                // Remove object
                this.scene.remove(action.object.mesh);
                this.scene.disposeMesh(action.object.mesh);
                
                if (action.objectType === 'stroke') {
                    const idx = this.state.strokes.indexOf(action.object);
                    if (idx !== -1) this.state.strokes.splice(idx, 1);
                } else if (action.objectType === 'block') {
                    const idx = this.state.blocks.indexOf(action.object);
                    if (idx !== -1) this.state.blocks.splice(idx, 1);
                }
                break;
            
            case 'delete':
                // Restore object
                this.scene.add(action.object.mesh);
                
                if (action.objectType === 'stroke') {
                    this.state.strokes.push(action.object);
                } else if (action.objectType === 'block') {
                    this.state.blocks.push(action.object);
                }
                break;
            
            case 'clear':
                // Restore all objects
                for (const obj of action.objects) {
                    this.scene.add(obj.mesh);
                    if (obj.type === 'stroke') {
                        this.state.strokes.push(obj);
                    } else if (obj.type === 'block') {
                        this.state.blocks.push(obj);
                    }
                }
                break;
        }
    }
    
    /**
     * Redo last undone action.
     */
    redo() {
        const action = this.state.popRedo();
        if (!action) return;
        
        // Redo is the opposite of undo
        switch (action.type) {
            case 'create':
                // Re-add object
                this.scene.add(action.object.mesh);
                
                if (action.objectType === 'stroke') {
                    this.state.strokes.push(action.object);
                } else if (action.objectType === 'block') {
                    this.state.blocks.push(action.object);
                }
                break;
            
            case 'delete':
                // Re-remove object
                this.scene.remove(action.object.mesh);
                
                if (action.objectType === 'stroke') {
                    const idx = this.state.strokes.indexOf(action.object);
                    if (idx !== -1) this.state.strokes.splice(idx, 1);
                } else if (action.objectType === 'block') {
                    const idx = this.state.blocks.indexOf(action.object);
                    if (idx !== -1) this.state.blocks.splice(idx, 1);
                }
                break;
            
            case 'clear':
                // Re-remove all objects
                for (const obj of action.objects) {
                    this.scene.remove(obj.mesh);
                    
                    if (obj.type === 'stroke') {
                        const idx = this.state.strokes.indexOf(obj);
                        if (idx !== -1) this.state.strokes.splice(idx, 1);
                    } else if (obj.type === 'block') {
                        const idx = this.state.blocks.indexOf(obj);
                        if (idx !== -1) this.state.blocks.splice(idx, 1);
                    }
                }
                break;
        }
    }
    
    /**
     * Clear all objects.
     */
    clearAll() {
        const allObjects = this.state.clearAll();
        
        for (const obj of allObjects) {
            this.scene.remove(obj.mesh);
            this.scene.disposeMesh(obj.mesh);
        }
    }
    
    /**
     * Save scene to JSON file.
     */
    save() {
        const data = this.state.exportToJSON();
        const json = JSON.stringify(data, null, 2);
        
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `aircanvas3d_${Date.now()}.json`;
        a.click();
        
        URL.revokeObjectURL(url);
    }
    
    /**
     * Load scene from JSON data.
     * @param {Object} data - Loaded JSON data
     */
    load(data) {
        // Clear existing
        this.clearAll();
        
        // Import data
        const imported = this.state.importFromJSON(data);
        
        // Recreate strokes
        for (const strokeData of imported.strokes) {
            const points = strokeData.points.map(p => 
                new THREE.Vector3(p[0] || p.x, p[1] || p.y, p[2] || p.z)
            );
            
            const stroke = createStroke(points, strokeData.color, strokeData.size);
            if (stroke) {
                this.scene.add(stroke.mesh);
                this.state.strokes.push(stroke);
            }
        }
        
        // Recreate blocks
        for (const blockData of imported.blocks) {
            const position = new THREE.Vector3(...blockData.position);
            const block = createBlock(position, blockData.color);
            this.scene.add(block.mesh);
            this.state.blocks.push(block);
        }
    }
    
    /**
     * Create dummy canvas for webcam preview.
     * @returns {HTMLCanvasElement}
     */
    createDummyCanvas() {
        const canvas = document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        return canvas;
    }
    
    /**
     * Handle WebSocket status change.
     * @param {string} status - Connection status
     */
    onSocketStatus(status) {
        this.ui.updateConnectionStatus(status);
    }
}

// Start application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new AirCanvas3D();
    });
} else {
    new AirCanvas3D();
}
