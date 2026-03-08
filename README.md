# ⌨ KeyViz v4.0
#This project is unrelated to the original Keyviz project.
### Made by D.T — Germany, Münster

A real-time keystroke visualizer overlay for Windows.

---

## 🚀 Quick Start

1. Double-click **"Launch KeyViz.bat"**
   - Automatically installs Python dependencies
   - Launches the overlay in the background

**Or manually:**
```
pip install pynput psutil pywin32
python keyviz_overlay.py
```

---

## 📁 Files in this folder

| File | Description |
|------|-------------|
| `keyviz_overlay.py` | Main application |
| `Launch KeyViz.bat` | One-click launcher |
| `keyviz.ico` | App icon (use for shortcuts) |
| `keyviz_icon.png` | Icon preview |
| `keyviz_config.json` | Settings (auto-created) |
| `keyviz_stats.json` | Lifetime stats (auto-created) |

---

## 🎮 Controls

| Action | How |
|--------|-----|
| Move overlay | Click & drag |
| Quick menu | Right-click |
| Hide/show | F9 (default, changeable) |
| Settings | Right-click → Settings or ⚙ button |
| Stats screen | 📊 button or right-click |

---

## ✨ Features

### v3.0 New
- 🌈 **RGB border cycling** — Smooth rainbow border with cycle/pulse/wave modes
- 💥 **Particle explosions** — Keys explode into particles when typing fast
- ⏱ **Key hold duration tracker** — See which keys you hold longest / tap fastest
- 🖼 **Custom app icon** — Proper .ico for shortcuts & taskbar
- 🎮 Gaming overlay with game detection
- 📊 Session stats with bar charts
- 🏆 15 unlockable achievements
- 🌡️ Live keyboard heatmap
- ⚡ Typing speed test
- 🔑 Streak counter
- 🖥 Per-app usage tracking
- 🚀 Auto-start with Windows
- 💾 Persistent lifetime stats

### v2.0
- Live WPM graph (60s rolling)
- Mouse click tracking
- Scrollable history log
- Custom color wheel editor
- 6 themes

---

## 🖼 Creating a Desktop Shortcut with Custom Icon

1. Right-click Desktop → New → Shortcut
2. Target: `pythonw "C:\path\to\keyviz_overlay.py"`
3. Right-click shortcut → Properties → Change Icon
4. Browse to `keyviz.ico` in this folder

---

## 🌈 RGB Modes

| Mode | Effect |
|------|--------|
| `cycle` | Smooth rainbow hue rotation |
| `pulse` | Brightness pulses in/out |
| `wave` | Each modifier badge gets offset hue |

Speed is in degrees/second (0.5 = slow, 20 = fast flash).

---

## 💥 Particle System

Particles trigger when your WPM hits the threshold (default: 60 WPM).
- **Shapes**: circles, sparks, stars
- **Physics**: gravity, fade-out, rotation
- **Colors**: follows RGB engine if enabled, else uses accent color

---

## ⏱ Hold Duration Tracker

Tracks how long each key is held:
- **Longest avg** = keys you hold (e.g. Shift, Ctrl)
- **Fastest tapped** = keys you hammer quickly

Visible as a row in the overlay and detailed in the Stats screen.

---

*KeyViz v4.0 — Built with Python + tkinter + pynput*
*Made by D.T — Germany, Münster*
