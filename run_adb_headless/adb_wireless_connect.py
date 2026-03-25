"""
adb_wireless_connect.py - v2.6.0

Clean & Streamlined Android Wireless Debugging.
Features: Auto-discovery, Pairing History, and Device Name Caching.
"""

import sys
import subprocess
import shutil
import time
import os
import re
import json

# --- Configuration ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(BASE_DIR, "device_cache.json")

# --- UI Helpers ---
def ok(msg: str):    print(f"\033[92m[OK]\033[0m  {msg}")
def info(msg: str):  print(f"\033[94m[..]\033[0m  {msg}")
def warn(msg: str):  print(f"\033[93m[!!]\033[0m  {msg}")
def err(msg: str):   print(f"\033[91m[ERR]\033[0m {msg}")

def run(cmd: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except Exception as e:
        err(f"Error: {e}")
        sys.exit(1)

def check_env():
    if not shutil.which("adb"):
        err("ADB not found in PATH.")
        sys.exit(1)

# --- Cache Management ---

def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_cache(cache: dict):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)
    except:
        pass

def update_cache_from_connected():
    """Parses adb devices -l and updates the ID -> Model mapping."""
    res = run(["adb", "devices", "-l"])
    cache = load_cache()
    updated = False
    
    for line in res.stdout.strip().splitlines():
        if "model:" in line:
            parts = line.split()
            device_id = parts[0]
            model = "Unknown"
            for p in parts:
                if p.startswith("model:"):
                    model = p.replace("model:", "").replace("_", " ")
            
            # Extract serial part if it's an adb-XXXXX style ID
            clean_id = device_id.split(".")[0] # Remove ._adb-tls-connect._tcp
            
            if cache.get(clean_id) != model:
                cache[clean_id] = model
                updated = True
    
    if updated:
        save_cache(cache)

# --- Commands ---

def cmd_sync():
    """Restarts ADB server and waits for auto-connection."""
    info("Restarting ADB server for auto-discovery...")
    run(["adb", "kill-server"])
    run(["adb", "start-server"])
    
    info("Polling for paired devices (10s timeout)...")
    start_time = time.time()
    while time.time() - start_time < 10:
        update_cache_from_connected()
        result = run(["adb", "devices"])
        lines = result.stdout.strip().splitlines()
        if len(lines) > 1 and any("device" in line and not line.startswith("List") for line in lines):
            ok("Wireless device(s) connected.")
            cmd_list()
            return
        time.sleep(1)
    
    warn("No devices found yet.")
    cmd_list()

def cmd_paired():
    """Reads paired devices from adb_known_hosts.pb and uses cache for names."""
    update_cache_from_connected()
    cache = load_cache()
    
    home = os.path.expanduser("~")
    pb_file = os.path.join(home, ".android", "adb_known_hosts.pb")
    
    if not os.path.exists(pb_file):
        warn("No pairing history file found.")
        return

    try:
        with open(pb_file, "rb") as f:
            data = f.read()
            matches = re.findall(b"adb-[a-zA-Z0-9._-]+", data)
            unique_paired = sorted(list(set(m.decode('utf-8') for m in matches)))
    except Exception as e:
        err(f"Failed to read pairing history: {e}")
        return

    res_dev = run(["adb", "devices", "-l"])
    connected_output = res_dev.stdout.strip().splitlines()
    connected_ids = [line.split()[0] for line in connected_output if len(line.split()) > 0 and not line.startswith("List")]

    if not unique_paired:
        warn("No paired devices found in history.")
    else:
        print("\n  \033[1mPaired Devices History\033[0m")
        print("  " + "─" * 50)
        for dev in unique_paired:
            name = cache.get(dev, "Unknown Device")
            status = "\033[92mONLINE\033[0m" if any(dev in cid for cid in connected_ids) else "\033[90mOFFLINE\033[0m"
            
            # Color name if online
            display_name = f"\033[1m{name}\033[0m" if "ONLINE" in status else name
            print(f"    \033[94m•\033[0m {display_name:<25} \033[90m({dev})\033[0m  {status}")
        print("")
        if "Unknown Device" in str(cache):
            info("Note: Device names appear after they connect for the first time.")

def cmd_list():
    """Shows all connected devices with friendly names."""
    update_cache_from_connected()
    res = run(["adb", "devices"])
    print("\n" + res.stdout.strip() + "\n")

def cmd_pair():
    """Helper for one-time pairing."""
    print("\n  \033[1mOne-Time Pairing\033[0m")
    print("  " + "─" * 30)
    print("  Phone: Wireless Debugging -> Pair with code\n")
    target = input("  Target (IP:Port): ").strip()
    code = input("  Pairing Code:    ").strip()
    if not target or not code:
        err("Target and Code are required.")
        return
    info(f"Pairing with {target}...")
    subprocess.run(["adb", "pair", target, code])
    print("")

# --- CLI Entry ---

def show_help():
    print(f"""
  \033[1mAndroid Wireless Helper\033[0m (v2.6.0)
  ──────────────────────────────────────
  \033[94msync\033[0m   (s)   Restart server & auto-connect
  \033[94mpaired\033[0m (pr)  List all paired devices (History)
  \033[94mlist\033[0m   (l)   Show all connected devices
  \033[94mpair\033[0m   (p)   One-time device pairing
  ──────────────────────────────────────
  Usage: \033[92madbw <command>\033[0m
    """)

def main():
    check_env()
    args = sys.argv[1:]
    if not args:
        show_help()
        return

    cmd = args[0].lower()
    if cmd in ["sync", "s"]: cmd_sync()
    elif cmd in ["paired", "pr"]: cmd_paired()
    elif cmd in ["list", "l"]: cmd_list()
    elif cmd in ["pair", "p"]: cmd_pair()
    else: show_help()

if __name__ == "__main__":
    main()
