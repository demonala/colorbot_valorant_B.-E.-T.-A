"""
detector.py — Jugs's v3.1 Smart Detector
Auto-switches HSV strategies until targets found.
"""
import cv2
import numpy as np
from typing import List, Optional, Tuple
from config import CFG
from capture import ScreenCapture
from models import Target, DetectionResult
from utils import distance


# Smart HSV fallback ranges (same as overlay)
HSV_STRATEGIES = [
    ("PRIMARY", np.array([130, 60, 180], dtype=np.uint8), np.array([170, 255, 255], dtype=np.uint8)),
    ("FALLBACK_0", np.array([120, 50, 150], dtype=np.uint8), np.array([180, 255, 255], dtype=np.uint8)),
    ("FALLBACK_1", np.array([140, 80, 200], dtype=np.uint8), np.array([170, 255, 255], dtype=np.uint8)),
    ("FALLBACK_2", np.array([110, 40, 100], dtype=np.uint8), np.array([180, 255, 255], dtype=np.uint8)),
]


class PurpleDetector:
    """Smart purple detector with auto HSV fallback."""
    
    def __init__(self, capture: ScreenCapture):
        self.capture = capture
        self.active_strategy = 0  # Index into HSV_STRATEGIES
        self.strategy_name = "PRIMARY"
        
    def _detect_with_hsv(self, frame: np.ndarray, lower: np.ndarray, upper: np.ndarray) -> List[Target]:
        """Detect targets with specific HSV range."""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        
        # Morphological cleanup
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        targets: List[Target] = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < CFG.detection.min_contour_area or area > CFG.detection.max_contour_area:
                continue
            
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Thin outline check
            if w > 15 and h > 30:
                continue
            
            aspect = h / w if w > 0 else 0
            if aspect < CFG.detection.min_aspect:
                continue
            
            # Confidence from purple density
            roi = mask[y:y+h, x:x+w]
            purple_pixels = cv2.countNonZero(roi)
            total_pixels = w * h
            purple_ratio = purple_pixels / total_pixels if total_pixels > 0 else 0
            confidence = purple_ratio * min(aspect, 3.0) / 3.0
            confidence = min(confidence, 1.0)
            
            center_x = x + w // 2
            center_y = y + h // 2
            
            targets.append(Target(
                x=x, y=y,
                width=w, height=h,
                confidence=round(confidence, 2),
                center=(center_x, center_y),
                aspect_ratio=round(aspect, 2),
                area=int(area)
            ))
        
        return targets
    
    def detect(self, frame: Optional[np.ndarray] = None) -> DetectionResult:
        """
        Detect with smart fallback.
        Tries primary first, then fallbacks until targets found.
        """
        if frame is None:
            frame = self.capture.grab()
        
        # Try primary first
        name, lower, upper = HSV_STRATEGIES[self.active_strategy]
        targets = self._detect_with_hsv(frame, lower, upper)
        
        # If nothing found, try all fallbacks
        if not targets:
            for i, (name, lower, upper) in enumerate(HSV_STRATEGIES):
                if i == self.active_strategy:
                    continue
                targets = self._detect_with_hsv(frame, lower, upper)
                if targets:
                    self.active_strategy = i
                    self.strategy_name = name
                    print(f"[DETECTOR] Auto-switched to {name} — found {len(targets)} targets")
                    break
        
        # Sort by distance from crosshair
        cx, cy = self.capture.center
        targets.sort(key=lambda t: distance((t.cx, t.cy), (cx, cy)))
        
        return DetectionResult(targets=targets, frame=frame)
    
    def check_purple_at_center(self, size: int) -> float:
        """Fast center check using active strategy."""
        frame = self.capture.grab_center(size)
        name, lower, upper = HSV_STRATEGIES[self.active_strategy]
        
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        
        purple = cv2.countNonZero(mask)
        total = frame.shape[0] * frame.shape[1]
        return purple / total if total > 0 else 0.0
    
    def get_closest_in_fov(self, result: DetectionResult, fov: int) -> Optional[Target]:
        """Get closest target within FOV radius."""
        cx, cy = self.capture.center
        
        for target in result.targets:
            dist = distance((target.cx, target.cy), (cx, cy))
            if dist <= fov:
                return target
        
        return None
