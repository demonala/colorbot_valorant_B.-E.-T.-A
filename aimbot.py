"""
aimbot.py — Jugs's v3 Aimbot
Lock-on only. Does NOT shoot. Hold key to activate.
"""
import time
import threading
from pynput.mouse import Controller
from typing import Optional
from config import CFG
from capture import ScreenCapture
from detector import PurpleDetector
from types import Target
from utils import calc_movement, distance, clamp


class Aimbot:
    """
    Aimbot mode: Locks crosshair onto nearest enemy.
    Hold CFG.aimbot.hold_key to activate.
    Does NOT fire — you pull the trigger.
    """
    
    def __init__(self, capture: ScreenCapture, detector: PurpleDetector):
        self.capture = capture
        self.detector = detector
        self.mouse = Controller()
        
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
    def start(self) -> None:
        """Start aimbot background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
    def stop(self) -> None:
        """Stop aimbot thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
            
    def _loop(self) -> None:
        """Main aimbot loop."""
        import keyboard as kb
        
        while self.running:
            if not CFG.aimbot.enabled:
                time.sleep(0.05)
                continue
            
            # Check hold key
            if not kb.is_pressed(CFG.aimbot.hold_key):
                time.sleep(0.01)
                continue
            
            # Detect
            result = self.detector.detect()
            target = self.detector.get_closest_in_fov(result, CFG.aimbot.fov)
            
            if not target:
                time.sleep(0.01)
                continue
            
            # Calculate absolute target position
            abs_x = self.capture.monitor["left"] + target.cx
            abs_y = self.capture.monitor["top"] + target.cy
            
            # Current mouse position
            mx, my = self.mouse.position
            
            # Deadzone check
            dist = distance((abs_x, abs_y), (mx, my))
            if dist < CFG.aimbot.deadzone:
                time.sleep(0.01)
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
                time.sleep(0.01)
                continue
            
            # Move mouse
            self.mouse.move(move[0], move[1])
            
            # Dynamic sleep based on distance
            sleep_time = clamp(0.008 + dist / 2500, 0.005, 0.025)
            time.sleep(sleep_time)
 
