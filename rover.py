import socket
import keyboard
import time
import datetime
import os

# === Logger Setup ===
log_filename = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.log")

def log(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(log_filename, "a") as f:
        f.write(full_message + "\n")

# === Connection Functions ===
def connect(ip):
    host = ip
    port = 6274
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    return s



def disconnect(s):
    s.close()


command_descriptions = {
    "w": "forward command",
    "wa": "forward-left command",
    "wd": "forward-right command",
    "s": "backward command",
    "sa": "backward-left command",
    "sd": "backward-right command",
    "x": "stop command",
    "esc": "escape command"
}

def send_message(message, s):
    data = (message + "\n").encode()
    start = time.perf_counter()
    s.send(data)
    end = time.perf_counter()

    rtt = (end - start) * 1000  # in ms
    packet_size = len(data)
    desc = command_descriptions.get(message, "unknown command")
    log(f"Transmitting: {desc} | Size: {packet_size} bytes | RTT: {rtt:.2f} ms")

# === Main Control Loop ===
ip = "192.168.1.187"


while True:
    try:
        log("Connecting to rover...")
        s = connect(ip)
        log("Connected!")
        break
    except Exception as e:
        log(f"Connection failed! Retrying...")

last = None
log("Control rover here!")

try:
    while True:
        if keyboard.is_pressed('w'):
            if keyboard.is_pressed('a'):
                if last != "wa":
                    last = "wa"
                    send_message("wa", s)
            elif keyboard.is_pressed('d'):
                if last != "wd":
                    last = "wd"
                    send_message("wd", s)
            else:
                if last != "w":
                    last = "w"
                    send_message("w", s)

        elif keyboard.is_pressed('s'):
            if keyboard.is_pressed('a'):
                if last != "sa":
                    last = "sa"
                    send_message("sa", s)
            elif keyboard.is_pressed('d'):
                if last != "sd":
                    last = "sd"
                    send_message("sd", s)
            else:
                if last != "s":
                    last = "s"
                    send_message("s", s)

        elif keyboard.is_pressed('esc'):
            if last != "esc":
                last = "esc"
                log("Escape key pressed. Disconnecting...")
                disconnect(s)
                log("Disconnected from rover.")
                break

        else:
            if last not in (None, "x"):
                last = "x"
                send_message("x", s)

        time.sleep(0.01)

except Exception as e:
    log(f"Error: {e}")
    disconnect(s)



