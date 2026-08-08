#!/usr/bin/env python3
"""
ui.py — Jugs's Colorbot v3.1 Control Panel
Dark theme, custom styling, live status, no bullshit.
"""
import tkinter as tk
from tkinter import ttk
import keyboard as kb
import time
import threading
from config import CFG, save_config
from capture import ScreenCapture
from detector import PurpleDetector
from aimbot import Aimbot
from triggerbot import Triggerbot


class JugsTheme:
    """Jugs's color palette — dark, purple accent, gritty."""
    BG = "#0a0a0f"
    PANEL = "#12121a"
    PANEL_HOVER = "#1a1a25"
    BORDER = "#2a2a3a"
    FG = "#c8c8d4"
    FG_DIM = "#6b6b7b"
    ACCENT = "#a855f7"       # Purple
    ACCENT_GLOW = "#c084fc"
    ACCENT_DARK = "#7c3aed"
    GREEN = "#22c55e"
    GREEN_DIM = "#15803d"
    RED = "#ef4444"
    RED_DIM = "#991b1b"
    YELLOW = "#eab308"
    ORANGE = "#f97316"


class StatusIndicator:
    """Animated status dot with label."""

    def __init__(self, parent):
        self.parent = parent
        self.canvas = tk.Canvas(parent, width=14, height=14, bg=JugsTheme.BG,
                                highlightthickness=0)
        self.canvas.pack(side="right", padx=(0, 8))
        self.dot = self.canvas.create_oval(3, 3, 11, 11, fill=JugsTheme.RED_DIM, outline="")

        self.label = tk.Label(parent, text="IDLE", font=("Consolas", 10, "bold"),
                             bg=JugsTheme.BG, fg=JugsTheme.RED)
        self.label.pack(side="right")

        self._pulse = 0
        self._pulse_id = None

    def set(self, text, color, pulse=False):
        self.label.config(text=text, fg=color)
        self.canvas.itemconfig(self.dot, fill=color)

        if self._pulse_id:
            self.parent.after_cancel(self._pulse_id)
            self._pulse_id = None

        if pulse:
            self._pulse = 0
            self._do_pulse(color)

    def _do_pulse(self, base_color):
        self._pulse = (self._pulse + 1) % 20
        brightness = 0.7 + 0.3 * abs(self._pulse - 10) / 10

        # Simple pulse by toggling between color and dim
        if self._pulse < 10:
            self.canvas.itemconfig(self.dot, fill=base_color)
        else:
            self.canvas.itemconfig(self.dot, fill=self._dim_color(base_color))

        self._pulse_id = self.parent.after(50, lambda: self._do_pulse(base_color))

    def _dim_color(self, hex_color):
        # Return a dimmed version
        dim_map = {
            JugsTheme.GREEN: JugsTheme.GREEN_DIM,
            JugsTheme.RED: JugsTheme.RED_DIM,
            JugsTheme.ACCENT: JugsTheme.ACCENT_DARK,
        }
        return dim_map.get(hex_color, hex_color)


