"""
capture.py — Jugs's v3 Screen Capture
Fast, clean, MSS-based.
"""
import numpy as np
import cv2
import mss
from typing import Optional, Tuple
from config import CFG


class ScreenCapture:
    """Handle screen capture with configurable region."""
    
    def __init__(self):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[CFG.monitor_index]
        
        self.width = self.monitor["width"]
        self.height = self.monitor["height"]
        self.cx = self.monitor["left"] + self.width // 2
        self.cy = self.monitor["top"] + self.height // 2
        
    def grab(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Capture screen region.
        region = (left, top, width, height) or None for full screen.
        Returns BGR numpy array.
        """
        if region:
            capture_area = {
                "left": region[0],
                "top": region[1],
                "width": region[2],
                "height": region[3],
            }
        else:
            capture_area = self.monitor
            
        screenshot = self.sct.grab(capture_area)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    def grab_center(self, size: int) -> np.ndarray:
        """Fast grab around screen center for triggerbot."""
        half = size // 2
        region = {
            "left": self.cx - half,
            "top": self.cy - half,
            "width": size,
            "height": size,
        }
        screenshot = self.sct.grab(region)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    @property
    def center(self) -> Tuple[int, int]:
        """Screen center coordinates."""
        return (self.cx, self.cy)
 
