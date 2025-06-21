#!/usr/bin/env python3
"""
Robust Configuration Consolidator for ncOS
Handles YAML errors gracefully and provides better error reporting
"""

import json
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml


class RobustConfigConsolidator:
    def __init__(self, root_dir="."):
        self.root_dir = Path(root_dir)
        self.config_files = []
        self.consolidated_config = defaultdict(dict)
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.skip_patterns = [
            r'\.git/',
            r'__pycache__',
            r'\.pyc$',
            r'\.egg-info',
            r'backup',
            r'\.DS_Store'
        ]

    def find_config_files(self):
        """Find all configuration files"""
        print("Scanning for configuration files...")
        config_patterns = [
            "*.yaml", "*.yml", "*.json", "*.toml", "*.ini", "*.conf", "*.config",
            "*config.py", "settings.py", "configuration.py"
        ]

        for pattern in config_patterns:
            for file_path in self.root_dir.rglob(pattern):
                # Skip files matching skip patterns
                if any(re.search(skip, str(file_path)) for skip in self.skip_patterns):
                    continue
                self.config_files.append(file_path)

        print(f"Found {len(self.config_files)} configuration files")

    def create_backup(self):
        """Create backup of existing configurations"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.root_dir / f"config_backup_{timestamp}"
        backup_dir.mkdir(exist_ok=True)

        print(f"Creating backup in {backup_dir}")

        for config_file in self.config_files:
            try:
                relative_path = config_file.relative_to(self.root_dir)
                backup_path = backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(config_file, backup_path)
            except Exception as e:
                self.warnings.append(f"Could not backup {config_file}: {e}")

        # Save backup metadata
        metadata = {
            'timestamp': timestamp,
            'total_files': len(self.config_files),
            'warnings': self.warnings
        }
        with open(backup_dir / 'backup_metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)

    def safe_load_yaml(self, file_path):
        """Safely load YAML file with error handling"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Try to fix common YAML issues
            # Remove undefined aliases
            content = re.sub(r'&\w+', '', content)
            content = re.sub(r'\*\w+', '', content)

            # Try to parse
            data = yaml.safe_load(content)
            return data
        except yaml.YAMLError as e:
            # Try loading as JSON if YAML fails
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except:
                self.errors.append(f"YAML Error in {file_path}: {str(e)}")
                return None
        except Exception as e:
            self.errors.append(f"Error loading {file_path}: {str(e)}")
            return None

    def load_config(self, file_path):
        """Load configuration file based on extension"""
        try:
            ext = file_path.suffix.lower()

            if ext in ['.yaml', '.yml']:
                return self.safe_load_yaml(file_path)
            elif ext == '.json':
                with open(file_path, 'r') as f:
                    return json.load(f)
            elif ext == '.toml':
                try:
                    import toml
                    with open(file_path, 'r') as f:
                        return toml.load(f)
                except ImportError:
                    self.warnings.append(f"toml library not available, skipping {file_path}")
                    return None
            elif ext in ['.ini', '.conf', '.config']:
                import configparser
                config = configparser.ConfigParser()
                config.read(file_path)
                return {section: dict(config[section]) for section in config.sections()}
            elif file_path.name.endswith('.py'):
                # For Python config files, extract variables
                return self.extract_python_config(file_path)
            else:
                return None

        except Exception as e:
            self.errors.append(f"Error loading {file_path}: {str(e)}")
            return None

    def extract_python_config(self, file_path):
        """Extract configuration from Python files"""
        config = {}
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Extract simple variable assignments
            pattern = r'^([A-Z_]+)\s*=\s*(.+)$'
            for match in re.finditer(pattern, content, re.MULTILINE):
                var_name = match.group(1)
                var_value = match.group(2).strip()
                try:
                    # Try to evaluate the value safely
                    if var_value.startswith('"') or var_value.startswith("'"):
                        config[var_name] = var_value.strip('"\'')
                    elif var_value.isdigit():
                        config[var_name] = int(var_value)
                    elif var_value.replace('.', '').isdigit():
                        config[var_name] = float(var_value)
                    elif var_value.lower() in ['true', 'false']:
                        config[var_name] = var_value.lower() == 'true'
                    else:
                        config[var_name] = var_value
                except:
                    config[var_name] = var_value

        except Exception as e:
            self.errors.append(f"Error extracting Python config from {file_path}: {str(e)}")

        return config if config else None

    def categorize_config(self, file_path, config):
        """Categorize configuration based on content and path"""
        if not config:
            return None

        path_str = str(file_path).lower()

        # Determine category based on path and content
        if 'agent' in path_str:
            return 'agents'
        elif 'database' in path_str or 'db' in path_str:
            return 'database'
        elif 'api' in path_str or 'endpoint' in path_str:
            return 'api'
        elif 'model' in path_str:
            return 'models'
        elif 'engine' in path_str:
            return 'engines'
        elif 'service' in path_str:
            return 'services'
        elif 'test' in path_str:
            return 'testing'
        else:
            # Check content for hints
            if isinstance(config, dict):
                keys = set(str(k).lower() for k in config.keys())
                if any(k in keys for k in ['host', 'port', 'database', 'db']):
                    return 'database'
                elif any(k in keys for k in ['api', 'endpoint', 'routes']):
                    return 'api'
                elif any(k in keys for k in ['model', 'weights', 'parameters']):
                    return 'models'

            return 'general'

    def merge_configs(self, base, new, path=""):
        """Recursively merge configurations"""
        if not isinstance(base, dict) or not isinstance(new, dict):
            return new

        for key, value in new.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = self.merge_configs(base[key], value, f"{path}.{key}")
                elif isinstance(base[key], list) and isinstance(value, list):
                    # Merge lists by extending
                    base[key].extend(x for x in value if x not in base[key])
                else:
                    # Override with new value
                    base[key] = value
            else:
                base[key] = value

        return base

    def consolidate(self):
        """Consolidate all configurations"""
        print("\nAnalyzing and consolidating configurations...")

        for config_file in self.config_files:
            config = self.load_config(config_file)
            if not config:
                continue

            category = self.categorize_config(config_file, config)
            if not category:
                continue

            # Store with file path as key for traceability
            file_key = str(config_file.relative_to(self.root_dir))

            if category not in self.consolidated_config:
                self.consolidated_config[category] = {}

            self.consolidated_config[category][file_key] = {
                'path': file_key,
                'category': category,
                'config': config
            }
            self.success_count += 1

        print(f"Successfully processed {self.success_count} configuration files")
        print(f"Encountered {len(self.errors)} errors")

    def save_consolidated(self):
        """Save consolidated configuration"""
        output_dir = self.root_dir / "consolidated_config"
        output_dir.mkdir(exist_ok=True)

        # Save by category
        for category, configs in self.consolidated_config.items():
            category_file = output_dir / f"{category}_consolidated.json"
            with open(category_file, 'w') as f:
                json.dump(configs, f, indent=2)
            print(f"Saved {category} configurations to {category_file}")

        # Save master configuration
        master_config = {
            'metadata': {
                'total_files': len(self.config_files),
                'processed': self.success_count,
                'errors': len(self.errors),
                'categories': list(self.consolidated_config.keys()),
                'timestamp': datetime.now().isoformat()
            },
            'configurations': dict(self.consolidated_config)
        }

        master_file = output_dir / "master_config.json"
        with open(master_file, 'w') as f:
            json.dump(master_config, f, indent=2)
        print(f"\nSaved master configuration to {master_file}")

        # Save error report
        if self.errors:
            error_file = output_dir / "consolidation_errors.txt"
            with open(error_file, 'w') as f:
                f.write("Configuration Consolidation Errors\n")
                f.write("=" * 50 + "\n\n")
                for error in self.errors:
                    f.write(f"{error}\n\n")
            print(f"Saved error report to {error_file}")

    def generate_summary(self):
        """Generate consolidation summary"""
        summary = {
            'total_files_found': len(self.config_files),
            'files_processed': self.success_count,
            'errors_encountered': len(self.errors),
            'warnings': len(self.warnings),
            'categories': {}
        }

        for category, configs in self.consolidated_config.items():
            summary['categories'][category] = {
                'count': len(configs),
                'files': list(configs.keys())[:5]  # First 5 files
            }

        summary_file = self.root_dir / "consolidated_config" / "consolidation_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        # Print summary
        print("\n" + "=" * 50)
        print("CONSOLIDATION SUMMARY")
        print("=" * 50)
        print(f"Total files found: {summary['total_files_found']}")
        print(f"Files processed: {summary['files_processed']}")
        print(f"Errors: {summary['errors_encountered']}")
        print(f"Warnings: {summary['warnings']}")
        print("\nCategories:")
        for cat, info in summary['categories'].items():
            print(f"  - {cat}: {info['count']} files")

    def run(self):
        """Run the consolidation process"""
        print("Starting robust configuration consolidation...")

        # Find all config files
        self.find_config_files()

        if not self.config_files:
            print("No configuration files found!")
            return

        # Create backup
        self.create_backup()

        # Consolidate configurations
        self.consolidate()

        # Save results
        self.save_consolidated()

        # Generate summary
        self.generate_summary()

        print("\nConsolidation complete!")
        if self.errors:
            print(f"\n⚠️  {len(self.errors)} errors were encountered. Check consolidation_errors.txt for details.")


if __name__ == "__main__":
    consolidator = RobustConfigConsolidator()
    consolidator.run()
