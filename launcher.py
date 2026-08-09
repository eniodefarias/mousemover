import os
import sys


def _hide_windows_console():
    if sys.platform != "win32":
        return
    try:
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def main():
    if len(sys.argv) == 1:
        _hide_windows_console()
        from mousemover.gui import main as gui_main
        return gui_main()

    from mousemover.cli import main as cli_main
    return cli_main()


if __name__ == "__main__":
    raise SystemExit(main())
