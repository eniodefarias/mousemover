import sys
from pathlib import Path


def app_dir() -> Path:
    """Writable directory beside the executable/script."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path.cwd()


def package_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def log_path() -> Path:
    return app_dir() / "debug.log"


def ini_path() -> Path:
    return app_dir() / "config.ini"


def json_path() -> Path:
    return app_dir() / "config.json"


def external_plugins_dir() -> Path:
    return app_dir() / "plugins"
