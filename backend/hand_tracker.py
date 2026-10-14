"""
MediaPipe Hands wrapper for hand landmark detection.
Compatible with MediaPipe 0.10.30+ (new task-based API).
"""

import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
import os
import urllib.request
import config

# Import MediaPipe with new API
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# Model URL for MediaPipe hand landmarker
HAND_LANDMARKER_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")


def download_model():
    """Download the MediaPipe hand landmarker model if not present."""
    if not os.path.exists(MODEL_PATH):
        print(f"Downloading hand landmarker model...")
        try:
            urllib.request.urlretrieve(HAND_LANDMARKER_MODEL_URL, MODEL_PATH)
            print(f"✓ Model downloaded to {MODEL_PATH}")
        except Exception as e:
            print(f"✗ Failed to download model: {e}")
            print(f"  Please download manually from: {HAND_LANDMARKER_MODEL_URL}")
            print(f"  Save it to: {MODEL_PATH}")
            raise


class HandTracker:
    """Wrapper around MediaPipe Hands for detecting and tracking hand landmarks."""
    
    def __init__(self):
        """Initialize MediaPipe Hands with new task-based API."""
        # Ensure model is downloaded
        download_model()
        
        # Create hand landmarker options
        base_options = python.BaseOptions(
            model_asset_path=MODEL_PATH,
            delegate=python.BaseOptions.Delegate.CPU
        )
        
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=config.MP_MAX_NUM_HANDS,
            min_hand_detection_confidence=config.MP_MIN_DETECTION_CONFIDENCE,
            min_hand_presence_confidence=config.MP_MIN_TRACKING_CONFIDENCE,
            min_tracking_confidence=config.MP_MIN_TRACKING_CONFIDENCE,
            running_mode=vision.RunningMode.IMAGE
        )
        
        self.detector = vision.HandLandmarker.create_from_options(options)
    
    def process(self, frame: np.ndarray) -> Optional[object]:
        """
        Process a frame and detect hands.
        
        Args:
            frame: BGR image from OpenCV
        
        Returns:
            MediaPipe results object or None
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Create MP Image and detect
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        results = self.detector.detect(mp_image)
        
        return results
    
    def extract_landmarks(
        self,
        results: object,
        image_width: int,
        image_height: int
    ) -> List[Dict]:
        """
        Extract normalized landmarks from MediaPipe results.
        
        Args:
            results: MediaPipe results object
            image_width: Width of the input image
            image_height: Height of the input image
        
        Returns:
            List of hand data dictionaries, one per detected hand
        """
        hands_data = []
        
        # Check if hands were detected
        if not results.hand_landmarks or len(results.hand_landmarks) == 0:
            return hands_data
        
        for hand_idx, hand_landmarks in enumerate(results.hand_landmarks):
            # Extract handedness
            if hand_idx < len(results.handedness):
                hand_label = results.handedness[hand_idx][0].category_name
                hand_confidence = results.handedness[hand_idx][0].score
            else:
                hand_label = "Unknown"
                hand_confidence = 0.5
            
            # Extract all 21 landmarks as normalized [x, y, z] coordinates
            landmarks = []
            for lm in hand_landmarks:
                landmarks.append([lm.x, lm.y, lm.z])
            
            # Calculate hand size
            hand_size = self._calculate_hand_size(landmarks)
            
            hands_data.append({
                'handedness': hand_label,
                'confidence': hand_confidence,
                'landmarks': landmarks,
                'hand_size': hand_size
            })
        
        return hands_data
    
    def draw_landmarks(
        self,
        frame: np.ndarray,
        results: object
    ) -> np.ndarray:
        """
        Draw hand landmarks on the frame for debugging.
        
        Args:
            frame: BGR image from OpenCV
            results: MediaPipe results object
        
        Returns:
            Frame with landmarks drawn
        """
        # Manually draw landmarks and connections
        if results.hand_landmarks:
            for hand_landmarks in results.hand_landmarks:
                # Draw connections
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
                    (0, 5), (5, 6), (6, 7), (7, 8),  # Index
                    (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
                    (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
                    (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
                    (5, 9), (9, 13), (13, 17)  # Palm
                ]
                
                h, w = frame.shape[:2]
                
                # Draw connections (lines)
                for start_idx, end_idx in connections:
                    start = hand_landmarks[start_idx]
                    end = hand_landmarks[end_idx]
                    
                    start_point = (int(start.x * w), int(start.y * h))
                    end_point = (int(end.x * w), int(end.y * h))
                    
                    cv2.line(frame, start_point, end_point, (0, 255, 0), 2)
                
                # Draw landmarks (circles)
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 5, (0, 255, 255), -1)
        
        return frame
    
    @staticmethod
    def _calculate_hand_size(landmarks: List[List[float]]) -> float:
        """
        Calculate hand size as the distance between wrist and middle finger MCP.
        
        Args:
            landmarks: List of 21 [x, y, z] coordinates
        
        Returns:
            Hand size (Euclidean distance in normalized coordinates)
        """
        wrist = np.array(landmarks[0][:2])  # Only use x, y
        middle_mcp = np.array(landmarks[9][:2])
        
        distance = np.linalg.norm(wrist - middle_mcp)
        
        # Avoid division by zero
        return max(distance, 0.01)
    
    def close(self):
        """Release MediaPipe resources."""
        if hasattr(self, 'detector'):
            self.detector.close()