class ModeButton:
    """Big mode toggle button with icon and status."""

    def __init__(self, parent, name, hotkey, icon, on_toggle):
        self.parent = parent
        self.name = name
        self.hotkey = hotkey
        self.icon = icon
        self.on_toggle = on_toggle
        self.active = False

        self.frame = tk.Frame(parent, bg=JugsTheme.PANEL, bd=1,
                             relief="solid", highlightbackground=JugsTheme.BORDER)
        self.frame.pack(fill="x", padx=12, pady=6)

        # Top row: icon + name + hotkey
        top = tk.Frame(self.frame, bg=JugsTheme.PANEL)
        top.pack(fill="x", padx=10, pady=(8, 2))

        self.icon_lbl = tk.Label(top, text=icon, font=("Segoe UI", 16),
                                bg=JugsTheme.PANEL, fg=JugsTheme.FG_DIM)
        self.icon_lbl.pack(side="left")

        self.name_lbl = tk.Label(top, text=name, font=("Consolas", 12, "bold"),
                                bg=JugsTheme.PANEL, fg=JugsTheme.FG)
        self.name_lbl.pack(side="left", padx=(8, 0))

        self.key_lbl = tk.Label(top, text=f"[{hotkey.upper()}]", font=("Consolas", 9),
                               bg=JugsTheme.PANEL, fg=JugsTheme.ACCENT)
        self.key_lbl.pack(side="right")

        # Status line
        self.status_lbl = tk.Label(self.frame, text="OFF", font=("Consolas", 9),
                                    bg=JugsTheme.PANEL, fg=JugsTheme.RED)
        self.status_lbl.pack(anchor="w", padx=10, pady=(0, 4))

        # Description
        self.desc_lbl = tk.Label(self.frame, text="", font=("Consolas", 8),
                                  bg=JugsTheme.PANEL, fg=JugsTheme.FG_DIM)
        self.desc_lbl.pack(anchor="w", padx=10, pady=(0, 8))

        # Click to toggle
        self.frame.bind("<Button-1>", lambda e: self.on_toggle())
        for child in self.frame.winfo_children():
            child.bind("<Button-1>", lambda e: self.on_toggle())

        # Hover effect
        self.frame.bind("<Enter>", self._on_enter)
        self.frame.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.frame.config(bg=JugsTheme.PANEL_HOVER)
        for child in self.frame.winfo_children():
            child.config(bg=JugsTheme.PANEL_HOVER)

    def _on_leave(self, e):
        self.frame.config(bg=JugsTheme.PANEL)
        for child in self.frame.winfo_children():
            child.config(bg=JugsTheme.PANEL)

    def set_active(self, active, desc=""):
        self.active = active
        if active:
            self.frame.config(highlightbackground=JugsTheme.ACCENT)
            self.icon_lbl.config(fg=JugsTheme.ACCENT_GLOW)
            self.status_lbl.config(text="ACTIVE", fg=JugsTheme.GREEN)
            self.name_lbl.config(fg=JugsTheme.ACCENT_GLOW)
        else:
            self.frame.config(highlightbackground=JugsTheme.BORDER)
            self.icon_lbl.config(fg=JugsTheme.FG_DIM)
            self.status_lbl.config(text="OFF", fg=JugsTheme.RED)
            self.name_lbl.config(fg=JugsTheme.FG)

        if desc:
            self.desc_lbl.config(text=desc)


class JugsSlider:
    """Custom styled slider with value display."""

    def __init__(self, parent, label, default, min_v, max_v, callback,
                 is_float=False, res=1.0, width=14):
        self.callback = callback
        self.is_float = is_float

        frm = tk.Frame(parent, bg=JugsTheme.PANEL)
        frm.pack(fill="x", padx=10, pady=4)

        tk.Label(frm, text=label, font=("Consolas", 9),
                bg=JugsTheme.PANEL, fg=JugsTheme.FG,
                width=width, anchor="w").pack(side="left")

        self.val_lbl = tk.Label(frm, text=f"{default:.2f}" if is_float else str(default),
                                 font=("Consolas", 9, "bold"),
                                 bg=JugsTheme.PANEL, fg=JugsTheme.ACCENT, width=8)
        self.val_lbl.pack(side="right")

        # Custom styled scale
        self.scale = tk.Scale(
            frm, from_=min_v, to=max_v, resolution=res,
            orient="horizontal", bg=JugsTheme.PANEL, fg=JugsTheme.FG,
            highlightthickness=0, bd=0, troughcolor=JugsTheme.BORDER,
            activebackground=JugsTheme.ACCENT, showvalue=0,
            sliderlength=16, sliderrelief="flat",
            command=self._on_change
        )
        self.scale.set(default)
        self.scale.pack(fill="x", padx=(6, 0), pady=(0, 2))

    def _on_change(self, val):
        v = float(val) if self.is_float else int(float(val))
        self.val_lbl.config(text=f"{v:.2f}" if self.is_float else str(v))
        self.callback(v)


