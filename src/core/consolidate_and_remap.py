#!/usr/bin/env python3
"""
ncOS Project Consolidation and Remapping Tool
Consolidates and reorganizes the ncOS project structure
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProjectConsolidator:
    """Handles project consolidation and remapping"""

    def __init__(self, source_dir: str, target_dir: str):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.backup_dir = Path(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.mapping_log = []
        self.errors = []

    def create_backup(self):
        """Create a backup of the source directory"""
        logger.info(f"Creating backup at {self.backup_dir}")
        shutil.copytree(self.source_dir, self.backup_dir)

    def create_new_structure(self):
        """Create the new project structure"""
        structure = {
            'src': {
                'core': ['__init__.py', 'config.py', 'utils.py', 'exceptions.py'],
                'engines': ['__init__.py', 'base.py', 'predictive.py', 'vector.py'],
                'agents': ['__init__.py', 'base.py'],
                'api': ['__init__.py', 'main.py'],
                'models': ['__init__.py']
            },
            'config': ['settings.yaml', 'logging.yaml'],
            'tests': ['__init__.py'],
            'scripts': [],
            'docs': ['README.md', 'ARCHITECTURE.md']
        }

        logger.info("Creating new directory structure")
        for parent, contents in structure.items():
            parent_path = self.target_dir / parent
            parent_path.mkdir(parents=True, exist_ok=True)

            if isinstance(contents, dict):
                for subdir, files in contents.items():
                    subdir_path = parent_path / subdir
                    subdir_path.mkdir(exist_ok=True)
                    for file in files:
                        if file.endswith('.py'):
                            self._create_python_file(subdir_path / file, subdir)
            else:
                for file in contents:
                    if file.endswith('.py'):
                        self._create_python_file(parent_path / file, parent)
                    elif file.endswith('.md'):
                        self._create_markdown_file(parent_path / file, parent)
                    elif file.endswith('.yaml'):
                        self._create_yaml_file(parent_path / file, parent)

    def _create_python_file(self, filepath: Path, module_name: str):
        """Create a Python file with proper header"""
        if filepath.name == '__init__.py':
            content = f'"""\n{module_name.capitalize()} module\n"""\n'
        else:
            content = f'"""\n{filepath.stem.capitalize()} module for {module_name}\n"""\n\n'

        filepath.write_text(content)

    def _create_markdown_file(self, filepath: Path, section: str):
        """Create a markdown file"""
        if filepath.name == 'README.md':
            content = """# ncOS - Neural Compute Operating System

## Overview
Consolidated and remapped ncOS project structure.

