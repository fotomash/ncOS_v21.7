# YAML Split Report

## Summary
- **Original File**: ncOS_v21.7-main/config/general_config.yaml
- **Original Size**: 24,089,894 bytes (22.97 MB)
- **Total Keys**: 93
- **Files Created**: 12

## Categories
- **backup**: 1 keys
- **bootstrap**: 1 keys
- **config**: 28 keys
- **deployment**: 2 keys
- **engines**: 2 keys
- **general**: 43 keys
- **manifest**: 3 keys
- **models**: 6 keys
- **monitoring**: 1 keys
- **ncos_system**: 1 keys
- **testing**: 3 keys
- **trigger**: 2 keys

## Benefits
1. ✅ Faster loading times
2. ✅ Lower memory usage
3. ✅ Easier to edit and maintain
4. ✅ Better IDE performance
5. ✅ Category-based organization

## Usage
```python
from config_loader import ConfigLoader

# Load all configs
loader = ConfigLoader('split_configs')
configs = loader.load_all()

# Get specific category
api_config = loader.get_category('api')

# Get specific key
engine_settings = loader.get_key('engine_config')
```