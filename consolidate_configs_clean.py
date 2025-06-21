#!/usr/bin/env python3
import json
import shutil
from datetime import datetime
from pathlib import Path

import yaml


class ConfigurationConsolidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir = self.project_root / f"config_backup_{timestamp}"
        self.consolidated_config = {}
        self.config_files = []
        self.agent_configs = {}

    def scan_config_files(self):
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.conf', '*.cfg', '*.ini']
        config_files = []

        for pattern in config_patterns:
            config_files.extend(self.project_root.rglob(pattern))

        filtered_files = []
        for file in config_files:
            skip_dirs = ['node_modules', '__pycache__', '.git', 'venv', 'backup']
            if any(skip in str(file) for skip in skip_dirs):
                continue
            filtered_files.append(file)

        self.config_files = filtered_files
        return filtered_files

    def backup_configs(self):
        print(f"Creating backup in {self.backup_dir}")
        self.backup_dir.mkdir(exist_ok=True)

        for config_file in self.config_files:
            try:
                relative_path = config_file.relative_to(self.project_root)
                backup_path = self.backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(config_file, backup_path)
            except Exception as e:
                print(f"Error backing up {config_file}: {e}")

    def load_config_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix == '.json':
                    return json.load(f)
                elif file_path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif file_path.suffix in ['.ini', '.cfg', '.conf']:
                    config = {}
                    current_section = 'default'
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        if line.startswith('[') and line.endswith(']'):
                            current_section = line[1:-1]
                            config[current_section] = {}
                        elif '=' in line:
                            key, value = line.split('=', 1)
                            if current_section not in config:
                                config[current_section] = {}
                            config[current_section][key.strip()] = value.strip()
                    return config
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}

    def analyze_configs(self):
        print("Analyzing configuration files...")

        config_by_dir = {}
        for config_file in self.config_files:
            dir_path = config_file.parent
            if dir_path not in config_by_dir:
                config_by_dir[dir_path] = []
            config_by_dir[dir_path].append(config_file)

        for dir_path, files in config_by_dir.items():
            if 'agents' in str(dir_path):
                agent_name = dir_path.name
                self.agent_configs[agent_name] = {
                    'files': files,
                    'configs': {}
                }
                for file in files:
                    config = self.load_config_file(file)
                    self.agent_configs[agent_name]['configs'][file.name] = config

    def consolidate(self):
        print("Consolidating configurations...")

        self.consolidated_config = {
            'version': '2.0',
            'created': datetime.now().isoformat(),
            'global': {
                'project_name': 'ncOS',
                'version': '21.7',
                'environment': 'production'
            },
            'agents': {},
            'services': {},
            'database': {},
            'api': {},
            'logging': {},
            'security': {}
        }

        for agent_name, agent_data in self.agent_configs.items():
            agent_config = {
                'enabled': True,
                'config_files': [str(f.relative_to(self.project_root)) for f in agent_data['files']],
                'settings': {}
            }

            for file_name, config in agent_data['configs'].items():
                if isinstance(config, dict):
                    agent_config['settings'].update(config)

            self.consolidated_config['agents'][agent_name] = agent_config

        for config_file in self.config_files:
            if 'agents' not in str(config_file):
                config = self.load_config_file(config_file)
                self._merge_config(config, config_file)

    def _merge_config(self, config, file_path):
        file_name = file_path.stem.lower()

        if 'database' in file_name or 'db' in file_name:
            self.consolidated_config['database'].update(config)
        elif 'api' in file_name:
            self.consolidated_config['api'].update(config)
        elif 'log' in file_name:
            self.consolidated_config['logging'].update(config)
        elif 'security' in file_name or 'auth' in file_name:
            self.consolidated_config['security'].update(config)
        else:
            service_name = file_path.parent.name
            if service_name not in self.consolidated_config['services']:
                self.consolidated_config['services'][service_name] = {}
            self.consolidated_config['services'][service_name].update(config)

    def save_consolidated_config(self):
        config_dir = self.project_root / 'config'
        config_dir.mkdir(exist_ok=True)

        config_path = config_dir / 'consolidated_config.json'
        with open(config_path, 'w') as f:
            json.dump(self.consolidated_config, f, indent=2)

        print(f"Consolidated configuration saved to: {config_path}")

        yaml_path = config_dir / 'consolidated_config.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(self.consolidated_config, f, default_flow_style=False)

        print(f"YAML version saved to: {yaml_path}")

    def generate_config_loader(self):
        loader_code = '''#!/usr/bin/env python3
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self.load_config()

    def load_config(self):
        config_path = Path(__file__).parent / 'config' / 'consolidated_config.json'

        with open(config_path, 'r') as f:
            self._config = json.load(f)

        env = os.getenv('NCOS_ENV', 'production')
        env_config_path = config_path.parent / f'config.{env}.json'
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = json.load(f)
                self._merge_configs(self._config, env_config)

    def _merge_configs(self, base: Dict, override: Dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value

    def get(self, key_path: str, default: Any = None) -> Any:
        keys = key_path.split('.')
        value = self._config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        return self.get(f'agents.{agent_name}')

    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        return self.get(f'services.{service_name}')

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

config = ConfigLoader()

def get_config(key_path: str, default: Any = None) -> Any:
    return config.get(key_path, default)

def get_agent_config(agent_name: str) -> Optional[Dict[str, Any]]:
    return config.get_agent_config(agent_name)

def get_service_config(service_name: str) -> Optional[Dict[str, Any]]:
    return config.get_service_config(service_name)
'''

        loader_path = self.project_root / 'config_loader.py'
        with open(loader_path, 'w') as f:
            f.write(loader_code)

        print(f"Configuration loader saved to: {loader_path}")

    def generate_migration_guide(self):
        guide = f'''# Configuration Migration Guide

## Overview
The configuration system has been consolidated from {len(self.config_files)} files into a unified structure.

## Backup Location
All original configuration files have been backed up to: {self.backup_dir}

## New Configuration Structure
- Main config: config/consolidated_config.json
- Environment configs: config/config.<env>.json
- Config loader: config_loader.py

## Migration Steps

### 1. Update Import Statements
Replace individual config imports with:
```python
from config_loader import get_config, get_agent_config
```

### 2. Update Configuration Access
Old way:
```python
with open('config.json') as f:
    config = json.load(f)
api_key = config['api_key']
```

New way:
```python
api_key = get_config('api.api_key')
```

### 3. Agent Configuration
```python
agent_config = get_agent_config('agent_name')
if agent_config and agent_config.get('enabled'):
    settings = agent_config.get('settings', {})
```

## Configuration Paths
'''

        for agent_name in self.consolidated_config['agents']:
            guide += f"- agents.{agent_name}


"

guide += "
## Environment Variables
"
guide += "- NCOS_ENV: Set to 'development', 'staging', or 'production'
"

guide_path = self.project_root / 'CONFIG_MIGRATION_GUIDE.md'
with open(guide_path, 'w') as f:
    f.write(guide)

print(f"Migration guide saved to: {guide_path}")


def run(self):
    print("Starting configuration consolidation...")

    config_files = self.scan_config_files()
    print(f"Found {len(config_files)} configuration files")

    if not config_files:
        print("No configuration files found!")
        return None

    self.backup_configs()
    self.analyze_configs()
    self.consolidate()
    self.save_consolidated_config()
    self.generate_config_loader()
    self.generate_migration_guide()

    print("
    Consolidation
    complete!")
    print(f"Total agents configured: {len(self.consolidated_config['agents'])}")
    print(f"Total services configured: {len(self.consolidated_config['services'])}")

    return self.consolidated_config


if __name__ == "__main__":
    import sys

    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    consolidator = ConfigurationConsolidator(project_root)
    consolidator.run()
