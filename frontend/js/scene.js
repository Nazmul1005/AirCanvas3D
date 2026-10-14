/**
 * Three.js scene setup and management.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export class Scene3D {
    constructor(container) {
        this.container = container;
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        
        // Cursor sphere
        this.cursor = null;
        this.cursorShadow = null;
        
        // Erase indicator
        this.eraseIndicator = null;
        
        this.init();
    }
    
    /**
     * Initialize the Three.js scene.
     */
    init() {
        // Scene
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.Fog(0x0a0a0a, 10, 50);
        
        // Camera
        this.camera = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 5, 10);
        this.camera.lookAt(0, 0, 0);
        
        // Renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        // Dark gradient background
        this.scene.background = new THREE.Color(0x0a0a0a);
        
        // Lights
        this.setupLights();
        
        // Grid floor
        this.setupGrid();
        
        // Cursor
        this.setupCursor();
        
        // Controls
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.maxPolarAngle = Math.PI / 2;
        this.controls.enablePan = true;
        
        // Handle resize
        window.addEventListener('resize', () => this.onResize());
        
        console.log('Scene initialized');
    }
    
    /**
     * Setup lighting.
     */
    setupLights() {
        // Ambient light
        const ambient = new THREE.AmbientLight(0xffffff, 0.4);
        this.scene.add(ambient);
        
        // Directional light with shadows
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(5, 10, 7);
        dirLight.castShadow = true;
        dirLight.shadow.camera.left = -10;
        dirLight.shadow.camera.right = 10;
        dirLight.shadow.camera.top = 10;
        dirLight.shadow.camera.bottom = -10;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        this.scene.add(dirLight);
        
        // Rim light
        const rimLight = new THREE.DirectionalLight(0x4444ff, 0.3);
        rimLight.position.set(-5, 5, -5);
        this.scene.add(rimLight);
    }
    
    /**
     * Setup grid floor.
     */
    setupGrid() {
        const gridHelper = new THREE.GridHelper(20, 20, 0x444444, 0x222222);
        this.scene.add(gridHelper);
        
        // Ground plane for shadows
        const groundGeometry = new THREE.PlaneGeometry(50, 50);
        const groundMaterial = new THREE.ShadowMaterial({ opacity: 0.3 });
        const ground = new THREE.Mesh(groundGeometry, groundMaterial);
        ground.rotation.x = -Math.PI / 2;
        ground.position.y = -0.01;
        ground.receiveShadow = true;
        this.scene.add(ground);
    }
    
    /**
     * Setup cursor sphere and shadow.
     */
    setupCursor() {
        // Cursor sphere
        const cursorGeometry = new THREE.SphereGeometry(0.15, 16, 16);
        const cursorMaterial = new THREE.MeshStandardMaterial({
            color: 0xffffff,
            emissive: 0xffffff,
            emissiveIntensity: 0.5,
            transparent: true,
            opacity: 0.9
        });
        this.cursor = new THREE.Mesh(cursorGeometry, cursorMaterial);
        this.cursor.castShadow = true;
        this.cursor.visible = false;
        this.scene.add(this.cursor);
        
        // Cursor shadow line (helps with depth perception)
        const shadowGeometry = new THREE.BufferGeometry();
        const shadowPositions = new Float32Array([0, 0, 0, 0, 0, 0]);
        shadowGeometry.setAttribute('position', new THREE.BufferAttribute(shadowPositions, 3));
        const shadowMaterial = new THREE.LineBasicMaterial({
            color: 0x888888,
            transparent: true,
            opacity: 0.3
        });
        this.cursorShadow = new THREE.Line(shadowGeometry, shadowMaterial);
        this.cursorShadow.visible = false;
        this.scene.add(this.cursorShadow);
        
        // Erase indicator (sphere)
        const eraseGeometry = new THREE.SphereGeometry(1.5, 32, 32);
        const eraseMaterial = new THREE.MeshBasicMaterial({
            color: 0xff4444,
            transparent: true,
            opacity: 0.2,
            wireframe: true
        });
        this.eraseIndicator = new THREE.Mesh(eraseGeometry, eraseMaterial);
        this.eraseIndicator.visible = false;
        this.scene.add(this.eraseIndicator);
    }
    
    /**
     * Update cursor position and appearance.
     * @param {Object} cursorData - {x, y, z} normalized coordinates
     * @param {string} gesture - Current gesture name
     * @param {boolean} visible - Whether cursor should be visible
     */
    updateCursor(cursorData, gesture, visible) {
        if (!visible) {
            this.cursor.visible = false;
            this.cursorShadow.visible = false;
            this.eraseIndicator.visible = false;
            return;
        }
        
        // Map normalized coordinates to world space
        const worldX = (cursorData.x - 0.5) * 10;
        const worldY = (0.5 - cursorData.y) * 10 + 3;  // Offset up
        const worldZ = -cursorData.z * 5;
        
        // Smooth cursor movement
        if (this.cursor.visible) {
            this.cursor.position.lerp(
                new THREE.Vector3(worldX, worldY, worldZ),
                0.3
            );
        } else {
            this.cursor.position.set(worldX, worldY, worldZ);
        }
        
        this.cursor.visible = true;
        
        // Update shadow line
        const positions = this.cursorShadow.geometry.attributes.position.array;
        positions[0] = this.cursor.position.x;
        positions[1] = this.cursor.position.y;
        positions[2] = this.cursor.position.z;
        positions[3] = this.cursor.position.x;
        positions[4] = 0;
        positions[5] = this.cursor.position.z;
        this.cursorShadow.geometry.attributes.position.needsUpdate = true;
        this.cursorShadow.visible = true;
        
        // Update cursor color based on gesture
        let color, emissive;
        switch (gesture) {
            case 'draw':
                color = 0x00ffff;
                emissive = 0x00ffff;
                break;
            case 'pinch':
                color = 0xffff00;
                emissive = 0xffff00;
                break;
            case 'palm':
                color = 0xff4444;
                emissive = 0xff4444;
                break;
            case 'two_hand_scale':
                color = 0xff00ff;
                emissive = 0xff00ff;
                break;
            default:
                color = 0xffffff;
                emissive = 0xffffff;
        }
        
        this.cursor.material.color.setHex(color);
        this.cursor.material.emissive.setHex(emissive);
        
        // Show erase indicator for palm gesture
        if (gesture === 'palm') {
            this.eraseIndicator.position.copy(this.cursor.position);
            this.eraseIndicator.visible = true;
        } else {
            this.eraseIndicator.visible = false;
        }
    }
    
    /**
     * Add an object to the scene.
     * @param {THREE.Object3D} object
     */
    add(object) {
        this.scene.add(object);
    }
    
    /**
     * Remove an object from the scene.
     * @param {THREE.Object3D} object
     */
    remove(object) {
        this.scene.remove(object);
    }
    
    /**
     * Dispose of a mesh and its resources.
     * @param {THREE.Mesh} mesh
     */
    disposeMesh(mesh) {
        if (mesh.geometry) {
            mesh.geometry.dispose();
        }
        if (mesh.material) {
            if (Array.isArray(mesh.material)) {
                mesh.material.forEach(m => m.dispose());
            } else {
                mesh.material.dispose();
            }
        }
    }
    
    /**
     * Enable or disable orbit controls.
     * @param {boolean} enabled
     */
    setControlsEnabled(enabled) {
        this.controls.enabled = enabled;
    }
    
    /**
     * Get the cursor world position.
     * @returns {THREE.Vector3}
     */
    getCursorPosition() {
        return this.cursor.position.clone();
    }
    
    /**
     * Handle window resize.
     */
    onResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    /**
     * Render a frame.
     */
    render() {
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
    
    /**
     * Get the scene object.
     * @returns {THREE.Scene}
     */
    getScene() {
        return this.scene;
    }
    
    /**
     * Get the camera object.
     * @returns {THREE.Camera}
     */
    getCamera() {
        return this.camera;
    }
}
