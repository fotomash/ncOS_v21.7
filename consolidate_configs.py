#!/usr/bin/env python3
"""
ncOS Configuration Consolidator
Consolidates 82 config files into a unified hierarchical structure
"""

import os
import yaml
import json
from pathlib import Path
from collections import defaultdict
import shutil
from datetime import datetime

class ConfigConsolidator:
    def __init__(self, project_root="ncOS_v21.7"):
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.backup_dir = Path(f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.consolidated_config = {
            'version': '21.7',
            'meta': {
                'created': datetime.now().isoformat(),
                'original_files': 0,
                'consolidated_from': []
            },
            'system': {},
            'agents': {},
            'strategies': {},
            'integrations': {},
            'monitoring': {},
            'api': {},
            'journal': {}
        }

    def backup_configs(self):
        """Backup existing configuration files"""
        print("📦 Creating configuration backup...")

        if self.config_dir.exists():
            shutil.copytree(self.config_dir, self.backup_dir)
            print(f"✅ Backup created: {self.backup_dir}")

        # Also backup any .yaml/.yml files in root
        for pattern in ['*.yaml', '*.yml']:
            for config_file in self.project_root.glob(pattern):
                backup_path = self.backup_dir / config_file.name
                shutil.copy2(config_file, backup_path)

    def categorize_config(self, file_name, content):
        """Categorize configuration based on filename and content"""
        file_lower = file_name.lower()

        # Categorization rules
        if 'agent' in file_lower:
            return 'agents'
        elif any(x in file_lower for x in ['strategy', 'trigger', 'trade', 'smc', 'wyckoff']):
            return 'strategies'
        elif any(x in file_lower for x in ['system', 'core', 'main', 'global']):
            return 'system'
        elif any(x in file_lower for x in ['api', 'endpoint', 'route']):
            return 'api'
        elif any(x in file_lower for x in ['journal', 'log', 'session']):
            return 'journal'
        elif any(x in file_lower for x in ['monitor', 'metric', 'alert']):
            return 'monitoring'
        elif any(x in file_lower for x in ['integration', 'external', 'finnhub', 'market']):
            return 'integrations'
        else:
            # Check content for hints
            if isinstance(content, dict):
                keys = ' '.join(content.keys()).lower()
                if 'agent' in keys:
                    return 'agents'
                elif 'strategy' in keys or 'trade' in keys:
                    return 'strategies'
            return 'system'  # Default

    def merge_config(self, category, name, content):
        """Merge configuration into consolidated structure"""
        if isinstance(content, dict):
            if name not in self.consolidated_config[category]:
                self.consolidated_config[category][name] = content
            else:
                # Deep merge
                self.deep_merge(self.consolidated_config[category][name], content)
        elif isinstance(content, list):
            if name not in self.consolidated_config[category]:
                self.consolidated_config[category][name] = content
            else:
                # Extend list, avoiding duplicates
                existing = self.consolidated_config[category][name]
                if isinstance(existing, list):
                    for item in content:
                        if item not in existing:
                            existing.append(item)

    def deep_merge(self, base, update):
        """Deep merge two dictionaries"""
        for key, value in update.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    self.deep_merge(base[key], value)
                elif isinstance(base[key], list) and isinstance(value, list):
                    for item in value:
                        if item not in base[key]:
                            base[key].append(item)
                else:
                    base[key] = value
            else:
                base[key] = value

    def process_configs(self):
        """Process all configuration files"""
        print("\n🔍 Scanning for configuration files...")

        config_files = []

        # Find all YAML/YML files
        for pattern in ['**/*.yaml', '**/*.yml']:
            config_files.extend(self.project_root.glob(pattern))

        # Find all JSON config files
        for json_file in self.project_root.glob('**/*.json'):
            if 'config' in json_file.name.lower() or json_file.parent.name == 'config':
                config_files.append(json_file)

        print(f"Found {len(config_files)} configuration files")

        # Process each file
        for config_file in config_files:
            relative_path = config_file.relative_to(self.project_root)

            try:
                # Load configuration
                if config_file.suffix in ['.yaml', '.yml']:
                    with open(config_file, 'r') as f:
                        content = yaml.safe_load(f)
                elif config_file.suffix == '.json':
                    with open(config_file, 'r') as f:
                        content = json.load(f)
                else:
                    continue

                if content:
                    # Categorize and merge
                    category = self.categorize_config(config_file.stem, content)
                    self.merge_config(category, config_file.stem, content)

                    # Track source
                    self.consolidated_config['meta']['consolidated_from'].append(str(relative_path))

                    print(f"  ✅ Processed: {relative_path} → {category}")

            except Exception as e:
                print(f"  ❌ Error processing {relative_path}: {e}")

        self.consolidated_config['meta']['original_files'] = len(config_files)

    def create_unified_structure(self):
        """Create the new unified configuration structure"""
        print("\n📁 Creating unified configuration structure...")

        # Create new config directory structure
        new_config = self.project_root / "config_unified"
        new_config.mkdir(exist_ok=True)

        # Main configuration file
        main_config = {
            'version': self.consolidated_config['version'],
            'meta': self.consolidated_config['meta'],
            'includes': {
                'system': './system.yaml',
                'agents': './agents/',
                'strategies': './strategies.yaml',
                'integrations': './integrations.yaml',
                'api': './api.yaml',
                'journal': './journal.yaml',
                'monitoring': './monitoring.yaml'
            }
        }

        # Write main config
        with open(new_config / 'config.yaml', 'w') as f:
            yaml.dump(main_config, f, default_flow_style=False, sort_keys=False)

        # Write category-specific configs
        for category in ['system', 'strategies', 'integrations', 'api', 'journal', 'monitoring']:
            if self.consolidated_config[category]:
                with open(new_config / f'{category}.yaml', 'w') as f:
                    yaml.dump(self.consolidated_config[category], f, default_flow_style=False)

        # Handle agents specially (one file per agent)
        agents_dir = new_config / 'agents'
        agents_dir.mkdir(exist_ok=True)

        for agent_name, agent_config in self.consolidated_config['agents'].items():
            with open(agents_dir / f'{agent_name}.yaml', 'w') as f:
                yaml.dump(agent_config, f, default_flow_style=False)

        # Create environment-specific overrides
        for env in ['development', 'staging', 'production']:
            env_dir = new_config / 'environments' / env
            env_dir.mkdir(parents=True, exist_ok=True)

            env_config = {
                'environment': env,
                'overrides': {
                    'system': {
                        'debug': env == 'development',
                        'log_level': 'DEBUG' if env == 'development' else 'INFO'
                    }
                }
            }

            with open(env_dir / 'config.yaml', 'w') as f:
                yaml.dump(env_config, f, default_flow_style=False)

        print(f"✅ Unified configuration created in: {new_config}")

        return new_config

    def create_config_loader(self):
        """Create a Python configuration loader"""
        loader_code = 
Unified Configuration Loader for ncOS