class JugsUI:
    """Jugs's main control panel."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jugs's Colorbot v3.1")
        self.root.geometry("460x720")
        self.root.resizable(False, False)
        self.root.attributes("-alpha", CFG.ui.opacity)
        self.root.configure(bg=JugsTheme.BG)
        self.root.attributes("-topmost", True)

        # Core systems
        self.capture = ScreenCapture()
        self.detector = PurpleDetector(self.capture)
        self.aimbot = Aimbot(self.capture, self.detector)
        self.triggerbot = Triggerbot(self.capture, self.detector)

        self.aimbot.start()
        self.triggerbot.start()

        # FPS tracking
        self.frame_count = 0
        self.fps = 0
        self.last_fps_time = time.time()

        # Register hotkeys
        self._register_hotkeys()

        # Build UI
        self._build_ui()

        # Start loops
        self._fps_loop()
        self._status_loop()

    def _register_hotkeys(self):
        try:
            kb.add_hotkey(CFG.aimbot.toggle_key, self._hotkey_aim)
            kb.add_hotkey(CFG.triggerbot.toggle_key, self._hotkey_trig)
            kb.add_hotkey("f12", self._shutdown)
        except Exception as e:
            print(f"[HOTKEY] Warning: {e}")

    def _hotkey_aim(self):
        self.root.after(0, self._toggle_aim)

    def _hotkey_trig(self):
        self.root.after(0, self._toggle_trig)

    def _shutdown(self):
        self.root.after(0, self._quit)

    def _build_ui(self):
        # ===== HEADER =====
        hdr = tk.Frame(self.root, bg=JugsTheme.BG, height=55)
        hdr.pack(fill="x", padx=16, pady=(16, 8))

        # Jugs branding
        brand = tk.Frame(hdr, bg=JugsTheme.BG)
        brand.pack(side="left")

        tk.Label(brand, text="◈", font=("Segoe UI", 18),
                bg=JugsTheme.BG, fg=JugsTheme.ACCENT).pack(side="left")

        title_frame = tk.Frame(brand, bg=JugsTheme.BG)
        title_frame.pack(side="left", padx=(6, 0))

        tk.Label(title_frame, text="JUGS'S COLORBOT", font=("Consolas", 14, "bold"),
                bg=JugsTheme.BG, fg=JugsTheme.ACCENT_GLOW).pack(anchor="w")
        tk.Label(title_frame, text="v3.1  //  EXTERNAL PIXEL BOT", font=("Consolas", 7),
                bg=JugsTheme.BG, fg=JugsTheme.FG_DIM).pack(anchor="w")

        self.status = StatusIndicator(hdr)

        # ===== STRATEGY INDICATOR =====
        strat_bar = tk.Frame(self.root, bg=JugsTheme.PANEL, bd=1,
                            relief="solid", highlightbackground=JugsTheme.BORDER)
        strat_bar.pack(fill="x", padx=16, pady=(0, 8))

        self.strat_lbl = tk.Label(strat_bar, text="HSV: PRIMARY",
                                  font=("Consolas", 9),
                                  bg=JugsTheme.PANEL, fg=JugsTheme.ACCENT)
        self.strat_lbl.pack(anchor="w", padx=10, pady=6)

        # ===== MODE BUTTONS =====
        tk.Label(self.root, text="MODES", font=("Consolas", 9, "bold"),
                bg=JugsTheme.BG, fg=JugsTheme.FG_DIM).pack(anchor="w", padx=16, pady=(4, 2))

        self.aim_btn = ModeButton(
            self.root, "AIMBOT", CFG.aimbot.toggle_key, "🔒",
            self._toggle_aim
        )
        self.aim_btn.set_active(False, "Locks onto enemy. Does NOT shoot.")

        self.trig_btn = ModeButton(
            self.root, "TRIGGERBOT", CFG.triggerbot.toggle_key, "🔫",
            self._toggle_trig
        )
        self.trig_btn.set_active(False, "Auto-tap on crosshair. Sniper/Guardian only.")

        # ===== AIMBOT SETTINGS =====
        aim_panel = tk.LabelFrame(self.root, text=" AIMBOT ", font=("Consolas", 9, "bold"),
                                 bg=JugsTheme.PANEL, fg=JugsTheme.ACCENT,
                                 bd=1, relief="solid", highlightbackground=JugsTheme.BORDER)
        aim_panel.pack(fill="x", padx=16, pady=8)
        aim_panel.configure(labelanchor="n")

        JugsSlider(aim_panel, "FOV", CFG.aimbot.fov, 50, 300,
                  lambda v: setattr(CFG.aimbot, "fov", int(v)))
        JugsSlider(aim_panel, "Smooth", CFG.aimbot.smooth, 1.0, 10.0,
                  lambda v: setattr(CFG.aimbot, "smooth", float(v)), is_float=True)
        JugsSlider(aim_panel, "Strength", CFG.aimbot.strength, 0.1, 1.0,
                  lambda v: setattr(CFG.aimbot, "strength", float(v)), is_float=True, res=0.05)
        JugsSlider(aim_panel, "Y Offset", CFG.aimbot.y_offset, -50, 50,
                  lambda v: setattr(CFG.aimbot, "y_offset", int(v)))
        JugsSlider(aim_panel, "Deadzone", CFG.aimbot.deadzone, 0, 20,
                  lambda v: setattr(CFG.aimbot, "deadzone", int(v)))

        # ===== TRIGGERBOT SETTINGS =====
        trig_panel = tk.LabelFrame(self.root, text=" TRIGGERBOT ", font=("Consolas", 9, "bold"),
                                  bg=JugsTheme.PANEL, fg=JugsTheme.ACCENT,
                                  bd=1, relief="solid", highlightbackground=JugsTheme.BORDER)
        trig_panel.pack(fill="x", padx=16, pady=8)
        trig_panel.configure(labelanchor="n")

        JugsSlider(trig_panel, "Confidence", CFG.triggerbot.confidence, 0.3, 1.0,
                  lambda v: setattr(CFG.triggerbot, "confidence", float(v)), is_float=True, res=0.05)
        JugsSlider(trig_panel, "Delay Min", CFG.triggerbot.delay_min_ms, 10, 300,
                  lambda v: setattr(CFG.triggerbot, "delay_min_ms", int(v)))
        JugsSlider(trig_panel, "Delay Max", CFG.triggerbot.delay_max_ms, 20, 500,
                  lambda v: setattr(CFG.triggerbot, "delay_max_ms", int(v)))

        # ===== FOOTER =====
        foot = tk.Frame(self.root, bg=JugsTheme.BG)
        foot.pack(fill="x", padx=16, pady=(10, 16))

        self.fps_lbl = tk.Label(foot, text="FPS: --", font=("Consolas", 9),
                               bg=JugsTheme.BG, fg=JugsTheme.FG_DIM)
        self.fps_lbl.pack(side="left")

        self.save_btn = tk.Button(foot, text="💾 SAVE", font=("Consolas", 9, "bold"),
                                  bg=JugsTheme.ACCENT_DARK, fg="white",
                                  bd=0, padx=20, pady=6, cursor="hand2",
                                  activebackground=JugsTheme.ACCENT,
                                  command=self._save)
        self.save_btn.pack(side="right")

        # Save button hover
        self.save_btn.bind("<Enter>", lambda e: self.save_btn.config(bg=JugsTheme.ACCENT))
        self.save_btn.bind("<Leave>", lambda e: self.save_btn.config(bg=JugsTheme.ACCENT_DARK))

    def _toggle_aim(self):
        CFG.aimbot.enabled = not CFG.aimbot.enabled
        if CFG.aimbot.enabled:
            CFG.triggerbot.enabled = False
        self._update_all()
        self._flash_notify("AIMBOT", CFG.aimbot.enabled)

    def _toggle_trig(self):
        CFG.triggerbot.enabled = not CFG.triggerbot.enabled
        if CFG.triggerbot.enabled:
            CFG.aimbot.enabled = False
        self._update_all()
        self._flash_notify("TRIGGERBOT", CFG.triggerbot.enabled)

    def _flash_notify(self, name, state):
        status = "ON" if state else "OFF"
        color = JugsTheme.GREEN if state else JugsTheme.RED
        self.status.set(f"{name} {status}", color, pulse=state)
        self.root.after(1200, self._update_status)

    def _update_all(self):
        self.aim_btn.set_active(CFG.aimbot.enabled)
        self.trig_btn.set_active(CFG.triggerbot.enabled)
        self._update_status()

    def _update_status(self):
        if CFG.aimbot.enabled:
            self.status.set("AIMBOT ACTIVE", JugsTheme.GREEN, pulse=True)
        elif CFG.triggerbot.enabled:
            self.status.set("TRIGGERBOT ACTIVE", JugsTheme.GREEN, pulse=True)
        else:
            self.status.set("IDLE", JugsTheme.RED)

    def _update_strategy(self):
        """Update HSV strategy display from detector."""
        strat = getattr(self.detector, 'strategy_name', 'PRIMARY')
        self.strat_lbl.config(text=f"HSV: {strat}")

    def _fps_loop(self):
        def tick():
            self.frame_count += 1
            now = time.time()
            if now - self.last_fps_time >= 1.0:
                self.fps = self.frame_count
                self.frame_count = 0
                self.last_fps_time = now
                self.fps_lbl.config(text=f"FPS: {self.fps}")
            self.root.after(16, tick)
        tick()

    def _status_loop(self):
        """Periodic status updates."""
        def tick():
            self._update_strategy()
            self.root.after(500, tick)
        tick()

    def _save(self):
        save_config(CFG)
        orig = self.fps_lbl.cget("text")
        self.fps_lbl.config(text="SAVED ✓", fg=JugsTheme.GREEN)
        self.root.after(1000, lambda: self.fps_lbl.config(text=orig, fg=JugsTheme.FG_DIM))

    def _quit(self):
        self.root.destroy()

    def run(self):
        self._update_all()
        self.root.mainloop()
        self.aimbot.stop()
        self.triggerbot.stop()
        save_config(CFG)
        try:
            kb.remove_hotkey(CFG.aimbot.toggle_key)
            kb.remove_hotkey(CFG.triggerbot.toggle_key)
            kb.remove_hotkey("f12")
        except:
            pass


if __name__ == "__main__":
    app = JugsUI()
    app.run()
