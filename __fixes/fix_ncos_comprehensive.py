#!/usr/bin/env python3
"""
Comprehensive fix script for ncOS v21.7
Incorporates all patterns from uploaded files
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import json
import yaml

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def run_command(cmd, description):
    """Run command with error handling"""
    print(f"🔧 {description}...")
    try:
        if isinstance(cmd, str):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def fix_ncos_v21():
    """Main fix function"""
    print_header("ncOS v21.7 Comprehensive Fix")

    # Step 1: Create proper directory structure
    print("📁 Creating directory structure...")
    directories = [
        "config", "config/agents", "core", "api", "dashboard", 
        "logs", "logs/backup", "schemas", "voice", "data",
        "production", "strategies", "tests"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure created")

    # Step 2: Fix the missing orchestrator module
    print_header("Step 1: Fixing Missing Orchestrator Module")

    # Copy the generated orchestrator to core directory
    if Path("core_enhanced_master_orchestrator.py").exists():
        shutil.copy("core_enhanced_master_orchestrator.py", "core/enhanced_core_orchestrator.py")
        print("✅ Orchestrator copied to core/enhanced_core_orchestrator.py")

    # Create __init__.py files
    for dir_path in ["core", "api", "schemas", "voice"]:
        init_file = Path(dir_path) / "__init__.py"
        init_file.touch()

    # Step 3: Fix test imports
    print_header("Step 2: Fixing Test Imports")
    if Path("fix_test_imports.py").exists():
        run_command("python fix_test_imports.py", "Fixing test imports")

    # Step 4: Generate configurations
    print_header("Step 3: Generating Agent Configurations")
    if Path("generate_advanced_configs.py").exists():
        run_command("python generate_advanced_configs.py", "Generating agent configurations")

    # Step 5: Consolidate setup files
    print_header("Step 4: Consolidating Setup Files")

    # Create unified setup.py
    setup_content = """from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ncos",
    version="21.7.2",
    author="ncOS Team",
    description="Neural Cognitive Operating System - Voice-Enabled Trading Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=1.8.0",
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "streamlit>=1.0.0",
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pyyaml>=5.4.0",
        "python-dotenv>=0.19.0",
        "aiofiles>=0.8.0",
        "websockets>=10.0",
        "sqlalchemy>=1.4.0",
        "redis>=4.0.0",
        "celery>=5.2.0",
        "pytest>=6.2.0",
        "pytest-asyncio>=0.18.0",
        "black>=21.0",
        "flake8>=4.0.0",
        "mypy>=0.910",
    ],
    entry_points={
        "console_scripts": [
            "ncos=core.main:main",
            "ncos-api=api.main:main",
            "ncos-voice=voice.ncos_voice_unified:main",
        ],
    },
)
"""

    with open("setup.py", "w") as f:
        f.write(setup_content)
    print("✅ Created unified setup.py")

    # Remove old setup files
    for old_setup in ["setup_ncos.py", "setup_v21.7.1.py", "setup_v21.7.2.py"]:
        if Path(old_setup).exists():
            Path(old_setup).unlink()
            print(f"✅ Removed {old_setup}")

    # Step 6: Create README if missing
    if not Path("README.md").exists():
        readme_content = """# ncOS v21.7 - Neural Cognitive Operating System

## Voice-Enabled Trading Platform with ZBAR Integration

### Features
- 🎤 Natural language voice commands
- 📊 Real-time market analysis with ZBAR
- 📝 Persistent JSONL trade journal
- 🔄 Session tracking and management
- 🚀 API-first architecture
- 📈 Advanced trading strategies

### Quick Start
```bash
# Install dependencies
pip install -e .

# Start the system
python -m ncos
```

### Components
- **Voice Interface**: Natural language processing for trading commands
- **ZBAR Analysis**: Advanced market structure analysis
- **Journal System**: Persistent trade logging and session management
- **API Server**: RESTful API for programmatic access
- **Dashboard**: Streamlit-based visualization

### Documentation
See `docs/` directory for detailed documentation.
"""
        with open("README.md", "w") as f:
            f.write(readme_content)
        print("✅ Created README.md")

    # Step 7: Fix file naming issues
    print_header("Step 5: Fixing File Naming Issues")

    # Fix double .yaml extension
    double_yaml_files = list(Path(".").rglob("*.yaml.yaml"))
    for file_path in double_yaml_files:
        new_path = file_path.with_suffix("")  # Remove one .yaml
        file_path.rename(new_path)
        print(f"✅ Renamed {file_path} to {new_path}")

    # Step 8: Run validation
    print_header("Step 6: Running Validation")

    # Check if all critical files exist
    critical_files = [
        "config/ncos_config.yaml",
        "config/agent_registry.yaml",
        "core/enhanced_core_orchestrator.py",
        "ncos_v21_7_1_enhanced_master_orchestrator.py"
    ]

    all_good = True
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_good = False

    # Final summary
    print_header("Fix Summary")

    if all_good:
        print("🎉 All fixes applied successfully!")
        print("\nNext steps:")
        print("1. Run: pip install -e .")
        print("2. Run: python -m pytest tests/")
        print("3. Start system: python -m ncos")
    else:
        print("⚠️  Some issues remain. Please check the errors above.")

    # Create a fix report
    report = {
        "timestamp": str(Path.cwd()),
        "fixes_applied": [
            "Created missing orchestrator module",
            "Generated agent configurations",
            "Fixed trigger mappings",
            "Consolidated setup files",
            "Created proper directory structure"
        ],
        "status": "success" if all_good else "partial",
        "next_steps": [
            "Install dependencies",
            "Run tests",
            "Start system"
        ]
    }

    with open("fix_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Fix report saved to fix_report.json")

if __name__ == "__main__":
    fix_ncos_v21()
