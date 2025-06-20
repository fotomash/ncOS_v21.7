#!/usr/bin/env python3
"""
NCOS Voice Journal System Setup Script
Automatically creates directory structure and initial configuration
"""

import os
import sys
from pathlib import Path

def setup_ncos_voice_journal():
    """Set up the NCOS Voice Journal System"""

    print("🚀 NCOS Voice Journal System Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        sys.exit(1)

    # Create directory structure
    directories = [
        "api",
        "core", 
        "dashboard",
        "config",
        "logs",
        "logs/backup",
        "data"
    ]

    print("\n📁 Creating directories...")
    for dir_name in directories:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_name}")

    # Create empty journal file
    journal_file = Path("logs/trade_journal.jsonl")
    if not journal_file.exists():
        journal_file.touch()
        print("\n📝 Created trade journal file")

    # Check for required files
    required_files = [
        ("core/voice_tag_parser.py", "Voice parser"),
        ("core/zbar_voice_integration.py", "ZBAR integration"),
        ("dashboard/zbar_journal_dashboard.py", "Dashboard"),
        ("config/system_config.yaml", "System configuration")
    ]

    print("\n🔍 Checking required files...")
    missing_files = []

    for file_path, description in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {description}")
        else:
            print(f"  ❌ Missing: {description} ({file_path})")
            missing_files.append(file_path)

    if missing_files:
        print(f"\n⚠️  {len(missing_files)} files missing. Please add them to continue.")
        print("\nMissing files:")
        for f in missing_files:
            print(f"  - {f}")
    else:
        print("\n✅ All files present!")
        print("\n🎉 Setup complete! Next steps:")
        print("  1. Run: python api/main.py")
        print("  2. Run: streamlit run dashboard/zbar_journal_dashboard.py")
        print("  3. Run: python core/ncos_voice_unified.py")

    # Create launch script if not exists
    launch_script = Path("launch.sh")
    if not launch_script.exists():
        launch_content = """#!/bin/bash
echo "🚀 Starting NCOS Voice Journal System..."
python api/main.py &
sleep 2
streamlit run dashboard/zbar_journal_dashboard.py &
python core/ncos_voice_unified.py
"""
        launch_script.write_text(launch_content)
        launch_script.chmod(0o755)
        print("\n📜 Created launch.sh script")

if __name__ == "__main__":
    setup_ncos_voice_journal()
