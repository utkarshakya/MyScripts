# adbw — Android Wireless Debugging Helper

A Python script that simplifies connecting to Android devices via **Wireless Debugging** (Android 11+) — no USB cable required, ever.

It stores your device IPs, remembers past connection ports, and can auto-reconnect using port history.

---

## Why

Android's Wireless Debugging requires you to:
1. Pair once using a 6-digit code
2. Then connect every session using an ephemeral IP:port shown on your phone

This script makes step 2 painless — and even attempts to reconnect automatically if a port repeats.

---

## Requirements

- Python 3.10+
- [Android SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) (`adb` must be in PATH)
- Android 11+ device with **Developer Options → Wireless Debugging** enabled

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/your-username/adbw.git
cd adbw
```

### 2. Run it

No manual configuration needed. Just run `adbw pair <device_name>` and the script creates and manages `devices.json` for you automatically.

> **Important:** `devices.json` stores your device IPs and connection history. It is git-ignored (stays on your machine), but **do not delete it** or you will lose your saved devices.

### 3. (Optional) Add a PowerShell alias

Add this to your PowerShell `$PROFILE` so you can run `adbw` from anywhere:

```powershell
function Invoke-AdbWireless {
    python "C:\path\to\adb_wireless_connect.py" @args
}
Set-Alias adbw Invoke-AdbWireless
```

---

## Usage

### Pair a new device *(one time only)*

On your phone: **Developer Options → Wireless Debugging → Pair device with pairing code**

```
adbw pair <device_name>
```

You'll be asked for:
- Device IP *(shown on the Wireless Debugging main screen)*
- Pairing port *(shown on the pairing code screen)*
- 6-digit pairing code *(shown on the pairing code screen)*

The script saves the device name and IP to `devices.json` automatically — **you never need to edit the file by hand.**

---

### Connect every session

On your phone: **Developer Options → Wireless Debugging** — the main screen shows `IP:PORT`.

```bash
# Provide the port directly
adbw connect <device_name> <port>

# Or let the script prompt you
adbw connect <device_name>
```

Every successful connection saves the port to `known_ports` in `devices.json`.

---

### Auto-reconnect *(tries saved ports)*

```bash
adbw autoconnect <device_name>
```

Tries all previously used ports (newest first) silently. If Android reuses a port from a past session, this connects instantly with zero input.

If all ports fail, it tells you to use `adbw connect` with the current port from your phone.

---

### List devices

```bash
adbw list
```

Shows all saved devices, their IPs, known port history, and currently connected ADB devices.

---

### Remove a device

```bash
adbw remove <device_name>
```

---

## Typical daily workflow

```bash
# Toggle Wireless Debugging on → glance at phone for IP:PORT

adbw autoconnect pixel      # port repeated from before? instant connect ✓
adbw connect pixel 44821    # new port? type it → saved for next time ✓
```

---

## devices.json structure

```json
{
  "pixel": {
    "ip": "192.168.1.105",
    "known_ports": [44821, 39217, 52009]
  }
}
```

| Field | Description |
|---|---|
| `ip` | Local network IP of the device (stable on same Wi-Fi) |
| `known_ports` | Past connection ports, newest first. Used by `autoconnect`. |

---

## License

MIT
