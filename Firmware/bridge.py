#!/usr/bin/env python3
"""
Nyx Pad — PC Bridge v2
Listens for keypresses from the Nyx Pad and calls Conductor CLI plugins.
Supports 3 profiles: CODE / CHILL / MEET

Usage:
    pip install pyserial plyer
    python bridge.py [PORT]

Author: Alexander Wondwossen (@thealxlabs)
"""

import serial, serial.tools.list_ports
import subprocess, threading, time, sys, os

BAUD = 115200
CONDUCTOR = "conductor"

# ── Plugin map per profile ─────────────────────────────────────────────────
ACTIONS = {
    "CODE": {
        "TAP": {
            0: ["conductor", "run", "github",    "user",     "--username", "thealxlabs"],
            1: ["conductor", "run", "system",    "status"],
            2: ["conductor", "run", "translate", "hello",    "--to", "fr"],
            3: ["conductor", "run", "weather",   "current"],
            4: ["conductor", "run", "crypto",    "price",    "--coin", "bitcoin"],
            5: ["conductor", "run", "fun",       "joke"],
        },
        "HOLD": {
            0: ["conductor", "run", "github",    "trending"],
            1: None,  # pomodoro handled on-device
            2: ["conductor", "run", "translate", "--dict"],
            3: ["conductor", "run", "weather",   "forecast", "--days", "7"],
            4: ["conductor", "run", "crypto",    "trending"],
            5: ["conductor", "run", "fun",       "quote"],
        }
    },
    "CHILL": {
        "TAP": {
            0: ["conductor", "run", "fun",       "fact"],
            1: ["conductor", "run", "weather",   "current"],
            2: ["conductor", "run", "fun",       "joke"],
            3: ["conductor", "run", "fun",       "quote"],
            4: ["conductor", "run", "fun",       "trivia"],
            5: ["conductor", "run", "fun",       "random"],
        },
        "HOLD": {
            0: ["conductor", "run", "fun",       "fact"],
            1: ["conductor", "run", "weather",   "forecast", "--days", "7"],
            2: ["conductor", "run", "fun",       "meme"],
            3: ["conductor", "run", "fun",       "affirmation"],
            4: ["conductor", "run", "fun",       "fact"],
            5: ["conductor", "run", "fun",       "mood"],
        }
    },
    "MEET": {
        "TAP": {
            0: [None],   # Mute — handled by system shortcut
            1: [None],   # Timer — on device
            2: [None],   # Focus mode — TBD
            3: [None],   # Lock screen — system
            4: ["conductor", "run", "fun",       "quote"],
            5: [None],   # Done
        },
        "HOLD": {
            0: [None],   # Cam off
            1: [None],   # Pomodoro
            2: [None],   # DND
            3: [None],   # Sleep
            4: ["conductor", "run", "fun",       "todo"],
            5: [None],   # End all
        }
    }
}

def notify(title, msg):
    try:
        from plyer import notification
        notification.notify(title=title, message=msg[:256], app_name="Nyx Pad", timeout=5)
    except Exception:
        print(f"\n┌─ {title} ───────────────────")
        print(f"│  {msg[:200]}")
        print("└────────────────────────────────\n")

def run_action(action_type, key_idx, profile):
    cmd = ACTIONS.get(profile, ACTIONS["CODE"]).get(action_type, {}).get(key_idx)
    if not cmd or cmd[0] is None:
        return
    print(f"[nyx] {profile}/{action_type}/K{key_idx+1}: {' '.join(cmd)}")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        out = (r.stdout or r.stderr or "Done.").strip()
        lines = [l for l in out.splitlines() if l.strip()]
        notify(f"Nyx · {profile} K{key_idx+1}", "\n".join(lines[:3]))
    except subprocess.TimeoutExpired:
        notify("Nyx · Timeout", "Command took too long")
    except FileNotFoundError:
        notify("Nyx · Error", "conductor not found — run install script")
    except Exception as e:
        notify("Nyx · Error", str(e))

def find_port():
    keywords = ["xiao", "rp2040", "circuitpython", "cp2102", "pico"]
    for p in serial.tools.list_ports.comports():
        if any(k in (p.description or "").lower() or k in (p.manufacturer or "").lower() for k in keywords):
            return p.device
    ports = serial.tools.list_ports.comports()
    return ports[0].device if ports else None

def listen(port):
    print(f"[nyx] Connecting on {port}...")
    with serial.Serial(port, BAUD, timeout=1) as ser:
        print("[nyx] Connected! Waiting for keypresses...\n")
        while True:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if not line.startswith("NYX:"): continue
            parts = line.split(":")
            if len(parts) < 4: continue
            _, action, idx_str, profile = parts[0], parts[1], parts[2], parts[3]
            try:
                idx = int(idx_str)
                threading.Thread(
                    target=run_action,
                    args=(action, idx, profile),
                    daemon=True
                ).start()
            except (ValueError, IndexError):
                pass

def main():
    print("╔══════════════════════════════════╗")
    print("║   Nyx Pad Bridge  v2             ║")
    print("║   by thealxlabs                  ║")
    print("╚══════════════════════════════════╝\n")
    port = sys.argv[1] if len(sys.argv) > 1 else find_port()
    if not port:
        print("[nyx] No port found. Plug in Nyx Pad or pass port as argument.")
        print("      python bridge.py /dev/ttyACM0   (Linux/Mac)")
        print("      python bridge.py COM3            (Windows)")
        sys.exit(1)
    while True:
        try:
            listen(port)
        except KeyboardInterrupt:
            print("\n[nyx] Bye!")
            break
        except Exception as e:
            print(f"[nyx] Reconnecting in 3s... ({e})")
            time.sleep(3)

if __name__ == "__main__":
    main()
