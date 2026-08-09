import threading
import time
from pynput import keyboard, mouse


class GlobalInputHooks:
    def __init__(self, logger):
        self.logger = logger
        self.kill_event = threading.Event()
        self.pause_event = threading.Event()
        self.resume_event = threading.Event()
        self.user_mouse_event = threading.Event()

        self._internal_lock = threading.Lock()
        self._ignore_mouse_until = 0.0
        self.last_user_activity = time.monotonic()

        self.keyboard_listener = keyboard.GlobalHotKeys({
            "<ctrl>+<shift>+<f9>": self.pause,
            "<ctrl>+<shift>+<f10>": self.resume,
            "<ctrl>+<shift>+<f12>": self.stop_loop,
            "<esc>": self.kill,
        })

        self.mouse_listener = mouse.Listener(on_move=self._on_move)

    def start(self):
        self.keyboard_listener.start()
        self.mouse_listener.start()

    def stop(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()

    def mark_internal_movement(self, seconds: float = 0.75):
        with self._internal_lock:
            self._ignore_mouse_until = max(
                self._ignore_mouse_until,
                time.monotonic() + seconds,
            )

    def _on_move(self, x, y):
        now = time.monotonic()
        with self._internal_lock:
            if now <= self._ignore_mouse_until:
                return

        self.last_user_activity = now
        self.user_mouse_event.set()

    def clear_user_mouse_event(self):
        self.user_mouse_event.clear()

    def pause(self):
        self.logger.info("Ctrl+Shift+F9: pausa solicitada.")
        self.pause_event.set()

    def resume(self):
        self.logger.info("Ctrl+Shift+F10: continuar solicitado.")
        self.resume_event.set()

    def stop_loop(self):
        self.logger.info("Ctrl+Shift+F12: parada do loop solicitada.")
        self.pause_event.set()

    def kill(self):
        self.logger.warning("ESC: encerramento global solicitado.")
        self.kill_event.set()
        self.pause_event.set()
        self.resume_event.set()
