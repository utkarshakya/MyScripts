"""
adb_wireless_connect.py - v2.1.0

Clean & Streamlined Android Wireless Debugging.
"""

import sys
import subprocess
import shutil
import time

# --- UI Helpers ---
def ok(msg: str):    print(f"\033[92m[OK]\033[0m  {msg}")
def info(msg: str):  print(f"\033[94m[..]\033[0m  {msg}")
def warn(msg: str):  print(f"\033[93m[!!]\033[0m  {msg}")
def err(msg: str):   print(f"\033[91m[ERR]\033[0m {msg}")

def run(cmd: list[str], capture=True) -> subprocess.CompletedProcess:
    try:
        if capture:
            return subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return subprocess.run(cmd)
    except Exception as e:
        err(f"Error executing {' '.join(cmd)}: {e}")
        sys.exit(1)

def check_env():
    if not shutil.which("adb"):
        err("ADB not found in PATH.")
        sys.exit(1)

# --- Commands ---

def cmd_sync():
    """Restarts ADB server and waits for auto-connection."""
    info("Restarting ADB server for auto-discovery...")
    run(["adb", "kill-server"])
    run(["adb", "start-server"])
    
    info("Waiting for device to connect automatically (10s timeout)...")
    time.sleep(10)  # Initial wait for devices to appear
    start_time = time.time()
    while time.time() - start_time < 10:
        result = run(["adb", "devices"])
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1 and "device" in lines[1]:
            ok("Wireless device(s) connected.")
            print(result.stdout.strip())
            return
        time.sleep(1)
    
    warn("No devices found yet. Current state:")
    result = run(["adb", "devices"])
    print(result.stdout.strip())

def cmd_pair():
    """Helper for one-time pairing."""
    print("\n  \033[1mOne-Time Pairing\033[0m")
    print("  " + "─" * 25)
    print("  Phone: Wireless Debugging -> Pair with code\n")
    
    target = input("  Target (IP:Port): ").strip()
    code = input("  Pairing Code:    ").strip()
    
    if not target or not code:
        err("Both Target and Code are required.")
        return

    info(f"Pairing with {target}...")
    run(["adb", "pair", target, code], capture=False)
    print("")

def cmd_list():
    """Shows connected devices."""
    result = run(["adb", "devices"])
    print("\n" + result.stdout.strip() + "\n")

# --- CLI Entry ---

def show_help():
    print(f"""
  \033[1mAndroid Wireless Helper\033[0m (v2.1.0)
  ─────────────────────────────
  \033[94msync\033[0m (s)   Restart server & auto-connect
  \033[94mpair\033[0m (p)   One-time device pairing
  \033[94mlist\033[0m (l)   Show connected devices
  ─────────────────────────────
  Usage: \033[92madbw <command>\033[0m
    """)

def main():
    check_env()
    args = sys.argv[1:]
    
    if not args:
        show_help()
        return

    cmd = args[0].lower()
    if cmd in ["sync", "s"]:
        cmd_sync()
    elif cmd in ["pair", "p"]:
        cmd_pair()
    elif cmd in ["list", "l"]:
        cmd_list()
    else:
        show_help()

if __name__ == "__main__":
    main()
