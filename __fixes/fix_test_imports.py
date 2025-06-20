#!/usr/bin/env python3
"""Fix integration test imports"""

import os
import re
from pathlib import Path

def fix_test_imports():
    """Fix imports in test files"""

    # Find all test files
    test_files = []
    for root, dirs, files in os.walk('tests'):
        for file in files:
            if file.endswith('.py'):
                test_files.append(Path(root) / file)

    # Pattern to find the problematic import
    old_import = r'from ncos_v21_7_1_enhanced_master_orchestrator import'

    # Try to find the actual orchestrator
    orchestrator_candidates = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if 'orchestrator' in file.lower() and file.endswith('.py'):
                module_path = Path(root) / file
                module_name = str(module_path).replace('/', '.').replace('\\', '.')[2:-3]
                orchestrator_candidates.append((module_path, module_name))

    print(f"Found {len(orchestrator_candidates)} orchestrator candidates:")
    for path, module in orchestrator_candidates:
        print(f"  - {module} ({path})")

    # Determine the best candidate
    best_candidate = None
    for path, module in orchestrator_candidates:
        if 'enhanced' in str(path) or 'master' in str(path):
            best_candidate = module
            break

    if not best_candidate and orchestrator_candidates:
        best_candidate = orchestrator_candidates[0][1]

    if not best_candidate:
        print("\n❌ No orchestrator module found!")
        return

    new_import = f'from {best_candidate} import'

    # Fix imports in test files
    fixed_count = 0
    for test_file in test_files:
        with open(test_file, 'r') as f:
            content = f.read()

        if old_import in content:
            new_content = content.replace(old_import, new_import)
            with open(test_file, 'w') as f:
                f.write(new_content)
            fixed_count += 1
            print(f"✓ Fixed imports in {test_file}")

    print(f"\n✅ Fixed {fixed_count} test files")
    print(f"New import: {new_import}")

if __name__ == "__main__":
    fix_test_imports()
