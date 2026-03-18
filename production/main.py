"""
███╗   ██╗██╗   ██╗██╗  ██╗    ██████╗  █████╗ ██████╗
████╗  ██║╚██╗ ██╔╝╚██╗██╔╝    ██╔══██╗██╔══██╗██╔══██╗
██╔██╗ ██║ ╚████╔╝  ╚███╔╝     ██████╔╝███████║██║  ██║
██║╚██╗██║  ╚██╔╝   ██╔██╗     ██╔═══╝ ██╔══██║██║  ██║
██║ ╚████║   ██║   ██╔╝ ██╗    ██║     ██║  ██║██████╔╝
╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝    ╚═╝     ╚═╝  ╚═╝╚═════╝

Every developer's macropad. Powered by Conductor AI.
by Alexander Wondwossen (@thealxlabs) — Hack Club Blueprint

Hardware : Seeed XIAO RP2040
Keys     : 6x MX switches (D0-D5)
Display  : SSD1306 128x32 OLED (D6=SDA, D7=SCL)
Encoder  : EC11 (D8=CLK, D9=DT, D10=SW)

Features:
  - Stream Deck style OLED display
  - Nyx pixel art mascot with unique reactions per key
  - 3 profiles: Code / Chill / Meet (encoder hold to switch)
  - Key hold (2s) = secondary action
  - Pomodoro timer (hold K1 in any profile)
  - Screensaver: Nyx plays with hexagon, then falls asleep
  - Boot greeting: Nyx wakes up and says hey!
"""

import board, busio, displayio, terminalio, time
from kmk.kmk_keyboard import KMKKeyboard
from kmk.keys import KC
from kmk.scanners.keypad import KeysScanner
from kmk.modules.encoder import EncoderHandler
from kmk.modules.holdtap import HoldTap
from adafruit_display_text import label
import adafruit_displayio_ssd1306

# ── Display ────────────────────────────────────────────────────────────────
displayio.release_displays()
i2c     = busio.I2C(scl=board.D7, sda=board.D6, frequency=400_000)
d_bus   = displayio.I2CDisplay(i2c, device_address=0x3C)
display = adafruit_displayio_ssd1306.SSD1306(d_bus, width=128, height=32)

# ════════════════════════════════════════════════════════════════════════════
# PROFILES
# ════════════════════════════════════════════════════════════════════════════
PROFILES = [
    {
        "name": "CODE", "icon": "[</> ]",
        "idle": [" [^.^] ", " [^-^] ", " [^.^] ", " [>.>] "],
        "keys": [
            {"tap": "GITHUB",  "hold": "TREND",   "ti": "gh", "hi": "tr"},
            {"tap": "SYSTEM",  "hold": "POMODOR", "ti": "sy", "hi": "25"},
            {"tap": "TRANSL",  "hold": "DICT",    "ti": "tr", "hi": "dc"},
            {"tap": "WEATHER", "hold": "FORECAST","ti": "wx", "hi": "7d"},
            {"tap": "CRYPTO",  "hold": "MARKETS", "ti": "$",  "hi": "mk"},
            {"tap": "FUN",     "hold": "QUOTE",   "ti": "ha", "hi": "qt"},
        ]
    },
    {
        "name": "CHILL", "icon": "[uwu]",
        "idle": [" [uwu] ", " [^w^] ", " [uwu] ", " [-w-] "],
        "keys": [
            {"tap": "MUSIC",   "hold": "PLAYLIST","ti": "mu", "hi": "pl"},
            {"tap": "WEATHER", "hold": "FORECAST","ti": "wx", "hi": "7d"},
            {"tap": "JOKE",    "hold": "MEME",    "ti": "ha", "hi": "mm"},
            {"tap": "QUOTE",   "hold": "AFFIRM",  "ti": '"',  "hi": "af"},
            {"tap": "TRIVIA",  "hold": "FACTS",   "ti": "?",  "hi": "fc"},
            {"tap": "VIBE",    "hold": "MOOD",    "ti": "vb", "hi": "md"},
        ]
    },
    {
        "name": "MEET", "icon": "[cam]",
        "idle": [" [o.o] ", " [O.O] ", " [o.o] ", " [-.o] "],
        "keys": [
            {"tap": "MUTE",    "hold": "CAM OFF", "ti": "mu", "hi": "cv"},
            {"tap": "TIMER",   "hold": "POMODOR", "ti": ">>", "hi": "25"},
            {"tap": "FOCUS",   "hold": "DND",     "ti": "[]", "hi": "dn"},
            {"tap": "LOCK",    "hold": "SLEEP",   "ti": "lk", "hi": "sl"},
            {"tap": "NOTES",   "hold": "TODO",    "ti": "nt", "hi": "td"},
            {"tap": "DONE",    "hold": "END ALL", "ti": "ok", "hi": "!!"},
        ]
    },
]

