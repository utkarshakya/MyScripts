#!/usr/bin/env python3
"""
Universal Script Runner v1.2.0
A robust tool to run scripts on multiple files in a folder.
"""

import sys
import subprocess
import os
import re
import argparse
from pathlib import Path

# --- UI Helpers (Standard Lib only, Rich optional) ---
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import track
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

def info(msg):
    if HAS_RICH: console.print(f"[blue][..][/blue] {msg}")
    else: print(f"[..] {msg}")

def ok(msg):
    if HAS_RICH: console.print(f"[green][OK][/green] {msg}")
    else: print(f"[OK] {msg}")

def warn(msg):
    if HAS_RICH: console.print(f"[yellow][!!][/yellow] {msg}")
    else: print(f"[!!] {msg}")

def err(msg):
    if HAS_RICH: console.print(f"[red][ERR][/red] {msg}")
    else: print(f"[ERR] {msg}")

# --- Core Logic ---

class ScriptRunner:
    def __init__(self, folder, command, pattern="*", recursive=False, mode="capture"):
        self.folder = Path(folder)
        self.command = command
        self.pattern = pattern
        self.recursive = recursive
        self.mode = mode
        self.results = {"success": [], "failed": []}

    def find_files(self):
        func = self.folder.rglob if self.recursive else self.folder.glob
        return [f for f in func(self.pattern) if f.is_file()]

    def run_on_file(self, file_path):
        cmd = self.command.replace("{FILE}", f'"{file_path}"') if "{FILE}" in self.command else f'{self.command} "{file_path}"'
        try:
            if self.mode == "passthrough":
                print(f"\n--- {file_path.name} ---")
                res = subprocess.run(cmd, shell=True)
                return res.returncode == 0, ""
            else:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
                return res.returncode == 0, res.stderr if res.returncode != 0 else res.stdout
        except Exception as e:
            return False, str(e)

    def execute(self):
        files = self.find_files()
        if not files:
            err(f"No files found matching '{self.pattern}' in {self.folder}")
            return

        info(f"Processing {len(files)} files...")
        
        file_iter = track(files, description="Running...") if HAS_RICH and self.mode == "capture" else files
        
        for f in file_iter:
            success, output = self.run_on_file(f)
            if success:
                self.results["success"].append(f)
                if self.mode == "capture": ok(f.name)
            else:
                self.results["failed"].append((f, output))
                err(f"{f.name} failed: {output.strip().splitlines()[0] if output else 'Unknown error'}")

        self.summary()

    def summary(self):
        total = len(self.results["success"]) + len(self.results["failed"])
        if total == 0: return
        
        print("\n" + "="*30)
        ok(f"Success: {len(self.results['success'])}")
        if self.results["failed"]:
            err(f"Failed:  {len(self.results['failed'])}")
        print("="*30)

# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="Run a script on all files matching a pattern.")
    parser.add_argument("-f", "--folder", required=True, help="Target folder")
    parser.add_argument("-s", "--script", required=True, help="Command to run (e.g. 'python process.py')")
    parser.add_argument("-p", "--pattern", default="*", help="File pattern (e.g. *.csv)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Search subfolders")
    parser.add_argument("-m", "--mode", choices=["capture", "passthrough"], default="capture", help="Execution mode")

    if len(sys.argv) == 1:
        # Simple Interactive Fallback
        print("🚀 Universal Script Runner (v1.2.0)")
        folder = input("Folder path: ").strip()
        script = input("Command (use {FILE} as placeholder): ").strip()
        pattern = input("Pattern [default *]: ").strip() or "*"
        recursive = input("Recursive? (y/n): ").lower() == "y"
        mode = "passthrough" if input("Show live output? (y/n): ").lower() == "y" else "capture"
        runner = ScriptRunner(folder, script, pattern, recursive, mode)
    else:
        args = parser.parse_args()
        runner = ScriptRunner(args.folder, args.script, args.pattern, args.recursive, args.mode)

    try:
        runner.execute()
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    main()
