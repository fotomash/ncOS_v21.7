# ncOS v21.7 Critical Issues Fix Guide

## 🚨 Priority 1: Fix Integration Test Failures

### Issue: Missing Module `ncos_v21_7_1_enhanced_master_orchestrator`

**Root Cause**: The test suite is looking for a module that either doesn't exist or has been renamed.

**Fix Steps**:

1. **Locate the actual orchestrator file**:
```bash
# Search for orchestrator files
find . -name "*orchestrator*.py" | grep -E "(master|enhanced)"
```

2. **Update test imports**:
```python
# In your test files, update the import
# FROM:
from ncos_v21_7_1_enhanced_master_orchestrator import MasterOrchestrator

# TO (based on what you find):
from core.enhanced_core_orchestrator import MasterOrchestrator
# OR
from orchestration.master_orchestrator import MasterOrchestrator
```

3. **Create a compatibility shim** (temporary fix):
```python
# Create: ncos_v21_7_1_enhanced_master_orchestrator.py
"""Compatibility shim for test suite"""
try:
    from core.enhanced_core_orchestrator import *
except ImportError:
    from orchestration.master_orchestrator import *
```

---

## 🔧 Priority 2: Populate Configuration Files

### Create Agent Configuration Generator

```python
#!/usr/bin/env python3
"""Generate proper agent configurations from registry"""

import yaml
from pathlib import Path

def generate_agent_configs():
    """Generate configuration files for all agents"""

    # Load agent registry
    with open('config/agent_registry.yaml', 'r') as f:
        registry = yaml.safe_load(f)

    # Template for agent configuration
    config_template = {
        'agent': {
            'name': None,
            'version': '1.0.0',
            'enabled': True
        },
        'settings': {
            'log_level': 'INFO',
            'timeout': 30,
            'retry_count': 3
        },
        'parameters': {}
    }

    # Generate configs for each agent
    for agent_name, agent_info in registry.get('agents', {}).items():
        config_file = f'config/{agent_name.lower()}_config.yaml'

        # Skip if already has real config
        if Path(config_file).exists():
            with open(config_file, 'r') as f:
                content = yaml.safe_load(f)
                if content and content.get('settings') != {}:
                    continue

        # Create proper configuration
        config = config_template.copy()
        config['agent']['name'] = agent_name

        # Add agent-specific settings
        if 'portfolio' in agent_name.lower():
            config['parameters'] = {
                'risk_limit': 0.02,
                'max_positions': 10,
                'rebalance_interval': 3600
            }
        elif 'market' in agent_name.lower():
            config['parameters'] = {
                'symbols': ['XAUUSD', 'EURUSD'],
                'timeframes': ['M15', 'H1', 'H4'],
                'update_interval': 60
            }
        elif 'signal' in agent_name.lower():
            config['parameters'] = {
                'min_confidence': 0.7,
                'signal_types': ['entry', 'exit'],
                'cooldown_period': 300
            }

        # Write configuration
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        print(f"✓ Generated config for {agent_name}")

if __name__ == "__main__":
    generate_agent_configs()
```

---

## 📦 Priority 3: Consolidate Setup Files

### Unified setup.py

```python
#!/usr/bin/env python3
"""Unified setup for ncOS v21.7"""

from setuptools import setup, find_packages
import os

# Read requirements from all requirements files
def read_requirements():
    """Consolidate all requirements"""
    requirements = set()

    for req_file in ['requirements.txt', 'requirements_dev.txt', 'requirements_prod.txt']:
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                requirements.update(line.strip() for line in f if line.strip() and not line.startswith('#'))

    return list(requirements)

setup(
    name='ncos',
    version='21.7.2',
    description='Neural Cognitive Operating System - Voice-Enabled Trading Platform',
    author='NCOS Team',
    packages=find_packages(exclude=['tests*', 'docs*']),
    install_requires=read_requirements(),
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'ncos=core.main:main',
            'ncos-voice=core.ncos_voice_unified:main',
            'ncos-api=api.main:main',
            'ncos-dashboard=dashboard.main:main'
        ],
    },
    include_package_data=True,
    package_data={
        'ncos': ['config/*.yaml', 'config/*.toml'],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Financial and Insurance Industry',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)
```

