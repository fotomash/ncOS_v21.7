# ncOS v21.7 Improvement Quick Reference

## 🚀 Three Key Scripts

### 1. Configuration Consolidator

```bash
python consolidate_configs.py
# Merges 82 configs → ~10 unified files
# Creates config_loader.py for easy access
```

### 2. Test Coverage Enhancer

```bash
python enhance_test_coverage.py
# Generates test structure and stubs
# Creates run_tests.py convenience script
# Target: 13.3% → 40% coverage
```

### 3. Agent Rationalizer

```bash
python rationalize_agents.py
# Consolidates 53 agents → ~25
# Creates base agent class
# Generates migration guide
```

## 📋 Order of Execution

1. **Backup Everything First!**
   ```bash
   cp -r ncOS_v21.7 ncOS_v21.7_backup
   ```

2. **Run Scripts in Order**
   ```bash
   python consolidate_configs.py
   python enhance_test_coverage.py  
   python rationalize_agents.py
   ```

3. **Verify Changes**
   ```bash
   python run_tests.py --coverage
   python api/main.py  # Test application
   ```

## 🎯 Key Files Generated

- `config_unified/` - New config structure
- `config_loader.py` - Config access utility
- `tests/` - Enhanced test structure
- `run_tests.py` - Test runner
- `agents/consolidated/` - New agent structure
- `*_report.*` - Various analysis reports

## ⚡ Emergency Rollback

```bash
# If something goes wrong
rm -rf config_unified tests/consolidated agents/consolidated
cp -r *_backup_*/* ./
```

---
*Save this card for quick reference during implementation!*
