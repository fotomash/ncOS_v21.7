# Migration Guide for Existing NCOS Projects

## Option 1: Side-by-Side Installation (Recommended for Testing)

Keep your existing NCOS separate and run voice journal alongside:

```bash
your-workspace/
├── ncos-v21/              # Your existing NCOS
└── ncos_journal/    # New voice system
```

## Option 2: Integrated Installation (For Production)

### Step 1: Backup Current System
```bash
cp -r your-ncos-project your-ncos-backup
```

### Step 2: Add Voice Components
```bash
# In your existing NCOS directory
mkdir -p core/voice
cp voice_tag_parser.py core/voice/
cp zbar_voice_integration.py core/voice/
cp menu_voice_integration.py core/voice/
cp ncos_voice_unified.py core/voice/
```

### Step 3: Update Imports
```python
# In your main files, add:
from core.voice.zbar_voice_integration import VoiceEnabledZBARAgent
from core.voice.menu_voice_integration import VoiceEnabledMenuSystem
```

### Step 4: Extend API
```python
# In your existing API main.py
from api.voice_api_routes import router as voice_router
app.include_router(voice_router, prefix="/voice")
```

## File Mapping

| New File | Where to Place | Purpose |
|----------|----------------|---------|
| voice_tag_parser.py | core/voice/ | NLP parsing |
| zbar_voice_integration.py | core/voice/ | ZBAR wrapper |
| menu_voice_integration.py | core/voice/ | Menu wrapper |
| voice_api_routes.py | api/ | API endpoints |
| zbar_journal_dashboard.py | dashboard/ | Streamlit UI |
| system_config.yaml | config/ | Voice config |

## Testing Integration

1. Start with voice standalone:
   ```bash
   python core/voice/ncos_voice_unified.py
   ```

2. Test voice commands:
   ```
   Voice> mark gold bullish h4
   ```

3. Verify journal creation:
   ```bash
   cat logs/trade_journal.jsonl
   ```

4. Check dashboard:
   ```bash
   streamlit run dashboard/zbar_journal_dashboard.py
   ```
