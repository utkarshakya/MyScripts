# Professional ADB Device Manager (Improved UX Version)

import subprocess
import os
import time
import re
import shutil
import socket
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

VERSION = "3.0.0"
LOG_FILE = "adb_manager.log"

# ANSI COLORS
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
BOLD = "\033[1m"
ENDC = "\033[0m"

# ============================================================
# UTILITY FUNCTIONS
# ============================================================


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")



def pause():
    input(f"\n{CYAN}Press ENTER to continue...{ENDC}")



def write_log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")



def log(message, level="info"):

    if level == "success":
        print(f"{GREEN}[SUCCESS]{ENDC} {message}")

    elif level == "error":
        print(f"{RED}[ERROR]{ENDC} {message}")

    elif level == "warn":
        print(f"{YELLOW}[WARNING]{ENDC} {message}")

    elif level == "info":
        print(f"{BLUE}[INFO]{ENDC} {message}")

    else:
        print(message)

    write_log(f"[{level.upper()}] {message}")



def get_terminal_width():
    return shutil.get_terminal_size((100, 20)).columns



def draw_line(char="="):
    print(BOLD + char * get_terminal_width() + ENDC)



def show_header():

    clear_screen()

    width = get_terminal_width()

    draw_line()

    print(f"{BOLD}{CYAN}{'ANDROID ADB DEVICE MANAGER'.center(width)}{ENDC}")
    print(f"{WHITE}{'Professional CLI Utility'.center(width)}{ENDC}")
    print(f"{WHITE}{('Version: ' + VERSION).center(width)}{ENDC}")

    draw_line()


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================


def is_adb_available():

    adb_path = shutil.which("adb")

    return adb_path is not None



def validate_ip(ip):

    try:
        socket.inet_aton(ip)
        return True

    except socket.error:
        return False



def validate_port(port):

    if not port.isdigit():
        return False

    port_num = int(port)

    return 1 <= port_num <= 65535


# ============================================================
# COMMAND EXECUTION
# ============================================================


def run_command(cmd):

    try:

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        return stdout, stderr, result.returncode

    except subprocess.TimeoutExpired:
        return "", "Operation timed out.", 1

    except Exception as e:
        return "", str(e), 1


# ============================================================
# ADB STATUS FUNCTIONS
# ============================================================


def check_adb_installation():

    if not is_adb_available():

        draw_line()

        log("ADB executable was not found.", "error")

        print()

        print("Please install Android Platform Tools.")
        print("Then add ADB to your system PATH.")
        print()
        print("Official Download:")
        print("https://developer.android.com/tools/releases/platform-tools")

        draw_line()

        return False

    return True



def restart_adb_server():

    log("Stopping ADB server...", "info")
    run_command("adb kill-server")

    log("Starting ADB server...", "info")
    run_command("adb start-server")

    log("ADB server restarted successfully.", "success")


# ============================================================
# DEVICE FUNCTIONS
# ============================================================


def parse_device_status(status):

    if status == "device":
        return f"{GREEN}READY{ENDC}"

    elif status == "offline":
        return f"{YELLOW}OFFLINE{ENDC}"

    elif status == "unauthorized":
        return (
            f"{RED}UNAUTHORIZED "
            f"(Allow USB Debugging on device){ENDC}"
        )

    return f"{RED}{status.upper()}{ENDC}"



def list_devices_verbose():

    show_header()

    stdout, stderr, code = run_command("adb devices -l")

    if code != 0:
        log(stderr, "error")
        pause()
        return

    lines = stdout.splitlines()
    device_lines = lines[1:]

    valid_devices = []

    for line in device_lines:
        if line.strip():
            valid_devices.append(line)

    draw_line()

    print(f"{BOLD}{CYAN}CONNECTED DEVICES{ENDC}")

    draw_line()

    if not valid_devices:

        print(f"{YELLOW}No connected devices detected.{ENDC}")

        draw_line()

        pause()

        return

    for index, line in enumerate(valid_devices, start=1):

        parts = line.split()

        device_id = parts[0]
        status = parts[1]

        # Detect model
        model_match = re.search(r"model:(\S+)", line)

        model_name = (
            model_match.group(1)
            if model_match
            else "Unknown Device"
        )

        model_name = model_name.replace("_", " ")

        # Connection type
        connection_type = (
            "Wireless"
            if ":" in device_id
            else "USB"
        )

        # Status formatting
        if status == "device":
            status_text = f"{GREEN}READY{ENDC}"

        elif status == "offline":
            status_text = f"{YELLOW}OFFLINE{ENDC}"

        elif status == "unauthorized":
            status_text = (
                f"{RED}UNAUTHORIZED "
                f"(Allow USB Debugging on device){ENDC}"
            )

        else:
            status_text = f"{RED}{status.upper()}{ENDC}"

        # Device Card
        print(f"{BOLD}[{index}] {model_name}{ENDC}")

        print(
            f"    {CYAN}Status{ENDC}      : "
            f"{status_text}"
        )

        print(
            f"    {CYAN}Connection{ENDC}  : "
            f"{connection_type}"
        )

        print(
            f"    {CYAN}Address{ENDC}     : "
            f"{device_id}"
        )

        draw_line("-")

    pause()


# ============================================================
# DEVICE INFORMATION
# ============================================================


