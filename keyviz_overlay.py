"""
KeyViz Overlay v3.0 — Ultimate Keystroke Visualizer
Made by D.T — Germany, Münster

Requirements: pip install pynput psutil pywin32
Run: python keyviz_overlay.py
"""

import tkinter as tk
from tkinter import messagebox
import threading
import time
import json
import os
import math
import colorsys
import random
import winreg
import subprocess
from collections import Counter, deque
from datetime import datetime, timedelta
from pynput import keyboard, mouse

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import win32gui
    import win32process
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False

# ─────────────────────────────────────────────────────────────────────────────
# PATHS & CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "keyviz_config.json")
STATS_FILE  = os.path.join(BASE_DIR, "keyviz_stats.json")
APP_NAME    = "KeyViz"
APP_VERSION = "3.0"
AUTOSTART_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

# ─────────────────────────────────────────────────────────────────────────────
# THEMES
# ─────────────────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "name": "Dark", "bg": "#0e0e12", "surface": "#16161e",
        "surface2": "#1e1e28", "border": "#2a2a3e", "accent": "#7c6aff",
        "accent2": "#ff6ab4", "text": "#e8e8f0", "muted": "#4a4a6a",
        "success": "#6affb4", "key_bg": "#1c1c24", "key_border": "#2e2e42",
        "heat_low": "#1c1c24", "heat_high": "#7c6aff",
    },
    "midnight": {
        "name": "Midnight", "bg": "#080812", "surface": "#0e0e1c",
        "surface2": "#14142a", "border": "#1e1e3a", "accent": "#4a9eff",
        "accent2": "#64ffda", "text": "#ccd6f6", "muted": "#3a3a5a",
        "success": "#64ffda", "key_bg": "#10101e", "key_border": "#20203a",
        "heat_low": "#10101e", "heat_high": "#4a9eff",
    },
    "rose": {
        "name": "Rose", "bg": "#120a0e", "surface": "#1e1016",
        "surface2": "#28141c", "border": "#3e1e2a", "accent": "#ff6b9d",
        "accent2": "#ffb347", "text": "#ffe0ec", "muted": "#6a3a4a",
        "success": "#ff9eb5", "key_bg": "#1c1016", "key_border": "#3c1e28",
        "heat_low": "#1c1016", "heat_high": "#ff6b9d",
    },
    "forest": {
        "name": "Forest", "bg": "#080e0a", "surface": "#0e1810",
        "surface2": "#142016", "border": "#1e3a22", "accent": "#4aff82",
        "accent2": "#a0ff6a", "text": "#d0f0d8", "muted": "#2a4a30",
        "success": "#6affa0", "key_bg": "#0e160f", "key_border": "#1e3020",
        "heat_low": "#0e160f", "heat_high": "#4aff82",
    },
    "gaming": {
        "name": "Gaming", "bg": "#090010", "surface": "#110022",
        "surface2": "#1a0033", "border": "#3a0066", "accent": "#cc00ff",
        "accent2": "#ff4400", "text": "#f0d0ff", "muted": "#5a2a6a",
        "success": "#00ffcc", "key_bg": "#130018", "key_border": "#400080",
        "heat_low": "#130018", "heat_high": "#cc00ff",
    },
    "custom": {
        "name": "Custom", "bg": "#0e0e12", "surface": "#16161e",
        "surface2": "#1e1e28", "border": "#2a2a3e", "accent": "#ff6a6a",
        "accent2": "#6aafff", "text": "#e8e8f0", "muted": "#4a4a6a",
        "success": "#6affb4", "key_bg": "#1c1c24", "key_border": "#2e2e42",
        "heat_low": "#1c1c24", "heat_high": "#ff6a6a",
    },
}

DEFAULT_CONFIG = {
    "theme": "dark", "custom_theme": THEMES["custom"].copy(),
    "opacity": 0.92, "corner": "bottom-left", "always_on_top": True,
    "fade_ms": 2500, "max_keys": 7, "font_size": 22,
    "show_stats": True, "show_modifiers": True, "show_history": True,
    "show_wpm_graph": True, "show_mouse": True, "show_clock": True,
    "show_heatmap": True, "show_app_tracker": True, "show_hold_tracker": True,
    "sound_enabled": False, "toggle_hotkey": "f9",
    "history_max": 80, "pos_x": -1, "pos_y": -1, "width": 360,
    "autostart": False, "glow_effects": True,
    "gaming_overlay": False, "gaming_pos_x": -1, "gaming_pos_y": -1,
    # RGB
    "rgb_enabled": False, "rgb_speed": 3.0, "rgb_mode": "cycle",
    # Particles
    "particles_enabled": True, "particle_threshold_wpm": 60,
}

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENTS
# ─────────────────────────────────────────────────────────────────────────────
ACHIEVEMENTS = [
    {"id": "first_key",    "name": "First Key!",      "desc": "Press your first key",           "icon": "⌨",  "req": ("total_keys", 1)},
    {"id": "hundred",      "name": "Century",          "desc": "100 keys pressed",               "icon": "💯", "req": ("total_keys", 100)},
    {"id": "thousand",     "name": "Keymaster",        "desc": "1,000 keys pressed",             "icon": "🔑", "req": ("total_keys", 1000)},
    {"id": "tenthousand",  "name": "Key Demon",        "desc": "10,000 keys pressed",            "icon": "😈", "req": ("total_keys", 10000)},
    {"id": "wpm30",        "name": "Speed Typer",      "desc": "Reach 30 WPM",                   "icon": "⚡", "req": ("max_wpm", 30)},
    {"id": "wpm60",        "name": "Fast Fingers",     "desc": "Reach 60 WPM",                   "icon": "🔥", "req": ("max_wpm", 60)},
    {"id": "wpm100",       "name": "Blazing",          "desc": "Reach 100 WPM",                  "icon": "🚀", "req": ("max_wpm", 100)},
    {"id": "streak10",     "name": "On a Roll",        "desc": "10 key streak (no pause)",       "icon": "🎯", "req": ("max_streak", 10)},
    {"id": "streak50",     "name": "Unstoppable",      "desc": "50 key streak",                  "icon": "🌊", "req": ("max_streak", 50)},
    {"id": "combo",        "name": "Combo King",       "desc": "Use 5 key combos",               "icon": "🎮", "req": ("total_combos", 5)},
    {"id": "session30",    "name": "Dedicated",        "desc": "30 min session",                 "icon": "⏰", "req": ("session_min", 30)},
    {"id": "night_owl",    "name": "Night Owl",        "desc": "Type after midnight",             "icon": "🦉", "req": ("night_typing", 1)},
    {"id": "mouse100",     "name": "Clicker",          "desc": "100 mouse clicks",               "icon": "🖱", "req": ("total_clicks", 100)},
    {"id": "space_bar",    "name": "Space Cadet",      "desc": "Press Space 500 times",          "icon": "🌌", "req": ("space_count", 500)},
    {"id": "backspace50",  "name": "Typo Eraser",      "desc": "Backspace 50 times",             "icon": "✏", "req": ("backspace_count", 50)},
]

# ─────────────────────────────────────────────────────────────────────────────
# KEY HELPERS
# ─────────────────────────────────────────────────────────────────────────────
SPECIAL_NAMES = {
    keyboard.Key.space: "Space", keyboard.Key.enter: "Enter",
    keyboard.Key.backspace: "⌫", keyboard.Key.tab: "Tab",
    keyboard.Key.esc: "Esc", keyboard.Key.delete: "Del",
    keyboard.Key.caps_lock: "Caps", keyboard.Key.shift: "Shift",
    keyboard.Key.shift_r: "Shift", keyboard.Key.ctrl: "Ctrl",
    keyboard.Key.ctrl_r: "Ctrl", keyboard.Key.alt: "Alt",
    keyboard.Key.alt_r: "Alt", keyboard.Key.alt_gr: "AltGr",
    keyboard.Key.cmd: "Win", keyboard.Key.cmd_r: "Win",
    keyboard.Key.up: "↑", keyboard.Key.down: "↓",
    keyboard.Key.left: "←", keyboard.Key.right: "→",
    keyboard.Key.home: "Home", keyboard.Key.end: "End",
    keyboard.Key.page_up: "PgUp", keyboard.Key.page_down: "PgDn",
    keyboard.Key.insert: "Ins", keyboard.Key.print_screen: "PrtSc",
    keyboard.Key.f1: "F1", keyboard.Key.f2: "F2", keyboard.Key.f3: "F3",
    keyboard.Key.f4: "F4", keyboard.Key.f5: "F5", keyboard.Key.f6: "F6",
    keyboard.Key.f7: "F7", keyboard.Key.f8: "F8", keyboard.Key.f9: "F9",
    keyboard.Key.f10: "F10", keyboard.Key.f11: "F11", keyboard.Key.f12: "F12",
}

MODIFIER_KEYS = {
    keyboard.Key.shift, keyboard.Key.shift_r,
    keyboard.Key.ctrl, keyboard.Key.ctrl_r,
    keyboard.Key.alt, keyboard.Key.alt_r, keyboard.Key.alt_gr,
    keyboard.Key.cmd, keyboard.Key.cmd_r, keyboard.Key.caps_lock,
}

KB_LAYOUT = [
    ["`","1","2","3","4","5","6","7","8","9","0","-","=","⌫"],
    ["Tab","Q","W","E","R","T","Y","U","I","O","P","[","]","\\"],
    ["Caps","A","S","D","F","G","H","J","K","L",";","'","Enter"],
    ["Shift","Z","X","C","V","B","N","M",",",".","/","Shift"],
    ["Ctrl","Alt","Space","Alt","Ctrl"],
]

KEY_WIDTHS_HEAT = {
    "⌫":1.8,"Tab":1.6,"Caps":1.8,"Enter":2.0,
    "Shift":2.4,"Ctrl":1.5,"Alt":1.3,"Space":5.0,"\\":1.5,
}

def get_key_label(key):
    if key in SPECIAL_NAMES:
        return SPECIAL_NAMES[key]
    try:
        c = key.char
        if c is None:
            return str(key).replace("Key.", "").upper()
        return c.upper() if len(c) == 1 else c
    except AttributeError:
        return str(key).replace("Key.", "").capitalize()

def is_modifier(key):
    return key in MODIFIER_KEYS

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f"#{int(max(0,min(255,r))):02x}{int(max(0,min(255,g))):02x}{int(max(0,min(255,b))):02x}"

def blend(c1, c2, t):
    try:
        r1,g1,b1 = hex_to_rgb(c1); r2,g2,b2 = hex_to_rgb(c2)
        return rgb_to_hex(r1*t+r2*(1-t), g1*t+g2*(1-t), b1*t+b2*(1-t))
    except Exception:
        return c1

def lighten(c, amount=0.2):
    try:
        r,g,b = [x/255 for x in hex_to_rgb(c)]
        h,s,v = colorsys.rgb_to_hsv(r,g,b)
        r2,g2,b2 = colorsys.hsv_to_rgb(h,s,min(1.0,v+amount))
        return rgb_to_hex(r2*255,g2*255,b2*255)
    except Exception:
        return c

def heat_color(low, high, ratio):
    return blend(high, low, ratio)

# ─────────────────────────────────────────────────────────────────────────────
# PERSISTENT STATS
# ─────────────────────────────────────────────────────────────────────────────
def load_stats():
    try:
        with open(STATS_FILE) as f:
            return json.load(f)
    except Exception:
        return {
            "total_keys": 0, "total_clicks": 0, "total_combos": 0,
            "max_wpm": 0, "max_streak": 0, "space_count": 0,
            "backspace_count": 0, "night_typing": 0, "session_min": 0,
            "achievements": [], "achievement_dates": {},
            "key_counts": {}, "daily": {}, "app_times": {},
        }

def save_stats(s):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

def load_config():
    try:
        with open(CONFIG_FILE) as f:
            cfg = DEFAULT_CONFIG.copy(); cfg.update(json.load(f)); return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────────────
# AUTOSTART
# ─────────────────────────────────────────────────────────────────────────────
def set_autostart(enable):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0,
                             winreg.KEY_SET_VALUE)
        if enable:
            exe = os.path.abspath(__file__)
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ,
                              f'pythonw "{exe}"')
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except Exception:
                pass
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

def get_autostart():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, AUTOSTART_KEY, 0,
                             winreg.KEY_READ)
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except Exception:
        return False

# ─────────────────────────────────────────────────────────────────────────────
# ACTIVE WINDOW
# ─────────────────────────────────────────────────────────────────────────────
def get_active_app():
    if not HAS_WIN32:
        return "Unknown"
    try:
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        proc = psutil.Process(pid) if HAS_PSUTIL else None
        name = proc.name().replace(".exe","") if proc else "Unknown"
        title = win32gui.GetWindowText(hwnd)
        return name, title[:40] if title else name
    except Exception:
        return "Unknown", ""

