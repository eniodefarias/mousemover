import argparse
import sys
import time

from .core.config import merged_config, save_ini_state
from .core.engine import Engine
from .core.input_hooks import GlobalInputHooks
from .core.logger import build_logger
from .core.monitors import monitors, monitor_description
from .core.plugin_loader import load_plugins
from .core.single_instance import SingleInstance


def build_parser():
    p = argparse.ArgumentParser(
        prog="mousemover",
        description="MouseMover - automação de mouse com CLI, GUI e plugins.",
    )
    p.add_argument("--plugin", help="Nome do plugin de movimento.")
    p.add_argument("--monitor", type=int, help="Índice do monitor.")
    hook = p.add_mutually_exclusive_group()
    hook.add_argument("--mouse-hook", dest="mouse_hook", action="store_true")
    hook.add_argument("--no-mouse-hook", dest="mouse_hook", action="store_false")
    p.set_defaults(mouse_hook=None)

    p.add_argument("--interval", type=float, help="Intervalo em segundos.")
    p.add_argument("--jitter-min", type=int, help="Jitter mínimo em pixels.")
    p.add_argument("--jitter-max", type=int, help="Jitter máximo em pixels.")
    p.add_argument("--watchdog", type=float, help="Timeout do watchdog.")
    p.add_argument("--daemon", action="store_true", default=None, help="Executa sem menu.")
    p.add_argument("--headless", action="store_true", default=None, help="Não imprime logs no console.")
    p.add_argument("--once", action="store_true", default=None, help="Executa um ciclo.")
    p.add_argument("--force", action="store_true", help="Ignora config.ini/config.json.")
    p.add_argument("--log-level", choices=["debug", "info", "warning", "error"])
    p.add_argument("--list-plugins", action="store_true", help="Lista plugins e sai.")
    p.add_argument("--list-monitors", action="store_true", help="Lista monitores e sai.")
    return p


def _overrides(args):
    return {
        "plugin": args.plugin,
        "monitor": args.monitor,
        "mouse_hook": args.mouse_hook,
        "interval": args.interval,
        "jitter_min": args.jitter_min,
        "jitter_max": args.jitter_max,
        "watchdog": args.watchdog,
        "daemon": args.daemon,
        "headless": args.headless,
        "once": args.once,
        "log_level": args.log_level,
    }


def interactive_menu(config, hooks, logger):
    engine = Engine(config, hooks, logger)

    while not hooks.kill_event.is_set():
        print("\n=== MouseMover ===")
        print(f"Monitor : {config.monitor}")
        print(f"Plugin  : {config.plugin}")
        print(f"Mouse hook: {'ATIVADO' if config.mouse_hook else 'DESATIVADO'}")
        print("1 = sair")
        print("2 = iniciar loop")
        print("3 = escolher monitor")
        print("4 = testar monitor")
        print("5 = alternar sensor global do mouse")
        print("6 = selecionar/recarregar plugin")
        choice = input("> ").strip()

        if choice == "1":
            return

        if choice == "2":
            hooks.pause_event.clear()
            hooks.clear_user_mouse_event()
            reason = engine.run()

            # F10 can resume without going back through configuration.
            while not hooks.kill_event.is_set():
                if reason == "pause":
                    break
                if hooks.resume_event.is_set():
                    hooks.resume_event.clear()
                    hooks.pause_event.clear()
                    reason = engine.run()
                    continue
                break
            continue

        if choice == "3":
            mons = monitors()
            for i, m in enumerate(mons):
                print(monitor_description(i, m))
            selected = input("Monitor: ").strip()
            if selected.isdigit():
                engine.select_monitor(int(selected))
                config.monitor = int(selected)
                save_ini_state(config)
            continue

        if choice == "4":
            m = engine.monitor
            x = m.x + m.width // 2
            y = m.y + m.height // 2
            hooks.mark_internal_movement(1.0)
            import pyautogui
            pyautogui.moveTo(x, y, duration=0.3)
            logger.info("Teste: centro do monitor %d = (%d,%d)", config.monitor, x, y)
            continue

        if choice == "5":
            config.mouse_hook = not config.mouse_hook
            save_ini_state(config)
            logger.info("Mouse hook=%s", config.mouse_hook)
            continue

        if choice == "6":
            plugins = engine.reload_plugins()
            names = list(plugins)
            for i, name in enumerate(names):
                print(f"{i} = {name}")
            selected = input("Plugin: ").strip()
            if selected.isdigit() and int(selected) < len(names):
                engine.select_plugin(names[int(selected)])
                config.plugin = names[int(selected)]
                save_ini_state(config)
            continue


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.list_plugins:
        for name in load_plugins():
            print(name)
        return 0

    if args.list_monitors:
        for i, m in enumerate(monitors()):
            print(monitor_description(i, m))
        return 0

    config = merged_config(_overrides(args), force=args.force)
    logger = build_logger(config.headless, config.log_level)

    try:
        with SingleInstance():
            hooks = GlobalInputHooks(logger)
            hooks.start()
            try:
                if config.daemon:
                    engine = Engine(config, hooks, logger)
                    reason = engine.run()
                    logger.info("Finalizado: %s", reason)
                else:
                    interactive_menu(config, hooks, logger)
            finally:
                hooks.stop()
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
