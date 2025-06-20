#!/usr/bin/env python3
"""Comprehensive fix script for ncOS v21.7."""

import subprocess
from pathlib import Path
import shutil


def print_header(text: str) -> None:
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def run_command(cmd: str, desc: str) -> None:
    print(f"\ud83d\udd27 {desc}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"\u2705 {desc} - Success")
    else:
        print(f"\u274c {desc} - Failed")
        print(result.stderr)


def fix_ncos_v21() -> None:
    print_header("ncOS v21.7 Comprehensive Fix")

    # directory setup
    dirs = [
        "config",
        "config/agents",
        "core",
        "api",
        "dashboard",
        "logs",
        "logs/backup",
        "schemas",
        "voice",
        "data",
        "production",
        "strategies",
        "tests",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print("\u2705 Directory structure created")

    print_header("Step 1: Fixing Missing Orchestrator Module")
    if Path("core_enhanced_master_orchestrator.py").exists():
        shutil.copy("core_enhanced_master_orchestrator.py", "core/enhanced_core_orchestrator.py")
        print("\u2705 Orchestrator copied to core/enhanced_core_orchestrator.py")

    for d in ["core", "api", "schemas", "voice"]:
        init_file = Path(d) / "__init__.py"
        init_file.touch()

    print_header("Step 2: Generating Agent Configurations")
    if Path("generate_advanced_configs.py").exists():
        run_command("python generate_advanced_configs.py", "Generating agent configurations")

    print_header("Step 3: Consolidating Setup Files")
    setup_content = """from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='ncos',
    version='21.7.2',
    author='ncOS Team',
    description='Neural Cognitive Operating System - Voice-Enabled Trading Platform',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        'pydantic>=1.8.0',
        'fastapi>=0.68.0',
        'uvicorn>=0.15.0',
        'streamlit>=1.0.0',
        'pandas>=1.3.0',
        'numpy>=1.21.0',
        'pyyaml>=5.4.0',
        'python-dotenv>=0.19.0',
        'aiofiles>=0.8.0',
        'websockets>=10.0',
        'sqlalchemy>=1.4.0',
        'redis>=4.0.0',
        'celery>=5.2.0',
        'pytest>=6.2.0',
        'pytest-asyncio>=0.18.0',
        'black>=21.0',
        'flake8>=4.0.0',
        'mypy>=0.910',
    ],
    entry_points={
        'console_scripts': [
            'ncos=core.main:main',
            'ncos-api=api.main:main',
            'ncos-voice=voice.ncos_voice_unified:main',
        ],
    },
)
"""
    Path("setup.py").write_text(setup_content)

    for old_setup in ["setup_ncos.py", "setup_v21.7.1.py", "setup_v21.7.2.py"]:
        if Path(old_setup).exists():
            Path(old_setup).unlink()

    if not Path("README.md").exists():
        Path("README.md").write_text("# ncOS v21.7 - Neural Cognitive Operating System\n")


if __name__ == "__main__":
    fix_ncos_v21()