def get_running_games():
    if not HAS_PSUTIL:
        return []
    game_keywords = [
        "steam","minecraft","valorant","fortnite","csgo","cs2","league",
        "overwatch","apex","roblox","gta","cyberpunk","elden","doom",
        "destiny","warzone","pubg","rocket","among","discord",
    ]
    games = []
    try:
        for proc in psutil.process_iter(["name","pid"]):
            n = proc.info["name"].lower().replace(".exe","")
            if any(k in n for k in game_keywords):
                games.append(proc.info["name"].replace(".exe",""))
    except Exception:
        pass
    return games[:5]

# ─────────────────────────────────────────────────────────────────────────────
# COLOR WHEEL
# ─────────────────────────────────────────────────────────────────────────────
class ColorWheel(tk.Canvas):
    def __init__(self, parent, size=180, command=None, **kwargs):
        super().__init__(parent, width=size, height=size,
                         highlightthickness=0, **kwargs)
        self.size = size; self.command = command
        self.hue = 0.0; self.sat = 1.0; self.val = 1.0
        self._sq_img = None; self._sq_x = 0; self._sq_y = 0; self._sq_size = 1
        self._draw_wheel()
        self.bind("<Button-1>", self._click)
        self.bind("<B1-Motion>", self._click)

    def _draw_wheel(self):
        self.delete("all")
        cx = cy = self.size // 2; r = cx - 4; ring_w = 14
        for i in range(180):
            a1 = 2*math.pi*i/180; a2 = 2*math.pi*(i+1)/180
            rc,gc,bc = colorsys.hsv_to_rgb(i/180,1.0,1.0)
            col = rgb_to_hex(rc*255,gc*255,bc*255)
            pts = [cx+(r-ring_w)*math.cos(a1), cy+(r-ring_w)*math.sin(a1),
                   cx+r*math.cos(a1), cy+r*math.sin(a1),
                   cx+r*math.cos(a2), cy+r*math.sin(a2),
                   cx+(r-ring_w)*math.cos(a2), cy+(r-ring_w)*math.sin(a2)]
            self.create_polygon(pts, fill=col, outline=col)
        ha = 2*math.pi*self.hue
        ix = cx+(r-ring_w//2)*math.cos(ha); iy = cy+(r-ring_w//2)*math.sin(ha)
        self.create_oval(ix-5,iy-5,ix+5,iy+5, outline="white", fill="", width=2)
        inner_r = r-ring_w-4; sq = int(inner_r*1.41); half = sq//2
        self._sq_x = cx-half; self._sq_y = cy-half; self._sq_size = sq
        rows = []
        for row in range(sq):
            line = []
            for col in range(sq):
                s = col/max(sq-1,1); v = 1.0-row/max(sq-1,1)
                rc2,gc2,bc2 = colorsys.hsv_to_rgb(self.hue,s,v)
                line.append(rgb_to_hex(rc2*255,gc2*255,bc2*255))
            rows.append("{"+' '.join(line)+"}")
        self._sq_img = tk.PhotoImage(width=sq, height=sq)
        self._sq_img.put(' '.join(rows))
        self.create_image(self._sq_x, self._sq_y, image=self._sq_img, anchor="nw")
        sx = self._sq_x+self.sat*(sq-1); sy = self._sq_y+(1-self.val)*(sq-1)
        self.create_oval(sx-5,sy-5,sx+5,sy+5, outline="white", fill="", width=2)

    def _click(self, e):
        cx = cy = self.size//2; r = cx-4; ring_w = 14
        dx,dy = e.x-cx, e.y-cy; dist = math.sqrt(dx*dx+dy*dy)
        if dist >= r-ring_w:
            self.hue = (math.atan2(dy,dx)/(2*math.pi))%1.0; self._draw_wheel()
        elif (self._sq_x<=e.x<=self._sq_x+self._sq_size and
              self._sq_y<=e.y<=self._sq_y+self._sq_size):
            self.sat = max(0,min(1,(e.x-self._sq_x)/max(self._sq_size-1,1)))
            self.val = max(0,min(1,1-(e.y-self._sq_y)/max(self._sq_size-1,1)))
            self._draw_wheel()
            if self.command: self.command(self.get_color())

    def set_color(self, hexcolor):
        try:
            r,g,b = [x/255 for x in hex_to_rgb(hexcolor)]
            self.hue,self.sat,self.val = colorsys.rgb_to_hsv(r,g,b)
            self._draw_wheel()
        except Exception:
            pass

    def get_color(self):
        rc,gc,bc = colorsys.hsv_to_rgb(self.hue,self.sat,self.val)
        return rgb_to_hex(rc*255,gc*255,bc*255)

# ─────────────────────────────────────────────────────────────────────────────
# WPM GRAPH
# ─────────────────────────────────────────────────────────────────────────────
class WPMGraph(tk.Canvas):
    def __init__(self, parent, theme, width=340, height=58, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, **kwargs)
        self.T = theme; self.W = width; self.H = height
        self.data = deque(maxlen=60)
        self.configure(bg=self.T["surface"]); self._draw()

    def update_theme(self, T):
        self.T = T; self.configure(bg=T["surface"]); self._draw()

    def push(self, wpm):
        self.data.append(wpm); self._draw()

    def _draw(self):
        self.delete("all")
        if not self.data or max(self.data) == 0:
            self.create_text(self.W//2, self.H//2, text="Type to see WPM graph",
                             fill=self.T["muted"], font=("Consolas",8)); return
        maxv = max(self.data); pts = list(self.data); n = len(pts)
        step = self.W/max(n-1,1)
        for i in range(1,4):
            y = self.H-int(self.H*i/4)-2
            self.create_line(0,y,self.W,y, fill=self.T["border"], dash=(2,4))
            self.create_text(3,y-6, text=str(int(maxv*i/4)),
                             fill=self.T["muted"], font=("Consolas",7), anchor="w")
        coords = [(int(i*step), self.H-int((v/maxv)*(self.H-10))-4)
                  for i,v in enumerate(pts)]
        if len(coords) >= 2:
            poly = [(0,self.H)]+coords+[(coords[-1][0],self.H)]
            self.create_polygon([c for pt in poly for c in pt],
                                fill=self.T["accent"]+"33", outline="")
            for i in range(len(coords)-1):
                self.create_line(coords[i][0],coords[i][1],
                                 coords[i+1][0],coords[i+1][1],
                                 fill=self.T["accent"], width=2, smooth=True)
            lx,ly = coords[-1]
            self.create_oval(lx-4,ly-4,lx+4,ly+4,
                             fill=self.T["accent"], outline=lighten(self.T["accent"]))
        self.create_text(self.W-4,5, text=f"{pts[-1]} WPM",
                         fill=self.T["accent"], font=("Consolas",8,"bold"), anchor="ne")

# ─────────────────────────────────────────────────────────────────────────────
# HEATMAP WIDGET
# ─────────────────────────────────────────────────────────────────────────────
class HeatmapWidget(tk.Canvas):
    def __init__(self, parent, theme, width=340, **kwargs):
        self.cell_w = 22; self.cell_h = 20; self.pad = 4
        rows = len(KB_LAYOUT)
        h = rows*(self.cell_h+self.pad)+self.pad
        super().__init__(parent, width=width, height=h,
                         highlightthickness=0, **kwargs)
        self.T = theme; self.W = width; self.counts = {}
        self.configure(bg=self.T["bg"]); self._draw()

    def update_theme(self, T):
        self.T = T; self.configure(bg=T["bg"]); self._draw()

    def update_counts(self, counts):
        self.counts = counts; self._draw()

    def _draw(self):
        self.delete("all")
        maxv = max(self.counts.values(), default=1)
        offsets = [0, 4, 7, 11, 30]
        for r, row in enumerate(KB_LAYOUT):
            x = self.pad + offsets[r]
            y = self.pad + r*(self.cell_h+self.pad)
            for key in row:
                w = int(self.cell_w * KEY_WIDTHS_HEAT.get(key, 1.0))
                count = self.counts.get(key, self.counts.get(key.lower(), 0))
                ratio = min(count/maxv, 1.0) if maxv > 0 else 0
                fill = heat_color(self.T["heat_low"], self.T["heat_high"], ratio)
                border = blend(self.T["accent"], self.T["key_border"], ratio)
                self.create_rectangle(x,y,x+w,y+self.cell_h,
                                      fill=fill, outline=border)
                lbl = key if len(key)<=3 else key[:2]
                fc = self.T["text"] if ratio > 0.4 else self.T["muted"]
                self.create_text(x+w//2, y+self.cell_h//2, text=lbl,
                                 fill=fc, font=("Consolas",6,"bold"))
                if ratio > 0:
                    self.create_text(x+w//2, y+self.cell_h-4, text=str(count),
                                     fill=fc+"88"[::-1] if len(fc)==7 else fc,
                                     font=("Consolas",5))
                x += w+self.pad

# ─────────────────────────────────────────────────────────────────────────────
# GLOW ANIMATION CANVAS
# ─────────────────────────────────────────────────────────────────────────────
class GlowCanvas(tk.Canvas):
    """Renders animated glowing key pop effects."""
    def __init__(self, parent, theme, width=360, height=80, **kwargs):
        super().__init__(parent, width=width, height=height,
                         highlightthickness=0, **kwargs)
        self.T = theme; self.W = width; self.H = height
        self.configure(bg=self.T["bg"])
        self._particles = []
        self._keys = []       # (label, is_mod, is_combo, ts, x, anim)
        self._anim_running = False

    def update_theme(self, T):
        self.T = T; self.configure(bg=T["bg"])

    def add_key(self, label, is_mod=False, is_combo=False):
        x = random.randint(40, self.W-40)
        self._keys.append({
            "label": label, "is_mod": is_mod, "is_combo": is_combo,
            "ts": time.time(), "x": x, "y": self.H//2,
            "scale": 0.0, "alpha": 1.0, "phase": "in",
        })
        if not self._anim_running:
            self._anim_running = True
            self._animate()

    def _animate(self):
        now = time.time()
        alive = []
        for k in self._keys:
            age = now - k["ts"]
            fade_s = 1.2
            if age < 0.15:
                k["scale"] = min(1.0, age/0.15)
                k["alpha"] = 1.0
            elif age < fade_s:
                k["scale"] = 1.0
                k["alpha"] = 1.0-(age-0.15)/(fade_s-0.15)
            else:
                continue
            alive.append(k)
        self._keys = alive
        self._draw_frame()
        if self._keys:
            self.after(30, self._animate)
        else:
            self._anim_running = False
            self.delete("all")

    def _draw_frame(self):
        self.delete("all")
        for k in self._keys:
            x, y = k["x"], k["y"]
            s = k["scale"]; a = k["alpha"]
            label = k["label"]
            col = (self.T["accent2"] if k["is_mod"]
                   else self.T["accent"] if k["is_combo"]
                   else self.T["accent"])
            faded = blend(col, self.T["bg"], a)
            # Glow rings
            for ring in range(3, 0, -1):
                rsize = int(26*s) + ring*8
                ga = a*(0.15/ring)
                gcol = blend(col, self.T["bg"], ga)
                self.create_oval(x-rsize, y-rsize//2, x+rsize, y+rsize//2,
                                 fill="", outline=gcol, width=1)
            # Key box
            bw = max(10, int(len(label)*10*s)); bh = int(30*s)
            self.create_rectangle(x-bw//2, y-bh//2, x+bw//2, y+bh//2,
                                  fill=blend(self.T["key_bg"], self.T["bg"], a),
                                  outline=faded, width=1)
            fs = max(8, int(14*s))
            self.create_text(x, y, text=label, fill=faded,
                             font=("Consolas", fs, "bold"))

# ─────────────────────────────────────────────────────────────────────────────
# TYPING SPEED TEST WINDOW
# ─────────────────────────────────────────────────────────────────────────────
SPEED_TEST_TEXTS = [
    "The quick brown fox jumps over the lazy dog",
    "Pack my box with five dozen liquor jugs",
    "How vexingly quick daft zebras jump",
    "The five boxing wizards jump quickly",
    "Sphinx of black quartz judge my vow",
    "Two driven jocks help fax my big quiz",
    "Crazy Fredrick bought many very exquisite opal jewels",
    "We promptly judged antique ivory buckles for the next prize",
]

class SpeedTestWindow:
    def __init__(self, parent, theme):
        self.T = theme
        self.win = tk.Toplevel(parent)
        self.win.title("KeyViz — Typing Speed Test")
        self.win.configure(bg=theme["bg"])
        self.win.geometry("600x380")
        self.win.resizable(False, False)
        self.win.attributes("-topmost", True)
        self.text = ""
        self.start_time = None
        self.active = False
        self.errors = 0
        self._build()

    def _build(self):
        T = self.T
        tk.Label(self.win, text="⚡  SPEED TEST", bg=T["bg"], fg=T["accent"],
                 font=("Consolas",14,"bold")).pack(pady=(16,4))
        tk.Label(self.win, text="Type the text below as fast as you can",
                 bg=T["bg"], fg=T["muted"], font=("Consolas",9)).pack()

        # Target text display
        self.target_frame = tk.Frame(self.win, bg=T["surface"],
                                     highlightbackground=T["border"],
                                     highlightthickness=1)
        self.target_frame.pack(fill="x", padx=20, pady=12)
        self.target_lbl = tk.Label(self.target_frame, text="",
                                   bg=T["surface"], fg=T["text"],
                                   font=("Consolas",13), wraplength=540,
                                   justify="left", pady=12, padx=12)
        self.target_lbl.pack()

        # Input box
        self.input_var = tk.StringVar()
        self.input_var.trace("w", self._on_type)
        self.entry = tk.Entry(self.win, textvariable=self.input_var,
                              bg=T["key_bg"], fg=T["text"],
                              insertbackground=T["accent"],
                              font=("Consolas",13), relief="flat",
                              highlightbackground=T["border"],
                              highlightthickness=1, state="disabled")
        self.entry.pack(fill="x", padx=20, pady=(0,8), ipady=8)

        # Stats row
        sf = tk.Frame(self.win, bg=T["bg"])
        sf.pack(fill="x", padx=20)
        self.lbl_wpm  = self._stat(sf, "0",  "WPM")
        self.lbl_acc  = self._stat(sf, "100%","ACC")
        self.lbl_time = self._stat(sf, "0s",  "TIME")
        self.lbl_err  = self._stat(sf, "0",   "ERRORS")

        # Progress bar
        self.prog_canvas = tk.Canvas(self.win, bg=T["surface"], height=6,
                                     highlightthickness=0)
        self.prog_canvas.pack(fill="x", padx=20, pady=8)

        # Result label
        self.result_lbl = tk.Label(self.win, text="", bg=T["bg"],
                                   fg=T["success"], font=("Consolas",11,"bold"))
        self.result_lbl.pack()

        # Buttons
        bf = tk.Frame(self.win, bg=T["bg"])
        bf.pack(pady=8)
        self._btn(bf, "▶  Start", self._start).pack(side="left", padx=6)
        self._btn(bf, "⟳  New Text", self._new_text).pack(side="left", padx=6)
        self._btn(bf, "✕  Close", self.win.destroy).pack(side="left", padx=6)

        self._new_text()

    def _stat(self, parent, val, lbl):
        f = tk.Frame(parent, bg=self.T["bg"])
        f.pack(side="left", expand=True)
        v = tk.Label(f, text=val, bg=self.T["bg"], fg=self.T["accent"],
                     font=("Consolas",16,"bold"))
        v.pack()
        tk.Label(f, text=lbl, bg=self.T["bg"], fg=self.T["muted"],
                 font=("Consolas",7,"bold")).pack()
        return v

    def _btn(self, parent, text, cmd):
        b = tk.Label(parent, text=text, bg=self.T["accent"], fg="#fff",
                     font=("Consolas",9,"bold"), padx=14, pady=6, cursor="hand2")
        b.bind("<Button-1>", lambda e: cmd())
        return b

    def _new_text(self):
        self.text = random.choice(SPEED_TEST_TEXTS)
        self.target_lbl.configure(text=self.text)
        self._reset()

    def _reset(self):
        self.start_time = None; self.active = False; self.errors = 0
        self.input_var.set("")
        self.entry.configure(state="disabled", bg=self.T["key_bg"])
        self.result_lbl.configure(text="")
        self.lbl_wpm.configure(text="0")
        self.lbl_acc.configure(text="100%")
        self.lbl_time.configure(text="0s")
        self.lbl_err.configure(text="0")
        self.prog_canvas.delete("all")

    def _start(self):
        self._reset()
        self.active = True
        self.entry.configure(state="normal")
        self.entry.focus_set()
        self.start_time = time.time()
        self._tick()

    def _on_type(self, *_):
        if not self.active: return
        typed = self.input_var.get()
        target = self.text
        # Count errors
        errs = sum(1 for i,c in enumerate(typed) if i < len(target) and c != target[i])
        self.errors = errs + max(0, len(typed)-len(target))
        # Progress bar
        prog = len(typed)/len(target)
        W = self.prog_canvas.winfo_width()
        self.prog_canvas.delete("all")
        self.prog_canvas.create_rectangle(0,0,int(W*prog),6,
                                          fill=self.T["accent"], outline="")
        # Check done
        if typed == target:
            self._finish()

    def _tick(self):
        if not self.active: return
        elapsed = time.time() - self.start_time
        typed = self.input_var.get()
        words = len(typed.split())
        wpm = int((words/elapsed)*60) if elapsed > 0 else 0
        acc = max(0, int((1-self.errors/max(len(typed),1))*100))
        self.lbl_wpm.configure(text=str(wpm))
        self.lbl_acc.configure(text=f"{acc}%")
        self.lbl_time.configure(text=f"{int(elapsed)}s")
        self.lbl_err.configure(text=str(self.errors))
        if self.active:
            self.win.after(200, self._tick)

    def _finish(self):
        self.active = False
        elapsed = time.time() - self.start_time
        words = len(self.text.split())
        wpm = int((words/elapsed)*60)
        acc = max(0, int((1-self.errors/max(len(self.text),1))*100))
        self.entry.configure(state="disabled", bg=self.T["success"]+"33")
        self.result_lbl.configure(
            text=f"✓  Done!  {wpm} WPM  •  {acc}% accuracy  •  {elapsed:.1f}s")

# ─────────────────────────────────────────────────────────────────────────────
# STATS SCREEN WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class StatsWindow:
    def __init__(self, parent, theme, stats, session_keys,
                 key_counts, app_times):
        T = theme
        win = tk.Toplevel(parent)
        win.title("KeyViz — Session Stats")
        win.configure(bg=T["bg"])
        win.geometry("560x520")
        win.resizable(False, False)
        win.attributes("-topmost", True)

        tk.Label(win, text="📊  SESSION STATS", bg=T["bg"], fg=T["accent"],
                 font=("Consolas",14,"bold")).pack(pady=(16,2))

        # Top stats grid
        sg = tk.Frame(win, bg=T["bg"])
        sg.pack(fill="x", padx=16, pady=8)
        stat_data = [
            ("⌨ Total Keys (session)", session_keys),
            ("⌨ Total Keys (all-time)", stats.get("total_keys",0)),
            ("⚡ Max WPM (all-time)", stats.get("max_wpm",0)),
            ("🔑 Unique keys used", len(key_counts)),
            ("🖱 Total Clicks", stats.get("total_clicks",0)),
            ("🎯 Max Streak", stats.get("max_streak",0)),
        ]
        for i,(lbl,val) in enumerate(stat_data):
            row,col = divmod(i,2)
            f = tk.Frame(sg, bg=T["surface"],
                         highlightbackground=T["border"], highlightthickness=1)
            f.grid(row=row,column=col,padx=4,pady=4,sticky="nsew")
            sg.columnconfigure(col, weight=1)
            tk.Label(f,text=lbl,bg=T["surface"],fg=T["muted"],
                     font=("Consolas",8)).pack(anchor="w",padx=8,pady=(6,0))
            tk.Label(f,text=str(val),bg=T["surface"],fg=T["accent"],
                     font=("Consolas",18,"bold")).pack(anchor="w",padx=8,pady=(0,6))

        # Most used keys bar chart
        tk.Label(win, text="TOP 10 KEYS", bg=T["bg"], fg=T["muted"],
                 font=("Consolas",8,"bold")).pack(anchor="w",padx=16,pady=(8,2))

        chart_c = tk.Canvas(win, bg=T["surface"], height=100,
                            highlightthickness=0)
        chart_c.pack(fill="x", padx=16)
        win.update_idletasks()
        cw = chart_c.winfo_width() or 520
        top10 = key_counts.most_common(10)
        if top10:
            maxv = top10[0][1]
            bw = cw // max(len(top10),1) - 4
            for i,(k,v) in enumerate(top10):
                x = 4 + i*(bw+4)
                h = int((v/maxv)*70)
                y = 90-h
                col = blend(T["accent"],T["accent2"],i/max(len(top10)-1,1))
                chart_c.create_rectangle(x,y,x+bw,90,fill=col,outline="")
                chart_c.create_text(x+bw//2,94,text=k[:3],
                                    fill=T["muted"],font=("Consolas",6),anchor="n")
                chart_c.create_text(x+bw//2,y-2,text=str(v),
                                    fill=T["text"],font=("Consolas",6),anchor="s")

        # App usage
        if app_times:
            tk.Label(win, text="APP USAGE", bg=T["bg"], fg=T["muted"],
                     font=("Consolas",8,"bold")).pack(anchor="w",padx=16,pady=(10,2))
            app_frame = tk.Frame(win, bg=T["surface"],
                                 highlightbackground=T["border"],
                                 highlightthickness=1)
            app_frame.pack(fill="x",padx=16,pady=(0,8))
            total_t = sum(app_times.values())
            for i,(app,t) in enumerate(sorted(app_times.items(),
                                               key=lambda x:-x[1])[:6]):
                pct = int(t/total_t*100) if total_t else 0
                af = tk.Frame(app_frame, bg=T["surface"])
                af.pack(fill="x",padx=8,pady=2)
                tk.Label(af,text=f"{app[:20]}",bg=T["surface"],fg=T["text"],
                         font=("Consolas",8),width=20,anchor="w").pack(side="left")
                bar_c = tk.Canvas(af,bg=T["surface"],height=14,width=200,
                                  highlightthickness=0)
                bar_c.pack(side="left",padx=4)
                bar_c.create_rectangle(0,2,int(200*pct/100),12,
                                       fill=T["accent"],outline="")
                tk.Label(af,text=f"{pct}% ({int(t)}s)",bg=T["surface"],
                         fg=T["muted"],font=("Consolas",7)).pack(side="left")

        tk.Label(win,text="✕  Close",bg=T["accent"],fg="#fff",
                 font=("Consolas",9,"bold"),padx=16,pady=6,
                 cursor="hand2").pack(pady=8)
        win.winfo_children()[-1].bind("<Button-1>",lambda e: win.destroy())

# ─────────────────────────────────────────────────────────────────────────────
# ACHIEVEMENT TOAST
# ─────────────────────────────────────────────────────────────────────────────
class AchievementToast:
    def __init__(self, parent, theme, achievement):
        T = theme
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.0)
        self.win.configure(bg=T["success"])

        sw = self.win.winfo_screenwidth()
        self.win.geometry(f"320x70+{sw-340}+20")

        outer = tk.Frame(self.win, bg=T["bg"],
                         highlightbackground=T["success"],
                         highlightthickness=2)
        outer.pack(fill="both", expand=True, padx=2, pady=2)

        tk.Label(outer, text=f"{achievement['icon']}  ACHIEVEMENT UNLOCKED!",
                 bg=T["bg"], fg=T["success"],
                 font=("Consolas",8,"bold")).pack(anchor="w",padx=10,pady=(6,0))
        tk.Label(outer,
                 text=f"{achievement['name']} — {achievement['desc']}",
                 bg=T["bg"], fg=T["text"],
                 font=("Consolas",9)).pack(anchor="w",padx=10,pady=(0,6))

        self._fade_in()

    def _fade_in(self, step=0):
        alpha = step/10
        try:
            self.win.attributes("-alpha", alpha)
        except Exception:
            return
        if step < 10:
            self.win.after(40, lambda: self._fade_in(step+1))
        else:
            self.win.after(3000, self._fade_out)

    def _fade_out(self, step=10):
        try:
            self.win.attributes("-alpha", step/10)
        except Exception:
            return
        if step > 0:
            self.win.after(40, lambda: self._fade_out(step-1))
        else:
            try: self.win.destroy()
            except Exception: pass


