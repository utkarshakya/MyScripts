#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

# --- UI Helpers ---
def ok(msg: str):    print(f"\033[92m[OK]\033[0m  {msg}")
def info(msg: str):  print(f"\033[94m[..]\033[0m  {msg}")
def warn(msg: str):  print(f"\033[93m[!!]\033[0m  {msg}")
def err(msg: str):   print(f"\033[91m[ERR]\033[0m {msg}")

def run_logcat(filters: list[str]) -> int:
    cmd = ["adb", "logcat", "-s", *filters]
    try:
        info(f"Starting logcat with filters: {', '.join(filters)}")
        subprocess.run(cmd, check=False)
    except FileNotFoundError:
        err("adb command not found.")
        return 1
    except KeyboardInterrupt:
        print("\n")
        ok("Logcat stopped.")
        return 0
    except Exception as exc:
        err(f"Failed to run adb logcat: {exc}")
        return 1
    return 0

# --- CLI Entry ---

def show_help():
    print(f"""
  \033[1mSchoolDriver Log Tools\033[0m
  ─────────────────────────────
  \033[94mnative\033[0m (n)   Show native logs (Ride, Location)
  \033[94mapp\033[0m    (a)   Show app logs (ReactNativeJS)
  \033[94mall\033[0m    (A)   Show both native and app logs
  ─────────────────────────────
  Usage: \033[92msdlog <command>\033[0m
    """)

def main() -> int:
    args = sys.argv[1:]
    if not args:
        show_help()
        return 0

    command = args[0].lower()

    if command in ["help", "h"]:
        show_help()
        return 0
    elif command in ["native", "n"]:
        return run_logcat(["RideService:*", "LocationServiceModule:*", "LocationServicePackage:*"])
    elif command in ["app", "a"]:
        return run_logcat(["ReactNativeJS:*"])
    elif command in ["all", "A"]:
        return run_logcat(
            ["RideService:*", "LocationServiceModule:*", "LocationServicePackage:*", "ReactNativeJS:*"]
        )
    else:
        show_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())
