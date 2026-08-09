import logging
import queue
import tkinter as tk
from tkinter import ttk, messagebox

import pyautogui

from .core.config import merged_config, save_ini_state
from .core.engine import Engine
from .core.input_hooks import GlobalInputHooks
from .core.logger import build_logger
from .core.monitors import monitors, monitor_description
from .core.plugin_loader import load_plugins
from .core.single_instance import SingleInstance


class QueueLogHandler(logging.Handler):
    def __init__(self, q):
        super().__init__()
        self.q = q

    def emit(self, record):
        self.q.put(self.format(record))


class MouseMoverGUI(tk.Tk):
    def __init__(self, config, lock):
        super().__init__()
        self.lock = lock
        self.config = config

        self.title("MouseMover")
        self.geometry("800x720")
        self.minsize(700, 620)

        self.logger = build_logger(False, config.log_level)
        self.log_queue = queue.Queue()
        handler = QueueLogHandler(self.log_queue)
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
        self.logger.addHandler(handler)

        self.hooks = GlobalInputHooks(self.logger)
        self.hooks.start()
        self.engine = Engine(config, self.hooks, self.logger)

        self.protocol("WM_DELETE_WINDOW", self.close_app)

        self._vars()
        self._build()
        self.reload_monitors()
        self.reload_plugins()
        self.after(100, self._drain_logs)
        self.after(100, self._watch_kill)
        self.after(100, self._watch_resume)

    def _vars(self):
        self.monitor_var = tk.StringVar()
        self.plugin_var = tk.StringVar(value=self.config.plugin)
        self.interval_var = tk.DoubleVar(value=self.config.interval)
        self.jitter_min_var = tk.IntVar(value=self.config.jitter_min)
        self.jitter_max_var = tk.IntVar(value=self.config.jitter_max)
        self.watchdog_var = tk.DoubleVar(value=self.config.watchdog)
        self.mouse_hook_var = tk.BooleanVar(value=self.config.mouse_hook)
        self.once_var = tk.BooleanVar(value=self.config.once)
        self.headless_var = tk.BooleanVar(value=self.config.headless)
        self.force_var = tk.BooleanVar(value=self.config.force)
        self.background_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Parado")

    def _build(self):
        main = ttk.Frame(self, padding=14)
        main.pack(fill="both", expand=True)

        mframe = ttk.LabelFrame(main, text="Monitor", padding=8)
        mframe.pack(fill="x", pady=4)
        self.monitor_combo = ttk.Combobox(mframe, textvariable=self.monitor_var, state="readonly")
        self.monitor_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(mframe, text="Atualizar", command=self.reload_monitors).pack(side="left", padx=5)
        ttk.Button(mframe, text="Testar", command=self.test_monitor).pack(side="left")

        pframe = ttk.LabelFrame(main, text="Plugin de movimento", padding=8)
        pframe.pack(fill="x", pady=4)
        self.plugin_combo = ttk.Combobox(pframe, textvariable=self.plugin_var, state="readonly")
        self.plugin_combo.pack(side="left", fill="x", expand=True)
        ttk.Button(pframe, text="Reload plugins", command=self.reload_plugins).pack(side="left", padx=5)

        values = ttk.LabelFrame(main, text="Parâmetros", padding=8)
        values.pack(fill="x", pady=4)
        self._spin(values, "Intervalo (s)", self.interval_var, 0.1, 3600, 0)
        self._spin(values, "Jitter mínimo (px)", self.jitter_min_var, 0, 100, 1)
        self._spin(values, "Jitter máximo (px)", self.jitter_max_var, 0, 100, 2)
        self._spin(values, "Watchdog (s)", self.watchdog_var, 0.1, 120, 3)

        flags = ttk.LabelFrame(main, text="Opções", padding=8)
        flags.pack(fill="x", pady=4)
        ttk.Checkbutton(flags, text="Sensor global de movimento do mouse", variable=self.mouse_hook_var).grid(row=0, column=0, sticky="w")
        ttk.Checkbutton(flags, text="Executar apenas um ciclo (--once)", variable=self.once_var).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(flags, text="Headless / sem console (--headless)", variable=self.headless_var).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(flags, text="Ignorar INI/JSON (--force)", variable=self.force_var).grid(row=3, column=0, sticky="w")
        ttk.Checkbutton(flags, text="Ocultar janela ao iniciar", variable=self.background_var).grid(row=4, column=0, sticky="w")

        ttk.Label(
            main,
            text="Ctrl+Shift+F9 = pausar | Ctrl+Shift+F10 = continuar | "
                 "Ctrl+Shift+F12 = parar | ESC = encerrar aplicativo",
        ).pack(fill="x", pady=7)

        buttons = ttk.Frame(main)
        buttons.pack(fill="x", pady=6)
        ttk.Button(buttons, text="Iniciar", command=self.start).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(buttons, text="Parar", command=self.stop).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(buttons, text="Sair", command=self.close_app).pack(side="left", fill="x", expand=True, padx=2)

        ttk.Label(main, textvariable=self.status_var).pack(anchor="w", pady=4)

        logframe = ttk.LabelFrame(main, text="Log", padding=5)
        logframe.pack(fill="both", expand=True)
        self.log_text = tk.Text(logframe, state="disabled", height=14)
        scroll = ttk.Scrollbar(logframe, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scroll.set)
        self.log_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _spin(self, parent, text, var, low, high, row):
        ttk.Label(parent, text=text).grid(row=row, column=0, sticky="w", padx=5, pady=3)
        ttk.Spinbox(parent, from_=low, to=high, textvariable=var, width=12).grid(row=row, column=1, sticky="w", padx=5)

    def reload_monitors(self):
        self._monitors = monitors()
        values = [monitor_description(i, m) for i, m in enumerate(self._monitors)]
        self.monitor_combo["values"] = values
        idx = min(max(self.config.monitor, 0), max(len(values) - 1, 0))
        if values:
            self.monitor_combo.current(idx)

    def reload_plugins(self):
        try:
            plugins = self.engine.reload_plugins()
            names = list(plugins)
            self.plugin_combo["values"] = names
            if self.plugin_var.get() not in names:
                self.plugin_var.set("nudge_inteligente" if "nudge_inteligente" in names else names[0])
        except Exception as exc:
            messagebox.showerror("Plugins", str(exc))

    def _apply_form(self):
        idx = self.monitor_combo.current()
        if idx < 0:
            raise ValueError("Selecione um monitor.")
        if self.jitter_min_var.get() > self.jitter_max_var.get():
            raise ValueError("Jitter mínimo não pode ser maior que o máximo.")

        self.config.monitor = idx
        self.config.plugin = self.plugin_var.get()
        self.config.interval = float(self.interval_var.get())
        self.config.jitter_min = int(self.jitter_min_var.get())
        self.config.jitter_max = int(self.jitter_max_var.get())
        self.config.watchdog = float(self.watchdog_var.get())
        self.config.mouse_hook = bool(self.mouse_hook_var.get())
        self.config.once = bool(self.once_var.get())
        self.config.headless = bool(self.headless_var.get())
        self.config.force = bool(self.force_var.get())

        self.engine.select_monitor(idx)
        self.engine.select_plugin(self.config.plugin)
        self.engine.config = self.config
        save_ini_state(self.config)

    def test_monitor(self):
        try:
            self._apply_form()
            m = self.engine.monitor
            x, y = m.x + m.width // 2, m.y + m.height // 2
            self.hooks.mark_internal_movement(1.0)
            pyautogui.moveTo(x, y, duration=0.3)
            self.logger.info("Teste monitor %d: centro=(%d,%d)", self.config.monitor, x, y)
        except Exception as exc:
            messagebox.showerror("Teste", str(exc))

    def start(self):
        if self.engine.running:
            return
        try:
            self._apply_form()
            self.hooks.pause_event.clear()
            self.hooks.clear_user_mouse_event()
            self.status_var.set("Executando")
            self.engine.start_background(self._engine_finished)
            if self.background_var.get():
                self.withdraw()
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def stop(self):
        self.hooks.pause_event.set()
        self.status_var.set("Parando...")

    def _engine_finished(self, reason):
        self.after(0, lambda: self._finished_ui(reason))

    def _finished_ui(self, reason):
        self.status_var.set(f"Parado ({reason})")
        if not self.hooks.kill_event.is_set():
            self.deiconify()

    def _watch_resume(self):
        if self.hooks.resume_event.is_set() and not self.engine.running and not self.hooks.kill_event.is_set():
            self.hooks.resume_event.clear()
            self.hooks.pause_event.clear()
            self.hooks.clear_user_mouse_event()
            self.status_var.set("Executando")
            self.engine.start_background(self._engine_finished)
        self.after(100, self._watch_resume)

    def _watch_kill(self):
        if self.hooks.kill_event.is_set():
            self.close_app()
            return
        self.after(100, self._watch_kill)

    def _drain_logs(self):
        try:
            while True:
                line = self.log_queue.get_nowait()
                self.log_text.configure(state="normal")
                self.log_text.insert("end", line + "\n")
                self.log_text.see("end")
                self.log_text.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self._drain_logs)

    def close_app(self):
        try:
            self.hooks.kill_event.set()
            self.hooks.stop()
        finally:
            self.lock.release()
            self.destroy()


def main():
    lock = SingleInstance()
    try:
        lock.acquire()
    except RuntimeError as exc:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("MouseMover", str(exc))
        root.destroy()
        return 1

    config = merged_config()
    app = MouseMoverGUI(config, lock)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
