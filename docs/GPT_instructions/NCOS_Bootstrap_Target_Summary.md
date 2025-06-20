# 🎯 NCOS Bootstrap Target Summary

⚠️ **Note:** The code snippets for automatic launching are provided for illustration only. Review all commands and scripts carefully before executing them.


## Correct Bootstrap Entry Points (Priority Order):

### 1. Primary Target (Recommended)
```bash
python -m ncOS.ncos_launcher --action=start_session
```
- **Source**: ncos_execution_guide.yaml
- **Purpose**: Initialize full NCOS system with orchestration
- **Config**: config/master_orchestrator.yaml

### 2. Secondary Target (Module Launch)
```bash
python -m ncOS.ncos_launcher --agent {agent_name} --config {config_path}
```
- **Source**: agent_launch_commands.txt
- **Purpose**: Launch individual agents with profiles
- **Config**: agent_profiles/*.yaml

### 3. Tertiary Target (Legacy Support)
```bash
python integration_bootstrap.py
```
- **Source**: Generated/uploaded bootstrap scripts
- **Purpose**: Fallback for older NCOS versions
- **Config**: Various configuration files

## Key Files to Reference:
- **ncos_execution_guide.yaml** - Contains 16 launch commands
- **agent_launch_commands.txt** - Module-based launch patterns
- **agent_profiles/*.yaml** - Agent configuration profiles
- **ncos_production_agents.yaml** - Agent specifications

## Auto-Detection Logic:
1. Check for ncOS.ncos_launcher module
2. Check for ncos.launch module
3. Check for integration_bootstrap.py
4. Generate bootstrap script if none found

**Result: LLM will target the modern NCOS v21 bootstrap methods correctly!**
