# NCOS v21 AUTOSTART - Quick Reference

## 🚀 Quick Start Commands

```bash
# Standard boot
python ncos_autostart.py

# Development mode
python ncos_autostart.py --mode development

# Skip errors and continue
python ncos_autostart.py --skip-errors

# Debug mode
python ncos_autostart.py --debug

# Custom config
python ncos_autostart.py --config my_autostart.yaml
```

## 📋 Boot Sequence

1. **Pre-flight Checks**
   - Python version
   - Disk space
   - Permissions
   - Core modules

2. **Configuration Loading**
   - AUTOSTART_v21.yaml
   - agents.yaml
   - triggers.yaml
   - predictive_engine_config.yaml

3. **Core Systems**
   - Event Bus
   - Session Manager
   - Orchestrator

4. **Mount Points**
   - /data → Market data
   - /csv → CSV discovery
   - /vectors → Vector store
   - /memory → Persistent state

5. **Predictive Engine**
   - Quality scoring system
   - Feature extraction
   - Grade assignment

6. **Agent Deployment**
   - Load in specified order
   - Configure triggers
   - Validate connections

7. **Workspaces**
   - Market workspace
   - Research workspace
   - Operations workspace

8. **Memory/Vector**
   - Hierarchical memory
   - Vector indices

9. **Data Feeds**
   - Market data connection
   - CSV file watching

10. **Final Validation**
    - Status report
    - Boot state save

## 🛠️ Configuration

### Key Files
- `AUTOSTART_v21.yaml` - Main configuration
- `config/agents.yaml` - Agent definitions
- `config/triggers.yaml` - Event routing
- `config/predictive_engine_config.yaml` - Quality scoring

### Environment Variables
```bash
export NCOS_MODE=production
export NCOS_DATA_PATH=/path/to/data
export MARKET_DATA_URL=ws://localhost:8080
```

## 🚨 Troubleshooting

### Boot Failures
```bash
# Check boot logs
cat logs/boot_state_*.json

# Run in debug mode
python ncos_autostart.py --debug

# Skip failing components
python ncos_autostart.py --skip-errors
```

### Common Issues

1. **Agent fails to load**
   - Check module exists
   - Verify class name
   - Check config syntax

2. **Mount point errors**
   - Verify permissions
   - Check disk space
   - Create directories

3. **Predictive engine issues**
   - Check config file
   - Verify dependencies
   - Review grade thresholds

## 📊 Status Commands

```bash
# System status
python ncos_status.py

# Agent status
python ncos_agents.py --list

# Workspace status
python workspace_status.py

# View active positions
python ncos_positions.py
```

## 🎯 Quick Actions

### Start Trading
```bash
python ncos_trade.py --symbol XAUUSD
```

### Run Predictive Backtest
```bash
python predictive_backtest.py
```

### Launch Grade Analysis Dashboard
```bash
streamlit run grade_analysis_dashboard.py
```

### Emergency Shutdown
```bash
python ncos_shutdown.py --emergency
```

## 📚 References

- Full documentation: `NCOS_v21_DOCUMENTATION.md`
- API reference: `API_REFERENCE.md`
- Predictive engine guide: `PREDICTIVE_ENGINE_GUIDE.md`
