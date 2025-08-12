import os
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
import socket

# Job names to monitor
MONITORED_NAMES = {"geogrid", "ungrib", "metgrid", "real", "wrf"}

# Detect current host (e.g., casper or derecho)
HOSTNAME = socket.gethostname().split(".")[0].lower()
if "casper" in HOSTNAME:
    HOST_TAG = "casper"
elif "derecho" in HOSTNAME:
    HOST_TAG = "derecho"
else:
    HOST_TAG = "unknown"

# Output directory
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_PATH = LOG_DIR / f"{HOST_TAG}_summary.json"
POLL_INTERVAL = 1  # seconds

def get_user_jobs():
    result = subprocess.run(["qstat", "-u", os.getenv("USER")], capture_output=True, text=True)
    lines = result.stdout.strip().split("\n")
    jobs = []

    for line in lines[3:]:  # Skip header lines
        parts = line.split()
        if len(parts) < 6:
            continue
        job_id = parts[0]
        name = parts[3]
        state = parts[4]
        jobs.append((job_id, name, state))
    return jobs

def get_job_info(job_id, extended=False):
    cmd = ["qstat", "-f" + ("x" if extended else ""), job_id]
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = {}
    for line in result.stdout.strip().split("\n"):
        parts = line.strip().split("=", maxsplit=1)
        if len(parts) == 2:
            key, val = [s.strip() for s in parts]
            info[key] = val
    return info

def load_summary():
    if SUMMARY_PATH.exists():
        with open(SUMMARY_PATH) as f:
            return json.load(f)
    return {}

def save_summary(summary):
    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)


def monitor_loop():
    summary = load_summary()
    all_jobs = set()

    print(f"📡 Starting PBS job monitor on {HOST_TAG}...")
    while True:
        jobs = get_user_jobs()
        now = datetime.utcnow().isoformat()

        # get pbs running pbs jobs
        for job_id, name, state in jobs:
            all_jobs.add(job_id)
            info = get_job_info(job_id)

            if job_id not in summary:
                summary[job_id] = {
                    "job_id": job_id,
                    "name": name,
                    "created": now,
                    "host": HOST_TAG,
                    "info":info,
                }
            else:
                if info:
                    summary[job_id]["info"] = info

        # to catch completed jobs
        for job_id in all_jobs:
            info = get_job_info(job_id)
            if info:
                summary[job_id]["info"] = info

        save_summary(summary)
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    try:
        monitor_loop()
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped by user.")
