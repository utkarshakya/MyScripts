# adb_manager_v4.py
# Simplified and Refactored ADB Device Manager

import os
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime

VERSION = "4.0.0"

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adb_manager.log")

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
ENDC = "\033[0m"


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input(f"\n{CYAN}Press ENTER to continue...{ENDC}")


def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def log(message, level="info"):
    colors = {
        "success": GREEN,
        "error": RED,
        "warn": YELLOW,
        "info": BLUE,
    }

    label = level.upper()
    color = colors.get(level, WHITE)

    print(f"{color}[{label}]{ENDC} {message}")
    write_log(f"[{label}] {message}")


def draw_line(char="="):
    width = shutil.get_terminal_size((100, 20)).columns
    print(BOLD + char * width + ENDC)


def show_header():
    clear_screen()
    width = shutil.get_terminal_size((100, 20)).columns

    draw_line()
    print(f"{BOLD}{CYAN}{'ANDROID ADB DEVICE MANAGER'.center(width)}{ENDC}")
    print(f"{WHITE}{('Version: ' + VERSION).center(width)}{ENDC}")
    draw_line()


def run_command(command):
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), 1


def check_adb():
    return shutil.which("adb") is not None


def validate_address(address):
    try:
        ip, port = address.split(":")
        socket.inet_aton(ip)

        port_num = int(port)
        return 1 <= port_num <= 65535

    except Exception:
        return False


def parse_status(status):
    if status == "device":
        return f"{GREEN}READY{ENDC}"

    if status == "offline":
        return f"{YELLOW}OFFLINE{ENDC}"

    if status == "unauthorized":
        return f"{RED}UNAUTHORIZED{ENDC}"

    return f"{RED}{status.upper()}{ENDC}"


def get_devices():
    stdout, _, code = run_command("adb devices -l")

    if code != 0:
        return []

    devices = []

    for line in stdout.splitlines()[1:]:
        line = line.strip()

        if not line:
            continue

        parts = line.split()

        if len(parts) < 2:
            continue

        device_id = parts[0]
        status = parts[1]

        model_match = re.search(r"model:(\S+)", line)

        model = (
            model_match.group(1).replace("_", " ")
            if model_match
            else "Unknown Device"
        )

        devices.append(
            {
                "id": device_id,
                "status": status,
                "model": model,
                "connection": (
                    "Wireless"
                    if ":" in device_id
                    or "_adb-tls-connect._tcp" in device_id
                    else "USB"
                ),
            }
        )

    return devices


def list_devices():
    show_header()

    devices = get_devices()

    print(f"{BOLD}{CYAN}CONNECTED DEVICES{ENDC}")
    draw_line("-")

    if not devices:
        print("No connected devices found.")
        pause()
        return

    for i, device in enumerate(devices, start=1):
        print(f"[{i}] {device['model']}")
        print(f"    Status     : {parse_status(device['status'])}")
        print(f"    Connection : {device['connection']}")
        print(f"    Address    : {device['id']}")
        draw_line("-")

    pause()


def select_device():
    devices = get_devices()

    if not devices:
        return None

    print()

    for index, device in enumerate(devices, start=1):
        print(
            f"{index}. {device['model']} "
            f"({device['id']})"
        )

    choice = input("\nSelect device: ").strip()

    if not choice.isdigit():
        return None

    index = int(choice) - 1

    if index < 0 or index >= len(devices):
        return None

    return devices[index]


def auto_connect():
    show_header()

    log("Restarting ADB...", "info")

    run_command("adb disconnect")
    run_command("adb kill-server")
    run_command("adb start-server")

    for attempt in range(1, 6):
        print(f"Scanning... ({attempt}/5)")
        time.sleep(1.5)

        if get_devices():
            log("Device detected.", "success")
            pause()
            return

    log("No device detected.", "warn")
    pause()


def manual_connect():
    show_header()

    address = input("Enter Device Address (IP:PORT): ").strip()

    if not validate_address(address):
        log("Invalid address format.", "error")
        pause()
        return

    stdout, stderr, code = run_command(f"adb connect {address}")

    if code == 0:
        log(stdout or "Connected.", "success")
    else:
        log(stderr or stdout, "error")

    pause()


def pair_device():
    show_header()

    print("Example: 192.168.1.20:37123 123456\n")

    pair_input = input(
        "Enter Pairing Details (IP:PORT CODE): "
    ).strip()

    try:
        address, code = pair_input.split()
    except ValueError:
        log("Invalid format.", "error")
        pause()
        return

    if not validate_address(address):
        log("Invalid address.", "error")
        pause()
        return

    stdout, stderr, result = run_command(
        f"adb pair {address} {code}"
    )

    if result == 0:
        log(stdout, "success")
    else:
        log(stderr or stdout, "error")

    pause()


def disconnect_device():
    show_header()

    wireless_devices = [
        d for d in get_devices()
        if d["connection"] == "Wireless"
    ]

    if not wireless_devices:
        log("No wireless devices connected.", "warn")
        pause()
        return

    for index, device in enumerate(wireless_devices, start=1):
        print(f"{index}. {device['model']} ({device['id']})")

    choice = input("\nSelect device to disconnect: ").strip()

    if not choice.isdigit():
        log("Invalid selection.", "error")
        pause()
        return

    idx = int(choice) - 1

    if idx < 0 or idx >= len(wireless_devices):
        log("Invalid selection.", "error")
        pause()
        return

    device = wireless_devices[idx]

    stdout, stderr, code = run_command(
        f"adb disconnect {device['id']}"
    )

    if code == 0:
        log(stdout or "Disconnected.", "success")
    else:
        log(stderr or stdout, "error")

    pause()


def show_device_info():
    show_header()

    device = select_device()

    if not device:
        log("No valid device selected.", "warn")
        pause()
        return

    device_id = device["id"]

    commands = {
        "Manufacturer": f'adb -s "{device_id}" shell getprop ro.product.manufacturer',
        "Model": f'adb -s "{device_id}" shell getprop ro.product.model',
        "Android Version": f'adb -s "{device_id}" shell getprop ro.build.version.release',
        "Device Name": f'adb -s "{device_id}" shell getprop ro.product.device',
    }

    print()

    for label, cmd in commands.items():
        stdout, _, _ = run_command(cmd)
        print(f"{label:<18}: {stdout}")

    pause()


def restart_adb():
    show_header()

    log("Disconnecting devices...", "info")
    run_command("adb disconnect")

    log("Stopping server...", "info")
    run_command("adb kill-server")

    log("Starting server...", "info")
    run_command("adb start-server")

    log("ADB restarted successfully.", "success")

    pause()


def show_menu():
    show_header()

    print("1. Auto Connect Device")
    print("2. Manual Connect")
    print("3. Pair Wireless Device")
    print("4. Show Connected Devices")
    print("5. Disconnect Device")
    print("6. Show Device Information")
    print("7. Restart ADB")
    print("8. Exit")

    draw_line("-")


def main():
    if not check_adb():
        print("ADB not found in PATH.")
        return

    while True:
        show_menu()

        choice = input("Enter Selection: ").strip()

        if choice == "1":
            auto_connect()
        elif choice == "2":
            manual_connect()
        elif choice == "3":
            pair_device()
        elif choice == "4":
            list_devices()
        elif choice == "5":
            disconnect_device()
        elif choice == "6":
            show_device_info()
        elif choice == "7":
            restart_adb()
        elif choice == "8":
            break
        else:
            log("Invalid selection.", "warn")
            pause()


if __name__ == "__main__":
    main()