## Structure
- `src/`: Source code
- `config/`: Configuration files
- `tests/`: Test suite
- `scripts/`: Utility scripts
- `docs/`: Documentation
"""
        else:
            content = f"# {filepath.stem.replace('_', ' ').title()}\n\n"

        filepath.write_text(content)

    def _create_yaml_file(self, filepath: Path, section: str):
        """Create a YAML configuration file"""
        config = {
            'version': '1.0',
            'description': f'{filepath.stem} configuration',
            'settings': {}
        }

        with open(filepath, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

    def consolidate_configs(self):
        """Consolidate all configuration files"""
        logger.info("Consolidating configuration files")

        config_files = list(self.source_dir.rglob('*.yaml')) + \
                       list(self.source_dir.rglob('*.yml')) + \
                       list(self.source_dir.rglob('*.json'))

        consolidated = {
            'agents': {},
            'engines': {},
            'models': {},
            'api': {},
            'general': {}
        }

        for config_file in config_files:
            try:
                category = self._categorize_config(config_file)
                content = self._load_config(config_file)

                if content:
                    key = config_file.stem
                    consolidated[category][key] = content
                    self.mapping_log.append({
                        'source': str(config_file),
                        'category': category,
                        'status': 'consolidated'
                    })
            except Exception as e:
                self.errors.append({
                    'file': str(config_file),
                    'error': str(e)
                })

        # Save consolidated configs
        config_dir = self.target_dir / 'config'
        config_dir.mkdir(exist_ok=True)

        for category, configs in consolidated.items():
            if configs:
                output_file = config_dir / f'{category}_config.yaml'
                with open(output_file, 'w') as f:
                    yaml.dump(configs, f, default_flow_style=False)
                logger.info(f"Saved {category} configurations to {output_file}")

    def _categorize_config(self, filepath: Path) -> str:
        """Categorize configuration file"""
        path_str = str(filepath).lower()

        if 'agent' in path_str:
            return 'agents'
        elif 'engine' in path_str:
            return 'engines'
        elif 'model' in path_str:
            return 'models'
        elif 'api' in path_str or 'route' in path_str:
            return 'api'
        else:
            return 'general'

    def _load_config(self, filepath: Path) -> Dict[str, Any]:
        """Load configuration file"""
        try:
            if filepath.suffix in ['.yaml', '.yml']:
                with open(filepath, 'r') as f:
                    return yaml.safe_load(f) or {}
            elif filepath.suffix == '.json':
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {filepath}: {e}")
            return {}

    def migrate_code(self):
        """Migrate and consolidate code files"""
        logger.info("Migrating code files")

        # Define migration rules
        migration_rules = {
            'main.py': 'src/api/main.py',
            'config.py': 'src/core/config.py',
            'utils.py': 'src/core/utils.py',
            'base_agent.py': 'src/agents/base.py',
            'base_engine.py': 'src/engines/base.py',
            'predictive_engine.py': 'src/engines/predictive.py',
            'vector_engine.py': 'src/engines/vector.py'
        }

        # Find and migrate Python files
        for py_file in self.source_dir.rglob('*.py'):
            filename = py_file.name

            # Skip __pycache__ and test files for now
            if '__pycache__' in str(py_file) or 'test_' in filename:
                continue

            # Determine destination
            if filename in migration_rules:
                dest = self.target_dir / migration_rules[filename]
            else:
                # Categorize based on path
                if 'agent' in str(py_file).lower():
                    dest = self.target_dir / 'src' / 'agents' / filename
                elif 'engine' in str(py_file).lower():
                    dest = self.target_dir / 'src' / 'engines' / filename
                elif 'model' in str(py_file).lower():
                    dest = self.target_dir / 'src' / 'models' / filename
                elif 'api' in str(py_file).lower() or 'route' in str(py_file).lower():
                    dest = self.target_dir / 'src' / 'api' / filename
                else:
                    dest = self.target_dir / 'src' / 'core' / filename

            # Copy file
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, dest)

            self.mapping_log.append({
                'source': str(py_file),
                'destination': str(dest),
                'status': 'migrated'
            })

    def create_unified_config(self):
        """Create a unified configuration system"""
        logger.info("Creating unified configuration")

        unified_config = {
            'project': {
                'name': 'ncOS',
                'version': '21.7',
                'description': 'Neural Compute Operating System'
            },
            'paths': {
                'root': '.',
                'src': './src',
                'config': './config',
                'tests': './tests',
                'logs': './logs',
                'data': './data'
            },
            'engines': {
                'predictive': {
                    'enabled': True,
                    'config_file': 'config/engines_config.yaml'
                },
                'vector': {
                    'enabled': True,
                    'config_file': 'config/engines_config.yaml'
                }
            },
            'agents': {
                'config_file': 'config/agents_config.yaml',
                'auto_discover': True
            },
            'api': {
                'host': '0.0.0.0',
                'port': 8000,
                'reload': True,
                'config_file': 'config/api_config.yaml'
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/ncOS.log'
            }
        }

        config_file = self.target_dir / 'config' / 'settings.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(unified_config, f, default_flow_style=False)

        logger.info(f"Created unified configuration at {config_file}")

    def generate_reports(self):
        """Generate consolidation reports"""
        logger.info("Generating reports")

        # Mapping report
        mapping_report = {
            'timestamp': datetime.now().isoformat(),
            'source_directory': str(self.source_dir),
            'target_directory': str(self.target_dir),
            'files_processed': len(self.mapping_log),
            'errors': len(self.errors),
            'mappings': self.mapping_log,
            'errors_detail': self.errors
        }

        report_file = self.target_dir / 'consolidation_report.json'
        with open(report_file, 'w') as f:
            json.dump(mapping_report, f, indent=2)

        # Summary report
        summary = f"""# ncOS Consolidation Summary

## Overview
- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Files Processed**: {len(self.mapping_log)}
- **Errors**: {len(self.errors)}

## New Structure
```
{self.target_dir}/
├── src/
│   ├── core/       # Core system components
│   ├── engines/    # Engine implementations
│   ├── agents/     # Agent implementations
│   ├── api/        # API layer
│   └── models/     # Data models
├── config/         # Consolidated configurations
├── tests/          # Test suite
├── scripts/        # Utility scripts
└── docs/           # Documentation
```

## Next Steps
1. Review the consolidation report
2. Update import statements in Python files
3. Run tests to ensure functionality
4. Update documentation
"""

        summary_file = self.target_dir / 'CONSOLIDATION_SUMMARY.md'
        summary_file.write_text(summary)

        logger.info(f"Reports generated: {report_file}, {summary_file}")

    def run(self):
        """Run the complete consolidation process"""
        logger.info("Starting ncOS consolidation and remapping")

        try:
            # Create backup
            self.create_backup()

            # Create new structure
            self.create_new_structure()

            # Consolidate configurations
            self.consolidate_configs()

            # Migrate code
            self.migrate_code()

            # Create unified config
            self.create_unified_config()

            # Generate reports
            self.generate_reports()

            logger.info("Consolidation completed successfully!")

        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            raise


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Consolidate and remap ncOS project')
    parser.add_argument('--source', default='ncOS_v21.7', help='Source directory')
    parser.add_argument('--target', default='ncOS_consolidated', help='Target directory')

    args = parser.parse_args()

    consolidator = ProjectConsolidator(args.source, args.target)
    consolidator.run()


if __name__ == '__main__':
    main()
