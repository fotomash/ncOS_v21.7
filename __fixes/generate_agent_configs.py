#!/usr/bin/env python3
"""Generate proper agent configurations from registry"""

import yaml
from pathlib import Path
import os

def generate_agent_configs():
    """Generate configuration files for all agents"""

    # Check if registry exists
    registry_path = Path('config/agent_registry.yaml')
    if not registry_path.exists():
        print("Error: agent_registry.yaml not found!")
        return

    # Load agent registry
    with open(registry_path, 'r') as f:
        registry = yaml.safe_load(f)

    # Agent-specific configuration templates
    agent_configs = {
        'CoreSystemAgent': {
            'agent': {'name': 'CoreSystemAgent', 'version': '1.0.0', 'enabled': True},
            'settings': {
                'log_level': 'INFO',
                'health_check_interval': 60,
                'max_retries': 3
            },
            'parameters': {
                'startup_delay': 5,
                'shutdown_timeout': 30
            }
        },
        'MarketDataCaptain': {
            'agent': {'name': 'MarketDataCaptain', 'version': '1.0.0', 'enabled': True},
            'settings': {
                'log_level': 'INFO',
                'buffer_size': 1000,
                'flush_interval': 10
            },
            'parameters': {
                'symbols': ['XAUUSD', 'EURUSD', 'GBPUSD'],
                'timeframes': ['M1', 'M5', 'M15', 'H1', 'H4'],
                'data_source': 'live',
                'update_frequency': 1
            }
        },
        'PortfolioManager': {
            'agent': {'name': 'PortfolioManager', 'version': '1.0.0', 'enabled': True},
            'settings': {
                'log_level': 'INFO',
                'rebalance_interval': 3600,
                'risk_check_interval': 300
            },
            'parameters': {
                'max_positions': 10,
                'risk_per_trade': 0.01,
                'max_daily_risk': 0.05,
                'position_sizing_method': 'fixed_fractional'
            }
        },
        'RiskManager': {
            'agent': {'name': 'RiskManager', 'version': '1.0.0', 'enabled': True},
            'settings': {
                'log_level': 'WARNING',
                'alert_threshold': 0.8,
                'emergency_close_threshold': 0.95
            },
            'parameters': {
                'max_drawdown': 0.20,
                'daily_loss_limit': 0.06,
                'correlation_threshold': 0.7,
                'var_confidence': 0.95
            }
        },
        'SignalProcessor': {
            'agent': {'name': 'SignalProcessor', 'version': '1.0.0', 'enabled': True},
            'settings': {
                'log_level': 'INFO',
                'queue_size': 100,
                'processing_threads': 4
            },
            'parameters': {
                'min_confidence': 0.7,
                'signal_types': ['entry', 'exit', 'adjustment'],
                'cooldown_period': 300,
                'confirmation_required': True
            }
        }
    }

    # Default template for agents not in specific configs
    default_template = {
        'agent': {
            'name': None,
            'version': '1.0.0',
            'enabled': True
        },
        'settings': {
            'log_level': 'INFO',
            'timeout': 30,
            'retry_count': 3
        },
        'parameters': {}
    }

    # Create config directory if it doesn't exist
    config_dir = Path('config')
    config_dir.mkdir(exist_ok=True)

    # Generate configs
    generated = []
    skipped = []

    for agent_name in registry.get('agents', {}):
        config_file = config_dir / f'{agent_name.lower()}_config.yaml'

        # Check if already has real config
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = yaml.safe_load(f)
                if content and content.get('settings', {}) != {}:
                    skipped.append(agent_name)
                    continue

        # Use specific config or default
        if agent_name in agent_configs:
            config = agent_configs[agent_name]
        else:
            config = default_template.copy()
            config['agent']['name'] = agent_name

        # Write configuration
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

        generated.append(agent_name)

    # Summary
    print(f"\n✅ Generated {len(generated)} agent configurations")
    if generated:
        print("\nGenerated configs for:")
        for agent in generated:
            print(f"  - {agent}")

    if skipped:
        print(f"\n⏭️  Skipped {len(skipped)} existing configurations")

    print(f"\nTotal configuration files: {len(list(config_dir.glob('*_config.yaml')))}")

if __name__ == "__main__":
    generate_agent_configs()
