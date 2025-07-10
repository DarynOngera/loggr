from flask import Flask, render_template, send_from_directory
import pandas as pd
import os
import time

app = Flask(__name__)

# === Paths ===
LOG_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_LOG_FILE = os.path.join(LOG_DIR, "output","activity.csv")
NETWORK_LOG_FILE = os.path.join(LOG_DIR,"output", "network_activity.csv")
BROWSER_LOG_FILE = os.path.join(LOG_DIR, "output", "browser_history.csv")
FILESYSTEM_LOG_FILE = os.path.join(LOG_DIR, "output", "filesystem_activity.csv")
SCREENSHOT_DIR = os.path.join(LOG_DIR, "output", "screenshots")

# === Data Loaders ===
key_data_cache = None
last_key_cache_update = None

def load_key_data():
    global key_data_cache, last_key_cache_update
    current_time = time.time()

    if key_data_cache is None or (current_time - last_key_cache_update > CACHE_TIMEOUT):
        try:
            df = pd.read_csv(KEY_LOG_FILE, names=[
                "timestamp", "user", "public_ip", "hostname", "os",
                "pid", "exe_path", "window_title", "key", "clipboard"
            ], skiprows=1, on_bad_lines="skip", low_memory=False,
            dtype={
                "timestamp": str, "user": str, "public_ip": str, "hostname": str, "os": str,
                "pid": str, "exe_path": str, "window_title": str, "key": str, "clipboard": str
            })
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=["timestamp", "key"]).fillna("")
            key_data_cache = df
            last_key_cache_update = current_time
            return df
        except Exception as e:
            print(f"[!] Failed to load key log: {e}")
            return pd.DataFrame()
    else:
        return key_data_cache

network_data_cache = None
last_network_cache_update = None

def load_network_data():
    global network_data_cache, last_network_cache_update
    current_time = time.time()

    if network_data_cache is None or (current_time - last_network_cache_update > CACHE_TIMEOUT):
        try:
            df = pd.read_csv(NETWORK_LOG_FILE, names=[
                "timestamp", "pid", "process_name", "local_address", "remote_address", "status"
            ], skiprows=1, on_bad_lines="skip", low_memory=False,
            dtype={
                "timestamp": str, "pid": str, "process_name": str,
                "local_address": str, "remote_address": str, "status": str
            })
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=["timestamp"]).fillna("")
            network_data_cache = df
            last_network_cache_update = current_time
            return df
        except Exception as e:
            print(f"[!] Failed to load network log: {e}")
            return pd.DataFrame()
    else:
        return network_data_cache

browser_data_cache = None
last_browser_cache_update = None

def load_browser_data():
    global browser_data_cache, last_browser_cache_update
    current_time = time.time()

    if browser_data_cache is None or (current_time - last_browser_cache_update > CACHE_TIMEOUT):
        try:
            df = pd.read_csv(BROWSER_LOG_FILE, names=[
                "timestamp", "source", "title", "url", "visit_count", "last_visit_time"
            ], skiprows=1, on_bad_lines="skip", low_memory=False,
            dtype={
                "timestamp": str, "source": str, "title": str,
                "url": str, "visit_count": str, "last_visit_time": str
            })
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=["timestamp"]).fillna("")
            browser_data_cache = df
            last_browser_cache_update = current_time
            return df
        except Exception as e:
            print(f"[!] Failed to load browser log: {e}")
            return pd.DataFrame()
    else:
        return browser_data_cache

filesystem_data_cache = None
last_filesystem_cache_update = None
CACHE_TIMEOUT = 60 # seconds

def load_filesystem_data():
    global filesystem_data_cache, last_filesystem_cache_update
    current_time = time.time()

    if filesystem_data_cache is None or (current_time - last_filesystem_cache_update > CACHE_TIMEOUT):
        try:
            df = pd.read_csv(FILESYSTEM_LOG_FILE, names=[
                "timestamp", "event_type", "src_path", "dest_path", "is_directory"
            ], skiprows=1, on_bad_lines="skip", low_memory=False,
            dtype={
                "timestamp": str, "event_type": str,
                "src_path": str, "dest_path": str, "is_directory": str
            })
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            df = df.dropna(subset=["timestamp"]).fillna("")
            filesystem_data_cache = df
            last_filesystem_cache_update = current_time
            return df
        except Exception as e:
            print(f"[!] Failed to load filesystem log: {e}")
            return pd.DataFrame()
    else:
        return filesystem_data_cache

# === Routes ===
@app.route("/")
def index():
    df = load_key_data()
    if not df.empty:
        df = df.sort_values("timestamp", ascending=False).head(100)
    return render_template("index.html", records=df.to_dict(orient="records"))

@app.route("/network")
def network():
    df = load_network_data()
    if not df.empty:
        df = df.sort_values("timestamp", ascending=False).head(100)
    return render_template("network.html", records=df.to_dict(orient="records"))

@app.route("/browser")
def browser():
    df = load_browser_data()
    if not df.empty:
        df = df.sort_values("timestamp", ascending=False).head(100)
    return render_template("browser.html", records=df.to_dict(orient="records"))

@app.route("/filesystem")
def filesystem():
    df = load_filesystem_data()
    if not df.empty:
        df = df.sort_values("timestamp", ascending=False).head(100)
    return render_template("filesystem.html", records=df.to_dict(orient="records"))

@app.route("/screenshots")
def screenshots():
    images = sorted(os.listdir(SCREENSHOT_DIR), reverse=True)
    return render_template("screenshots.html", images=images)

@app.route("/screenshots/<path:filename>")
def serve_screenshot(filename):
    return send_from_directory(SCREENSHOT_DIR, filename)

# === Start Server ===
if __name__ == "__main__":
    app.run(debug=True)

