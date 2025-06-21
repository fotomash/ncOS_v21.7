# auto_merge_phoenix.py - Automated Phoenix merge
import os
import json
import shutil
from pathlib import Path

def auto_merge():
    """Automated Phoenix Session merge"""
    print("🤖 Automated Phoenix Merge Starting...")

    # Check if in NCOS directory


    # Create Phoenix structure
    phoenix_dir = Path("phoenix_session")
    phoenix_dir.mkdir(exist_ok=True)

    for subdir in ["core", "adapters", "engines", "config"]:
        (phoenix_dir / subdir).mkdir(exist_ok=True)
        (phoenix_dir / subdir / "__init__.py").write_text('"""Phoenix Module"""')

    # Copy optimized controller if exists
    if Path("ncos_session_optimized.py").exists():
        shutil.copy("ncos_session_optimized.py", phoenix_dir / "core" / "ncos_session_optimized.py")
        print("✅ Copied optimized controller")

    # Create Phoenix config
    phoenix_config = {
        "phoenix_session": {
            "enabled": True,
            "fast_mode": True,
            "cache_enabled": True
        }
    }

    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)

    with open(config_dir / "phoenix_config.json", "w") as f:
        json.dump(phoenix_config, f, indent=2)

    print("✅ Phoenix structure created")
    print("📝 Next: Copy implementation from PHOENIX_MERGE_IMPLEMENTATION.py")

    return True

if __name__ == "__main__":
    auto_merge()
