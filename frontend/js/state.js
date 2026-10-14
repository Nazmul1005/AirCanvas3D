/**
 * Global state management for AirCanvas 3D.
 * Manages strokes, blocks, undo/redo stacks, and current tool state.
 */

export class State {
    constructor() {
        // Drawing objects
        this.strokes = [];  // Array of stroke objects with geometry and mesh
        this.blocks = [];   // Array of block objects with mesh and position
        
        // Undo/redo stacks
        this.undoStack = [];
        this.redoStack = [];
        this.maxStackSize = 50;
        
        // Current tool state
        this.currentTool = 'draw';  // 'draw' or 'blocks'
        this.brushColor = '#00ffff';
        this.brushSize = 0.08;
        
        // Active drawing state
        this.activeStroke = null;
        this.grabbedObject = null;
        this.grabbedOffset = null;
        
        // Hand tracking state
        this.lastHandData = null;
    }
    
    /**
     * Set the current tool.
     * @param {string} tool - 'draw' or 'blocks'
     */
    setTool(tool) {
        this.currentTool = tool;
    }
    
    /**
     * Set brush color.
     * @param {string} color - Hex color string
     */
    setColor(color) {
        this.brushColor = color;
    }
    
    /**
     * Set brush size.
     * @param {number} size - Brush radius
     */
    setSize(size) {
        this.brushSize = parseFloat(size);
    }
    
    /**
     * Add a stroke to the scene.
     * @param {Object} stroke - Stroke object with mesh and metadata
     */
    addStroke(stroke) {
        this.strokes.push(stroke);
        this.recordAction({
            type: 'create',
            objectType: 'stroke',
            object: stroke
        });
    }
    
    /**
     * Add a block to the scene.
     * @param {Object} block - Block object with mesh and metadata
     */
    addBlock(block) {
        this.blocks.push(block);
        this.recordAction({
            type: 'create',
            objectType: 'block',
            object: block
        });
    }
    
    /**
     * Remove an object from the scene.
     * @param {Object} obj - Object to remove
     */
    removeObject(obj) {
        let removed = false;
        let objectType = null;
        
        // Check strokes
        const strokeIndex = this.strokes.indexOf(obj);
        if (strokeIndex !== -1) {
            this.strokes.splice(strokeIndex, 1);
            objectType = 'stroke';
            removed = true;
        }
        
        // Check blocks
        const blockIndex = this.blocks.indexOf(obj);
        if (blockIndex !== -1) {
            this.blocks.splice(blockIndex, 1);
            objectType = 'block';
            removed = true;
        }
        
        if (removed) {
            this.recordAction({
                type: 'delete',
                objectType: objectType,
                object: obj
            });
        }
        
        return removed;
    }
    
    /**
     * Clear all objects.
     */
    clearAll() {
        const allObjects = [...this.strokes, ...this.blocks];
        
        this.strokes = [];
        this.blocks = [];
        
        if (allObjects.length > 0) {
            this.recordAction({
                type: 'clear',
                objects: allObjects
            });
        }
        
        return allObjects;
    }
    
    /**
     * Record an action for undo/redo.
     * @param {Object} action - Action object
     */
    recordAction(action) {
        this.undoStack.push(action);
        
        // Limit stack size
        if (this.undoStack.length > this.maxStackSize) {
            this.undoStack.shift();
        }
        
        // Clear redo stack on new action
        this.redoStack = [];
    }
    
    /**
     * Get the last action from undo stack without removing it.
     * @returns {Object|null}
     */
    peekUndo() {
        return this.undoStack.length > 0 ? this.undoStack[this.undoStack.length - 1] : null;
    }
    
    /**
     * Get the last action from redo stack without removing it.
     * @returns {Object|null}
     */
    peekRedo() {
        return this.redoStack.length > 0 ? this.redoStack[this.redoStack.length - 1] : null;
    }
    
    /**
     * Pop an action from undo stack.
     * @returns {Object|null}
     */
    popUndo() {
        const action = this.undoStack.pop();
        if (action) {
            this.redoStack.push(action);
        }
        return action;
    }
    
    /**
     * Pop an action from redo stack.
     * @returns {Object|null}
     */
    popRedo() {
        const action = this.redoStack.pop();
        if (action) {
            this.undoStack.push(action);
        }
        return action;
    }
    
    /**
     * Get all objects in the scene.
     * @returns {Array}
     */
    getAllObjects() {
        return [...this.strokes, ...this.blocks];
    }
    
    /**
     * Export state as JSON.
     * @returns {Object}
     */
    exportToJSON() {
        return {
            strokes: this.strokes.map(s => ({
                points: s.points,
                color: s.color,
                size: s.size
            })),
            blocks: this.blocks.map(b => ({
                position: b.mesh.position.toArray(),
                color: b.color
            }))
        };
    }
    
    /**
     * Import state from JSON.
     * @param {Object} data
     * @returns {Object} - Object with strokes and blocks arrays
     */
    importFromJSON(data) {
        return {
            strokes: data.strokes || [],
            blocks: data.blocks || []
        };
    }
}
