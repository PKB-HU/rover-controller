from flask import Flask, render_template, request, jsonify
import socket
import threading
import datetime

app = Flask(__name__)

# Log filename with date-time to avoid overwriting logs
log_filename = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S.log")

def log(message: str):
    """Log message with timestamp to console and file."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    full_message = f"[{timestamp}] {message}"
    print(full_message)
    with open(log_filename, "a") as f:
        f.write(full_message + "\n")

# Global socket connection and lock for thread safety
s = None
socket_lock = threading.Lock()  # To avoid race conditions
ip = "192.168.1.186"
port = 6274

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

def connect(ip_address: str):
    global s
    with socket_lock:
        if s:
            log("Already connected.")
            return
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)  # optional timeout for connect
            s.connect((ip_address, port))
            s.settimeout(None)  # disable timeout after connect
            log(f"Connected to rover at {ip_address}:{port}")
        except Exception as e:
            log(f"Connection failed: {e}")
            s = None

def disconnect():
    global s
    with socket_lock:
        if s:
            try:
                s.close()
                log("Disconnected from rover.")
            except Exception as e:
                log(f"Error during disconnect: {e}")
            finally:
                s = None
        else:
            log("No active connection to disconnect.")

def send_message(message: str) -> bool:
    global s
    with socket_lock:
        if s:
            try:
                data = (message + "\n").encode()
                s.sendall(data)
                desc = command_descriptions.get(message, message)
                log(f"Sent command: {desc}")
                return True
            except Exception as e:
                log(f"Failed to send message: {e}")
                return False
        else:
            log("Socket not connected")
            return False

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/connect', methods=['POST'])
def route_connect():
    threading.Thread(target=connect, args=(ip,), daemon=True).start()
    return jsonify({"status": "connecting"})

@app.route('/disconnect', methods=['POST'])
def route_disconnect():
    disconnect()
    return jsonify({"status": "disconnected"})

@app.route('/command', methods=['POST'])
def route_command():
    data = request.json
    command = data.get("command")
    if command:
        success = send_message(command)
        return jsonify({"status": "sent" if success else "failed"})
    else:
        return jsonify({"status": "no command"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
