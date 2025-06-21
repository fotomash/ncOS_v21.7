# ncOS Project Consolidation and Remapping Guide

## Overview
This guide explains the consolidation and remapping process for the ncOS project.

## What This Does

### 1. **Backup Creation**
- Creates a timestamped backup of your current project
- Ensures you can revert if needed

### 2. **Structure Reorganization**
- Consolidates duplicate files
- Creates a clean, modular structure
- Organizes code by functionality

### 3. **Configuration Consolidation**
- Merges all configuration files
- Creates category-based config files
- Establishes a unified configuration system

### 4. **Code Migration**
- Moves Python files to appropriate modules
- Maintains functionality while improving organization
- Updates module structure

## New Project Structure

```
ncOS_consolidated/
├── src/                    # All source code
│   ├── core/              # Core utilities and config
│   ├── engines/           # Engine implementations
│   ├── agents/            # Agent implementations
│   ├── api/               # API and routes
│   └── models/            # Data models
├── config/                # All configuration files
│   ├── settings.yaml      # Main settings
│   ├── agents_config.yaml # Agent configurations
│   ├── engines_config.yaml # Engine configurations
│   └── api_config.yaml    # API configurations
├── tests/                 # Test suite
├── scripts/               # Utility scripts
├── docs/                  # Documentation
└── logs/                  # Log files
```

## How to Use

1. **Run the Consolidation**:
   ```bash
   python consolidate_and_remap.py
   ```

2. **Review the Results**:
   - Check `consolidation_report.json` for details
   - Review `CONSOLIDATION_SUMMARY.md` for overview

3. **Update Your Code**:
   - Update import statements
   - Test functionality
   - Update documentation

## Benefits

1. **Cleaner Structure**: Organized by functionality
2. **No Duplicates**: Single source of truth
3. **Better Imports**: Clear module hierarchy
4. **Unified Config**: One configuration system
5. **Maintainable**: Easier to extend and modify

## Post-Consolidation Tasks

1. **Update Imports**:
   ```python
   # Old
   from engines.predictive_engine import PredictiveEngine

   # New
   from src.engines.predictive import PredictiveEngine
   ```

2. **Update Configuration Paths**:
   ```python
   # Old
   config_path = "configs/engine_config.yaml"

   # New
   config_path = "config/engines_config.yaml"
   ```

3. **Run Tests**:
   ```bash
   pytest tests/
   ```

4. **Update Documentation**:
   - Update README.md
   - Update API documentation
   - Update deployment guides
