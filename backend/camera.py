"""
Camera capture module using OpenCV.

Captures frames in a background thread, mirrors horizontally for natural interaction.
"""

import cv2
import numpy as np
import threading
import time
from typing import Optional, Tuple
import config


class Camera:
    """Threaded camera capture with mirroring and resizing."""
    
    def __init__(self):
        """Initialize camera capture."""
        self.cap: Optional[cv2.VideoCapture] = None
        self.frame: Optional[np.ndarray] = None
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
        self.fps = 0.0
        self.frame_count = 0
        self.last_fps_time = time.time()
    
    def start(self) -> bool:
        """
        Start camera capture thread.
        
        Returns:
            True if camera opened successfully, False otherwise
        """
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        
        if not self.cap.isOpened():
            print(f"ERROR: Could not open camera {config.CAMERA_INDEX}")
            return False
        
        # Set camera properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, config.CAMERA_FPS)
        
        # Read first frame
        ret, frame = self.cap.read()
        if not ret:
            print("ERROR: Could not read from camera")
            self.cap.release()
            return False
        
        self.frame = self._process_frame(frame)
        
        # Start capture thread
        self.running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        
        print(f"Camera started: {config.CAMERA_WIDTH}x{config.CAMERA_HEIGHT} @ {config.CAMERA_FPS} FPS")
        return True
    
    def _capture_loop(self):
        """Background thread that continuously captures frames."""
        while self.running:
            ret, frame = self.cap.read()
            
            if not ret:
                print("WARNING: Failed to read frame from camera")
                time.sleep(0.1)
                continue
            
            processed = self._process_frame(frame)
            
            with self.lock:
                self.frame = processed
                self.frame_count += 1
            
            # Calculate FPS
            current_time = time.time()
            if current_time - self.last_fps_time >= 1.0:
                with self.lock:
                    self.fps = self.frame_count / (current_time - self.last_fps_time)
                    self.frame_count = 0
                    self.last_fps_time = current_time
            
            # Yield to other threads
            time.sleep(0.001)
    
    def _process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process frame: mirror horizontally for natural interaction.
        
        Args:
            frame: Raw frame from camera
        
        Returns:
            Processed frame
        """
        # Mirror horizontally
        mirrored = cv2.flip(frame, 1)
        
        # Resize if needed
        h, w = mirrored.shape[:2]
        if w != config.CAMERA_WIDTH or h != config.CAMERA_HEIGHT:
            mirrored = cv2.resize(mirrored, (config.CAMERA_WIDTH, config.CAMERA_HEIGHT))
        
        return mirrored
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """
        Read the latest frame.
        
        Returns:
            (success, frame) tuple
        """
        with self.lock:
            if self.frame is None:
                return False, None
            return True, self.frame.copy()
    
    def get_fps(self) -> float:
        """Get current capture FPS."""
        with self.lock:
            return self.fps
    
    def get_frame_size(self) -> Tuple[int, int]:
        """
        Get frame dimensions.
        
        Returns:
            (width, height) tuple
        """
        return (config.CAMERA_WIDTH, config.CAMERA_HEIGHT)
    
    def stop(self):
        """Stop camera capture and release resources."""
        self.running = False
        
        if self.thread is not None:
            self.thread.join(timeout=2.0)
        
        if self.cap is not None:
            self.cap.release()
        
        print("Camera stopped")
    
    def is_running(self) -> bool:
        """Check if camera is running."""
        return self.running
