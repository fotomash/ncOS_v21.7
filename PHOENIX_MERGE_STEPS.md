# Phoenix Session Merge - Step by Step Instructions

## Prerequisites
- Working NCOS v21.7 installation
- Python 3.8+
- Required packages: pandas, numpy, pydantic

## Step 1: Prepare Files
1. Ensure you have `ncos_session_optimized.py` in your current directory
2. Navigate to your NCOS root directory (where config/ and agents/ folders are)

## Step 2: Create Phoenix Structure
```bash
# Create directories
mkdir -p phoenix_session/core
mkdir -p phoenix_session/adapters
mkdir -p phoenix_session/engines
mkdir -p phoenix_session/config

# Create __init__ files
echo '"""Phoenix Session Module"""' > phoenix_session/__init__.py
echo '"""Phoenix Core Module"""' > phoenix_session/core/__init__.py
echo '"""Phoenix Adapters Module"""' > phoenix_session/adapters/__init__.py
```

## Step 3: Copy Core Files
```bash
# Copy the optimized Phoenix controller
cp ncos_session_optimized.py phoenix_session/core/

# Create the NCOS Phoenix controller wrapper
# Copy PHOENIX_CORE_CONTROLLER from PHOENIX_MERGE_IMPLEMENTATION.py
# to phoenix_session/core/controller.py
```

## Step 4: Install Adapters
```bash
# Create Wyckoff adapter
# Copy WYCKOFF_ADAPTER from PHOENIX_MERGE_IMPLEMENTATION.py
# to phoenix_session/adapters/wyckoff_adapter.py

# Create Chart adapter  
# Copy CHART_ADAPTER from PHOENIX_MERGE_IMPLEMENTATION.py
# to phoenix_session/adapters/chart_adapter.py
```

## Step 5: Create Integration Module
```bash
# Copy INTEGRATION_MODULE from PHOENIX_MERGE_IMPLEMENTATION.py
# to phoenix_session/integration.py
```

## Step 6: Update Configuration
```bash
# Add Phoenix configuration to your master config
# Use the PHOENIX_CONFIG from PHOENIX_MERGE_IMPLEMENTATION.py
```

## Step 7: Test the Integration
```python
# Test Phoenix is working
from phoenix_session.integration import create_phoenix_integration

# Create instance
phoenix = create_phoenix_integration()

# Run test
result = phoenix.phoenix.analyze()
print(f"Phoenix working: {result}")
```

## Troubleshooting

### Import Errors
- Ensure all __init__.py files are created
- Check that ncos_session_optimized.py is in phoenix_session/core/

### Configuration Issues
- Verify config/phoenix_config.json exists
- Check that phoenix_session.enabled is set to true

### Performance Issues
- Ensure fast_mode is enabled in configuration
- Check that cache_enabled is true
