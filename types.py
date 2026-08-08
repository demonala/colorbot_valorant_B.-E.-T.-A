"""
types.py — Jugs's v3 Type Definitions
Clean dataclasses for targets and detection results.
"""
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class Target:
    """Detected enemy target with all metadata."""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    center: Tuple[int, int]
    aspect_ratio: float
    area: int
    
    @property
    def cx(self) -> int:
        """Center X."""
        return self.center[0]
    
    @property
    def cy(self) -> int:
        """Center Y."""
        return self.center[1]


@dataclass
class DetectionResult:
    """Result of a detection pass."""
    targets: list
    frame: Optional[object] = None  # numpy array, kept for debug
    
    @property
    def best_target(self) -> Optional[Target]:
        """Closest target to crosshair (already sorted)."""
        return self.targets[0] if self.targets else None
    
    @property
    def count(self) -> int:
        return len(self.targets)
 
