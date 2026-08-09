import configparser
import json
from dataclasses import fields
from pathlib import Path

from mousemover.models import AppConfig
from .paths import ini_path, json_path


DEFAULTS = AppConfig()


def load_json_config() -> dict:
    path = json_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_ini_state() -> dict:
    path = ini_path()
    if not path.exists():
        return {}
    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    if not parser.has_section("state"):
        return {}

    result = {}
    section = parser["state"]

    if "monitor_index" in section:
        result["monitor"] = section.getint("monitor_index", fallback=0)
    if "plugin" in section:
        result["plugin"] = section.get("plugin", fallback=DEFAULTS.plugin)
    if "mouse_hook" in section:
        result["mouse_hook"] = section.getboolean("mouse_hook", fallback=False)

    return result


def save_ini_state(config: AppConfig) -> None:
    parser = configparser.ConfigParser()
    parser["state"] = {
        "monitor_index": str(config.monitor),
        "plugin": config.plugin,
        "mouse_hook": str(config.mouse_hook).lower(),
    }
    with open(ini_path(), "w", encoding="utf-8") as fp:
        parser.write(fp)


def merged_config(cli_overrides: dict | None = None, force: bool = False) -> AppConfig:
    values = {
        "plugin": DEFAULTS.plugin,
        "monitor": DEFAULTS.monitor,
        "interval": DEFAULTS.interval,
        "jitter_min": DEFAULTS.jitter_min,
        "jitter_max": DEFAULTS.jitter_max,
        "watchdog": DEFAULTS.watchdog,
        "mouse_hook": DEFAULTS.mouse_hook,
        "keep_awake": DEFAULTS.keep_awake,
        "once": DEFAULTS.once,
        "headless": DEFAULTS.headless,
        "force": force,
        "daemon": DEFAULTS.daemon,
        "log_level": DEFAULTS.log_level,
    }

    if not force:
        raw_json = load_json_config()
        json_map = {
            "movement_plugin": "plugin",
            "monitor_index": "monitor",
            "interval_seconds": "interval",
            "jitter_min": "jitter_min",
            "jitter_max": "jitter_max",
            "watchdog_timeout": "watchdog",
            "mouse_hook": "mouse_hook",
            "keep_awake": "keep_awake",
            "log_level": "log_level",
        }
        for src, dst in json_map.items():
            if src in raw_json:
                values[dst] = raw_json[src]

        values.update(load_ini_state())

    if cli_overrides:
        values.update({k: v for k, v in cli_overrides.items() if v is not None})

    return AppConfig(**values)