def get_connected_device():

    stdout, _, _ = run_command("adb devices")

    lines = stdout.splitlines()[1:]

    for line in lines:

        if "device" in line and "offline" not in line:
            return line.split()[0]

    return None



def get_device_info():

    show_header()

    device = get_connected_device()

    if not device:
        log("No active device connected.", "warn")
        pause()
        return

    log(f"Fetching information for device: {device}", "info")

    commands = {
        "Manufacturer": "adb shell getprop ro.product.manufacturer",
        "Model": "adb shell getprop ro.product.model",
        "Android Version": "adb shell getprop ro.build.version.release",
        "Device Name": "adb shell getprop ro.product.device",
        "Battery Level": "adb shell dumpsys battery | findstr level"
        if os.name == "nt"
        else "adb shell dumpsys battery | grep level",
    }

    draw_line()

    for label, cmd in commands.items():

        stdout, _, _ = run_command(cmd)

        value = stdout.strip()

        if "Battery Level" in label:
            value = value.replace("level:", "").strip() + "%"

        print(f"{BOLD}{label:<20}:{ENDC} {value}")

    draw_line()

    pause()


# ============================================================
# CONNECTION FUNCTIONS
# ============================================================


def auto_connect():

    show_header()

    log("Refreshing ADB server...", "info")

    run_command("adb kill-server")
    run_command("adb start-server")

    print()

    for attempt in range(1, 6):

        print(
            f"{CYAN}Scanning for devices "
            f"(Attempt {attempt}/5)...{ENDC}"
        )

        time.sleep(1.5)

        stdout, _, _ = run_command("adb devices")

        if (
            "device" in stdout
            and "offline" not in stdout
            and len(stdout.splitlines()) > 1
        ):

            print()

            log("Device connected successfully.", "success")

            pause()

            list_devices_verbose()

            return

    print()

    log("Automatic connection timed out.", "warn")

    choice = input(
        f"\n{YELLOW}Would you like to connect manually? (y/n): {ENDC}"
    ).lower()

    if choice == "y":
        manual_connect()



def manual_connect():

    show_header()

    ip = input("Enter Device IP Address : ").strip()
    port = input("Enter Device Port       : ").strip()

    print()

    if not validate_ip(ip):
        log("Invalid IP address format.", "error")
        pause()
        return

    if not validate_port(port):
        log("Invalid port number.", "error")
        pause()
        return

    log(f"Connecting to {ip}:{port}...", "info")

    stdout, stderr, code = run_command(
        f"adb connect {ip}:{port}"
    )

    print()

    if code == 0 and "connected" in stdout.lower():
        log(stdout, "success")

    elif "failed to authenticate" in stderr.lower():
        log(
            "Authentication failed. Please allow USB debugging on your device.",
            "error"
        )

    else:
        log(stderr if stderr else stdout, "error")

    pause()



def pair_new_device():

    show_header()

    print("WIRELESS DEBUGGING PAIRING GUIDE")

    draw_line("-")

    print("1. Open Developer Options on your Android device")
    print("2. Open Wireless Debugging")
    print("3. Tap 'Pair Device with Pairing Code'")
    print("4. Enter the information below")

    draw_line("-")

    ip = input("Enter Device IP Address : ").strip()
    port = input("Enter Pairing Port      : ").strip()
    code = input("Enter Pairing Code      : ").strip()

    print()

    if not validate_ip(ip):
        log("Invalid IP address format.", "error")
        pause()
        return

    if not validate_port(port):
        log("Invalid pairing port.", "error")
        pause()
        return

    if not code:
        log("Pairing code cannot be empty.", "error")
        pause()
        return

    log("Starting pairing process...", "info")

    stdout, stderr, result_code = run_command(
        f"adb pair {ip}:{port} {code}"
    )

    print()

    if result_code == 0:
        log(stdout, "success")

    else:
        log(stderr if stderr else stdout, "error")

    pause()


# ============================================================
# RESET FUNCTION
# ============================================================


def reset_adb():

    show_header()

    log("Disconnecting all devices...", "info")
    run_command("adb disconnect")

    log("Stopping ADB server...", "info")
    run_command("adb kill-server")

    print()

    log("ADB reset completed successfully.", "success")

    pause()


# ============================================================
# MAIN MENU
# ============================================================


def show_menu():

    show_header()

    print(f"{BOLD}MAIN MENU{ENDC}\n")

    print("1. Auto Connect Device")
    print("2. Manual Connect")
    print("3. Pair Wireless Device")
    print("4. Show Connected Devices")
    print("5. Show Device Information")
    print("6. Restart ADB Server")
    print("7. Reset ADB")
    print("8. Exit")

    draw_line("-")



def main():

    if not check_adb_installation():
        return

    while True:

        show_menu()

        choice = input(f"{CYAN}Enter Selection: {ENDC}").strip()

        if choice == "1":
            auto_connect()

        elif choice == "2":
            manual_connect()

        elif choice == "3":
            pair_new_device()

        elif choice == "4":
            list_devices_verbose()

        elif choice == "5":
            get_device_info()

        elif choice == "6":
            show_header()
            restart_adb_server()
            pause()

        elif choice == "7":
            reset_adb()

        elif choice == "8":

            show_header()

            log("Thank you for using ADB Device Manager.", "success")

            break

        else:
            log("Invalid selection. Please choose a valid option.", "warn")
            pause()


# ============================================================
# ENTRY POINT
# ============================================================


if __name__ == "__main__":
    main()