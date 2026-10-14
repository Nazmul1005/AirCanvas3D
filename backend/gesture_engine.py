"""
Gesture classification engine with debouncing and hysteresis.

Recognizes: DRAW, PINCH, PALM, FIST, TWO_HAND_SCALE
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from collections import deque
import time

import config
from filters import LandmarkFilter


class GestureEngine:
    """
    Classifies hand gestures based on landmark positions with debouncing.
    """
    
    # Finger tip and pip indices for MediaPipe Hands (21 landmarks)
    WRIST = 0
    THUMB_TIP = 4
    INDEX_TIP = 8
    INDEX_PIP = 6
    MIDDLE_TIP = 12
    MIDDLE_PIP = 10
    RING_TIP = 16
    RING_PIP = 14
    PINKY_TIP = 20
    PINKY_PIP = 18
    
    def __init__(self):
        """Initialize gesture engine with filters and debouncing state."""
        # Smoothing filters for cursor position (index tip) per hand
        self.cursor_filters: Dict[str, LandmarkFilter] = {}
        
        # Palm center filters
        self.palm_filters: Dict[str, LandmarkFilter] = {}
        
        # Gesture debouncing: track recent classifications
        self.gesture_history: Dict[str, deque] = {}
        self.current_gesture: Dict[str, str] = {}
        
        # Pinch state with hysteresis
        self.pinch_state: Dict[str, bool] = {}
        
        # Timestamp for filters
        self.start_time = time.time()
    
    def process_hands(self, hands_data: List[Dict]) -> List[Dict]:
        """
        Process hand data and classify gestures.
        
        Args:
            hands_data: List of hand dictionaries from hand_tracker
        
        Returns:
            List of enriched hand dictionaries with gesture, cursor, palm, etc.
        """
        current_time = time.time() - self.start_time
        processed = []
        
        for hand_data in hands_data:
            hand_id = hand_data['handedness']
            landmarks = hand_data['landmarks']
            hand_size = hand_data['hand_size']
            
            # Initialize filters for new hands
            if hand_id not in self.cursor_filters:
                self.cursor_filters[hand_id] = LandmarkFilter(
                    dimensions=3,
                    min_cutoff=config.ONE_EURO_MIN_CUTOFF,
                    beta=config.ONE_EURO_BETA,
                    derivate_cutoff=config.ONE_EURO_DERIVATE_CUTOFF
                )
                self.palm_filters[hand_id] = LandmarkFilter(
                    dimensions=2,
                    min_cutoff=config.ONE_EURO_MIN_CUTOFF,
                    beta=config.ONE_EURO_BETA,
                    derivate_cutoff=config.ONE_EURO_DERIVATE_CUTOFF
                )
                self.gesture_history[hand_id] = deque(maxlen=max(
                    config.GESTURE_DEBOUNCE_START,
                    config.GESTURE_DEBOUNCE_END
                ))
                self.current_gesture[hand_id] = "fist"
                self.pinch_state[hand_id] = False
            
            # Calculate cursor position (index tip) with depth
            cursor_raw = self._get_cursor_position(landmarks, hand_size)
            cursor_smooth = self.cursor_filters[hand_id](cursor_raw, current_time)
            
            # Calculate palm center (average of wrist and middle MCP)
            palm_raw = self._get_palm_center(landmarks)
            palm_smooth = self.palm_filters[hand_id](palm_raw, current_time)
            
            # Calculate pinch distance
            pinch_dist = self._calculate_pinch_distance(landmarks, hand_size)
            
            # Classify gesture
            raw_gesture = self._classify_gesture(landmarks, hand_size, hand_id, pinch_dist)
            
            # Apply debouncing
            final_gesture = self._debounce_gesture(hand_id, raw_gesture)
            
            processed.append({
                'handedness': hand_data['handedness'],
                'gesture': final_gesture,
                'confidence': hand_data['confidence'],
                'cursor': {
                    'x': cursor_smooth[0],
                    'y': cursor_smooth[1],
                    'z': cursor_smooth[2]
                },
                'palm': {
                    'x': palm_smooth[0],
                    'y': palm_smooth[1]
                },
                'pinch': pinch_dist,
                'landmarks': landmarks
            })
        
        # Check for two-hand scale gesture
        if len(processed) == 2:
            if all(h['gesture'] == 'pinch' for h in processed):
                # Both hands pinching = scale/rotate mode
                for hand in processed:
                    hand['gesture'] = 'two_hand_scale'
        
        return processed
    
    def _get_cursor_position(
        self,
        landmarks: List[List[float]],
        hand_size: float
    ) -> Tuple[float, float, float]:
        """
        Get cursor position from index finger tip with depth estimation.
        
        Args:
            landmarks: 21 hand landmarks
            hand_size: Normalized hand size
        
        Returns:
            (x, y, z) tuple
        """
        index_tip = landmarks[self.INDEX_TIP]
        
        # Depth proxy: smaller hand_size = farther away, larger z
        z = config.DEPTH_OFFSET + (1.0 / (hand_size * 10 + 0.1)) * config.DEPTH_SCALE
        
        return (index_tip[0], index_tip[1], z)
    
    def _get_palm_center(self, landmarks: List[List[float]]) -> Tuple[float, float]:
        """
        Calculate palm center as average of wrist and middle MCP.
        
        Args:
            landmarks: 21 hand landmarks
        
        Returns:
            (x, y) tuple
        """
        wrist = np.array(landmarks[self.WRIST][:2])
        middle_mcp = np.array(landmarks[9][:2])
        
        center = (wrist + middle_mcp) / 2
        return (center[0], center[1])
    
    def _calculate_pinch_distance(
        self,
        landmarks: List[List[float]],
        hand_size: float
    ) -> float:
        """
        Calculate normalized distance between thumb tip and index tip.
        
        Args:
            landmarks: 21 hand landmarks
            hand_size: Normalized hand size for scaling
        
        Returns:
            Normalized distance
        """
        thumb_tip = np.array(landmarks[self.THUMB_TIP][:2])
        index_tip = np.array(landmarks[self.INDEX_TIP][:2])
        
        distance = np.linalg.norm(thumb_tip - index_tip)
        
        # Normalize by hand size
        return distance / hand_size
    
    def _is_finger_extended(
        self,
        landmarks: List[List[float]],
        tip_idx: int,
        pip_idx: int
    ) -> bool:
        """
        Check if a finger is extended based on tip-to-wrist vs pip-to-wrist distance.
        
        Args:
            landmarks: 21 hand landmarks
            tip_idx: Index of fingertip
            pip_idx: Index of PIP joint
        
        Returns:
            True if finger is extended
        """
        wrist = np.array(landmarks[self.WRIST][:2])
        tip = np.array(landmarks[tip_idx][:2])
        pip = np.array(landmarks[pip_idx][:2])
        
        tip_dist = np.linalg.norm(tip - wrist)
        pip_dist = np.linalg.norm(pip - wrist)
        
        # Avoid division by zero
        if pip_dist < 1e-6:
            return False
        
        ratio = tip_dist / pip_dist
        
        return ratio > config.FINGER_EXTEND_THRESHOLD
    
    def _is_finger_curled(
        self,
        landmarks: List[List[float]],
        tip_idx: int,
        pip_idx: int
    ) -> bool:
        """Check if a finger is curled (opposite of extended)."""
        wrist = np.array(landmarks[self.WRIST][:2])
        tip = np.array(landmarks[tip_idx][:2])
        pip = np.array(landmarks[pip_idx][:2])
        
        tip_dist = np.linalg.norm(tip - wrist)
        pip_dist = np.linalg.norm(pip - wrist)
        
        if pip_dist < 1e-6:
            return True
        
        ratio = tip_dist / pip_dist
        
        return ratio < config.FINGER_CURL_THRESHOLD
    
    def _classify_gesture(
        self,
        landmarks: List[List[float]],
        hand_size: float,
        hand_id: str,
        pinch_dist: float
    ) -> str:
        """
        Classify the current gesture based on finger positions.
        
        Args:
            landmarks: 21 hand landmarks
            hand_size: Normalized hand size
            hand_id: Hand identifier
            pinch_dist: Normalized pinch distance
        
        Returns:
            Gesture name: "draw", "pinch", "palm", or "fist"
        """
        # Check finger extension states
        index_extended = self._is_finger_extended(landmarks, self.INDEX_TIP, self.INDEX_PIP)
        middle_extended = self._is_finger_extended(landmarks, self.MIDDLE_TIP, self.MIDDLE_PIP)
        ring_extended = self._is_finger_extended(landmarks, self.RING_TIP, self.RING_PIP)
        pinky_extended = self._is_finger_extended(landmarks, self.PINKY_TIP, self.PINKY_PIP)
        
        middle_curled = self._is_finger_curled(landmarks, self.MIDDLE_TIP, self.MIDDLE_PIP)
        ring_curled = self._is_finger_curled(landmarks, self.RING_TIP, self.RING_PIP)
        pinky_curled = self._is_finger_curled(landmarks, self.PINKY_TIP, self.PINKY_PIP)
        
        # PINCH: hysteresis to prevent flickering
        current_pinch = self.pinch_state.get(hand_id, False)
        
        if current_pinch:
            # Already pinching, need to open wider to release
            if pinch_dist > config.PINCH_THRESHOLD_END:
                self.pinch_state[hand_id] = False
                current_pinch = False
        else:
            # Not pinching, need to close tighter to start
            if pinch_dist < config.PINCH_THRESHOLD_START:
                self.pinch_state[hand_id] = True
                current_pinch = True
        
        if current_pinch:
            return "pinch"
        
        # PALM: all fingers extended and spread
        all_extended = all([
            index_extended,
            middle_extended,
            ring_extended,
            pinky_extended
        ])
        
        if all_extended:
            # Check if fingers are spread apart
            finger_tips = [
                np.array(landmarks[self.INDEX_TIP][:2]),
                np.array(landmarks[self.MIDDLE_TIP][:2]),
                np.array(landmarks[self.RING_TIP][:2]),
                np.array(landmarks[self.PINKY_TIP][:2])
            ]
            
            # Check distances between adjacent fingertips
            spreads = [
                np.linalg.norm(finger_tips[i] - finger_tips[i+1]) / hand_size
                for i in range(3)
            ]
            
            if all(s > config.PALM_SPREAD_THRESHOLD for s in spreads):
                return "palm"
        
        # DRAW: index extended, others curled
        if index_extended and middle_curled and ring_curled and pinky_curled:
            return "draw"
        
        # Default: FIST
        return "fist"
    
    def _debounce_gesture(self, hand_id: str, raw_gesture: str) -> str:
        """
        Apply debouncing to prevent flickering.
        
        A new gesture must appear for GESTURE_DEBOUNCE_START consecutive frames
        to become active, and must be absent for GESTURE_DEBOUNCE_END frames
        to deactivate.
        
        Args:
            hand_id: Hand identifier
            raw_gesture: Raw classified gesture
        
        Returns:
            Debounced gesture
        """
        history = self.gesture_history[hand_id]
        history.append(raw_gesture)
        
        current = self.current_gesture[hand_id]
        
        # Check if we should switch to a new gesture
        if len(history) >= config.GESTURE_DEBOUNCE_START:
            recent = list(history)[-config.GESTURE_DEBOUNCE_START:]
            if all(g == raw_gesture for g in recent) and raw_gesture != current:
                self.current_gesture[hand_id] = raw_gesture
                return raw_gesture
        
        # Check if current gesture has ended
        if len(history) >= config.GESTURE_DEBOUNCE_END:
            recent = list(history)[-config.GESTURE_DEBOUNCE_END:]
            if all(g != current for g in recent):
                # Current gesture ended, switch to most recent
                self.current_gesture[hand_id] = raw_gesture
                return raw_gesture
        
        return current
    
    def reset_hand(self, hand_id: str):
        """Reset state for a specific hand (when it disappears)."""
        if hand_id in self.cursor_filters:
            self.cursor_filters[hand_id].reset()
        if hand_id in self.palm_filters:
            self.palm_filters[hand_id].reset()
        if hand_id in self.gesture_history:
            self.gesture_history[hand_id].clear()
        if hand_id in self.current_gesture:
            self.current_gesture[hand_id] = "fist"
        if hand_id in self.pinch_state:
            self.pinch_state[hand_id] = False