# ─────────────────────────────────────────────────────────────────────────────
# TROPHY ROOM WINDOW
# ─────────────────────────────────────────────────────────────────────────────
class TrophyRoom:
    """Full trophy cabinet — shows all achievements, locked/unlocked, with dates."""

    RARITY = {
        "first_key":   ("Common",    "#8888aa"),
        "hundred":     ("Common",    "#8888aa"),
        "thousand":    ("Uncommon",  "#4aff82"),
        "tenthousand": ("Legendary", "#ffcc00"),
        "wpm30":       ("Common",    "#8888aa"),
        "wpm60":       ("Uncommon",  "#4aff82"),
        "wpm100":      ("Epic",      "#cc00ff"),
        "streak10":    ("Common",    "#8888aa"),
        "streak50":    ("Rare",      "#4a9eff"),
        "combo":       ("Common",    "#8888aa"),
        "session30":   ("Uncommon",  "#4aff82"),
        "night_owl":   ("Rare",      "#4a9eff"),
        "mouse100":    ("Common",    "#8888aa"),
        "space_bar":   ("Uncommon",  "#4aff82"),
        "backspace50": ("Common",    "#8888aa"),
    }

    def __init__(self, parent, theme, stats):
        self.T      = theme
        self.stats  = stats
        self.win    = tk.Toplevel(parent)
        self.win.title("KeyViz — Trophy Room 🏆")
        self.win.configure(bg=theme["bg"])
        self.win.geometry("620x580")
        self.win.resizable(True, True)
        self.win.attributes("-topmost", True)
        self._build()

    def _build(self):
        T = self.T
        unlocked_ids = set(self.stats.get("achievements", []))
        unlock_dates = self.stats.get("achievement_dates", {})
        total        = len(ACHIEVEMENTS)
        earned       = len(unlocked_ids)

        # ── Header
        hdr = tk.Frame(self.win, bg=T["surface"])
        hdr.pack(fill="x")

        tk.Label(hdr, text="🏆  TROPHY ROOM",
                 bg=T["surface"], fg=T["accent"],
                 font=("Consolas", 14, "bold")).pack(side="left", padx=16, pady=10)

        # Progress pill
        pct = int(earned / total * 100)
        tk.Label(hdr, text=f"{earned}/{total}  ({pct}%)",
                 bg=T["accent"], fg="#fff",
                 font=("Consolas", 9, "bold"),
                 padx=10, pady=4).pack(side="right", padx=16)

        tk.Frame(self.win, bg=T["border"], height=1).pack(fill="x")

        # ── Progress bar
        prog_frame = tk.Frame(self.win, bg=T["surface2"])
        prog_frame.pack(fill="x")
        prog_c = tk.Canvas(prog_frame, bg=T["surface2"], height=6,
                           highlightthickness=0)
        prog_c.pack(fill="x", padx=0)
        self.win.update_idletasks()
        pw = prog_c.winfo_width() or 620
        prog_c.create_rectangle(0, 0, int(pw * pct / 100), 6,
                                 fill=T["accent"], outline="")

        tk.Frame(self.win, bg=T["border"], height=1).pack(fill="x")

        # ── Filter bar
        filter_frame = tk.Frame(self.win, bg=T["bg"])
        filter_frame.pack(fill="x", padx=12, pady=6)
        tk.Label(filter_frame, text="Show:", bg=T["bg"], fg=T["muted"],
                 font=("Consolas", 8)).pack(side="left", padx=(0, 6))

        self._filter = tk.StringVar(value="all")
        for label, val in [("All", "all"), ("Unlocked ✓", "unlocked"),
                            ("Locked 🔒", "locked")]:
            rb = tk.Radiobutton(filter_frame, text=label,
                                variable=self._filter, value=val,
                                bg=T["bg"], fg=T["text"],
                                selectcolor=T["surface2"],
                                activebackground=T["bg"],
                                font=("Consolas", 8),
                                command=lambda: self._refresh_grid(
                                    scroll_canvas, inner_frame,
                                    unlocked_ids, unlock_dates))
            rb.pack(side="left", padx=4)

        # Rarity legend
        for rarity, col in [("Common","#8888aa"),("Uncommon","#4aff82"),
                             ("Rare","#4a9eff"),("Epic","#cc00ff"),
                             ("Legendary","#ffcc00")]:
            tk.Label(filter_frame, text=f"● {rarity}",
                     bg=T["bg"], fg=col,
                     font=("Consolas", 7)).pack(side="right", padx=3)

        # ── Scrollable grid
        canvas_frame = tk.Frame(self.win, bg=T["bg"])
        canvas_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        scroll_canvas = tk.Canvas(canvas_frame, bg=T["bg"],
                                   highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical",
                                  command=scroll_canvas.yview,
                                  bg=T["bg"])
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        inner_frame = tk.Frame(scroll_canvas, bg=T["bg"])
        win_id = scroll_canvas.create_window(0, 0, window=inner_frame,
                                              anchor="nw")

        def on_configure(e):
            scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
            scroll_canvas.itemconfig(win_id, width=scroll_canvas.winfo_width())
        inner_frame.bind("<Configure>", on_configure)
        scroll_canvas.bind("<Configure>",
                           lambda e: scroll_canvas.itemconfig(
                               win_id, width=e.width))
        # Mousewheel
        def on_wheel(e):
            scroll_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
        scroll_canvas.bind_all("<MouseWheel>", on_wheel)

        self._refresh_grid(scroll_canvas, inner_frame,
                           unlocked_ids, unlock_dates)

        # ── Close button
        tk.Label(self.win, text="  Close  ",
                 bg=T["accent"], fg="#fff",
                 font=("Consolas", 9, "bold"),
                 padx=6, pady=6, cursor="hand2").pack(pady=(0, 10))
        self.win.winfo_children()[-1].bind(
            "<Button-1>", lambda e: self.win.destroy())

    def _refresh_grid(self, canvas, frame, unlocked_ids, unlock_dates):
        T   = self.T
        flt = self._filter.get()
        for w in frame.winfo_children():
            w.destroy()

        shown = []
        for ach in ACHIEVEMENTS:
            is_unlocked = ach["id"] in unlocked_ids
            if flt == "unlocked" and not is_unlocked: continue
            if flt == "locked"   and     is_unlocked: continue
            shown.append((ach, is_unlocked))

        # 2-column grid
        for idx, (ach, is_unlocked) in enumerate(shown):
            row, col = divmod(idx, 2)
            rarity_name, rarity_col = self.RARITY.get(
                ach["id"], ("Common", "#8888aa"))

            card = tk.Frame(frame,
                            bg=T["surface"] if is_unlocked else T["surface2"],
                            highlightbackground=(rarity_col if is_unlocked
                                                 else T["border"]),
                            highlightthickness=2)
            card.grid(row=row, column=col, padx=6, pady=5, sticky="nsew")
            frame.columnconfigure(col, weight=1)

            # Top row: icon + name + rarity
            top = tk.Frame(card,
                           bg=T["surface"] if is_unlocked else T["surface2"])
            top.pack(fill="x", padx=10, pady=(8, 2))

            icon_col = rarity_col if is_unlocked else T["muted"]
            tk.Label(top, text=ach["icon"],
                     bg=top["bg"], fg=icon_col,
                     font=("Consolas", 20)).pack(side="left", padx=(0, 8))

            name_frame = tk.Frame(top, bg=top["bg"])
            name_frame.pack(side="left", fill="x", expand=True)

            name_fg = T["text"] if is_unlocked else T["muted"]
            tk.Label(name_frame, text=ach["name"],
                     bg=top["bg"], fg=name_fg,
                     font=("Consolas", 10, "bold"),
                     anchor="w").pack(fill="x")
            tk.Label(name_frame, text=rarity_name,
                     bg=top["bg"], fg=rarity_col,
                     font=("Consolas", 7, "bold"),
                     anchor="w").pack(fill="x")

            # Lock/unlock badge
            badge_text = "✓ UNLOCKED" if is_unlocked else "🔒 LOCKED"
            badge_bg   = (T["success"] + "33" if is_unlocked
                          else T["surface2"])
            badge_fg   = T["success"] if is_unlocked else T["muted"]
            tk.Label(top, text=badge_text,
                     bg=badge_bg, fg=badge_fg,
                     font=("Consolas", 7, "bold"),
                     padx=6, pady=2).pack(side="right", anchor="n")

            # Description
            desc_bg = T["surface"] if is_unlocked else T["surface2"]
            tk.Label(card, text=ach["desc"],
                     bg=desc_bg, fg=T["muted"],
                     font=("Consolas", 8),
                     anchor="w").pack(fill="x", padx=10, pady=(0, 4))

            # Unlock date or requirement hint
            if is_unlocked:
                date_str = unlock_dates.get(ach["id"], "Unlocked ✓")
                tk.Label(card, text=f"🗓  {date_str}",
                         bg=desc_bg, fg=T["accent"],
                         font=("Consolas", 7),
                         anchor="w").pack(fill="x", padx=10, pady=(0, 6))
            else:
                stat_key, req_val = ach["req"]
                tk.Label(card,
                         text=f"Req: {req_val:,} {stat_key.replace('_',' ')}",
                         bg=desc_bg, fg=T["border"],
                         font=("Consolas", 7),
                         anchor="w").pack(fill="x", padx=10, pady=(0, 6))