### Cleanup Script

```bash
#!/bin/bash
# cleanup_setup_files.sh

echo "Consolidating setup files..."

# Backup old files
mkdir -p .backup
cp setup*.py .backup/

# Remove old setup files
rm -f setup_ncos.py setup_v21.7.1.py setup_v21.7.2.py

# Keep only the unified setup.py
echo "✓ Setup files consolidated"

# Remove redundant production files
mv production_config.py production/
mv production_logging.py production/
mv monitoring.py production/

echo "✓ Production files moved to production/"
```

---

## 🔗 Priority 4: Fix Trigger Mappings

### Update trigger_routes.toml

```toml
# config/trigger_routes.toml

[triggers.data.tick.xauusd]
description = "XAUUSD tick data trigger"
actions = ["update_market_data", "check_signals"]
conditions = ["market_open", "valid_spread"]
agents = ["MarketDataCaptain", "SignalProcessor"]

[triggers.analysis.manipulation.spread_detected]
description = "Spread manipulation detection"
actions = ["log_manipulation", "adjust_risk", "notify_trader"]
conditions = ["spread_threshold_exceeded", "volume_spike"]
agents = ["RiskManager", "NotificationAgent"]

[triggers.strategy.divergence]
description = "Divergence strategy trigger"
actions = ["analyze_divergence", "generate_signal"]
conditions = ["divergence_confirmed", "volume_support"]
agents = ["divergence_strategy_agent", "SignalProcessor"]
```

---

## 🐛 Priority 5: Fix File Naming Issues

```bash
#!/bin/bash
# fix_naming_issues.sh

# Fix double .yaml extension
mv config/market_bias_system.yaml.yaml config/market_bias_system.yaml 2>/dev/null

# Fix any other double extensions
find . -name "*.yaml.yaml" -exec bash -c 'mv "$0" "${0%.yaml}"' {} \;

echo "✓ File naming issues fixed"
```

---

## 📚 Priority 6: Update Documentation

### Updated FOLDER_STRUCTURE.md

```markdown
# ncOS v21.7 Actual Folder Structure

\`\`\`
ncos_v21.7/
├── api/                     # API endpoints and routes
├── config/                  # Configuration files
├── core/                    # Core system modules
├── dashboard/               # Streamlit dashboards
├── data/                    # Data storage
├── docs/                    # Documentation
├── logs/                    # Log files and journals
├── production/              # Production utilities
├── strategies/              # Trading strategies
├── tests/                   # Test suites
├── voice/                   # Voice processing modules
└── [root files]             # Setup, requirements, etc.
\`\`\`
```

---

## 🔄 Implementation Order

1. **Day 1**: Fix integration tests (Priority 1)
2. **Day 2**: Generate agent configurations (Priority 2)
3. **Day 3**: Consolidate setup files (Priority 3)
4. **Day 4**: Fix trigger mappings (Priority 4)
5. **Day 5**: Clean up naming and documentation

## 🚀 Quick Fix Script

```bash
#!/bin/bash
# quick_fix_ncos.sh

echo "🔧 Starting ncOS v21.7 Quick Fix..."

# 1. Fix module import
echo "Fixing module imports..."
find . -name "*.py" -exec sed -i 's/ncos_v21_7_1_enhanced_master_orchestrator/core.enhanced_core_orchestrator/g' {} +

# 2. Generate configs
echo "Generating agent configurations..."
python generate_agent_configs.py

# 3. Fix file naming
echo "Fixing file naming issues..."
mv config/market_bias_system.yaml.yaml config/market_bias_system.yaml 2>/dev/null

# 4. Consolidate setup
echo "Consolidating setup files..."
cp setup.py setup.py.backup
# Copy new unified setup.py here

# 5. Run tests
echo "Running integration tests..."
python -m pytest tests/integration/

echo "✅ Quick fixes applied!"
```