# ════════════════════════════════════════════════════════════════════════════
# NYX ANIMATIONS
# ════════════════════════════════════════════════════════════════════════════
BOOT_SEQ = [
    (" [-.o] ", " booting...   "),
    (" [o.o] ", " nyx pad v1   "),
    (" [^.^] ", " hey alex!    "),
    (" [^.^] ", " lets code :) "),
]

NYX_REACT = [
    (" [*.^] ", " fetching...  "),
    (" [!.!] ", " loading...   "),
    (" [?.?] ", " working...   "),
    (" [~.~] ", " checking...  "),
    (" [$.#] ", " crunching... "),
    (" [^w^] ", " hehe...      "),
]

NYX_DONE = [
    (" [^.^] ", " done!        "),
    (" [^.^] ", " got it!      "),
    (" [^.^] ", " here ya go!  "),
    (" [^.^] ", " fetched!     "),
    (" [uwu] ", " moon!        "),
    (" [uwu] ", " lol!         "),
]

# Screensaver: Nyx bats a hexagon then falls asleep
SS_PLAY = [
    (" [^.^]  ", "  hex >>      "),
    (" [^.^]/ ", "    >> hex    "),
    (" [^o^]/ ", "      hex >>  "),
    (" [^o^]/~", "        >> hex"),
    (" [^-^]  ", "      << hex  "),
    (" [^.^]  ", "    hex <<    "),
    (" [^.^]  ", "  hex <<      "),
    (" [^.^]/ ", "hex >>        "),
]
SS_SLEEP = [
    (" [^.^]  ", " tired...     "),
    (" [-.-]  ", " zzz          "),
    (" [=.=]  ", "  ZZZ         "),
    (" [=.=]  ", "   ZZzz       "),
    (" [=.=]  ", "    Zzzz...   "),
    (" [=.=]  ", "    Zzzz...   "),
    (" [=.=]  ", "    Zzzz...   "),
    (" [^.^]  ", " !  hex >>    "),  # wakes up
]
SS_TYPE = [
    (" [^.^]  ", " tap tap tap  "),
    (" [^-^]  ", " clackclack   "),
    (" [>.<]  ", " CLACK CLACK  "),
    (" [^.^]  ", " tap tap...   "),
]

