# ⬡ Nyx Pad

<div align="center">

**Every developer's macropad. Powered by [Conductor](https://github.com/thealxlabs/conductor) AI.**

[![Hack Club Blueprint](https://img.shields.io/badge/Hack%20Club-Blueprint-red?style=flat-square)](https://hackclub.com/blueprint)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![KMK Firmware](https://img.shields.io/badge/firmware-KMK-purple?style=flat-square)](https://github.com/KMKfw/kmk_firmware)
[![CircuitPython](https://img.shields.io/badge/CircuitPython-9.x-orange?style=flat-square)](https://circuitpython.org)

*by Alexander Wondwossen ([@thealxlabs](https://github.com/thealxlabs)) — Grade 7, Toronto 🇨🇦*

</div>

---

## What is Nyx Pad?

Nyx Pad is a custom 6-key macropad — think DIY Stream Deck — that talks to **Conductor**, my own AI integration CLI. Press a key and Nyx (the [LocalCode](https://github.com/TheLocalCodeTeam/localcode) mascot) animates on the OLED while Conductor fetches weather, crypto prices, GitHub stats, and more.

**3 profiles · hold actions · Pomodoro timer · screensaver · boot greeting**

Built on a Seeed XIAO RP2040 with KMK firmware. Designed from scratch for Hack Club Blueprint. Cost to me: $0.

---

## Features

### Stream Deck style OLED
128×32 OLED shows Nyx as a pixel art character reacting to every keypress. Status bar shows profile and key hints.

### 3 Profiles (encoder hold to switch)
| Profile | Keys |
|---------|------|
| **CODE** `</>` | GitHub, system stats, translate, weather, crypto, jokes |
| **CHILL** `uwu` | Music, weather, jokes, quotes, trivia, vibes |
| **MEET** `cam` | Mute, timer, focus, lock, notes, done |

### Key hold (2 seconds)
Every key has a secondary action on hold. K1 hold always starts a **Pomodoro timer**.

### Encoder
- Rotate = volume
- Click = mute
- Hold = switch profile

### Screensaver (30s idle)
Nyx cycles through: batting a hexagon around → getting tired → falling asleep with ZZZs → waking back up.

### Boot greeting
On plug-in, Nyx wakes up with an animation and says *"hey alex!"*

---

## Hardware

| Part | Qty |
|------|-----|
| Seeed XIAO RP2040 | 1 |
| Cherry MX Switches | 6 |
| MX Keycaps 1U | 6 |
| SSD1306 OLED 128×32 (0.91") | 1 |
| EC11 Rotary Encoder | 1 |
| 4.7kΩ Resistor 0402 | 2 |
| 100nF Capacitor 0402 | 1 |
| Custom PCB 80×70mm 2-layer | 1 |
| 3D Printed Case | 1 set |
| M2.5 Screws 6mm | 4 |

---

## Pin Map

| Signal | XIAO Pin |
|--------|----------|
| K1–K6 | D0–D5 |
| OLED SDA | D6 |
| OLED SCL | D7 |
| Encoder CLK | D8 |
| Encoder DT | D9 |
| Encoder SW | D10 |

---

## Setup

### 1. Flash CircuitPython
Hold BOOT on XIAO while plugging in. Copy [CircuitPython 9.x for XIAO RP2040](https://circuitpython.org/board/seeeduino_xiao_rp2040/) `.uf2` onto the `RPI-RP2` drive.

### 2. Install libraries
Copy to `lib/` on CIRCUITPY:
- `kmk/` from [KMKfw/kmk_firmware](https://github.com/KMKfw/kmk_firmware)
- `adafruit_displayio_ssd1306.mpy`
- `adafruit_display_text/`

### 3. Flash firmware
Copy `Firmware/main.py` to root of CIRCUITPY drive.

### 4. Install Conductor
```bash
curl -fsSL https://raw.githubusercontent.com/thealxlabs/conductor/main/install.sh | bash
conductor ai setup
```

### 5. Run the bridge
```bash
pip install pyserial plyer
python Firmware/bridge.py
```

---

## How it works

```
Key press → KMK sends F-key via USB HID
          → bridge.py reads serial signal
          → calls conductor CLI command
          → result shown as desktop notification
          → OLED shows Nyx reaction
```

---

## Project Structure

```
nyxpad/
├── PCB/                  KiCAD source files
├── CAD/                  OpenSCAD case
├── Firmware/
│   ├── main.py           KMK firmware (drop onto XIAO)
│   └── bridge.py         PC-side Conductor bridge
├── production/           Gerbers, STLs, compiled firmware
├── BOM.csv               Bill of materials
└── README.md
```

---

## Related

- [Conductor](https://github.com/thealxlabs/conductor) — AI CLI powering the keys
- [LocalCode](https://github.com/TheLocalCodeTeam/localcode) — Nyx's home
- [KMK Firmware](https://github.com/KMKfw/kmk_firmware) — keyboard firmware

---

<div align="center">
Made with ❤️ in Toronto for <a href="https://hackclub.com/blueprint">Hack Club Blueprint</a>
</div>
