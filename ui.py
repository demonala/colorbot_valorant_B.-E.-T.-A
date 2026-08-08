"""
ui.py — Jugs's v3 Control Panel
Dark theme, live sliders, global hotkeys, mode toggle.
"""
import tkinter as tk
import keyboard as kb
import time
from config import CFG, save_config
from capture import ScreenCapture
from detector import PurpleDetector
from aimbot import Aimbot
from triggerbot import Triggerbot


class JugsUI:
    """Main application UI."""
    
    # Colors
    BG = "#0d0d0d"
    FG = "#e0e0e0"
    ACCENT = "#8b5cf6"
    ACCENT_DARK = "#6d28d9"
    PANEL = "#1a1a1a"
    BORDER = "#2d2d2d"
    GREEN = "#22c55e"
    RED = "#ef4444"
    YELLOW = "#eab308"
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jugs's Colorbot v3.0")
        self.root.geometry("440x640")
        self.root.resizable(False, False)
        self.root.attributes("-alpha", CFG.ui.opacity)
        self.root.configure(bg=self.BG)
        self.root.attributes("-topmost", True)
        
        # Core systems
        self.capture = ScreenCapture()
        self.detector = PurpleDetector(self.capture)
        self.aimbot = Aimbot(self.capture, self.detector)
        self.triggerbot = Triggerbot(self.capture, self.detector)
        
        self.aimbot.start()
        self.triggerbot.start()
        
        # Hotkeys
        self._register_hotkeys()
        
        # Build UI
        self._build_ui()
        
    def _register_hotkeys(self):
        """Global hotkeys via keyboard library."""
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
        """Construct all UI elements."""
        
        # === HEADER ===
        hdr = tk.Frame(self.root, bg=self.BG, height=50)
        hdr.pack(fill="x", padx=15, pady=(15, 5))
        
        tk.Label(hdr, text="JUGS'S COLORBOT v3.0", font=("Consolas", 16, "bold"),
                bg=self.BG, fg=self.ACCENT).pack(side="left")
        
        self.status_dot = tk.Canvas(hdr, width=10, height=10, bg=self.BG, highlightthickness=0)
        self.status_dot.pack(side="right", padx=5)
        self.status_dot.create_oval(2, 2, 8, 8, fill=self.RED, tags="dot")
        
        self.status_lbl = tk.Label(hdr, text="IDLE", font=("Consolas", 9), bg=self.BG, fg=self.RED)
        self.status_lbl.pack(side="right")
        
        # === HOTKEY BAR ===
        hk_bar = tk.Frame(self.root, bg=self.PANEL, bd=1, relief="solid",
                         highlightbackground=self.BORDER)
        hk_bar.pack(fill="x", padx=15, pady=(0, 10))
        
        tk.Label(hk_bar, text="HOTKEYS", font=("Consolas", 9, "bold"),
                bg=self.PANEL, fg=self.YELLOW).pack(anchor="w", padx=10, pady=(6, 2))
        
        keys = [
            (CFG.aimbot.toggle_key.upper(), "Toggle Aimbot"),
            (CFG.triggerbot.toggle_key.upper(), "Toggle Triggerbot"),
            ("F12", "Emergency Exit"),
            (CFG.aimbot.hold_key.upper(), "Hold for Aimbot"),
            (CFG.triggerbot.hold_key.upper(), "Hold for Triggerbot"),
        ]
        for key, desc in keys:
            row = tk.Frame(hk_bar, bg=self.PANEL)
            row.pack(fill="x", padx=10, pady=1)
            tk.Label(row, text=key, font=("Consolas", 9, "bold"),
                    bg=self.PANEL, fg=self.ACCENT, width=8, anchor="w").pack(side="left")
            tk.Label(row, text=desc, font=("Consolas", 9),
                    bg=self.PANEL, fg="#888888").pack(side="left")
        
        # === MODE SELECTOR ===
        mode_frm = tk.Frame(self.root, bg=self.PANEL, bd=1, relief="solid",
                           highlightbackground=self.BORDER)
        mode_frm.pack(fill="x", padx=15, pady=10)
        
        tk.Label(mode_frm, text="SELECT MODE", font=("Consolas", 10, "bold"),
                bg=self.PANEL, fg=self.ACCENT).pack(anchor="w", padx=10, pady=(8, 4))
        
        # Aimbot button
        self.aim_btn = tk.Button(
            mode_frm, text=f"🔒 AIMBOT  [{CFG.aimbot.toggle_key.upper()}]",
            font=("Consolas", 11, "bold"),
            bg=self.BORDER, fg=self.FG, activebackground=self.ACCENT_DARK,
            activeforeground="white", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._toggle_aim
        )
        self.aim_btn.pack(fill="x", padx=10, pady=5)
        
        tk.Label(mode_frm, text="Locks onto enemy. Does NOT shoot.",
                font=("Consolas", 8), bg=self.PANEL, fg="#888888").pack(anchor="w", padx=10, pady=(0, 5))
        
        # Triggerbot button
        self.trig_btn = tk.Button(
            mode_frm, text=f"🔫 TRIGGERBOT  [{CFG.triggerbot.toggle_key.upper()}]",
            font=("Consolas", 11, "bold"),
            bg=self.BORDER, fg=self.FG, activebackground=self.ACCENT_DARK,
            activeforeground="white", bd=0, padx=20, pady=10,
            cursor="hand2", command=self._toggle_trig
        )
        self.trig_btn.pack(fill="x", padx=10, pady=5)
        
        tk.Label(mode_frm, text="Auto-tap on crosshair. Sniper/Guardian only.",
                font=("Consolas", 8), bg=self.PANEL, fg="#888888").pack(anchor="w", padx=10, pady=(0, 8))
        
        self._update_buttons()
        
        # === AIMBOT SETTINGS ===
        aim_set = tk.Frame(self.root, bg=self.PANEL, bd=1, relief="solid",
                          highlightbackground=self.BORDER)
        aim_set.pack(fill="x", padx=15, pady=5)
        
        tk.Label(aim_set, text="AIMBOT SETTINGS", font=("Consolas", 10, "bold"),
                bg=self.PANEL, fg=self.ACCENT).pack(anchor="w", padx=10, pady=(8, 4))
        
        self._slider(aim_set, "FOV", CFG.aimbot.fov, 50, 300, 
                    lambda v: setattr(CFG.aimbot, "fov", int(v)))
        self._slider(aim_set, "Smooth", CFG.aimbot.smooth, 1.0, 10.0,
                    lambda v: setattr(CFG.aimbot, "smooth", float(v)), is_float=True)
        self._slider(aim_set, "Strength", CFG.aimbot.strength, 0.1, 1.0,
                    lambda v: setattr(CFG.aimbot, "strength", float(v)), is_float=True, res=0.05)
        self._slider(aim_set, "Y Offset", CFG.aimbot.y_offset, -50, 50,
                    lambda v: setattr(CFG.aimbot, "y_offset", int(v)))
        
        # === TRIGGERBOT SETTINGS ===
        trig_set = tk.Frame(self.root, bg=self.PANEL, bd=1, relief="solid",
                           highlightbackground=self.BORDER)
        trig_set.pack(fill="x", padx=15, pady=5)
        
        tk.Label(trig_set, text="TRIGGERBOT SETTINGS", font=("Consolas", 10, "bold"),
                bg=self.PANEL, fg=self.ACCENT).pack(anchor="w", padx=10, pady=(8, 4))
        
        self._slider(trig_set, "Confidence", CFG.triggerbot.confidence, 0.3, 1.0,
                    lambda v: setattr(CFG.triggerbot, "confidence", float(v)), is_float=True, res=0.05)
        self._slider(trig_set, "Delay Min (ms)", CFG.triggerbot.delay_min_ms, 10, 300,
                    lambda v: setattr(CFG.triggerbot, "delay_min_ms", int(v)))
        self._slider(trig_set, "Delay Max (ms)", CFG.triggerbot.delay_max_ms, 20, 500,
                    lambda v: setattr(CFG.triggerbot, "delay_max_ms", int(v)))
        
        # === FOOTER ===
        foot = tk.Frame(self.root, bg=self.BG)
        foot.pack(fill="x", padx=15, pady=(10, 15))
        
        self.fps_lbl = tk.Label(foot, text="FPS: --", font=("Consolas", 9),
                               bg=self.BG, fg="#666666")
        self.fps_lbl.pack(side="left")
        
        tk.Button(foot, text="💾 SAVE", font=("Consolas", 9), bg=self.ACCENT_DARK,
                 fg="white", bd=0, padx=15, pady=5, cursor="hand2",
                 command=self._save).pack(side="right")
        
        self._fps_loop()
        
    def _slider(self, parent, label, default, min_v, max_v, callback, is_float=False, res=1.0):
        """Create a labeled slider row."""
        frm = tk.Frame(parent, bg=self.PANEL)
        frm.pack(fill="x", padx=10, pady=3)
        
        tk.Label(frm, text=label, font=("Consolas", 9), bg=self.PANEL,
                fg=self.FG, width=14, anchor="w").pack(side="left")
        
        val_lbl = tk.Label(frm, text=str(default), font=("Consolas", 9),
                          bg=self.PANEL, fg=self.ACCENT, width=8)
        val_lbl.pack(side="right")
        
        scale = tk.Scale(
            frm, from_=min_v, to=max_v, resolution=res,
            orient="horizontal", bg=self.PANEL, fg=self.FG,
            highlightthickness=0, bd=0, troughcolor=self.BORDER,
            activebackground=self.ACCENT, showvalue=0,
            command=lambda v: self._on_slider(v, val_lbl, callback, is_float)
        )
        scale.set(default)
        scale.pack(fill="x", padx=(5, 0))
        
    def _on_slider(self, val, lbl, callback, is_float):
        v = float(val) if is_float else int(float(val))
        lbl.config(text=f"{v:.2f}" if is_float else str(v))
        callback(v)
        
    def _toggle_aim(self):
        """Toggle aimbot. Mutually exclusive with triggerbot."""
        CFG.aimbot.enabled = not CFG.aimbot.enabled
        if CFG.aimbot.enabled:
            CFG.triggerbot.enabled = False
        self._update_buttons()
        self._update_status()
        self._flash_notify("AIMBOT", CFG.aimbot.enabled)
        
    def _toggle_trig(self):
        """Toggle triggerbot. Mutually exclusive with aimbot."""
        CFG.triggerbot.enabled = not CFG.triggerbot.enabled
        if CFG.triggerbot.enabled:
            CFG.aimbot.enabled = False
        self._update_buttons()
        self._update_status()
        self._flash_notify("TRIGGERBOT", CFG.triggerbot.enabled)
        
    def _flash_notify(self, name, state):
        """Brief status flash."""
        status = "ON" if state else "OFF"
        color = self.GREEN if state else self.RED
        self.status_lbl.config(text=f"{name} {status}", fg=color)
        self.root.after(1500, self._update_status)
        
    def _update_buttons(self):
        """Sync button visuals."""
        if CFG.aimbot.enabled:
            self.aim_btn.config(bg=self.ACCENT, fg="white", 
                               text=f"🔒 AIMBOT  [{CFG.aimbot.toggle_key.upper()}]  ✓ ACTIVE")
            self.trig_btn.config(bg=self.BORDER, fg=self.FG,
                                text=f"🔫 TRIGGERBOT  [{CFG.triggerbot.toggle_key.upper()}]")
        elif CFG.triggerbot.enabled:
            self.aim_btn.config(bg=self.BORDER, fg=self.FG,
                               text=f"🔒 AIMBOT  [{CFG.aimbot.toggle_key.upper()}]")
            self.trig_btn.config(bg=self.ACCENT, fg="white",
                                text=f"🔫 TRIGGERBOT  [{CFG.triggerbot.toggle_key.upper()}]  ✓ ACTIVE")
        else:
            self.aim_btn.config(bg=self.BORDER, fg=self.FG,
                               text=f"🔒 AIMBOT  [{CFG.aimbot.toggle_key.upper()}]")
            self.trig_btn.config(bg=self.BORDER, fg=self.FG,
                                text=f"🔫 TRIGGERBOT  [{CFG.triggerbot.toggle_key.upper()}]")
            
    def _update_status(self):
        """Update status dot and label."""
        dot = self.status_dot.find_withtag("dot")
        
        if CFG.aimbot.enabled:
            self.status_dot.itemconfig(dot, fill=self.GREEN)
            self.status_lbl.config(text="AIMBOT ACTIVE", fg=self.GREEN)
        elif CFG.triggerbot.enabled:
            self.status_dot.itemconfig(dot, fill=self.GREEN)
            self.status_lbl.config(text="TRIGGERBOT ACTIVE", fg=self.GREEN)
        else:
            self.status_dot.itemconfig(dot, fill=self.RED)
            self.status_lbl.config(text="IDLE", fg=self.RED)
            
    def _fps_loop(self):
        """FPS counter loop."""
        frame_count = 0
        last_time = time.time()
        
        def update():
            nonlocal frame_count, last_time
            frame_count += 1
            now = time.time()
            if now - last_time >= 1.0:
                self.fps_lbl.config(text=f"FPS: {frame_count}")
                frame_count = 0
                last_time = now
            self.root.after(16, update)
            
        update()
        
    def _save(self):
        save_config(CFG)
        orig = self.fps_lbl.cget("text")
        self.fps_lbl.config(text="SAVED ✓", fg=self.GREEN)
        self.root.after(1000, lambda: self.fps_lbl.config(text=orig, fg="#666666"))
        
    def _quit(self):
        self.root.destroy()
        
    def run(self):
        self._update_status()
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
 
