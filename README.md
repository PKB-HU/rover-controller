# Rover Control System

A Python-based rover control project with **two control interfaces**:

1. **`rover.py`** — a **keyboard-controlled desktop client** for directly driving the rover from a computer.
2. **`server.py`** — a **Flask web server** that exposes rover controls through a browser-based interface.

Both files connect to the rover over **TCP sockets** and send movement commands such as forward, backward, turning, and stop.

---

# Project Structure

```bash
project/
│
├── rover.py          # Keyboard-based rover controller
├── server.py         # Flask web server for browser-based control
├── templates/
│   └── index.html    # Web control interface used by server.py
└── README.md
```

---

# Overview

This project provides two different ways to control the same rover:

## 1. `rover.py`

A local Python script that:

* Connects directly to the rover over TCP
* Reads keyboard input in real time
* Sends movement commands based on pressed keys
* Logs all activity with timestamps, packet sizes, and send timing

This is useful when you want **low-latency direct keyboard control** from a laptop or PC.

## 2. `server.py`

A Flask-based control server that:

* Runs a web application locally or on a networked machine
* Accepts HTTP requests from a browser UI
* Converts those requests into rover socket commands
* Logs connection events and commands sent to the rover

This is useful when you want **browser-based control**, mobile access, or a cleaner remote-control interface.

---

# How the System Works

The rover listens for TCP commands on a specific IP address and port.

Both `rover.py` and `server.py` connect to the rover using:

* **IP address** — configurable in each file
* **Port** — `6274`

Once connected, commands are sent as plain text strings followed by a newline, for example:

```text
w
wa
x
```

These commands correspond to movement actions like forward, forward-left, stop, etc.

---

# Command Reference

The project uses the following rover commands:

| Command | Action                                   |
| ------- | ---------------------------------------- |
| `w`     | Move forward                             |
| `wa`    | Move forward-left                        |
| `wd`    | Move forward-right                       |
| `s`     | Move backward                            |
| `sa`    | Move backward-left                       |
| `sd`    | Move backward-right                      |
| `x`     | Stop                                     |
| `esc`   | Escape / disconnect (used in `rover.py`) |

---

# File 1: `rover.py`

## Purpose

`rover.py` is a **real-time keyboard controller** for the rover. It continuously checks for key presses and sends the corresponding command over a socket connection.

## Features

* Connects directly to the rover over TCP
* Supports **W/A/S/D style directional control**
* Sends commands only when the movement state changes
* Automatically sends a **stop (`x`)** command when no movement key is pressed
* Logs:

  * timestamps
  * command descriptions
  * packet sizes
  * send timing (labeled as RTT in the script)

## Keyboard Controls

| Keys Pressed    | Command Sent                | Action              |
| --------------- | --------------------------- | ------------------- |
| `W`             | `w`                         | Forward             |
| `W + A`         | `wa`                        | Forward-left        |
| `W + D`         | `wd`                        | Forward-right       |
| `S`             | `s`                         | Backward            |
| `S + A`         | `sa`                        | Backward-left       |
| `S + D`         | `sd`                        | Backward-right      |
| No movement key | `x`                         | Stop                |
| `ESC`           | `esc` (disconnect behavior) | Disconnect and exit |

## How It Works

1. The script attempts to connect to the rover using the configured IP and port.
2. Once connected, it enters an infinite loop.
3. It checks keyboard state using the `keyboard` module.
4. When a valid movement combination is detected, it sends the corresponding command.
5. If no movement key is pressed, it sends `x` to stop the rover.
6. Pressing `ESC` disconnects and exits the program.

## Connection Settings in `rover.py`

```python
ip = "192.168.1.187"
port = 6274
```

If your rover uses a different IP, update the `ip` variable before running the script.

## Logging

Each run creates a timestamped `.log` file in the project directory, for example:

```bash
2026_07_07_14_22_31.log
```

Example log output:

```text
[14:22:31.114] Connecting to rover...
[14:22:31.320] Connected!
[14:22:35.101] Transmitting: forward command | Size: 2 bytes | RTT: 0.12 ms
[14:22:36.210] Transmitting: stop command | Size: 2 bytes | RTT: 0.08 ms
```

> Note: the script labels send timing as **RTT**, but the current implementation only measures the time taken to call `send()` locally. It does **not** measure a full round-trip response from the rover unless the rover explicitly sends acknowledgements back and the client measures them.

---

# File 2: `server.py`

## Purpose

`server.py` provides a **web-based control API and interface** for the rover using Flask.

Instead of reading the keyboard directly, it exposes HTTP routes that:

* connect to the rover
* disconnect from the rover
* send movement commands

A browser UI (typically `templates/index.html`) can call these routes using JavaScript.

## Features

* Flask web server
* Socket connection management for the rover
* Thread-safe socket access using `threading.Lock`
* Separate connect/disconnect/command routes
* Timestamped logging to console and file
* Background connection thread to avoid blocking the Flask request

## Connection Settings in `server.py`

```python
ip = "192.168.1.186"
port = 6274
```

If your rover has a different IP, update this value before running the server.

> Important: `rover.py` and `server.py` currently use **different rover IP addresses** in your code:
>
> * `rover.py` → `192.168.1.187`
> * `server.py` → `192.168.1.186`
>
> Make sure these are intentional. If both are meant to control the same rover, they should probably use the same IP address.

---

# Flask Routes in `server.py`

## `GET /`

Loads the web control page:

```python
@app.route('/')
def index():
    return render_template("index.html")
```

This expects a file at:

```bash
templates/index.html
```

---

## `POST /connect`

Starts a background thread to connect to the rover.

### Response

```json
{"status": "connecting"}
```

---

## `POST /disconnect`

Disconnects the active socket connection to the rover.

### Response

```json
{"status": "disconnected"}
```

---

## `POST /command`

Sends a movement command to the rover.

### Example request body

```json
{
  "command": "w"
}
```

### Example response

```json
{"status": "sent"}
```

Possible statuses:

* `"sent"` → command was successfully transmitted
* `"failed"` → sending failed
* `"no command"` → request did not include a command

---

# Example Browser/API Usage

## Connect to rover

```bash
curl -X POST http://localhost:5000/connect
```

## Send forward command

```bash
curl -X POST http://localhost:5000/command \
  -H "Content-Type: application/json" \
  -d "{\"command\":\"w\"}"
```

## Send stop command

```bash
curl -X POST http://localhost:5000/command \
  -H "Content-Type: application/json" \
  -d "{\"command\":\"x\"}"
```

## Disconnect

```bash
curl -X POST http://localhost:5000/disconnect
```

---

# Requirements

## Python Version

Recommended: **Python 3.9+**

## Python Packages

Install the required dependencies:

```bash
pip install flask keyboard
```

### Standard library modules used

These are built into Python and do not need installation:

* `socket`
* `threading`
* `time`
* `datetime`
* `os`

---

# Setup Instructions

## 1. Clone or copy the project

Place all files in one project folder.

Example structure:

```bash
project/
├── rover.py
├── server.py
├── templates/
│   └── index.html
└── README.md
```

## 2. Update rover IP addresses

Edit the rover IP in both scripts if needed.

### In `rover.py`

```python
ip = "192.168.1.187"
```

### In `server.py`

```python
ip = "192.168.1.186"
```

If both scripts are meant to control the same rover, use the same IP in both.

## 3. Make sure the rover is reachable

* The rover must be powered on
* The rover must be connected to the same network as the controlling device
* The rover must be listening on port **6274**

---

# Running the Project

# Option A — Keyboard Control with `rover.py`

Run:

```bash
python rover.py
```

### What happens

* The script repeatedly attempts to connect to the rover
* Once connected, it starts reading keyboard input
* Use the movement keys to drive the rover
* Press `ESC` to disconnect and exit

### Notes

* The `keyboard` module may require administrator/root permissions on some operating systems
* On Linux, you may need to run with elevated privileges depending on your environment

---

