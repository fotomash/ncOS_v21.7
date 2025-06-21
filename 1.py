# Fixed Configuration Consolidator for ncOS
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

import yaml


class ConfigurationConsolidator:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.consolidated_config = {}
        self.config_files = []
        self.agent_configs = {}
        
    def scan_config_files(self) -> List[Path]:
        """Scan for all configuration files in the project"""
        config_patterns = ['*.json', '*.yaml', '*.yml', '*.conf', '*.cfg', '*.ini']
        config_files = []
        
        for pattern in config_patterns:
            config_files.extend(self.project_root.rglob(pattern))
        
        # Filter out non-config files
        filtered_files = []
        for file in config_files:
            if any(skip in str(file) for skip in ['node_modules', '__pycache__', '.git', 'venv']):
                continue
            filtered_files.append(file)
        
        self.config_files = filtered_files
        return filtered_files
    
    def backup_configs(self):
        """Create backup of all configuration files"""
        print(f"Creating backup in {self.backup_dir}")
        self.backup_dir.mkdir(exist_ok=True)
        
        for config_file in self.config_files:
            relative_path = config_file.relative_to(self.project_root)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(config_file, backup_path)
    
    def load_config_file(self, file_path: Path) -> Dict[str, Any]:
        """Load configuration from a file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.suffix in ['.json']:
                    return json.load(f)
                elif file_path.suffix in ['.yaml', '.yml']:
                    return yaml.safe_load(f) or {}
                elif file_path.suffix in ['.ini', '.cfg', '.conf']:
                    # Simple key-value parser for ini files
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
        """Analyze all configuration files and identify patterns"""
        print("\nAnalyzing configuration files...")
        
        # Group configs by directory
        config_by_dir = {}
        for config_file in self.config_files:
            dir_path = config_file.parent
            if dir_path not in config_by_dir:
                config_by_dir[dir_path] = []
            config_by_dir[dir_path].append(config_file)
        
        # Analyze agent configurations
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
        """Consolidate configurations into a unified structure"""
        print("\nConsolidating configurations...")
        
        # Create main configuration structure
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
        
        # Process agent configurations
        for agent_name, agent_data in self.agent_configs.items():
            agent_config = {
                'enabled': True,
                'config_files': [str(f.relative_to(self.project_root)) for f in agent_data['files']],
                'settings': {}
            }
            
            # Merge all agent configs
            for file_name, config in agent_data['configs'].items():
                if isinstance(config, dict):
                    agent_config['settings'].update(config)
            
            self.consolidated_config['agents'][agent_name] = agent_config
        
        # Process other configurations
        for config_file in self.config_files:
            if 'agents' not in str(config_file):
                config = self.load_config_file(config_file)
                self._merge_config(config, config_file)
    
    def _merge_config(self, config: Dict[str, Any], file_path: Path):
        """Merge configuration into appropriate section"""
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
            # Add to services section
            service_name = file_path.parent.name
            if service_name not in self.consolidated_config['services']:
                self.consolidated_config['services'][service_name] = {}
            self.consolidated_config['services'][service_name].update(config)
    
    def generate_config_loader(self):
        """Generate configuration loader module"""
        loader_code = '''#!/usr/bin/env python3
"""
Centralized Configuration Loader for ncOS
Generated on: {timestamp}
"""

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
        """Load the consolidated configuration"""
        config_path = Path(__file__).parent / 'config' / 'consolidated_config.json'
        
        # Load main config
        with open(config_path, 'r') as f:
            self._config = json.load(f)
        
        # Override with environment-specific config if exists
        env = os.getenv('NCOS_ENV', 'production')
        env_config_path = config_path.parent / f'config.{env}.json'
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config = json.load(f)
                self._merge_configs(self._config, env_config)
    
    def _merge_configs(self, base: Dict, override: Dict):
        """Deep merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path"""
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_agent_config(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific agent"""
        return self.get(f'agents.{agent_name}')
    
    def get_service_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific service"""
        return self.get(f'services.{service_name}')
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the entire configuration"""
        return self._config

# Singleton instance
config = ConfigLoader()

# Convenience functions
def get_config(key_path: str, default: Any = None) -> Any:
    """Get configuration value"""
    return config.get(key_path, default)

def get_agent_config(agent_name: str) -> Optional[Dict[str, Any]]:
    """Get agent configuration"""
    return config.get_agent_config(agent_name)

def get_service_config(service_name: str) -> Optional[Dict[str, Any]]:
    """Get service configuration"""
    return config.get_service_config(service_name)
'''.format(timestamp=datetime.now().isoformat())
        
        # Save the loader
        loader_path = self.project_root / 'config_loader.py'
        with open(loader_path, 'w') as f:
            f.write(loader_code)
        
        print(f"Configuration loader saved to: {loader_path}")
    
    def save_consolidated_config(self):
        """Save the consolidated configuration"""
        config_dir = self.project_root / 'config'
        config_dir.mkdir(exist_ok=True)
        
        config_path = config_dir / 'consolidated_config.json'
        with open(config_path, 'w') as f:
            json.dump(self.consolidated_config, f, indent=2)
        
        print(f"Consolidated configuration saved to: {config_path}")
        
        # Also save a YAML version for readability
        yaml_path = config_dir / 'consolidated_config.yaml'
        with open(yaml_path, 'w') as f:
            yaml.dump(self.consolidated_config, f, default_flow_style=False)
        
        print(f"YAML version saved to: {yaml_path}")
    
    def generate_migration_guide(self):
        """Generate migration guide for developers"""
'''
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
'''