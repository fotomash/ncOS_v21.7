#!/usr/bin/env python3
'''
NCOS v21 Phoenix Mesh - Quick Start Script
'''

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 NCOS v21 Phoenix Mesh - Quick Start")
    print("=" * 50)

    # Step 1: Check Python version
    print("\n1️⃣ Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return 1
    print(f"✅ Python {sys.version.split()[0]}")

    # Step 2: Install dependencies
    print("\n2️⃣ Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    except:
        print("❌ Failed to install dependencies")
        return 1

    # Step 3: Run fix script
    print("\n3️⃣ Running fix script...")
    if Path("fix_ncos_complete.py").exists():
        try:
            subprocess.run([sys.executable, "fix_ncos_complete.py"], check=True)
            print("✅ Fixes applied")
        except:
            print("⚠️  Fix script failed, continuing...")
    else:
        print("⚠️  Fix script not found, skipping...")

    # Step 4: Run integration test
    print("\n4️⃣ Testing integration...")
    if Path("test_integration.py").exists():
        result = subprocess.run([sys.executable, "test_integration.py"])
        if result.returncode != 0:
            print("⚠️  Some tests failed, but continuing...")

    # Step 5: Start the system
    print("\n5️⃣ Starting NCOS...")
    print("\n" + "=" * 50)
    print("🎯 NCOS is starting up!")
    print("📊 API will be available at:")
    print("   - Main: http://localhost:8000")
    print("   - ZBAR: http://localhost:8001")
    print("   - Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    print("=" * 50 + "\n")

    # Start the system
    try:
        subprocess.run([sys.executable, "start_ncos.py"])
    except KeyboardInterrupt:
        print("\n\n✅ NCOS stopped gracefully")

    return 0

if __name__ == "__main__":
    sys.exit(main())