# Option B — Web Control with `server.py`

Run:

```bash
python server.py
```

Flask will start on:

```text
http://0.0.0.0:5000
```

Open a browser and go to:

```text
http://localhost:5000
```

or from another device on the same network:

```text
http://<your-computer-ip>:5000
```

From there, the browser UI in `index.html` can send commands to the rover through the Flask API.

---

# Logging

Both `rover.py` and `server.py` create timestamped log files automatically.

## Log format

Each log entry includes a time with millisecond precision:

```text
[14:30:12.123] Connected to rover at 192.168.1.186:6274
[14:30:13.055] Sent command: forward command
```

## Why logging is useful

Logs help you:

* confirm connection attempts
* verify that commands are being sent
* debug socket failures
* trace control events during testing

---

# Differences Between `rover.py` and `server.py`

| Feature                  | `rover.py`     | `server.py`                        |
| ------------------------ | -------------- | ---------------------------------- |
| Control method           | Keyboard input | Browser / HTTP requests            |
| Interface type           | Desktop script | Flask web server                   |
| Real-time manual control | Yes            | Depends on frontend implementation |
| Uses `keyboard` module   | Yes            | No                                 |
| Uses Flask               | No             | Yes                                |
| Direct socket commands   | Yes            | Yes                                |
| Logging                  | Yes            | Yes                                |
| Disconnect with ESC      | Yes            | No direct ESC handling             |

---

# Recommended Workflow

Choose the control method based on your use case:

## Use `rover.py` when:

* you want direct keyboard control
* you are testing movement logic quickly
* you are controlling the rover from a laptop/desktop on the same network

## Use `server.py` when:

* you want a browser-based UI
* you want to control the rover from a phone/tablet/browser
* you want to build a dashboard or remote-control panel
* you want to separate frontend and backend logic

---

# Known Limitations / Notes

## 1. Different rover IPs in the two scripts

The two files currently point to different rover IP addresses:

* `rover.py` → `192.168.1.187`
* `server.py` → `192.168.1.186`

If this is not intentional, update them to match.

## 2. `keyboard` library permissions

On some systems, the `keyboard` module may require elevated privileges to detect key presses globally.

## 3. `rover.py` reconnect logic

`rover.py` retries connection until successful, which is helpful during rover startup, but it currently retries forever without delay backoff.

## 4. `server.py` does not validate commands

The `/command` route sends whatever string is passed in `command`. If you want stricter behavior, add command validation against the allowed command set.

## 5. Logging timing in `rover.py`

The reported “RTT” is not a true network round-trip time. It measures the duration of the local send call only.

## 6. No rover acknowledgement handling

Neither script currently waits for or parses a response from the rover after sending commands. If the rover supports acknowledgements, you could extend the protocol to confirm delivery or state.

---

# Troubleshooting

## Problem: `Connection failed`

Check:

* rover IP address is correct
* rover is powered on
* rover is on the same network
* port `6274` is open and the rover is listening

## Problem: Keyboard controls do not work

Check:

* `keyboard` package is installed
* script is running with sufficient permissions
* the terminal session is active and the script is still running

## Problem: Web page loads but commands do nothing

Check:

* `server.py` is actually connected to the rover
* the frontend is calling `/command` correctly
* the command strings match the rover protocol
* the rover IP in `server.py` is correct

## Problem: Commands are sent but rover does not move

Check:

* rover firmware/server is parsing commands correctly
* the rover expects newline-terminated commands
* movement command names match the rover-side implementation

---

# Quick Start

## Keyboard mode

```bash
pip install keyboard
python rover.py
```

## Web mode

```bash
pip install flask
python server.py
```

Then open:

```text
http://localhost:5000
```

---

# Summary

This project provides two complementary rover control interfaces:

* **`rover.py`** for direct keyboard-based driving
* **`server.py`** for browser/API-based control

Both communicate with the rover using a simple TCP command protocol and produce timestamped logs for debugging and testing. Together, they form a flexible base for local rover driving, remote web control, and future expansion into a more advanced rover dashboard.
