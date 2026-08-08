"""
aimbot.py — Jugs's v3.1 Aimbot
Toggle ON/OFF with F2. No hold key. Smart HSV fallback.
"""
import time
import threading
from pynput.mouse import Controller
from typing import Optional
from config import CFG
from capture import ScreenCapture
from detector import PurpleDetector
from models import Target
from utils import calc_movement, distance, clamp


class Aimbot:
    def __init__(self, capture: ScreenCapture, detector: PurpleDetector):
        self.capture = capture
        self.detector = detector
        self.mouse = Controller()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def start(self) -> None:
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
    def stop(self) -> None:
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
            
    def _loop(self) -> None:
        """Toggle-only: runs when enabled, stops when disabled."""
        while self.running:
            if not CFG.aimbot.enabled:
                time.sleep(0.05)
                continue
            
            # Detect with smart HSV fallback
            result = self.detector.detect()
            target = self.detector.get_closest_in_fov(result, CFG.aimbot.fov)
            
            if not target:
                time.sleep(0.008)
                continue
            
            # Calculate absolute target position
            abs_x = self.capture.monitor["left"] + target.cx
            abs_y = self.capture.monitor["top"] + target.cy
            
            # Current mouse position
            mx, my = self.mouse.position
            
            # Deadzone check
            dist = distance((abs_x, abs_y), (mx, my))
            if dist < CFG.aimbot.deadzone:
                time.sleep(0.008)
                continue
            
            # Calculate movement
            move = calc_movement(
                target=(abs_x, abs_y),
                current=(mx, my),
                strength=CFG.aimbot.strength,
                smooth=CFG.aimbot.smooth,
                y_offset=CFG.aimbot.y_offset,
                randomize=CFG.aimbot.randomize
            )
            
            if move == (0, 0):
                time.sleep(0.008)
                continue
            
            # Move mouse
            self.mouse.move(move[0], move[1])
            
            # Dynamic sleep
            sleep_time = clamp(0.008 + dist / 2500, 0.005, 0.025)
            time.sleep(sleep_time)
