import importlib
import importlib.util
import pkgutil
import sys
from pathlib import Path

import mousemover.plugins as builtin_plugins
from .paths import external_plugins_dir


def _instantiate(module):
    cls = getattr(module, "MovementPlugin", None)
    if cls is None:
        return None
    instance = cls()
    if not getattr(instance, "name", None):
        return None
    return instance


def load_plugins() -> dict[str, object]:
    result = {}

    importlib.invalidate_caches()

    # Built-ins bundled with the application.
    prefix = builtin_plugins.__name__ + "."
    for info in pkgutil.iter_modules(builtin_plugins.__path__, prefix):
        module = sys.modules.get(info.name)
        if module is not None:
            module = importlib.reload(module)
        else:
            module = importlib.import_module(info.name)

        plugin = _instantiate(module)
        if plugin:
            result[plugin.name] = plugin

    # Optional .py plugins beside the executable in ./plugins.
    ext_dir = external_plugins_dir()
    ext_dir.mkdir(exist_ok=True)

    for path in sorted(ext_dir.glob("*.py")):
        if path.name.startswith("_"):
            continue

        module_name = f"mousemover_external_{path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            continue

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        plugin = _instantiate(module)
        if plugin:
            # External plugin with same name intentionally overrides built-in.
            result[plugin.name] = plugin

    return dict(sorted(result.items()))