# ─────────────────────────────────────────────────────────────────────────────
# GAMING OVERLAY
# ─────────────────────────────────────────────────────────────────────────────
class GamingOverlay:
    def __init__(self, parent, theme, cfg):
        self.T = theme; self.cfg = cfg; self.parent = parent
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", 0.85)
        self.win.configure(bg=self.T["bg"])
        self._drag_x = self._drag_y = 0
        self.win.bind("<ButtonPress-1>", self._ds)
        self.win.bind("<B1-Motion>", self._dm)
        self._build()
        self._place()
        self._tick()

    def _place(self):
        sw = self.win.winfo_screenwidth()
        px = self.cfg.get("gaming_pos_x", -1)
        py = self.cfg.get("gaming_pos_y", -1)
        if px != -1:
            self.win.geometry(f"+{px}+{py}")
        else:
            self.win.geometry(f"+{sw//2-180}+20")

    def _build(self):
        T = self.T
        outer = tk.Frame(self.win, bg=T["bg"],
                         highlightbackground=T["accent"],
                         highlightthickness=1)
        outer.pack(fill="both", expand=True)

        bar = tk.Frame(outer, bg=T["surface"])
        bar.pack(fill="x")
        tk.Label(bar, text="🎮  GAMING MODE", bg=T["surface"], fg=T["accent"],
                 font=("Consolas",8,"bold")).pack(side="left",padx=8,pady=3)
        cl = tk.Label(bar, text="✕", bg=T["surface"], fg=T["muted"],
                      font=("Consolas",9), cursor="hand2")
        cl.pack(side="right",padx=6)
        cl.bind("<Button-1>", lambda e: self.win.destroy())

        self.games_frame = tk.Frame(outer, bg=T["bg"])
        self.games_frame.pack(fill="x",padx=6,pady=4)

        self.no_game_lbl = tk.Label(self.games_frame,
                                    text="No games detected",
                                    bg=T["bg"], fg=T["muted"],
                                    font=("Consolas",8))
        self.no_game_lbl.pack()

        self.stats_lbl = tk.Label(outer, text="",
                                  bg=T["bg"], fg=T["text"],
                                  font=("Consolas",8))
        self.stats_lbl.pack(padx=8,pady=(0,4))

    def update_stats(self, keys, wpm, clicks):
        try:
            self.stats_lbl.configure(
                text=f"⌨ {keys} keys  ⚡ {wpm} wpm  🖱 {clicks} clicks")
        except Exception:
            pass

    def _tick(self):
        try:
            if not self.win.winfo_exists():
                return
            for w in self.games_frame.winfo_children():
                w.destroy()
            games = get_running_games()
            if games:
                for g in games:
                    tk.Label(self.games_frame, text=f"🎮 {g}",
                             bg=self.T["bg"], fg=self.T["success"],
                             font=("Consolas",8,"bold")).pack(anchor="w",padx=4)
            else:
                tk.Label(self.games_frame, text="No games detected",
                         bg=self.T["bg"], fg=self.T["muted"],
                         font=("Consolas",8)).pack()
            self.win.after(5000, self._tick)
        except Exception:
            pass

    def _ds(self, e): self._drag_x = e.x; self._drag_y = e.y
    def _dm(self, e):
        x = self.win.winfo_x()+e.x-self._drag_x
        y = self.win.winfo_y()+e.y-self._drag_y
        self.win.geometry(f"+{x}+{y}")
        self.cfg["gaming_pos_x"] = x; self.cfg["gaming_pos_y"] = y


