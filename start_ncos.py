#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("🚀 Starting NCOS v21 Phoenix Mesh...")

    # Start API server
    print("Starting API server on port 8000...")
    api_cmd = [sys.executable, "src/api/main.py"]
    api_proc = subprocess.Popen(api_cmd)

    time.sleep(2)
    print("✅ API Server: http://localhost:8000")

    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        api_proc.terminate()

if __name__ == "__main__":
    main()
