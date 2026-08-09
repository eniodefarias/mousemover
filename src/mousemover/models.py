from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AppConfig:
    plugin: str = "nudge_inteligente"
    monitor: int = 0
    interval: float = 30.0
    jitter_min: int = 1
    jitter_max: int = 10
    watchdog: float = 3.0
    mouse_hook: bool = False
    once: bool = False
    headless: bool = False
    force: bool = False
    daemon: bool = False
    log_level: str = "info"
    keep_awake: bool = False


@dataclass
class MovementContext:
    monitor: object
    interval: float
    jitter_min: int
    jitter_max: int
    last_user_activity: float
    now: float
    current_x: int
    current_y: int

    @property
    def center_x(self) -> int:
        return self.monitor.x + self.monitor.width // 2

    @property
    def center_y(self) -> int:
        return self.monitor.y + self.monitor.height // 2
