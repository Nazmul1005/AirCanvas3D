/**
 * Drawing tools: stroke creation, block placement, grabbing, and erasing.
 */

import * as THREE from 'three';

/**
 * Create a 3D stroke using TubeGeometry.
 * @param {Array} points - Array of THREE.Vector3 points
 * @param {string} color - Hex color string
 * @param {number} radius - Tube radius
 * @returns {Object} - Stroke object with mesh and metadata
 */
export function createStroke(points, color, radius) {
    if (points.length < 2) {
        return null;
    }
    
    // Create a curve from points
    const curve = new THREE.CatmullRomCurve3(points, false);
    
    // Create tube geometry
    const geometry = new THREE.TubeGeometry(curve, points.length * 2, radius, 8, false);
    
    // Create material with emissive color
    const material = new THREE.MeshStandardMaterial({
        color: color,
        emissive: color,
        emissiveIntensity: 0.5,
        roughness: 0.5,
        metalness: 0.3
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    return {
        mesh: mesh,
        points: points,
        color: color,
        size: radius,
        type: 'stroke'
    };
}

/**
 * Create a block (cube).
 * @param {THREE.Vector3} position - World position
 * @param {string} color - Hex color string (optional, random if not provided)
 * @returns {Object} - Block object with mesh and metadata
 */
export function createBlock(position, color = null) {
    // Random pastel color if not provided
    if (!color) {
        const hue = Math.random();
        const saturation = 0.5 + Math.random() * 0.3;
        const lightness = 0.7 + Math.random() * 0.2;
        color = hslToHex(hue, saturation, lightness);
    }
    
    // Snap to grid (0.5 unit grid)
    const snappedPos = new THREE.Vector3(
        Math.round(position.x * 2) / 2,
        Math.round(position.y * 2) / 2,
        Math.round(position.z * 2) / 2
    );
    
    // Create cube
    const geometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const material = new THREE.MeshStandardMaterial({
        color: color,
        roughness: 0.7,
        metalness: 0.2
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(snappedPos);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    
    return {
        mesh: mesh,
        color: color,
        type: 'block'
    };
}

/**
 * Find the nearest object to a position within a radius.
 * @param {THREE.Vector3} position - Search position
 * @param {Array} objects - Array of objects to search
 * @param {number} maxDistance - Maximum distance to search
 * @returns {Object|null} - Nearest object or null
 */
export function findNearestObject(position, objects, maxDistance = 2.0) {
    let nearest = null;
    let minDistance = maxDistance;
    
    for (const obj of objects) {
        const objPos = obj.mesh.position;
        const distance = position.distanceTo(objPos);
        
        if (distance < minDistance) {
            minDistance = distance;
            nearest = obj;
        }
    }
    
    return nearest;
}

/**
 * Find all objects within a radius.
 * @param {THREE.Vector3} position - Center position
 * @param {Array} objects - Array of objects to search
 * @param {number} radius - Search radius
 * @returns {Array} - Array of objects within radius
 */
export function findObjectsInRadius(position, objects, radius) {
    return objects.filter(obj => {
        const distance = position.distanceTo(obj.mesh.position);
        return distance < radius;
    });
}

/**
 * Highlight an object (for grab feedback).
 * @param {Object} obj - Object to highlight
 * @param {boolean} highlight - Whether to highlight or unhighlight
 */
export function highlightObject(obj, highlight) {
    if (!obj || !obj.mesh) return;
    
    if (highlight) {
        // Add outline effect (emissive boost)
        if (obj.mesh.material.emissive) {
            obj.mesh.material.emissive.setHex(0xffff00);
            obj.mesh.material.emissiveIntensity = 0.5;
        } else {
            obj.mesh.material.emissive = new THREE.Color(0xffff00);
            obj.mesh.material.emissiveIntensity = 0.5;
        }
    } else {
        // Remove outline
        if (obj.type === 'stroke') {
            obj.mesh.material.emissive.setHex(parseInt(obj.color.replace('#', '0x')));
            obj.mesh.material.emissiveIntensity = 0.5;
        } else {
            obj.mesh.material.emissiveIntensity = 0;
        }
    }
}

/**
 * Animate object removal (fade + scale).
 * @param {THREE.Mesh} mesh - Mesh to animate
 * @param {Function} onComplete - Callback when animation completes
 */
export function animateRemoval(mesh, onComplete) {
    const startTime = performance.now();
    const duration = 300; // ms
    
    const animate = () => {
        const elapsed = performance.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out
        const eased = 1 - Math.pow(1 - progress, 3);
        
        // Scale down
        const scale = 1 - eased;
        mesh.scale.set(scale, scale, scale);
        
        // Fade out
        if (mesh.material.transparent === undefined) {
            mesh.material.transparent = true;
        }
        mesh.material.opacity = 1 - eased;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        } else {
            onComplete();
        }
    };
    
    animate();
}

/**
 * Snap position to grid.
 * @param {THREE.Vector3} position - Position to snap
 * @param {number} gridSize - Grid size
 * @returns {THREE.Vector3} - Snapped position
 */
export function snapToGrid(position, gridSize = 0.5) {
    return new THREE.Vector3(
        Math.round(position.x / gridSize) * gridSize,
        Math.round(position.y / gridSize) * gridSize,
        Math.round(position.z / gridSize) * gridSize
    );
}

/**
 * Convert HSL to hex color.
 * @param {number} h - Hue (0-1)
 * @param {number} s - Saturation (0-1)
 * @param {number} l - Lightness (0-1)
 * @returns {string} - Hex color string
 */
function hslToHex(h, s, l) {
    const color = new THREE.Color();
    color.setHSL(h, s, l);
    return '#' + color.getHexString();
}

/**
 * Optimize stroke points by removing redundant close points.
 * @param {Array} points - Array of THREE.Vector3 points
 * @param {number} minDistance - Minimum distance between points
 * @returns {Array} - Optimized points array
 */
export function optimizeStrokePoints(points, minDistance = 0.1) {
    if (points.length < 2) return points;
    
    const optimized = [points[0]];
    
    for (let i = 1; i < points.length; i++) {
        const last = optimized[optimized.length - 1];
        const current = points[i];
        
        if (last.distanceTo(current) >= minDistance) {
            optimized.push(current);
        }
    }
    
    return optimized;
}

/**
 * Calculate smooth position with lerp.
 * @param {THREE.Vector3} current - Current position
 * @param {THREE.Vector3} target - Target position
 * @param {number} alpha - Lerp factor (0-1)
 * @returns {THREE.Vector3} - Smoothed position
 */
export function smoothPosition(current, target, alpha = 0.3) {
    return current.clone().lerp(target, alpha);
}
