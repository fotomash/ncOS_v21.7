#!/usr/bin/env python3
# verify_ncos_structure.py - Verify NCOS directory structure

import os
from pathlib import Path
import json

def verify_structure():
    """Verify and report NCOS structure"""
    current = Path.cwd()
    print(f"📍 Current directory: {current}")
    print(f"📂 Directory name: {current.name}")

    # Check for various NCOS indicators
    checks = {
        "Has Python files": len(list(current.glob("**/*.py"))) > 0,
        "Has config files": len(list(current.glob("*config*"))) > 0,
        "Has YAML files": len(list(current.glob("**/*.yaml"))) > 0,
        "Has JSON files": len(list(current.glob("**/*.json"))) > 0,
    }

    print("\n🔍 Structure checks:")
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"{status} {check}")

    # List main directories
    dirs = [d for d in current.iterdir() if d.is_dir() and not d.name.startswith('.')]
    if dirs:
        print(f"\n📁 Main directories ({len(dirs)}):")
        for d in sorted(dirs)[:15]:
            file_count = len(list(d.glob("**/*")))
            print(f"   - {d.name:20} ({file_count} files)")

    # Look for key files
    key_files = ["requirements.txt", "setup.py", "README.md", "main.py"]
    print("\n📄 Key files:")
    for kf in key_files:
        exists = (current / kf).exists()
        status = "✅" if exists else "❌"
        print(f"{status} {kf}")

    return current.name == "ncOS_v21.7" or "ncOS" in current.name

if __name__ == "__main__":
    print("🔍 NCOS Structure Verification")
    print("=" * 50)

    is_ncos = verify_structure()

    if is_ncos:
        print("\n✅ This appears to be an NCOS directory!")
        print("Ready to run: python adaptive_phoenix_merge.py")
    else:
        print("\n⚠️  This might not be the NCOS root directory")
        print("Look for the directory containing your NCOS project files")
