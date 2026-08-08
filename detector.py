"""
detector.py — Jugs's v3 Detection Engine
HSV-based purple outline detection with clean filtering.
"""
import cv2
import numpy as np
from typing import List, Optional
from config import CFG
from capture import ScreenCapture
from types import Target, DetectionResult
from utils import distance


class PurpleDetector:
    """Detect purple enemy outlines in captured frames."""
    
    def __init__(self, capture: ScreenCapture):
        self.capture = capture
        self.lower = np.array(CFG.color.lower_hsv, dtype=np.uint8)
        self.upper = np.array(CFG.color.upper_hsv, dtype=np.uint8)
        
    def detect(self, frame: Optional[np.ndarray] = None) -> DetectionResult:
        """
        Detect all purple outlines in frame.
        If frame is None, captures fresh frame.
        """
        if frame is None:
            frame = self.capture.grab()
        
        # HSV color mask
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        
        # Morphological cleanup
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        targets: List[Target] = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < CFG.detection.min_contour_area or area > CFG.detection.max_contour_area:
                continue
            
            x, y, w, h = cv2.boundingRect(cnt)
            
            # Aspect ratio filter — outlines are tall and thin
            aspect = h / w if w > 0 else 0
            if aspect < CFG.detection.min_aspect:
                continue
            
            # Calculate confidence from purple pixel density
            roi = mask[y:y+h, x:x+w]
            purple_pixels = cv2.countNonZero(roi)
            total_pixels = w * h
            confidence = (purple_pixels / total_pixels) * min(aspect, 3.0) / 3.0
            confidence = min(confidence, 1.0)
            
            center_x = x + w // 2
            center_y = y + h // 2
            
            targets.append(Target(
                x=x, y=y,
                width=w, height=h,
                confidence=confidence,
                center=(center_x, center_y),
                aspect_ratio=aspect,
                area=int(area)
            ))
        
        # Sort by distance from crosshair (closest first)
        cx, cy = self.capture.center
        targets.sort(key=lambda t: distance((t.cx, t.cy), (cx, cy)))
        
        return DetectionResult(targets=targets, frame=frame)
    
    def check_purple_at_center(self, size: int) -> float:
        """
        Check purple concentration at screen center.
        Returns 0.0-1.0 confidence.
        Used by triggerbot for fast center checks.
        """
        frame = self.capture.grab_center(size)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        
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

