#!/usr/bin/env python3
# quickfix_phoenix.py - Quick Phoenix setup without directory checks

from pathlib import Path
import shutil

print("⚡ Quick Phoenix Setup (No checks)")
print("=" * 40)

# Just create what we need
Path("phoenix_session/core").mkdir(parents=True, exist_ok=True)
Path("phoenix_session/adapters").mkdir(parents=True, exist_ok=True)

# Copy controller if exists
if Path("ncos_session_optimized.py").exists():
    shutil.copy("ncos_session_optimized.py", "phoenix_session/core/")
    print("✅ Phoenix ready!")
    print("Test with: from phoenix_session.core.ncos_session_optimized import phoenix_rise")
else:
    print("⚠️  Missing ncos_session_optimized.py")
