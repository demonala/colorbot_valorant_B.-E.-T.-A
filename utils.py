"""
utils.py — Jugs's v3 Utilities
"""
import math
import random
import time
from typing import Tuple


def distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Euclidean distance."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def smoothstep(t: float) -> float:
    """Smoothstep easing for human-like acceleration."""
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def jitter(magnitude: float = 1.5) -> Tuple[float, float]:
    """Random offset for human imperfection."""
    return (random.uniform(-magnitude, magnitude), 
            random.uniform(-magnitude, magnitude))


def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp value to range."""
    return max(lo, min(hi, value))


def calc_movement(
    target: Tuple[int, int],
    current: Tuple[int, int],
    strength: float,
    smooth: float,
    y_offset: int = 0,
    randomize: bool = True
) -> Tuple[int, int]:
    """
    Calculate mouse movement delta.
    Uses smoothstep for acceleration curves.
    """
    tx, ty = target
    cx, cy = current
    ty += y_offset
    
    dx = tx - cx
    dy = ty - cy
    dist = math.sqrt(dx * dx + dy * dy)
    
    if dist < 1:
        return (0, 0)
    
    # Apply strength
    mx = dx * strength
    my = dy * strength
    
    # Smoothstep easing
    t = clamp(1.0 / smooth, 0.01, 1.0)
    eased = smoothstep(t)
    mx *= eased
    my *= eased
    
    # Human jitter
    if randomize:
        jx, jy = jitter(1.2)
        mx += jx
        my += jy
    
    return (int(round(mx)), int(round(my)))


def human_delay(min_ms: int, max_ms: int) -> None:
    """Sleep for randomized human-like duration."""
    time.sleep(random.uniform(min_ms, max_ms) / 1000.0)


def now_ms() -> int:
    """Current time in milliseconds."""
    return int(time.time() * 1000)

