"""
adb_wireless_connect.py

Manages Android Wireless Debugging (Android 11+) without requiring a USB cable.

Workflow:
  1. On your phone: Developer Options → Wireless Debugging  (enable it)
  2. First time only: tap "Pair device with pairing code" and run:
         adbw pair <device_name>
  3. Every session: look at the IP:Port on the Wireless Debugging screen and run:
         adbw connect <device_name> <port>

Commands:
  pair    <device_name>              - Pair a new device (interactive). Saves IP to devices.json.
  connect <device_name> [port]       - Connect using stored IP + the current session port.
  list                               - Show saved devices and currently connected ADB devices.
  remove  <device_name>              - Remove a saved device from devices.json.
"""

import sys
import subprocess
import json
import os
import shutil

# --- Configuration ---
VERSION = "1.1.0"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "devices.json")

# --- UI Helpers ---
def ok(msg: str):    print(f"\033[92m[OK]\033[0m  {msg}")
def info(msg: str):  print(f"\033[94m[..]\033[0m  {msg}")
def warn(msg: str):  print(f"\033[93m[!!]\033[0m  {msg}")
def err(msg: str):   print(f"\033[91m[ERR]\033[0m {msg}")

# --- Robustness Helpers ---

def check_env():
    """Verify adb is installed and in PATH."""
    if not shutil.which("adb"):
        err("ADB not found! Please install Android Platform Tools and add 'adb' to your PATH.")
        sys.exit(1)

def validate_port(port: str) -> str:
    """Ensure the port is a valid numeric string."""
    if not port.isdigit():
        err(f"Invalid port: '{port}'. Port must be a number.")
        sys.exit(1)
    return port

def load_config() -> dict:
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        err(f"Config file {CONFIG_FILE} is corrupt. Delete it to reset.")
        sys.exit(1)

def save_config(config: dict):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        err(f"Failed to save config: {e}")

def save_known_port(device_name: str, port: str):
    config = load_config()
    if device_name not in config:
        return
    device = config[device_name]
    ports = device.get("known_ports", [])
    try:
        port_int = int(port)
    except ValueError:
        return
    ports = [p for p in ports if p != port_int]
    ports.insert(0, port_int)
    device["known_ports"] = ports[:10]  # Keep only last 10
    save_config(config)

def run(cmd: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        err(f"Error executing command {' '.join(cmd)}: {e}")
        sys.exit(1)

def prompt(label: str, default: str = "") -> str:
    shown = f" [{default}]" if default else ""
    try:
        value = input(f"  {label}{shown}: ").strip()
        return value or default
    except EOFError:
        print()
        sys.exit(0)

# --- Commands ---

def cmd_pair(device_name: str):
    config = load_config()
    existing = config.get(device_name, {})

    print(f"\n  Pairing '{device_name}' (v{VERSION})")
    print("  " + "─" * 40)
    print("  On phone: Developer Options -> Wireless Debugging -> Pair with code\n")

    ip           = prompt("Device IP address", existing.get("ip", ""))
    pairing_port = validate_port(prompt("Pairing port"))
    pairing_code = prompt("6-digit pairing code")

    if not ip or not pairing_port or not pairing_code:
        err("All fields are required.")
        sys.exit(1)

    target = f"{ip}:{pairing_port}"
    info(f"Pairing with {target}...")

    result = run(["adb", "pair", target, pairing_code])
    output = (result.stdout + result.stderr).strip()

    if "successfully paired" in output.lower():
        ok("Paired successfully!")
        config[device_name] = {
            "ip": ip,
            "known_ports": existing.get("known_ports", []),
        }
        save_config(config)
        ans = input("\n  Connect now? (y/n): ").strip().lower()
        if ans == "y":
            conn_port = validate_port(prompt("Connection port from main screen"))
            _do_connect(device_name, ip, conn_port)
    else:
        err(f"Pairing failed: {output}")

def cmd_connect(device_name: str, port: str | None = None):
    config = load_config()
    if device_name not in config:
        err(f"Device '{device_name}' not found. Run 'adbw pair {device_name}' first.")
        sys.exit(1)

    ip = config[device_name]["ip"]
    if port is None:
        print(f"\n  Phone: Wireless Debugging -> IP:PORT is {ip}:XXXXX")
        port = validate_port(prompt("Connection port"))
    else:
        port = validate_port(port)

    _do_connect(device_name, ip, port)

def _do_connect(device_name: str, ip: str, port: str):
    target = f"{ip}:{port}"
    run(["adb", "start-server"])
    info(f"Connecting to {target}...")
    result = run(["adb", "connect", target])
    output = (result.stdout + result.stderr).strip()

    if "connected" in output.lower():
        ok(f"Connected to {device_name}")
        save_known_port(device_name, port)
    else:
        err(f"Connection failed: {output}")

def cmd_autoconnect(device_name: str):
    config = load_config()
    if device_name not in config:
        err(f"Device '{device_name}' not found.")
        sys.exit(1)

    ip = config[device_name]["ip"]
    ports = config[device_name].get("known_ports", [])

    if not ports:
        err("No history for this device. Use 'connect' once.")
        sys.exit(1)

    run(["adb", "start-server"])
    for port in ports:
        target = f"{ip}:{port}"
        info(f"Trying {target}...")
        result = run(["adb", "connect", target])
        if "connected" in (result.stdout + result.stderr).lower():
            ok(f"Auto-connected to {target}")
            save_known_port(device_name, str(port))
            return
    err("None of the known ports worked.")

def cmd_list():
    config = load_config()
    if config:
        print("\n  Saved Devices:")
        for name, data in config.items():
            ports = ", ".join(map(str, data.get("known_ports", [])))
            print(f"    • {name:<12} | {data['ip']} | Ports: {ports or 'None'}")
    else:
        warn("No devices saved.")

    print("\n  Active ADB Devices:")
    result = run(["adb", "devices"])
    print(result.stdout.strip())

def cmd_remove(device_name: str):
    config = load_config()
    if device_name in config:
        del config[device_name]
        save_config(config)
        ok(f"Removed '{device_name}'.")
    else:
        err(f"Device '{device_name}' not found.")

# --- CLI Entry ---

USAGE = f"""
Android Wireless Debugging Helper v{VERSION}

Usage:
  adbw pair <name>         One-time pairing
  adbw connect <name> [p]  Connect via specific port
  adbw autoconnect <name>  Try past ports automatically
  adbw list                Show devices
  adbw remove <name>       Remove device
"""

def main():
    check_env()
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        return

    try:
        cmd = args[0].lower()
        if cmd == "pair" and len(args) > 1: cmd_pair(args[1])
        elif cmd == "connect" and len(args) > 1: cmd_connect(args[1], args[2] if len(args) > 2 else None)
        elif cmd == "autoconnect" and len(args) > 1: cmd_autoconnect(args[1])
        elif cmd == "list": cmd_list()
        elif cmd == "remove" and len(args) > 1: cmd_remove(args[1])
        else: print(USAGE)
    except KeyboardInterrupt:
        print("\n  Cancelled by user.")
        sys.exit(0)

if __name__ == "__main__":
    main()
