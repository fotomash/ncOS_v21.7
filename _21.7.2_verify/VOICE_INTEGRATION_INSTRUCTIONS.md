# NCOS Voice Integration Instructions

## Quick Integration Steps

### 1. ZBAR Agent Integration

To add voice capabilities to your existing ZBAR agent:

```python
# In your main ZBAR file, replace:
from zbar_agent import ZBARAgent

# With:
from zbar_voice_integration import VoiceEnabledZBARAgent as ZBARAgent
```

That's it! Your ZBAR agent now supports voice commands.

### 2. Menu System Integration

To add voice menu to your existing menu system:

```python
# In your main application file:
from menu_voice_integration import integrate_voice_menu

# After creating your menu system:
menu_system = MenuSystem(config)

# Upgrade it to voice-enabled:
menu_system = integrate_voice_menu(menu_system)
```

### 3. API Integration

Add voice routes to your FastAPI app:

```python
# In your main API file (where you define app)
from voice_api_routes import router as voice_router

# Add the router
app.include_router(voice_router)
```

## Usage Examples

### Example 1: Voice-Triggered ZBAR Analysis

```python
# Initialize voice-enabled agent
agent = VoiceEnabledZBARAgent()

# Process voice command
result = agent.process_voice_command("Analyze gold on H4 timeframe")

# Check result
if result["status"] == "success":
    print(f"Analysis: {result['analysis']}")
```

### Example 2: Voice Menu Navigation

```python
# In your menu loop
if user_choice == "v":  # Voice command option
    menu_system.execute_voice_action("voice_mark_setup", {})
```

### Example 3: Unified System

```python
# Use the unified system for everything
from ncos_voice_unified import NCOSVoiceSystem

system = NCOSVoiceSystem(config)
system.start_interactive_session()
```

## Voice Command Reference

### Marking/Logging
- "Mark [symbol] [bias] on [timeframe]"
- "Log trade idea: [your notes]"
- "Mark [symbol] [bias], [session] session, maturity [score]"

### Analysis
- "Analyze [symbol] [timeframe]"
- "Run ZBAR on [symbol]"
- "Scan for [pattern] in [session]"

### Queries
- "Show all [bias] setups"
- "Check [session] trades"
- "Find [symbol] entries today"

## Configuration

Add to your config file:

```yaml
voice:
  confidence_threshold: 0.7
  default_symbol: "XAUUSD"
  default_timeframe: "H4"
  api_base: "http://localhost:8001"
```

## Testing

Run the demo scripts to test:

```bash
# Test ZBAR voice integration
python zbar_voice_integration.py

# Test menu voice integration
python menu_voice_integration.py

# Test unified system
python core/ncos_voice_unified.py
```
