# Android ADB Device Manager

Interactive Python utility for working with **ADB** (Android Debug Bridge): list devices, inspect the active phone or tablet, restart or reset ADB, and use **Wireless Debugging** (pair + connect by IP and port).

Run it once and drive everything from a numbered **main menu** in the terminal.

---

## What it does

| Menu | Action |
|------|--------|
| **1. Auto Connect Device** | Restarts the ADB server, then polls `adb devices` up to five times (about 1.5s apart) to detect a device that shows as connected and ready. |
| **2. Manual Connect** | Prompts for **IP** and **port**, validates them, then runs `adb connect IP:PORT` (for Wireless Debugging after pairing). |
| **3. Pair Wireless Device** | Walks you through **Wireless Debugging → Pair device with pairing code**, then runs `adb pair IP:PORT CODE`. |
| **4. Show Connected Devices** | Runs `adb devices -l` and prints a readable card per device (model, USB vs wireless, address, status). |
| **5. Show Device Information** | Uses the first connected **ready** device and prints manufacturer, model, Android version, codename, and battery level via `adb shell` / `dumpsys`. |
| **6. Restart ADB Server** | `adb kill-server` then `adb start-server`. |
| **7. Reset ADB** | `adb disconnect` (all), then `adb kill-server`. |
| **8. Exit** | Quits the program. |

After most actions the script waits for **Enter** before returning to the menu. Success, warning, and error lines are also appended to a log file (see below).

---

## Requirements

- **Python** 3.8+ (tested with 3.10+)
- **[Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools)** — `adb` must be on your `PATH`
- For wireless workflows: **Android 11+** with **Developer options → Wireless debugging** enabled (pair once, then connect using the IP and ports shown on the device)

---

## Run

From the project directory:

```bash
python adb_manager.py
```

If `adb` is missing, the program prints install and PATH instructions and exits.

---

## Typical wireless workflow

1. On the phone: enable **Wireless debugging** and use **Pair device with pairing code** when the tool asks you to pair.
2. In the app: choose **3**, enter **IP**, **pairing port**, and **6-digit code** from the phone.
3. On the phone: note the **IP** and **port** on the main Wireless debugging screen for normal TCP connections.
4. Choose **2** and enter that **IP** and **port** to run `adb connect`.

If the device was already authorized and the network is stable, **1** may pick it up after a server refresh without typing IP/port again.

---

## Logging

The script appends human-readable lines to **`adb_manager.log`** in the current working directory (usually the folder you launched the script from). Log entries mirror the on-screen `[INFO]`, `[SUCCESS]`, `[WARNING]`, and `[ERROR]` messages.

`*.log` is listed in `.gitignore` so logs are not committed by mistake.

---

## Optional: PowerShell alias

To run the manager from anywhere, add something like this to your PowerShell profile (`$PROFILE`):

```powershell
function Invoke-AdbManager {
    python "C:\path\to\run_adb_headless\adb_manager.py" @args
}
Set-Alias adbmenu Invoke-AdbManager
```

Then run `adbmenu` (or use the function name you prefer).

---

## License

MIT
