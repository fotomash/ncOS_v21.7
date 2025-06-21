# Config Loader for Split YAML Files
# Automatically loads all split configuration files

from pathlib import Path
from typing import Dict, Any

import yaml


class ConfigLoader:
    def __init__(self, config_dir: str = '.'):
        self.config_dir = Path(config_dir)
        self.configs = {}

    def load_all(self) -> Dict[str, Any]:
        # Load index first
        index_file = self.config_dir / 'index.yaml'
        if index_file.exists():
            with open(index_file, 'r') as f:
                index = yaml.safe_load(f)

            # Load each file listed in index
            for filename in index.get('files', {}):
                filepath = self.config_dir / filename
                if filepath.exists():
                    with open(filepath, 'r') as f:
                        data = yaml.safe_load(f)

                    # Remove metadata before storing
                    if '_metadata' in data:
                        category = data['_metadata']['category']
                        del data['_metadata']
                    else:
                        category = filename.replace('_config.yaml', '')

                    self.configs[category] = data

        return self.configs

    def get_category(self, category: str) -> Dict[str, Any]:
        if not self.configs:
            self.load_all()
        return self.configs.get(category, {})

    def get_key(self, key: str) -> Any:
        if not self.configs:
            self.load_all()

        for category_data in self.configs.values():
            if key in category_data:
                return category_data[key]

        return None


# Example usage
if __name__ == '__main__':
    loader = ConfigLoader('.')
    configs = loader.load_all()

    print(f"Loaded {len(configs)} configuration categories")
    for category, data in configs.items():
        print(f"  {category}: {len(data)} keys")
