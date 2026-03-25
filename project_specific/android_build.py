#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable

# --- UI Helpers ---
def ok(msg: str):    print(f"\033[92m[OK]\033[0m  {msg}")
def info(msg: str):  print(f"\033[94m[..]\033[0m  {msg}")
def warn(msg: str):  print(f"\033[93m[!!]\033[0m  {msg}")
def err(msg: str):   print(f"\033[91m[ERR]\033[0m {msg}")

def project_paths(cwd: Path) -> tuple[Path, Path, Path, Path]:
    return (
        cwd / "android" / "app" / "build" / "outputs" / "apk" / "development" / "debug",
        cwd / "android" / "app" / "build" / "outputs" / "apk" / "staging" / "release",
        cwd / "android" / "app" / "build" / "outputs" / "apk" / "production" / "release",
        cwd / "android",
    )

def get_gradle_wrapper(android_dir: Path) -> Path | None:
    candidates = [android_dir / "gradlew.bat", android_dir / "gradlew"]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None

def run_gradle(cwd: Path, task: str, label: str, clean: bool = False) -> int:
    _, _, _, android_dir = project_paths(cwd)
    if not android_dir.exists():
        err("Android folder not found. Run this from project root.")
        return 1

    wrapper = get_gradle_wrapper(android_dir)
    if wrapper is None:
        err("Gradle wrapper not found.")
        return 1

    info(f"Building {label}...")
    command = [str(wrapper)]
    if clean:
        command.append("clean")
    if task in {":app:assembleStagingRelease", ":app:assembleProductionRelease"}:
        command.append("-PreactNativeArchitectures=armeabi-v7a,arm64-v8a")
    command.append(task)

    try:
        completed = subprocess.run(command, cwd=str(android_dir), check=False)
    except Exception as exc:
        err(f"Failed to execute Gradle: {exc}")
        return 1

    if completed.returncode != 0:
        err(f"{label} build failed.")
        return completed.returncode

    ok(f"{label} build complete.")
    return 0

def open_apk_output(cwd: Path) -> int:
    debug_dir, staging_dir, release_dir, _ = project_paths(cwd)
    all_apks = list(debug_dir.glob("*.apk")) + list(staging_dir.glob("*.apk")) + list(release_dir.glob("*.apk"))
    
    if not all_apks:
        err("No APKs found. Build first.")
        return 1

    latest_apk = max(all_apks, key=lambda p: p.stat().st_mtime)
    try:
        subprocess.run(["explorer", str(latest_apk.parent)], check=False)
        ok(f"Opened: {latest_apk.parent.name}")
    except Exception as exc:
        err(f"Failed to open explorer: {exc}")
        return 1
    return 0

def rename_apk(cwd: Path) -> int:
    package_json_path = cwd / "package.json"
    if not package_json_path.exists():
        err("package.json not found.")
        return 1

    try:
        package_data = json.loads(package_json_path.read_text(encoding="utf-8"))
        project_name = package_data.get("name")
    except Exception:
        err("Failed to parse package.json.")
        return 1

    debug_dir, staging_dir, release_dir, _ = project_paths(cwd)
    all_apks = list(debug_dir.glob("*.apk")) + list(staging_dir.glob("*.apk")) + list(release_dir.glob("*.apk"))
    
    if not all_apks:
        err("No APK found to rename.")
        return 1

    apk_file = max(all_apks, key=lambda p: p.stat().st_mtime)
    
    # Simple env detection
    env = "debug"
    if "staging" in str(apk_file).lower(): env = "staging"
    if "production" in str(apk_file).lower() or "release" in str(apk_file).lower(): env = "release"

    date_part = datetime.now().strftime("%b_%d")
    new_name = f"{project_name}_{env}_{date_part}.apk"
    new_path = apk_file.parent / new_name

    try:
        if new_path.exists(): new_path.unlink()
        apk_file.rename(new_path)
        ok(f"Renamed to: {new_name}")
    except Exception as exc:
        err(f"Rename failed: {exc}")
        return 1
    return 0

# --- CLI Entry ---

def show_help():
    print(f"""
  \033[1mAndroid Build Tools\033[0m
  ─────────────────────────────
  \033[94mdbg\033[0m / \033[94mdc\033[0m    Build Debug APK (dc = clean)
  \033[94mstg\033[0m / \033[94msc\033[0m    Build Staging APK (sc = clean)
  \033[94mrel\033[0m / \033[94mrc\033[0m    Build Release APK (rc = clean)
  \033[94mopen\033[0m (o)    Open APK output folder
  \033[94mrename\033[0m (rn)  Rename latest APK with date
  ─────────────────────────────
  Usage: \033[92mab <command>\033[0m
    """)

def main() -> int:
    args = sys.argv[1:]
    if not args:
        show_help()
        return 0

    cmd = args[0].lower()
    cwd = Path.cwd()

    if cmd in ["help", "h"]: show_help()
    elif cmd == "dbg": return run_gradle(cwd, ":app:assembleDevelopmentDebug", "Debug APK")
    elif cmd == "dc":  return run_gradle(cwd, ":app:assembleDevelopmentDebug", "Debug APK", clean=True)
    elif cmd == "stg": return run_gradle(cwd, ":app:assembleStagingRelease", "Staging APK")
    elif cmd == "sc":  return run_gradle(cwd, ":app:assembleStagingRelease", "Staging APK", clean=True)
    elif cmd == "rel": return run_gradle(cwd, ":app:assembleProductionRelease", "Release APK")
    elif cmd == "rc":  return run_gradle(cwd, ":app:assembleProductionRelease", "Release APK", clean=True)
    elif cmd in ["open", "o"]: return open_apk_output(cwd)
    elif cmd in ["rename", "rn", "rapk"]: return rename_apk(cwd)
    else:
        show_help()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