# ─────────────────────────────────────────────────────────────────────────────
# RGB ENGINE  (runs in its own thread, pushes hue to shared state)
# ─────────────────────────────────────────────────────────────────────────────
class RGBEngine:
    """Generates a smoothly cycling hue that other widgets can read."""
    def __init__(self):
        self.hue      = 0.0          # 0–1
        self.running  = False
        self._thread  = None
        self.speed    = 3.0          # degrees/second
        self.mode     = "cycle"      # cycle | pulse | wave
        self._pulse_v = 0.0
        self._pulse_d = 1

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _run(self):
        while self.running:
            self.hue = (self.hue + self.speed / 360 / 30) % 1.0   # ~30 fps
            if self.mode == "pulse":
                self._pulse_v += self._pulse_d * 0.04
                if self._pulse_v >= 1.0: self._pulse_v = 1.0; self._pulse_d = -1
                if self._pulse_v <= 0.0: self._pulse_v = 0.0; self._pulse_d =  1
            time.sleep(1/30)

    def get_color(self, saturation=1.0, value=1.0):
        """Return current RGB hex."""
        v = value
        if self.mode == "pulse":
            v = 0.4 + self._pulse_v * 0.6
        r, g, b = colorsys.hsv_to_rgb(self.hue, saturation, v)
        return rgb_to_hex(r*255, g*255, b*255)

    def get_wave_color(self, offset=0.0):
        """Return color at hue+offset (for wave effect across keys)."""
        h = (self.hue + offset) % 1.0
        r, g, b = colorsys.hsv_to_rgb(h, 1.0, 1.0)
        return rgb_to_hex(r*255, g*255, b*255)

RGB_ENGINE = RGBEngine()


# ─────────────────────────────────────────────────────────────────────────────
# PARTICLE SYSTEM  (canvas overlay, spawns on fast typing)
# ─────────────────────────────────────────────────────────────────────────────
class ParticleOverlay:
    """Full-screen transparent Toplevel for particle bursts — separate from main root."""

    SHAPES = ["circle", "star", "spark"]

    def __init__(self, root, theme):
        self.root = root
        self.T    = theme
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.sw = sw; self.sh = sh

        # Use a separate Toplevel so transparentcolor only affects this window
        self._win = tk.Toplevel(root)
        self._win.overrideredirect(True)
        self._win.attributes("-topmost", True)
        self._win.attributes("-transparentcolor", "#010101")
        self._win.geometry(f"{sw}x{sh}+0+0")
        self._win.configure(bg="#010101")
        # Click-through: Windows only
        try:
            import ctypes
            hwnd = ctypes.windll.user32.FindWindowW(None, None)
            GWL_EXSTYLE = -20
            WS_EX_LAYERED    = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            style = ctypes.windll.user32.GetWindowLongW(int(self._win.frame()), GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(
                int(self._win.frame()), GWL_EXSTYLE,
                style | WS_EX_LAYERED | WS_EX_TRANSPARENT)
        except Exception:
            pass

        self._canvas = tk.Canvas(self._win, width=sw, height=sh,
                                  highlightthickness=0, bg="#010101")
        self._canvas.pack()
        self._particles = []
        self._running   = False

    def burst(self, x, y, color, count=18):
        try:
            if not self._win.winfo_exists():
                return
        except Exception:
            return
        for _ in range(count):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(2, 9)
            life  = random.uniform(0.5, 1.1)
            size  = random.uniform(3, 8)
            shape = random.choice(self.SHAPES)
            self._particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle)*speed,
                "vy": math.sin(angle)*speed - random.uniform(1, 4),
                "life": life, "max_life": life,
                "size": size, "color": color, "shape": shape,
            })
        if not self._running:
            self._running = True
            self._animate()

    def _animate(self):
        try:
            if not self._win.winfo_exists():
                self._running = False
                return
        except Exception:
            self._running = False
            return
        now_alive = []
        c = self._canvas
        c.delete("all")
        for p in self._particles:
            p["life"] -= 1/30
            if p["life"] <= 0:
                continue
            p["x"]  += p["vx"]
            p["y"]  += p["vy"]
            p["vy"] += 0.35
            alpha = p["life"] / p["max_life"]
            col = blend(p["color"], "#010101", alpha)
            s   = max(1, p["size"] * alpha)
            x, y = p["x"], p["y"]
            if p["shape"] == "circle":
                c.create_oval(x-s, y-s, x+s, y+s, fill=col, outline="")
            elif p["shape"] == "spark":
                ex = x + p["vx"]*2; ey = y + p["vy"]*2
                c.create_line(x, y, ex, ey, fill=col, width=max(1,int(s/2)))
            else:
                c.create_line(x-s, y, x+s, y, fill=col, width=2)
                c.create_line(x, y-s, x, y+s, fill=col, width=2)
                d = s*0.7
                c.create_line(x-d, y-d, x+d, y+d, fill=col, width=1)
                c.create_line(x+d, y-d, x-d, y+d, fill=col, width=1)
            now_alive.append(p)
        self._particles = now_alive
        if self._particles:
            self._canvas.after(33, self._animate)
        else:
            self._running = False
            c.delete("all")


# ─────────────────────────────────────────────────────────────────────────────
# KEY HOLD DURATION TRACKER
# ─────────────────────────────────────────────────────────────────────────────
class HoldTracker:
    """Tracks press/release times and keeps per-key averages."""
    def __init__(self):
        self._press_times = {}          # key_label -> press timestamp
        self.hold_totals  = {}          # key_label -> total hold ms
        self.hold_counts  = {}          # key_label -> number of holds
        self.last_hold_ms = 0           # most recent hold in ms

    def on_press(self, label):
        self._press_times[label] = time.time()

    def on_release(self, label):
        if label in self._press_times:
            ms = int((time.time() - self._press_times.pop(label)) * 1000)
            self.hold_totals[label] = self.hold_totals.get(label, 0) + ms
            self.hold_counts[label] = self.hold_counts.get(label, 0) + 1
            self.last_hold_ms = ms

    def avg_ms(self, label):
        c = self.hold_counts.get(label, 0)
        return int(self.hold_totals.get(label, 0) / c) if c else 0

    def top_held(self, n=5):
        """Return [(label, avg_ms)] sorted by longest average hold."""
        avgs = [(k, int(self.hold_totals[k]/self.hold_counts[k]))
                for k in self.hold_counts if self.hold_counts[k] > 0]
        return sorted(avgs, key=lambda x: -x[1])[:n]

    def top_tapped(self, n=5):
        """Return [(label, avg_ms)] sorted by shortest average hold (fastest tappers)."""
        avgs = [(k, int(self.hold_totals[k]/self.hold_counts[k]))
                for k in self.hold_counts if self.hold_counts[k] > 0]
        return sorted(avgs, key=lambda x: x[1])[:n]

# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
class KeyVizApp:
    def __init__(self):
        self.cfg   = load_config()
        self.stats = load_stats()
        self.T     = self._get_theme()
        self.visible = True

        # Session state
        self.active_keys    = []
        self.held_modifiers = set()
        self.key_counts     = Counter(self.stats.get("key_counts", {}))
        self.mouse_counts   = Counter()
        self.session_keys   = 0
        self.session_start  = time.time()
        self.wpm_window     = deque(maxlen=1000)
        self._last_wpm_push = time.time()
        self._last_stat_save = time.time()
        self.lock           = threading.Lock()

        # Streak tracking
        self.streak         = 0
        self._streak_timer  = None

        # App tracking
        self.app_times      = {}
        self._cur_app       = ""
        self._app_start     = time.time()

        # UI refs
        self._key_widgets   = []
        self._hist_widgets  = []
        self._setting_vars  = {}
        self.mod_widgets    = {}
        self._drag_x = self._drag_y = 0
        self._gaming_overlay = None
        self._pending_achievements = []

        # New v4 systems
        self.hold_tracker     = HoldTracker()
        self._particle_overlay = None
        # Start RGB if enabled
        if self.cfg.get("rgb_enabled"):
            RGB_ENGINE.speed = self.cfg.get("rgb_speed", 3.0)
            RGB_ENGINE.mode  = self.cfg.get("rgb_mode",  "cycle")
            RGB_ENGINE.start()

        self._build_ui()
        self._start_listeners()
        self._start_app_tracker()
        self._tick()

    def _get_theme(self):
        name = self.cfg.get("theme","dark")
        if name == "custom":
            t = THEMES["custom"].copy()
            t.update(self.cfg.get("custom_theme",{}))
            return t
        return THEMES.get(name, THEMES["dark"]).copy()

    # ─────────────────────────────────────────────
    # UI BUILD
    # ─────────────────────────────────────────────
    def _build_ui(self):
        self.root = tk.Tk()
        self.root.title("KeyViz")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", self.cfg["always_on_top"])
        self.root.attributes("-alpha", self.cfg["opacity"])
        self.root.configure(bg=self.T["bg"])
        self.root.resizable(False, False)
        self.root.bind("<ButtonPress-1>", self._drag_start)
        self.root.bind("<B1-Motion>",     self._drag_motion)
        self.root.bind("<ButtonRelease-1>",self._drag_end)
        self.root.bind("<Button-3>",      self._ctx_menu)
        self._build_inner()
        self._reposition()
        # Particle overlay spans full screen
        if self.cfg.get("particles_enabled"):
            try:
                self._particle_overlay = ParticleOverlay(self.root, self.T)
            except Exception:
                self._particle_overlay = None

    def _build_inner(self):
        T = self.T
        for w in self.root.winfo_children():
            w.destroy()
        self._key_widgets.clear(); self._hist_widgets.clear()
        self.mod_widgets.clear()
        self.root.configure(bg=T["bg"])

        self.outer = tk.Frame(self.root, bg=T["bg"],
                              highlightbackground=T["border"],
                              highlightthickness=1)
        self.outer.pack(fill="both", expand=True)

        # ── Title bar
        bar = tk.Frame(self.outer, bg=T["surface"])
        bar.pack(fill="x")
        tk.Label(bar, text=f"⌨  KeyViz v{APP_VERSION}",
                 bg=T["surface"], fg=T["muted"],
                 font=("Consolas",8,"bold")).pack(side="left",padx=8,pady=4)
        for sym, cmd in [("✕",self._quit),("⚙",self._open_settings),
                         ("📊",self._open_stats),("🏆",self._open_trophies),
                         ("👁",self._toggle_vis)]:
            lbl = tk.Label(bar, text=sym, bg=T["surface"], fg=T["muted"],
                           font=("Consolas",10), cursor="hand2")
            lbl.pack(side="right", padx=4)
            lbl.bind("<Button-1>", lambda e,c=cmd: c())
        hk = self.cfg.get("toggle_hotkey","f9").upper()
        tk.Label(bar, text=f"[{hk}]", bg=T["surface"], fg=T["border"],
                 font=("Consolas",7)).pack(side="right",padx=4)
        tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── Clock & session timer
        if self.cfg.get("show_clock", True):
            cf = tk.Frame(self.outer, bg=T["surface"])
            cf.pack(fill="x")
            self.clock_lbl = tk.Label(cf, text="", bg=T["surface"],
                                      fg=T["accent"], font=("Consolas",9,"bold"))
            self.clock_lbl.pack(side="left", padx=10, pady=3)
            self.session_lbl = tk.Label(cf, text="", bg=T["surface"],
                                        fg=T["muted"], font=("Consolas",8))
            self.session_lbl.pack(side="right", padx=10)
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── Glow key display
        self.glow_canvas = GlowCanvas(self.outer, T,
                                       width=self.cfg.get("width",360), height=76)
        self.glow_canvas.pack(fill="x")
        tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── Modifier badges
        if self.cfg["show_modifiers"]:
            mf = tk.Frame(self.outer, bg=T["bg"])
            mf.pack(fill="x", padx=8, pady=(4,4))
            for mod in ["Ctrl","Alt","Shift","Win","Caps"]:
                lbl = tk.Label(mf, text=mod, bg=T["key_bg"], fg=T["muted"],
                               font=("Consolas",8,"bold"), padx=6, pady=2,
                               highlightbackground=T["key_border"],
                               highlightthickness=1)
                lbl.pack(side="left", padx=2)
                self.mod_widgets[mod] = lbl

            # Streak display
            self.streak_lbl = tk.Label(mf, text="", bg=T["bg"],
                                       fg=T["success"],
                                       font=("Consolas",8,"bold"))
            self.streak_lbl.pack(side="right", padx=4)
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── Stats row
        if self.cfg["show_stats"]:
            sr = tk.Frame(self.outer, bg=T["surface"])
            sr.pack(fill="x")
            self.sv_keys   = self._stat_col(sr,"0","KEYS")
            self.sv_wpm    = self._stat_col(sr,"0","WPM")
            self.sv_clicks = self._stat_col(sr,"0","CLICKS")
            self.sv_streak = self._stat_col(sr,"0","STREAK")
            self.sv_top    = self._stat_col(sr,"—","TOP KEY")
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── WPM graph
        if self.cfg.get("show_wpm_graph", True):
            self.wpm_graph = WPMGraph(self.outer, T,
                                      width=self.cfg.get("width",360)-16)
            self.wpm_graph.pack(padx=8, pady=6)
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── App tracker
        if self.cfg.get("show_app_tracker", True):
            af = tk.Frame(self.outer, bg=T["surface"])
            af.pack(fill="x")
            tk.Label(af, text="🖥", bg=T["surface"], fg=T["muted"],
                     font=("Consolas",9)).pack(side="left",padx=8,pady=3)
            self.app_lbl = tk.Label(af, text="Tracking...",
                                    bg=T["surface"], fg=T["muted"],
                                    font=("Consolas",8))
            self.app_lbl.pack(side="left")
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── Mouse log
        if self.cfg["show_mouse"]:
            mrow = tk.Frame(self.outer, bg=T["surface"])
            mrow.pack(fill="x")
            tk.Label(mrow, text="🖱", bg=T["surface"], fg=T["muted"],
                     font=("Consolas",9)).pack(side="left",padx=8,pady=3)
            self.mouse_lbl = tk.Label(mrow, text="No clicks yet",
                                      bg=T["surface"], fg=T["muted"],
                                      font=("Consolas",8))
            self.mouse_lbl.pack(side="left")
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── Heatmap
        if self.cfg.get("show_heatmap", True):
            hdr = tk.Frame(self.outer, bg=T["surface"])
            hdr.pack(fill="x")
            tk.Label(hdr, text="HEATMAP", bg=T["surface"], fg=T["muted"],
                     font=("Consolas",7,"bold")).pack(side="left",padx=8,pady=3)
            self.heatmap = HeatmapWidget(self.outer, T,
                                          width=self.cfg.get("width",360))
            self.heatmap.pack(fill="x", padx=0)
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── Hold duration tracker row
        if self.cfg.get("show_hold_tracker", True):
            hold_row = tk.Frame(self.outer, bg=T["surface"])
            hold_row.pack(fill="x")
            tk.Label(hold_row, text="⏱", bg=T["surface"], fg=T["muted"],
                     font=("Consolas",9)).pack(side="left", padx=8, pady=3)
            self.hold_lbl = tk.Label(hold_row, text="Hold duration tracking...",
                                     bg=T["surface"], fg=T["muted"],
                                     font=("Consolas",8))
            self.hold_lbl.pack(side="left")
            tk.Frame(self.outer, bg=T["border"], height=1).pack(fill="x")

        # ── History log
        if self.cfg["show_history"]:
            hdr2 = tk.Frame(self.outer, bg=T["surface"])
            hdr2.pack(fill="x")
            tk.Label(hdr2, text="HISTORY", bg=T["surface"], fg=T["muted"],
                     font=("Consolas",7,"bold")).pack(side="left",padx=8,pady=3)
            clr = tk.Label(hdr2, text="clear", bg=T["surface"], fg=T["muted"],
                           font=("Consolas",7), cursor="hand2")
            clr.pack(side="right",padx=8)
            clr.bind("<Button-1>", lambda e: self._clear_history())
            self.hist_canvas = tk.Canvas(self.outer, bg=T["bg"],
                                          height=72, highlightthickness=0)
            self.hist_canvas.pack(fill="x")
            self.hist_inner = tk.Frame(self.hist_canvas, bg=T["bg"])
            self.hist_canvas.create_window(0,0,window=self.hist_inner,anchor="nw")
            self.hist_inner.bind("<Configure>",
                lambda e: self.hist_canvas.configure(
                    scrollregion=self.hist_canvas.bbox("all")))

    def _stat_col(self, parent, val, label):
        T = self.T
        f = tk.Frame(parent, bg=T["surface"])
        f.pack(side="left", expand=True, fill="x", pady=5)
        v = tk.Label(f, text=val, bg=T["surface"], fg=T["accent"],
                     font=("Consolas",15,"bold"))
        v.pack()
        tk.Label(f, text=label, bg=T["surface"], fg=T["muted"],
                 font=("Consolas",6,"bold")).pack()
        return v

    # ─────────────────────────────────────────────
    # POSITIONING
    # ─────────────────────────────────────────────
    def _reposition(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w  = self.cfg.get("width",360)
        h  = self.root.winfo_reqheight()
        px, py = self.cfg.get("pos_x",-1), self.cfg.get("pos_y",-1)
        if px != -1 and py != -1:
            self.root.geometry(f"{w}x{h}+{px}+{py}")
        else:
            pad = 20
            c = self.cfg.get("corner","bottom-left")
            if   c=="bottom-left":  x,y = pad, sh-h-60
            elif c=="bottom-right": x,y = sw-w-pad, sh-h-60
            elif c=="top-left":     x,y = pad, pad+30
            else:                   x,y = sw-w-pad, pad+30
            self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _drag_start(self,e): self._drag_x=e.x; self._drag_y=e.y
    def _drag_motion(self,e):
        x=self.root.winfo_x()+e.x-self._drag_x
        y=self.root.winfo_y()+e.y-self._drag_y
        self.root.geometry(f"+{x}+{y}")
    def _drag_end(self,e):
        self.cfg["pos_x"]=self.root.winfo_x()
        self.cfg["pos_y"]=self.root.winfo_y()
        save_config(self.cfg)

    # ─────────────────────────────────────────────
    # TICK
    # ─────────────────────────────────────────────
    def _tick(self):
        now = time.time()
        fade_s = self.cfg["fade_ms"]/1000
        with self.lock:
            self.active_keys = [(l,m,c,ts) for l,m,c,ts in self.active_keys
                                if now-ts < fade_s]
        self._update_clock(now)
        self._update_modifiers()
        self._update_stats()
        # WPM graph
        if now-self._last_wpm_push >= 1.0 and self.cfg.get("show_wpm_graph"):
            wpm = self._calc_wpm()
            try:
                if hasattr(self,"wpm_graph") and self.wpm_graph.winfo_exists():
                    self.wpm_graph.push(wpm)
            except Exception: pass
            self._last_wpm_push = now
        # Heatmap refresh every 2s
        if int(now*0.5)%2==0 and hasattr(self,"heatmap"):
            try:
                if self.heatmap.winfo_exists():
                    self.heatmap.update_counts(dict(self.key_counts))
            except Exception: pass
        # Gaming overlay stats
        if self._gaming_overlay:
            try:
                wpm = self._calc_wpm()
                self._gaming_overlay.update_stats(
                    self.session_keys, wpm,
                    sum(self.mouse_counts.values()))
            except Exception: pass
        # Pending achievements
        if self._pending_achievements:
            ach = self._pending_achievements.pop(0)
            AchievementToast(self.root, self.T, ach)
        # Auto-save stats every 30s
        if now-self._last_stat_save > 30:
            self._save_stats_snapshot()
            self._last_stat_save = now

        # RGB border cycling
        if self.cfg.get("rgb_enabled"):
            try:
                col = RGB_ENGINE.get_color(saturation=0.9, value=0.95)
                self.outer.configure(highlightbackground=col)
                # Also tint modifier badges with wave offset
                for i,(name,w) in enumerate(self.mod_widgets.items()):
                    if w.winfo_exists():
                        wc = RGB_ENGINE.get_wave_color(i*0.07)
                        w.configure(highlightbackground=wc)
            except Exception:
                pass

        # Particle explosions on fast typing
        if self.cfg.get("particles_enabled"):
            wpm = self._calc_wpm()
            thresh = self.cfg.get("particle_threshold_wpm", 60)
            if wpm >= thresh and self._particle_overlay:
                try:
                    # Burst near a random key widget position
                    kws = self._key_widgets
                    if kws:
                        w = random.choice(kws)
                        rx = self.root.winfo_x() + w.winfo_x() + w.winfo_width()//2
                        ry = self.root.winfo_y() + w.winfo_y() + w.winfo_height()//2
                        col = RGB_ENGINE.get_color() if self.cfg.get("rgb_enabled") else self.T["accent"]
                        self._particle_overlay.burst(rx, ry, col, count=14)
                except Exception:
                    pass

        # Hold tracker display update
        if self.cfg.get("show_hold_tracker"):
            try:
                if hasattr(self,"hold_lbl") and self.hold_lbl.winfo_exists():
                    ms = self.hold_tracker.last_hold_ms
                    top = self.hold_tracker.top_held(1)
                    if top:
                        k,avg = top[0]
                        self.hold_lbl.configure(
                            text=f"Last: {ms}ms  |  Longest avg: {k} {avg}ms")
            except Exception:
                pass

        self.root.after(50, self._tick)

    def _update_clock(self, now):
        try:
            if hasattr(self,"clock_lbl") and self.clock_lbl.winfo_exists():
                self.clock_lbl.configure(text=datetime.now().strftime("🕐 %H:%M:%S"))
                elapsed = int(now-self.session_start)
                h,r = divmod(elapsed,3600); m,s = divmod(r,60)
                self.session_lbl.configure(
                    text=f"Session {h:02d}:{m:02d}:{s:02d}")
        except Exception: pass

    def _calc_wpm(self):
        now = time.time()
        while self.wpm_window and now-self.wpm_window[0]>60:
            self.wpm_window.popleft()
        return round(len(self.wpm_window)/5)

    def _update_stats(self):
        wpm = self._calc_wpm()
        try:
            if hasattr(self,"sv_keys") and self.sv_keys.winfo_exists():
                self.sv_keys.configure(text=str(self.session_keys))
                self.sv_wpm.configure(text=str(wpm))
                self.sv_clicks.configure(text=str(sum(self.mouse_counts.values())))
                self.sv_streak.configure(text=str(self.streak))
                if self.key_counts:
                    top = self.key_counts.most_common(1)[0][0]
                    self.sv_top.configure(text=top[:6])
        except Exception: pass
        try:
            if hasattr(self,"mouse_lbl") and self.mouse_lbl.winfo_exists():
                parts=[f"{b}:{c}" for b,c in self.mouse_counts.most_common(3)]
                self.mouse_lbl.configure(
                    text="  ".join(parts) if parts else "No clicks yet")
        except Exception: pass
        try:
            if hasattr(self,"streak_lbl") and self.streak_lbl.winfo_exists():
                if self.streak >= 10:
                    self.streak_lbl.configure(
                        text=f"🔥 {self.streak} streak!")
                else:
                    self.streak_lbl.configure(text="")
        except Exception: pass
        try:
            if hasattr(self,"app_lbl") and self.app_lbl.winfo_exists():
                self.app_lbl.configure(text=self._cur_app[:30] if self._cur_app else "")
        except Exception: pass

    def _update_modifiers(self):
        if not self.mod_widgets: return
        mod_map={"Ctrl":{"Ctrl"},"Alt":{"Alt","AltGr"},
                 "Shift":{"Shift"},"Win":{"Win"},"Caps":{"Caps"}}
        active={get_key_label(k) for k in self.held_modifiers}
        for name,variants in mod_map.items():
            w=self.mod_widgets.get(name)
            if not w: continue
            try:
                if not w.winfo_exists(): continue
                if variants & active:
                    w.configure(fg=self.T["accent2"],
                                highlightbackground=self.T["accent2"],
                                bg=self.T["surface2"])
                else:
                    w.configure(fg=self.T["muted"],
                                highlightbackground=self.T["key_border"],
                                bg=self.T["key_bg"])
            except Exception: pass

    # ─────────────────────────────────────────────
    # HISTORY
    # ─────────────────────────────────────────────
    def _add_history(self, label, is_mod, is_combo):
        if not self.cfg["show_history"] or not hasattr(self,"hist_inner"):
            return
        T=self.T
        bg=T["surface2"] if is_mod else T["key_bg"]
        fg=T["accent2"] if is_mod else (T["accent"] if is_combo else T["muted"])
        border=T["accent"] if is_combo else T["key_border"]
        lbl=tk.Label(self.hist_inner, text=label, bg=bg, fg=fg,
                     font=("Consolas",8,"bold"), padx=5, pady=2,
                     highlightbackground=border, highlightthickness=1)
        lbl.pack(side="left",padx=2,pady=5)
        self._hist_widgets.append(lbl)
        while len(self._hist_widgets) > self.cfg["history_max"]:
            self._hist_widgets[0].destroy(); self._hist_widgets.pop(0)
        self.root.after(30, lambda: self.hist_canvas.xview_moveto(1.0))

    def _clear_history(self):
        for w in self._hist_widgets:
            try: w.destroy()
            except: pass
        self._hist_widgets.clear()

    # ─────────────────────────────────────────────
    # ACHIEVEMENTS
    # ─────────────────────────────────────────────
    def _check_achievements(self):
        unlocked = set(self.stats.get("achievements",[]))
        s = self.stats
        check_map = {
            "total_keys":     s.get("total_keys",0),
            "max_wpm":        s.get("max_wpm",0),
            "max_streak":     s.get("max_streak",0),
            "total_combos":   s.get("total_combos",0),
            "total_clicks":   s.get("total_clicks",0),
            "space_count":    s.get("space_count",0),
            "backspace_count":s.get("backspace_count",0),
            "night_typing":   s.get("night_typing",0),
            "session_min":    int((time.time()-self.session_start)/60),
        }
        for ach in ACHIEVEMENTS:
            if ach["id"] in unlocked: continue
            stat_key, req_val = ach["req"]
            if check_map.get(stat_key,0) >= req_val:
                unlocked.add(ach["id"])
                self.stats["achievements"] = list(unlocked)
                # Save unlock date
                dates = self.stats.get("achievement_dates", {})
                dates[ach["id"]] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.stats["achievement_dates"] = dates
                self._pending_achievements.append(ach)

    def _save_stats_snapshot(self):
        wpm = self._calc_wpm()
        self.stats["total_keys"] = (self.stats.get("total_keys",0)
                                    + self.session_keys)
        self.session_keys = 0
        if wpm > self.stats.get("max_wpm",0):
            self.stats["max_wpm"] = wpm
        self.stats["total_clicks"] = (self.stats.get("total_clicks",0)
                                      + sum(self.mouse_counts.values()))
        self.mouse_counts.clear()
        # Key counts
        kc = self.stats.get("key_counts",{})
        for k,v in self.key_counts.items():
            kc[k] = kc.get(k,0)+v
        self.stats["key_counts"] = kc
        self.key_counts.clear()
        # App times
        at = self.stats.get("app_times",{})
        for app,t in self.app_times.items():
            at[app] = at.get(app,0)+t
        self.stats["app_times"] = at
        # Night typing
        if datetime.now().hour >= 23 or datetime.now().hour < 4:
            self.stats["night_typing"] = self.stats.get("night_typing",0)+1
        save_stats(self.stats)
        self._check_achievements()

    # ─────────────────────────────────────────────
    # APP TRACKER
    # ─────────────────────────────────────────────
    def _start_app_tracker(self):
        def track():
            while True:
                try:
                    name, title = get_active_app()
                    display = f"{name}: {title}" if title and title != name else name
                    if display != self._cur_app:
                        if self._cur_app:
                            elapsed = time.time()-self._app_start
                            self.app_times[self._cur_app] = (
                                self.app_times.get(self._cur_app,0)+elapsed)
                        self._cur_app = display
                        self._app_start = time.time()
                except Exception:
                    pass
                time.sleep(2)
        t = threading.Thread(target=track, daemon=True)
        t.start()

    # ─────────────────────────────────────────────
    # LISTENERS
    # ─────────────────────────────────────────────
    def _start_listeners(self):
        def on_press(key):
            label = get_key_label(key)
            mod   = is_modifier(key)
            self.hold_tracker.on_press(label)
            if mod:
                self.held_modifiers.add(key)
            else:
                self.session_keys += 1
                self.wpm_window.append(time.time())
                self.key_counts[label] += 1
                # Streak
                self.streak += 1
                if self.streak > self.stats.get("max_streak",0):
                    self.stats["max_streak"] = self.streak
                if self._streak_timer:
                    try: self._streak_timer.cancel()
                    except: pass
                self._streak_timer = threading.Timer(
                    2.0, self._reset_streak)
                self._streak_timer.daemon = True
                self._streak_timer.start()
                # Special key counts
                if label == "Space":
                    self.stats["space_count"] = self.stats.get("space_count",0)+1
                if label == "⌫":
                    self.stats["backspace_count"] = self.stats.get("backspace_count",0)+1
                if self.cfg.get("sound_enabled"):
                    self.root.after(0, self._play_click)

            is_combo = bool(self.held_modifiers) and not mod
            if is_combo:
                self.stats["total_combos"] = self.stats.get("total_combos",0)+1

            # Add to glow canvas
            self.root.after(0, lambda l=label,m=mod,c=is_combo:
                            self.glow_canvas.add_key(l,m,c)
                            if hasattr(self,"glow_canvas") else None)

            with self.lock:
                if (self.active_keys and
                        self.active_keys[-1][0]==label and not mod):
                    l,m,c,_ = self.active_keys[-1]
                    self.active_keys[-1] = (l,m,c,time.time())
                else:
                    self.active_keys.append((label,mod,is_combo,time.time()))
                    mk = self.cfg["max_keys"]
                    if len(self.active_keys) > mk:
                        self.active_keys = self.active_keys[-mk:]

            self.root.after(0, lambda: self._add_history(label,mod,is_combo))

            # Toggle hotkey
            try:
                hk = self.cfg.get("toggle_hotkey","f9")
                if hasattr(keyboard.Key,hk) and key==getattr(keyboard.Key,hk):
                    self.root.after(0, self._toggle_vis)
            except Exception: pass

        def on_release(key):
            label = get_key_label(key)
            self.hold_tracker.on_release(label)
            self.held_modifiers.discard(key)

        def on_click(x,y,button,pressed):
            if pressed:
                self.mouse_counts[str(button).replace("Button.","").capitalize()] += 1
                if self.cfg["show_mouse"]:
                    label = f"🖱{str(button).replace('Button.','').capitalize()}"
                    with self.lock:
                        self.active_keys.append((label,False,False,time.time()))
                        if len(self.active_keys)>self.cfg["max_keys"]:
                            self.active_keys=self.active_keys[-self.cfg["max_keys"]:]
                    self.root.after(0,lambda: self._add_history(label,False,False))

        self._kb = keyboard.Listener(on_press=on_press,on_release=on_release)
        self._kb.daemon = True; self._kb.start()
        self._ms = mouse.Listener(on_click=on_click)
        self._ms.daemon = True; self._ms.start()

    def _reset_streak(self):
        self.streak = 0

    def _play_click(self):
        try:
            import winsound; winsound.Beep(900,18)
        except Exception: pass

    def _toggle_vis(self):
        self.visible = not self.visible
        self.root.attributes("-alpha",
                             self.cfg["opacity"] if self.visible else 0.0)

    # ─────────────────────────────────────────────
    # CONTEXT MENU
    # ─────────────────────────────────────────────
    def _ctx_menu(self, e):
        T = self.T
        m = tk.Menu(self.root, tearoff=0, bg=T["surface"], fg=T["text"],
                    activebackground=T["accent"], activeforeground="#fff",
                    font=("Consolas",9))
        m.add_command(label="⚙  Settings",    command=self._open_settings)
        m.add_command(label="📊  Stats",       command=self._open_stats)
        m.add_command(label="🏆  Trophy Room", command=self._open_trophies)
        m.add_command(label="⚡  Speed Test",  command=self._open_speed_test)
        m.add_command(label="🎮  Gaming Mode", command=self._toggle_gaming)
        m.add_separator()
        thm = tk.Menu(m,tearoff=0,bg=T["surface"],fg=T["text"],
                      activebackground=T["accent"],activeforeground="#fff",
                      font=("Consolas",9))
        for k,v in THEMES.items():
            thm.add_command(label=f"  {v['name']}",
                            command=lambda k=k: self._set_theme(k))
        m.add_cascade(label="🎨  Theme", menu=thm)
        cn = tk.Menu(m,tearoff=0,bg=T["surface"],fg=T["text"],
                     activebackground=T["accent"],activeforeground="#fff",
                     font=("Consolas",9))
        for c in ["bottom-left","bottom-right","top-left","top-right"]:
            cn.add_command(label=f"  {c}",
                           command=lambda cc=c: self._set_corner(cc))
        m.add_cascade(label="📍  Corner", menu=cn)
        m.add_separator()
        m.add_command(label="🗑  Clear history", command=self._clear_history)
        hk=self.cfg.get("toggle_hotkey","f9").upper()
        m.add_command(label=f"👁  Toggle [{hk}]", command=self._toggle_vis)
        m.add_separator()
        m.add_command(label="✕  Quit", command=self._quit)
        m.tk_popup(e.x_root, e.y_root)

    def _toggle_gaming(self):
        if self._gaming_overlay:
            try: self._gaming_overlay.win.destroy()
            except: pass
            self._gaming_overlay = None
        else:
            self._gaming_overlay = GamingOverlay(self.root, self.T, self.cfg)

    # ─────────────────────────────────────────────
    # OPEN WINDOWS
    # ─────────────────────────────────────────────
    def _open_stats(self):
        StatsWindow(self.root, self.T, self.stats,
                    self.session_keys, self.key_counts,
                    self.app_times)

    def _open_trophies(self):
        # Save latest snapshot so trophy room shows current progress
        self._save_stats_snapshot()
        TrophyRoom(self.root, self.T, self.stats)

    def _open_speed_test(self):
        SpeedTestWindow(self.root, self.T)

    # ─────────────────────────────────────────────
    # SETTINGS WINDOW
    # ─────────────────────────────────────────────
    def _open_settings(self):
        if hasattr(self,"_settings_win"):
            try:
                if self._settings_win.winfo_exists():
                    self._settings_win.lift(); return
            except Exception: pass

        win = tk.Toplevel(self.root)
        self._settings_win = win
        T = self.T
        win.title("KeyViz — Settings")
        win.configure(bg=T["bg"])
        win.geometry("560x680")
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.grab_set()

        tab_bar = tk.Frame(win, bg=T["surface"])
        tab_bar.pack(fill="x")
        content = tk.Frame(win, bg=T["bg"])
        content.pack(fill="both",expand=True,padx=14,pady=10)

        pages={}; tab_btns={}
        tab_names=["General","Display","Theme","System","Info"]

        def show_tab(name):
            for n,f in pages.items(): f.pack_forget()
            pages[name].pack(fill="both",expand=True)
            for n,b in tab_btns.items():
                b.configure(bg=T["accent"] if n==name else T["surface"],
                            fg="#fff" if n==name else T["muted"])

        for tn in tab_names:
            b=tk.Label(tab_bar,text=tn,bg=T["surface"],fg=T["muted"],
                       font=("Consolas",9,"bold"),padx=14,pady=7,cursor="hand2")
            b.pack(side="left")
            b.bind("<Button-1>",lambda e,n=tn: show_tab(n))
            tab_btns[tn]=b; pages[tn]=tk.Frame(content,bg=T["bg"])

        self._setting_vars={}

        # ── GENERAL
        pg=pages["General"]
        for i,(lbl,key,wt,kw) in enumerate([
            ("Opacity",          "opacity",         "scale",{"from_":0.2,"to":1.0,"resolution":0.05}),
            ("Font size (px)",   "font_size",       "scale",{"from_":12,"to":42}),
            ("Max visible keys", "max_keys",        "scale",{"from_":1,"to":14}),
            ("Fade delay (ms)",  "fade_ms",         "scale",{"from_":300,"to":8000,"resolution":100}),
            ("History buffer",   "history_max",     "scale",{"from_":20,"to":200}),
            ("Toggle hotkey",    "toggle_hotkey",   "entry",{}),
            ("Always on top",    "always_on_top",   "bool", {}),
            ("Sound on keypress","sound_enabled",   "bool", {}),
            ("Glow effects",     "glow_effects",    "bool", {}),
            ("RGB mode",          "rgb_enabled",     "bool", {}),
            ("RGB speed (deg/s)", "rgb_speed",       "scale",{"from_":0.5,"to":20.0,"resolution":0.5}),
            ("RGB mode style",    "rgb_mode",        "choice",{"choices":["cycle","pulse","wave"]}),
            ("Particle explosions","particles_enabled","bool",{}),
            ("Particle WPM trigger","particle_threshold_wpm","scale",{"from_":20,"to":200}),
            ("Show hold tracker", "show_hold_tracker","bool",{}),
        ]):
            self._srow(pg,i,lbl,key,wt,**kw)

        # ── DISPLAY
        pg2=pages["Display"]
        for i,(lbl,key) in enumerate([
            ("Show clock & timer", "show_clock"),
            ("Show modifier row",  "show_modifiers"),
            ("Show stats bar",     "show_stats"),
            ("Show WPM graph",     "show_wpm_graph"),
            ("Show heatmap",       "show_heatmap"),
            ("Show mouse events",  "show_mouse"),
            ("Show app tracker",   "show_app_tracker"),
            ("Show history log",   "show_history"),
        ]):
            self._srow(pg2,i,lbl,key,"bool")
        tk.Label(pg2,text="Screen corner:",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9)).grid(row=9,column=0,sticky="w",padx=4,pady=8)
        corner_var=tk.StringVar(value=self.cfg["corner"])
        om=tk.OptionMenu(pg2,corner_var,
                         "bottom-left","bottom-right","top-left","top-right")
        om.configure(bg=T["surface"],fg=T["text"],highlightthickness=0,
                     font=("Consolas",9),activebackground=T["accent"])
        om["menu"].configure(bg=T["surface"],fg=T["text"])
        om.grid(row=9,column=1,sticky="w",padx=4)

        # ── THEME
        pg3=pages["Theme"]
        tk.Label(pg3,text="Preset themes:",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9,"bold")).grid(
            row=0,column=0,columnspan=6,sticky="w",padx=4,pady=(4,6))
        for i,(k,v) in enumerate(THEMES.items()):
            btn=tk.Label(pg3,text=v["name"],bg=v["accent"],fg="#fff",
                         font=("Consolas",8,"bold"),padx=10,pady=5,cursor="hand2")
            btn.grid(row=1,column=i,padx=3,pady=2)
            btn.bind("<Button-1>",lambda e,k=k: self._set_theme(k))
        tk.Frame(pg3,bg=T["border"],height=1).grid(
            row=2,column=0,columnspan=6,sticky="ew",pady=10)
        tk.Label(pg3,text="Custom color editor:",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9,"bold")).grid(
            row=3,column=0,columnspan=6,sticky="w",padx=4)
        self._color_target=tk.StringVar(value="accent")
        targets=["accent","accent2","bg","text","key_bg","border","surface","success"]
        tf=tk.Frame(pg3,bg=T["bg"])
        tf.grid(row=4,column=0,columnspan=6,sticky="w",padx=4,pady=4)
        for t in targets:
            rb=tk.Radiobutton(tf,text=t,variable=self._color_target,value=t,
                              bg=T["bg"],fg=T["text"],selectcolor=T["surface2"],
                              activebackground=T["bg"],font=("Consolas",8),
                              command=self._sync_wheel)
            rb.pack(side="left",padx=3)
        wr=tk.Frame(pg3,bg=T["bg"])
        wr.grid(row=5,column=0,columnspan=6,pady=6)
        self._color_wheel=ColorWheel(wr,size=180,bg=T["bg"],
                                     command=self._on_wheel_pick)
        self._color_wheel.pack(side="left",padx=8)
        swf=tk.Frame(wr,bg=T["bg"])
        swf.pack(side="left",padx=12)
        tk.Label(swf,text="Selected:",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",8)).pack(anchor="w")
        self._swatch=tk.Label(swf,text="        ",bg=T["accent"],
                              width=8,height=3)
        self._swatch.pack(pady=4)
        self._hex_lbl=tk.Label(swf,text=T["accent"],bg=T["bg"],fg=T["muted"],
                               font=("Consolas",8))
        self._hex_lbl.pack()
        ab=tk.Label(swf,text=" Apply ",bg=T["accent"],fg="#fff",
                    font=("Consolas",8,"bold"),cursor="hand2",pady=4)
        ab.pack(pady=6)
        ab.bind("<Button-1>",lambda e:self._apply_color())
        self._sync_wheel()

        # ── SYSTEM
        pg4=pages["System"]
        autostart_var=tk.BooleanVar(value=get_autostart())
        tk.Label(pg4,text="Auto-start with Windows:",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9)).grid(row=0,column=0,sticky="w",padx=4,pady=8)
        tk.Checkbutton(pg4,variable=autostart_var,bg=T["bg"],fg=T["text"],
                       selectcolor=T["surface2"],activebackground=T["bg"],
                       font=("Consolas",9)).grid(row=0,column=1,sticky="w",padx=4)
        tk.Label(pg4,text="Gaming overlay:",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9)).grid(row=1,column=0,sticky="w",padx=4,pady=8)
        gaming_var=tk.BooleanVar(value=bool(self._gaming_overlay))
        tk.Checkbutton(pg4,variable=gaming_var,bg=T["bg"],fg=T["text"],
                       selectcolor=T["surface2"],activebackground=T["bg"],
                       font=("Consolas",9)).grid(row=1,column=1,sticky="w",padx=4)

        # Stats file location
        tk.Label(pg4,text="Stats file:",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9)).grid(row=2,column=0,sticky="w",padx=4,pady=4)
        tk.Label(pg4,text=STATS_FILE,bg=T["bg"],fg=T["text"],
                 font=("Consolas",7),wraplength=340).grid(
            row=2,column=1,sticky="w",padx=4)

        def open_stats_file():
            try: subprocess.Popen(f'explorer /select,"{STATS_FILE}"')
            except Exception: pass
        tk.Label(pg4,text="Open stats folder",bg=T["accent"],fg="#fff",
                 font=("Consolas",8,"bold"),padx=10,pady=4,cursor="hand2").grid(
            row=3,column=0,columnspan=2,padx=4,pady=8,sticky="w")
        pg4.winfo_children()[-1].bind("<Button-1>",lambda e:open_stats_file())

        # Reset stats
        def reset_stats():
            if messagebox.askyesno("Reset?","Reset all lifetime stats?",
                                   parent=win):
                self.stats = load_stats.__wrapped__() if hasattr(
                    load_stats,"__wrapped__") else {
                    "total_keys":0,"total_clicks":0,"total_combos":0,
                    "max_wpm":0,"max_streak":0,"space_count":0,
                    "backspace_count":0,"night_typing":0,"session_min":0,
                    "achievements":[],"key_counts":{},"daily":{},"app_times":{}}
                save_stats(self.stats)
        tk.Label(pg4,text="⚠ Reset all stats",bg=T["accent2"],fg="#fff",
                 font=("Consolas",8,"bold"),padx=10,pady=4,cursor="hand2").grid(
            row=4,column=0,columnspan=2,padx=4,sticky="w")
        pg4.winfo_children()[-1].bind("<Button-1>",lambda e:reset_stats())

        # ── INFO
        pg5=pages["Info"]
        info=(
            f"KeyViz v{APP_VERSION}  —  Keyboard Overlay\n\n"
            "Controls:\n"
            "  • Drag anywhere to reposition\n"
            "  • Right-click for quick menu\n"
            "  • F9 (default) to show/hide overlay\n\n"
            "New in v3.0:\n"
            "  • Animated glow key effects\n"
            "  • Live keyboard heatmap\n"
            "  • Session stats with bar chart\n"
            "  • 15 unlockable achievements\n"
            "  • Typing speed test mode\n"
            "  • Per-app usage tracking\n"
            "  • Typing streak counter\n"
            "  • Clock & session timer\n"
            "  • Gaming overlay (game detector)\n"
            "  • Auto-start with Windows\n"
            "  • Persistent lifetime stats\n\n"
            f"Config:  {CONFIG_FILE}\n"
            f"Stats:   {STATS_FILE}"
        )
        tk.Label(pg5,text=info,bg=T["bg"],fg=T["text"],
                 font=("Consolas",9),justify="left",
                 wraplength=460).pack(padx=4,pady=(8,4),anchor="w")
        tk.Frame(pg5,bg=T["border"],height=1).pack(fill="x",pady=6)
        cf=tk.Frame(pg5,bg=T["surface2"],
                    highlightbackground=T["accent"],highlightthickness=1)
        cf.pack(fill="x",padx=4,pady=4)
        tk.Label(cf,text="✦  Made by D.T  —  Germany, Münster",
                 bg=T["surface2"],fg=T["accent"],
                 font=("Consolas",9,"bold"),pady=8).pack()
        tk.Label(cf,text=f"KeyViz v{APP_VERSION}  •  2025",
                 bg=T["surface2"],fg=T["muted"],font=("Consolas",7)).pack(pady=(0,6))

        # ── Save / Cancel
        def do_save():
            for key,var in self._setting_vars.items():
                try: self.cfg[key]=var.get()
                except Exception: pass
            self.cfg["corner"]=corner_var.get()
            # Apply RGB engine settings live
            if self.cfg.get("rgb_enabled"):
                RGB_ENGINE.speed = float(self.cfg.get("rgb_speed", 3.0))
                RGB_ENGINE.mode  = str(self.cfg.get("rgb_mode", "cycle"))
                RGB_ENGINE.start()
            else:
                RGB_ENGINE.stop()
                try:
                    self.outer.configure(highlightbackground=self.T["border"])
                except Exception:
                    pass
            # Autostart
            set_autostart(autostart_var.get())
            self.cfg["autostart"]=autostart_var.get()
            # Gaming
            if gaming_var.get() and not self._gaming_overlay:
                self._gaming_overlay=GamingOverlay(self.root,self.T,self.cfg)
            elif not gaming_var.get() and self._gaming_overlay:
                try: self._gaming_overlay.win.destroy()
                except: pass
                self._gaming_overlay=None
            save_config(self.cfg)
            self.root.attributes("-topmost",self.cfg["always_on_top"])
            self.root.attributes("-alpha",self.cfg["opacity"])
            self.cfg["pos_x"]=-1; self.cfg["pos_y"]=-1
            self._build_inner(); self._reposition()
            win.destroy()

        btn_row=tk.Frame(win,bg=T["bg"])
        btn_row.pack(fill="x",padx=14,pady=8)
        tk.Label(btn_row,text="cancel",bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9),cursor="hand2").pack(side="right",padx=12)
        btn_row.winfo_children()[-1].bind("<Button-1>",lambda e:win.destroy())
        sb=tk.Label(btn_row,text="  Save & Apply  ",bg=T["accent"],fg="#fff",
                    font=("Consolas",10,"bold"),padx=6,pady=6,cursor="hand2")
        sb.pack(side="right")
        sb.bind("<Button-1>",lambda e:do_save())

        show_tab("General")

    def _srow(self,parent,row,label_text,cfg_key,wtype,**kwargs):
        T=self.T
        tk.Label(parent,text=label_text,bg=T["bg"],fg=T["muted"],
                 font=("Consolas",9)).grid(row=row,column=0,sticky="w",padx=4,pady=5)
        val=self.cfg.get(cfg_key)
        if wtype=="scale":
            var=(tk.DoubleVar(value=val) if isinstance(val,float)
                 else tk.IntVar(value=int(val) if val is not None else 0))
            tk.Scale(parent,variable=var,orient="horizontal",length=220,
                     bg=T["bg"],fg=T["text"],troughcolor=T["surface"],
                     highlightthickness=0,bd=0,**kwargs).grid(
                row=row,column=1,sticky="w",padx=4)
        elif wtype=="bool":
            var=tk.BooleanVar(value=bool(val))
            tk.Checkbutton(parent,variable=var,bg=T["bg"],fg=T["text"],
                           selectcolor=T["surface2"],activebackground=T["bg"],
                           font=("Consolas",9)).grid(
                row=row,column=1,sticky="w",padx=4)
        elif wtype=="entry":
            var=tk.StringVar(value=str(val or ""))
            tk.Entry(parent,textvariable=var,width=10,bg=T["surface"],
                     fg=T["text"],insertbackground=T["text"],
                     font=("Consolas",9),relief="flat",
                     highlightbackground=T["border"],
                     highlightthickness=1).grid(
                row=row,column=1,sticky="w",padx=4)
        elif wtype=="choice":
            choices = kwargs.get("choices", [])
            var = tk.StringVar(value=str(val or (choices[0] if choices else "")))
            om = tk.OptionMenu(parent, var, *choices)
            om.configure(bg=T["surface"], fg=T["text"], highlightthickness=0,
                         font=("Consolas",9), activebackground=T["accent"])
            om["menu"].configure(bg=T["surface"], fg=T["text"])
            om.grid(row=row, column=1, sticky="w", padx=4)
        self._setting_vars[cfg_key]=var

    def _sync_wheel(self):
        if not hasattr(self,"_color_wheel"): return
        color=self.T.get(self._color_target.get(),"#ffffff")
        self._color_wheel.set_color(color); self._update_swatch(color)

    def _on_wheel_pick(self,color): self._update_swatch(color)
    def _update_swatch(self,color):
        if hasattr(self,"_swatch"):
            self._swatch.configure(bg=color)
            self._hex_lbl.configure(text=color)

    def _apply_color(self):
        target=self._color_target.get()
        color=self._color_wheel.get_color()
        custom=self.cfg.get("custom_theme",THEMES["custom"].copy())
        custom[target]=color; custom["name"]="Custom"
        self.cfg["custom_theme"]=custom; self.cfg["theme"]="custom"
        THEMES["custom"].update(custom)
        self.T=self._get_theme(); save_config(self.cfg); self._build_inner()

    def _set_theme(self,name):
        self.cfg["theme"]=name; self.T=self._get_theme()
        save_config(self.cfg); self._build_inner()

    def _set_corner(self,corner):
        self.cfg["corner"]=corner
        self.cfg["pos_x"]=-1; self.cfg["pos_y"]=-1
        save_config(self.cfg); self._reposition()

    def _quit(self):
        self._save_stats_snapshot()
        save_config(self.cfg)
        try: self._kb.stop()
        except: pass
        try: self._ms.stop()
        except: pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()

# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"KeyViz v{APP_VERSION} starting...")
    print(f"Toggle hotkey: {load_config().get('toggle_hotkey','f9').upper()}")
    print("Right-click overlay for options.")
    if not HAS_PSUTIL:
        print("TIP: pip install psutil  — for app tracking & game detection")
    if not HAS_WIN32:
        print("TIP: pip install pywin32 — for active window tracking")
    KeyVizApp().run()
