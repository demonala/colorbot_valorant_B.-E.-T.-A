"""
triggerbot.py — Jugs's v3 Triggerbot
Single tap when crosshair on purple. Sniper/guardian optimized.
"""
import time
import threading
import random
from pynput.mouse import Controller, Button
from typing import Optional
from config import CFG
from capture import ScreenCapture
from detector import PurpleDetector
from utils import human_delay


class Triggerbot:
    """
    Triggerbot mode: Auto-tap when purple detected at crosshair.
    Hold CFG.triggerbot.hold_key to activate.
    Designed for slow-firing weapons (Operator, Marshal, Guardian).
    """
    
    def __init__(self, capture: ScreenCapture, detector: PurpleDetector):
        self.capture = capture
        self.detector = detector
        self.mouse = Controller()
        
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        self.last_shot_time = 0.0
        self.cooldown = 0.5
        
    def start(self) -> None:
        """Start triggerbot background thread."""
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        
    def stop(self) -> None:
        """Stop triggerbot thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.5)
            
    def _loop(self) -> None:
        """Main triggerbot loop."""
        import keyboard as kb
        
        while self.running:
            if not CFG.triggerbot.enabled:
                time.sleep(0.05)
                continue
            
            # Check hold key
            if not kb.is_pressed(CFG.triggerbot.hold_key):
                time.sleep(0.01)
                continue
            
            # Cooldown check
            now = time.time()
            if now - self.last_shot_time < self.cooldown:
                time.sleep(0.01)
                continue
            
            # Fast center check
            size = CFG.triggerbot.pixel_check * 5
            confidence = self.detector.check_purple_at_center(size)
            
            if confidence > CFG.triggerbot.confidence:
                # Humanized delay before tap
                human_delay(
                    CFG.triggerbot.delay_min_ms,
                    CFG.triggerbot.delay_max_ms
                )
                
                # Single tap
                self.mouse.click(Button.left)
                self.last_shot_time = time.time()
                
                # Random cooldown for next shot
                self.cooldown = random.uniform(
                    CFG.triggerbot.cooldown_min,
                    CFG.triggerbot.cooldown_max
                )
            
            time.sleep(0.005)  # Very fast polling

