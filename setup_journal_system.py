#!/usr/bin/env python
"""
Quick setup script for ncOS Journal v2.0
Sets up the refactored journal system
"""

import os
import sys
from pathlib import Path

def setup_journal_system():
    """Setup the journal system directory structure"""

    print("Setting up ncOS Journal v2.0...")

    # Create directory structure
    base_dir = Path("ncos_journal")
    directories = [
        base_dir / "core",
        base_dir / "core" / "writers",
        base_dir / "zbar",
        base_dir / "api",
        base_dir / "dashboard",
        base_dir / "data" / "journals",
        base_dir / "data" / "exports",
        base_dir / "data" / "cache",
        base_dir / "config"
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"Created: {directory}")

    # Create __init__.py files
    init_files = [
        base_dir / "__init__.py",
        base_dir / "core" / "__init__.py",
        base_dir / "core" / "writers" / "__init__.py",
        base_dir / "zbar" / "__init__.py",
        base_dir / "api" / "__init__.py",
        base_dir / "dashboard" / "__init__.py"
    ]

    for init_file in init_files:
        init_file.touch()
        print(f"Created: {init_file}")

    # Create default config
    config_content = """# ncOS Journal Configuration
journal:
  base_path: ./data/journals
  writers:
    - csv
    - jsonl
  rotation:
    enabled: true
    size_mb: 100
    retention_days: 90

zbar:
  min_confidence: 0.7
  lookback_periods: 20

api:
  host: localhost
  port: 8000

dashboard:
  port: 8501
"""

    config_file = base_dir / "config" / "default.yaml"
    with open(config_file, 'w') as f:
        f.write(config_content)
    print(f"Created: {config_file}")

    # Create requirements.txt
    requirements = """# ncOS Journal v2.0 Requirements
pandas>=1.5.0
numpy>=1.24.0
fastapi>=0.100.0
uvicorn>=0.23.0
streamlit>=1.25.0
plotly>=5.15.0
pydantic>=2.0.0
python-multipart>=0.0.6
pyyaml>=6.0
"""

    req_file = base_dir / "requirements.txt"
    with open(req_file, 'w') as f:
        f.write(requirements)
    print(f"Created: {req_file}")

    # Create launch script
    launch_content = """#!/bin/bash
# Launch ncOS Journal System

echo "Starting ncOS Journal v2.0..."

# Start API server
echo "Starting API server..."
cd api && uvicorn journal_api:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait for API to start
sleep 3

# Start dashboard
echo "Starting dashboard..."
cd ../dashboard && streamlit run app.py --server.port 8501 &
DASHBOARD_PID=$!

echo "ncOS Journal is running!"
echo "API: http://localhost:8000"
echo "Dashboard: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop..."

# Wait for interrupt
trap "kill $API_PID $DASHBOARD_PID" INT
wait
"""

    launch_file = base_dir / "launch.sh"
    with open(launch_file, 'w') as f:
        f.write(launch_content)
    launch_file.chmod(0o755)
    print(f"Created: {launch_file}")

    print("✅ Setup complete!")
    print("Next steps:")
    print("1. Move the journal component files to their respective directories")
    print("2. Install requirements: pip install -r ncos_journal/requirements.txt")
    print("3. Launch the system: ./ncos_journal/launch.sh")
    print("The journal system is now independent of voice components!")

if __name__ == "__main__":
    setup_journal_system()
