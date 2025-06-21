#!/usr/bin/env python3
"""
NCOS v21 Universal Launcher
Handles path setup and launches the system from any directory
"""

import argparse
import os
import sys

import yaml

# Fast mode toggle
FAST_MODE = os.getenv("NCOS_FAST_MODE", "0") == "1"
from pathlib import Path


def find_ncos_root():
    """Find the NCOS root directory"""
    # Check if we're already in the right place
    current = Path.cwd()

    # Look for key directories
    if (current / "agents").exists() and (current / "config").exists():
        return current

    # Check if we're in scripts directory
    if current.name == "scripts" and (current.parent / "agents").exists():
        return current.parent

    # Check common locations
    possible_paths = [
        current / "ncos_v21_complete",
        current / "ncos_v21_complete_deployment",
        Path.home() / "Desktop" / "XANFLOW" / "_build_agent" / "ph5" / "ncos_v21_complete",
        Path.home() / "Desktop" / "XANFLOW" / "_build_agent" / "ph5" / "ncos_v21_complete_deployment",
    ]

    for path in possible_paths:
        if path.exists() and (path / "agents").exists():
            return path

    return None


def setup_environment(ncos_root):
    """Set up the Python environment"""
    # Add paths to Python path
    paths_to_add = [
        str(ncos_root),
        str(ncos_root / "agents"),
        str(ncos_root / "scripts"),
    ]

    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)

    # Set environment variable
    os.environ['PYTHONPATH'] = ':'.join(paths_to_add) + ':' + os.environ.get('PYTHONPATH', '')
    os.environ['NCOS_ROOT'] = str(ncos_root)

    return True


def validate_all_configs():
    """Validate YAML config files."""
    config_dir = Path('config')
    for cfg in config_dir.glob('*.yaml'):
        with open(cfg, 'r') as f:
            yaml.safe_load(f)


def register_agents():
    """Ensure agents in registry can be imported."""
    registry_path = Path('config') / 'agent_registry.yaml'
    if not registry_path.exists():
        return
    with open(registry_path, 'r') as f:
        registry = yaml.safe_load(f) or {}
    for agent, data in registry.get('agents', {}).items():
        module_name = data.get('module')
        if module_name:
            __import__(module_name)


def verify_schema_mapping():
    """Verify each agent has a corresponding config file."""
    registry_path = Path('config') / 'agent_registry.yaml'
    if not registry_path.exists():
        print("⚠️  Warning: agent_registry.yaml not found, cannot verify schema mapping")
        return
    with open(registry_path, 'r') as f:
        registry = yaml.safe_load(f) or {}
    missing = []
    # Validate config files for both core and strategy agents
    for section in ("agents", "strategy_agents"):
        for agent in registry.get(section, {}):
            cfg_path = Path('config') / f"{agent.lower()}_config.yaml"
            if not cfg_path.exists():
                print(
                    f"⚠️  Warning: Config file for '{agent}' not found at {cfg_path}"
                )
                missing.append(agent)

    if missing:
        print(f"❌ Error: {len(missing)} configuration file(s) missing for registered agents")


def parse_args():
    parser = argparse.ArgumentParser(description="NCOS Launcher")
    parser.add_argument("--fast", action="store_true", help="Enable FAST_MODE")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.fast:
        os.environ["NCOS_FAST_MODE"] = "1"
    global FAST_MODE
    FAST_MODE = os.getenv("NCOS_FAST_MODE", "0") == "1"

    print("🚀 NCOS v21 Universal Launcher")
    print("=" * 40)

    # Find NCOS root
    ncos_root = find_ncos_root()

    if not ncos_root:
        print("❌ Error: Cannot find NCOS installation directory")
        print("Please run this script from the NCOS directory or specify the path")
        sys.exit(1)

    print(f"✓ Found NCOS at: {ncos_root}")

    # Change to NCOS root
    os.chdir(ncos_root)
    print(f"✓ Changed directory to: {os.getcwd()}")

    # Set up environment
    setup_environment(ncos_root)
    print("✓ Environment configured")

    if not FAST_MODE:
        validate_all_configs()
        register_agents()
        verify_schema_mapping()
        print("[ncOS] Full validation complete.")
    else:
        print("[ncOS] FAST_MODE: Skipping deep validation and checks.")

    # Check for required files
    bootstrap_script = ncos_root / "scripts" / "integration_bootstrap.py"
    if not bootstrap_script.exists():
        print(f"❌ Error: Bootstrap script not found at {bootstrap_script}")
        sys.exit(1)

    # Check for config files
    if not (ncos_root / "config" / "bootstrap.yaml").exists():
        print("⚠️  Warning: bootstrap.yaml not found, will use defaults")

    # Launch the bootstrap
    print("\n" + "=" * 40)
    print("Launching NCOS Bootstrap...")
    print("=" * 40 + "\n")

    # Run the bootstrap script
    try:
        # Change to scripts directory for relative imports
        os.chdir(ncos_root / "scripts")

        # Import and run
        import integration_bootstrap
        # The script will run automatically on import

    except Exception as e:
        print(f"❌ Error launching bootstrap: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
