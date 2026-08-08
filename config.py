"""
config.py — Jugs's v3.1 Final Config
Toggle-only, no hold keys.
"""
import json
import os
from dataclasses import dataclass, asdict, field
from typing import List


@dataclass
class ColorConfig:
    lower_hsv: List[int] = field(default_factory=lambda: [130, 60, 180])
    upper_hsv: List[int] = field(default_factory=lambda: [170, 255, 255])
    mode: str = "hsv"


@dataclass
class DetectionConfig:
    min_contour_area: int = 25
    max_contour_area: int = 6000
    threshold: float = 0.5
    min_aspect: float = 0.35


@dataclass
class AimbotConfig:
    enabled: bool = False
    toggle_key: str = "f2"
    fov: int = 140
    smooth: float = 4.0
    strength: float = 0.35
    deadzone: int = 6
    y_offset: int = -18
    randomize: bool = True


@dataclass
class TriggerbotConfig:
    enabled: bool = False
    toggle_key: str = "f5"
    delay_min_ms: int = 55
    delay_max_ms: int = 130
    pixel_check: int = 4
    confidence: float = 0.8
    cooldown_min: float = 0.4
    cooldown_max: float = 0.7


@dataclass
class UIConfig:
    theme: str = "dark"
    opacity: float = 0.92
    show_fps: bool = True


@dataclass
class AppConfig:
    color: ColorConfig = field(default_factory=ColorConfig)
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    aimbot: AimbotConfig = field(default_factory=AimbotConfig)
    triggerbot: TriggerbotConfig = field(default_factory=TriggerbotConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    capture_fps: int = 144
    monitor_index: int = 1


CONFIG_PATH = "jugs_config_v3.json"


def load_config(path: str = CONFIG_PATH) -> AppConfig:
    if not os.path.exists(path):
        return AppConfig()
    try:
        with open(path, "r") as f:
            data = json.load(f)
        return AppConfig(
            color=ColorConfig(**data.get("color", {})),
            detection=DetectionConfig(**data.get("detection", {})),
            aimbot=AimbotConfig(**data.get("aimbot", {})),
            triggerbot=TriggerbotConfig(**data.get("triggerbot", {})),
            ui=UIConfig(**data.get("ui", {})),
            capture_fps=data.get("capture_fps", 144),
            monitor_index=data.get("monitor_index", 1),
        )
    except Exception as e:
        print(f"[CONFIG] Load failed ({e}), using defaults.")
        return AppConfig()


def save_config(cfg: AppConfig, path: str = CONFIG_PATH) -> None:
    data = {
        "color": asdict(cfg.color),
        "detection": asdict(cfg.detection),
        "aimbot": asdict(cfg.aimbot),
        "triggerbot": asdict(cfg.triggerbot),
        "ui": asdict(cfg.ui),
        "capture_fps": cfg.capture_fps,
        "monitor_index": cfg.monitor_index,
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


CFG = load_config()