# ════════════════════════════════════════════════════════════════════════════
# DISPLAY CLASS
# ════════════════════════════════════════════════════════════════════════════
class NyxDisplay:
    SS_TIMEOUT = 30.0

    def __init__(self, disp):
        g = displayio.Group()
        disp.show(g)
        self._face   = label.Label(terminalio.FONT, text=" [-.o] ", color=0xFFFFFF, x=0, y=8)
        self._status = label.Label(terminalio.FONT, text=" booting...   ", color=0x888888, x=0, y=22)
        g.append(self._face)
        g.append(self._status)

        self._profile      = 0
        self._idle_idx     = 0
        self._ss_idx       = 0
        self._ss_phase     = 0   # 0=play, 1=sleep, 2=type
        self._last_idle    = time.monotonic()
        self._last_ss      = time.monotonic()
        self._last_action  = time.monotonic()
        self._state        = "boot"
        self._until        = time.monotonic() + 3.5
        self._boot_idx     = 0
        self._pomo_end     = 0
        self._pomo_on      = False

    @property
    def profile(self): return self._profile

    def wake(self):
        self._last_action = time.monotonic()
        if self._state == "screensaver":
            self._state = "idle"

    def next_profile(self):
        self.wake()
        self._profile = (self._profile + 1) % len(PROFILES)
        p = PROFILES[self._profile]
        self._face.text   = p["icon"]
        self._status.text = f" mode: {p['name']:<8}"
        self._state = "react"
        self._until = time.monotonic() + 1.5

    def react(self, idx, held=False):
        self.wake()
        p = PROFILES[self._profile]["keys"][idx]
        lbl = p["hold"] if held else p["tap"]
        self._face.text   = NYX_REACT[idx][0]
        self._status.text = f" {lbl.lower():<13}"
        self._state = "react"
        self._until = time.monotonic() + 2.5
        print(f"NYX:{'HOLD' if held else 'TAP'}:{idx}:{PROFILES[self._profile]['name']}", flush=True)

    def start_pomodoro(self):
        self.wake()
        self._pomo_on  = True
        self._pomo_end = time.monotonic() + 25 * 60
        self._face.text   = " [>.<] "
        self._status.text = " focus: 25:00  "

    def tick(self):
        now = time.monotonic()

        # Boot
        if self._state == "boot":
            elapsed = now - (self._until - 3.5)
            idx = min(int(elapsed / 0.9), len(BOOT_SEQ) - 1)
            if idx != self._boot_idx:
                self._boot_idx = idx
                f, s = BOOT_SEQ[idx]
                self._face.text, self._status.text = f, s
            if now > self._until:
                self._state = "idle"
                self._last_action = now
            return

        # Pomodoro overlay
        if self._pomo_on:
            rem = self._pomo_end - now
            if rem <= 0:
                self._pomo_on = False
                self._face.text   = " [^o^] "
                self._status.text = " break time!! "
            else:
                self._face.text   = " [>.<] "
                self._status.text = f" focus {int(rem//60):02d}:{int(rem%60):02d}   "
            return

        # React
        if self._state == "react":
            if now >= self._until:
                self._state = "idle"
            return

        # Screensaver
        if now - self._last_action > self.SS_TIMEOUT:
            if self._state != "screensaver":
                self._state   = "screensaver"
                self._ss_idx  = 0
                self._ss_phase = 0
            if now - self._last_ss > 0.5:
                if self._ss_phase == 0:
                    frames = SS_PLAY
                elif self._ss_phase == 1:
                    frames = SS_SLEEP
                else:
                    frames = SS_TYPE
                f, s = frames[self._ss_idx % len(frames)]
                self._face.text, self._status.text = f, s
                self._ss_idx += 1
                if self._ss_idx >= len(frames):
                    self._ss_idx   = 0
                    self._ss_phase = (self._ss_phase + 1) % 3
                self._last_ss = now
            return

        # Idle
        self._state = "idle"
        if now - self._last_idle > 0.7:
            idles = PROFILES[self._profile]["idle"]
            self._idle_idx = (self._idle_idx + 1) % len(idles)
            self._face.text   = idles[self._idle_idx]
            p = PROFILES[self._profile]
            keys = p["keys"]
            hints = " ".join(k["ti"] for k in keys)
            self._status.text = f"[{p['name']}]{hints}"
            self._last_idle = now

nyx = NyxDisplay(display)

# ════════════════════════════════════════════════════════════════════════════
# KEYBOARD
# ════════════════════════════════════════════════════════════════════════════
keyboard = KMKKeyboard()
keyboard.modules.append(HoldTap())
keyboard.matrix = KeysScanner(pins=[
    board.D0, board.D1, board.D2,
    board.D3, board.D4, board.D5,
])

KEYS = [KC.F13, KC.F14, KC.F15, KC.F16, KC.F17, KC.F18]
keyboard.keymap = [KEYS]

enc = EncoderHandler()
keyboard.modules.append(enc)
enc.pins = ((board.D8, board.D9, board.D10, False),)
enc.map  = [((KC.VOLU, KC.VOLD, KC.MUTE),)]

_press_time = {}
HOLD_MS = 2.0

def _on_press(key, keyboard, *args):
    nyx.wake()
    try:
        idx = KEYS.index(key)
        _press_time[idx] = time.monotonic()
        nyx.react(idx, held=False)
    except (ValueError, IndexError):
        pass
    return True

def _on_release(key, keyboard, *args):
    try:
        idx = KEYS.index(key)
        dur = time.monotonic() - _press_time.get(idx, time.monotonic())
        if dur >= HOLD_MS:
            if idx == 0:
                nyx.start_pomodoro()
            else:
                nyx.react(idx, held=True)
        _press_time.pop(idx, None)
    except (ValueError, IndexError):
        pass
    return True

keyboard.before_matrix_scan  = lambda: nyx.tick()
keyboard.on_press_handlers    = [_on_press]
keyboard.on_release_handlers  = [_on_release]

if __name__ == "__main__":
    keyboard.go()
