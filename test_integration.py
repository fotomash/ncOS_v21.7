#!/usr/bin/env python3
'''
NCOS v21 Integration Test Script
Tests that all components are properly integrated
'''

import sys
from pathlib import Path
import json

def test_integration():
    print("🧪 Testing NCOS v21 Integration...")
    print("=" * 50)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Check directory structure
    required_dirs = [
        "src/orchestrators",
        "src/agents", 
        "src/api",
        "src/api/routes",
        "src/core",
        "config",
        "data/zbar"
    ]

    print("\n📁 Checking directory structure...")
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"  ✅ {dir_path}")
            tests_passed += 1
        else:
            print(f"  ❌ {dir_path} missing")
            tests_failed += 1

    # Test 2: Check key files
    key_files = [
        "fix_ncos_complete.py",
        "start_ncos.py",
        ".env",
        "config/enhanced_config.yaml"
    ]

    print("\n📄 Checking key files...")
    for file_path in key_files:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
            tests_passed += 1
        else:
            print(f"  ❌ {file_path} missing")
            tests_failed += 1

    # Test 3: Check component files
    components = [
        "src/orchestrators/enhanced_orchestrator.py",
        "src/agents/zbar_agent.py",
        "src/api/zbar_api.py",
        "src/api/routes/zbar_routes.py"
    ]

    print("\n🔧 Checking components...")
    for comp in components:
        if Path(comp).exists():
            print(f"  ✅ {comp}")
            tests_passed += 1
        else:
            print(f"  ❌ {comp} missing")
            tests_failed += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")

    if tests_failed == 0:
        print("\n✨ All integration tests passed!")
        print("\n🚀 Ready to run: python start_ncos.py")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} tests failed.")
        print("\n📝 Run fix_ncos_complete.py to fix issues")
        return 1

if __name__ == "__main__":
    sys.exit(test_integration())
