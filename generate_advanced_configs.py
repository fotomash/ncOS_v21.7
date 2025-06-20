#!/usr/bin/env python3
"""
Advanced Agent Configuration Generator
Based on patterns from agent_profile_schemas.py and module_configs.py
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any

# Templates for agent profiles
AGENT_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "CoreSystemAgent": {
        "profile_name": "CoreSystemAgent",
        "description": "Core system orchestration and health monitoring",
        "version": "21.7.0",
        "execution_sequence": ["health_check", "system_monitor", "log_aggregator"],
        "code_map": {
            "health_check": "ncos.core.health_check.HealthChecker",
            "system_monitor": "ncos.core.system_monitor.SystemMonitor",
            "log_aggregator": "ncos.core.log_aggregator.LogAggregator",
        },
        "meta_agent": {
            "agent_id": "NCOS_Core_001",
            "strategy_tags": ["System", "Health", "Monitoring"],
            "llm_contextualization_enabled": False,
        },
        "settings": {
            "log_level": "INFO",
            "health_check_interval": 60,
            "max_retries": 3,
            "startup_delay": 5,
            "shutdown_timeout": 30,
        },
    },
    "MarketDataCaptain": {
        "profile_name": "MarketDataCaptain",
        "description": "Real-time market data ingestion and processing",
        "version": "21.7.0",
        "execution_sequence": ["data_ingestion", "tick_processor", "spread_tracker"],
        "code_map": {
            "data_ingestion": "ncos.data.ingestion.DataIngestion",
            "tick_processor": "ncos.data.tick_processor.TickProcessor",
            "spread_tracker": "ncos.data.spread_tracker.SpreadTracker",
        },
        "meta_agent": {
            "agent_id": "NCOS_Market_001",
            "strategy_tags": ["Market", "Data", "RealTime"],
            "llm_contextualization_enabled": True,
        },
        "data_enricher": {
            "enabled": True,
            "spread_settings": {
                "enabled": True,
                "window_size": 25,
                "high_vol_baseline": 0.0008,
            },
            "tick_context_settings": {
                "enable_tick_merge": True,
                "journal_tick_context": True,
            },
        },
        "settings": {
            "symbols": ["XAUUSD", "EURUSD", "GBPUSD"],
            "timeframes": ["M1", "M5", "M15", "H1", "H4"],
            "data_source": "live",
            "update_frequency": 1,
            "buffer_size": 1000,
            "flush_interval": 10,
        },
    },
    "PortfolioManager": {
        "profile_name": "PortfolioManager",
        "description": "Portfolio optimization and position management",
        "version": "21.7.0",
        "execution_sequence": ["risk_calculator", "position_sizer", "portfolio_optimizer"],
        "code_map": {
            "risk_calculator": "ncos.portfolio.risk_calculator.RiskCalculator",
            "position_sizer": "ncos.portfolio.position_sizer.PositionSizer",
            "portfolio_optimizer": "ncos.portfolio.optimizer.PortfolioOptimizer",
        },
        "meta_agent": {
            "agent_id": "NCOS_Portfolio_001",
            "strategy_tags": ["Portfolio", "Risk", "Optimization"],
            "llm_contextualization_enabled": True,
        },
        "risk_manager": {"enabled": True, "max_risk_per_trade": 0.01},
        "settings": {
            "max_positions": 10,
            "risk_per_trade": 0.01,
            "max_daily_risk": 0.05,
            "position_sizing_method": "fixed_fractional",
            "rebalance_interval": 3600,
            "risk_check_interval": 300,
        },
    },
    "SignalProcessor": {
        "profile_name": "SignalProcessor",
        "description": "Trading signal processing and validation",
        "version": "21.7.0",
        "execution_sequence": ["context_analyzer", "liquidity_engine", "structure_validator", "fvg_locator", "confluence_stacker"],
        "code_map": {
            "context_analyzer": "ncos.signals.context_analyzer.ContextAnalyzer",
            "liquidity_engine": "ncos.signals.liquidity_engine.LiquidityEngine",
            "structure_validator": "ncos.signals.structure_validator.StructureValidator",
            "fvg_locator": "ncos.signals.fvg_locator.FVGLocator",
            "confluence_stacker": "ncos.signals.confluence_stacker.ConfluenceStacker",
        },
        "meta_agent": {
            "agent_id": "NCOS_Signal_001",
            "strategy_tags": ["Signal", "Analysis", "Validation"],
            "llm_contextualization_enabled": True,
            "memory_embedding_strategy": "on_signal_zbar_summary",
        },
        "context_analyzer": {"enabled": True, "bias_determination_timeframes": ["H1", "H4"]},
        "liquidity_engine": {"enabled": True, "lookback_period": 100},
        "structure_validator": {
            "enabled": True,
            "swing_engine_config": {"swing_n": 1, "break_on_close": True},
        },
        "settings": {
            "min_confidence": 0.7,
            "signal_types": ["entry", "exit", "adjustment"],
            "cooldown_period": 300,
            "confirmation_required": True,
            "queue_size": 100,
            "processing_threads": 4,
        },
        "journaling": {
            "verbosity": "detailed",
            "enable_zbar_format": True,
            "log_directory": "/logs/signals/",
        },
    },
    "VoiceCommandAgent": {
        "profile_name": "VoiceCommandAgent",
        "description": "Natural language voice command processing",
        "version": "21.7.0",
        "execution_sequence": ["voice_parser", "command_router", "response_generator"],
        "code_map": {
            "voice_parser": "ncos.voice.voice_tag_parser.VoiceTagParser",
            "command_router": "ncos.voice.llm_orchestrator.CommandRouter",
            "response_generator": "ncos.voice.response_generator.ResponseGenerator",
        },
        "meta_agent": {
            "agent_id": "NCOS_Voice_001",
            "strategy_tags": ["Voice", "NLP", "Interface"],
            "llm_contextualization_enabled": True,
        },
        "settings": {
            "wake_word": "ncos",
            "language": "en-US",
            "confidence_threshold": 0.7,
            "max_command_length": 100,
            "timeout": 5,
        },
    },
}


def generate_agent_configurations() -> None:
    config_dir = Path("config")
    agents_dir = config_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)
    agent_registry: Dict[str, Any] = {"version": "21.7.0", "agents": {}}
    for agent_name, template in AGENT_TEMPLATES.items():
        agent_file = agents_dir / f"{agent_name.lower()}_profile.yaml"
        with open(agent_file, "w") as f:
            yaml.dump(template, f, default_flow_style=False, sort_keys=False)
        agent_registry["agents"][agent_name] = {
            "profile_path": str(agent_file.relative_to(config_dir)),
            "enabled": True,
            "priority": 1,
        }
        simple_config = {
            "agent": {"name": agent_name, "version": template["version"], "enabled": True},
            "settings": template.get("settings", {}),
        }
        simple_file = config_dir / f"{agent_name.lower()}_config.yaml"
        with open(simple_file, "w") as f:
            yaml.dump(simple_config, f, default_flow_style=False, sort_keys=False)
    registry_file = config_dir / "agent_registry.yaml"
    with open(registry_file, "w") as f:
        yaml.dump(agent_registry, f, default_flow_style=False, sort_keys=False)
    generate_trigger_routes(config_dir)
    generate_system_config(config_dir)
    print(f"\u2713 Generated {len(AGENT_TEMPLATES)} agent profiles")


def generate_trigger_routes(config_dir: Path) -> None:
    trigger_routes = {
        "version": "21.7.0",
        "triggers": {
            "data": {
                "tick": {
                    "xauusd": {
                        "description": "XAUUSD tick data trigger",
                        "actions": ["update_market_data", "check_signals", "update_spread"],
                        "conditions": ["market_open", "valid_spread"],
                        "agents": ["MarketDataCaptain", "SignalProcessor"],
                    }
                }
            },
            "analysis": {
                "manipulation": {
                    "spread_detected": {
                        "description": "Spread manipulation detection",
                        "actions": ["log_manipulation", "adjust_risk", "notify_trader"],
                        "conditions": ["spread_threshold_exceeded", "volume_spike"],
                        "agents": ["MarketDataCaptain", "PortfolioManager", "NotificationAgent"],
                    }
                },
                "signal": {
                    "zbar_complete": {
                        "description": "ZBAR analysis completed",
                        "actions": ["validate_signal", "calculate_position", "prepare_order"],
                        "conditions": ["signal_confidence_met", "risk_approved"],
                        "agents": ["SignalProcessor", "PortfolioManager"],
                    }
                },
            },
            "voice": {
                "command": {
                    "received": {
                        "description": "Voice command received",
                        "actions": ["parse_command", "route_to_handler", "generate_response"],
                        "conditions": ["wake_word_detected", "command_valid"],
                        "agents": ["VoiceCommandAgent"],
                    }
                }
            },
            "session": {
                "trading": {
                    "start": {
                        "description": "Trading session started",
                        "actions": ["initialize_agents", "load_market_state", "start_monitoring"],
                        "conditions": ["market_open", "system_ready"],
                        "agents": ["CoreSystemAgent", "MarketDataCaptain", "PortfolioManager"],
                    },
                    "end": {
                        "description": "Trading session ended",
                        "actions": ["save_state", "generate_report", "cleanup"],
                        "conditions": ["market_close", "positions_flat"],
                        "agents": ["CoreSystemAgent", "PortfolioManager"],
                    },
                }
            },
        },
    }
    trigger_yaml = config_dir / "trigger_routes.yaml"
    with open(trigger_yaml, "w") as f:
        yaml.dump(trigger_routes, f, default_flow_style=False, sort_keys=False)


def generate_system_config(config_dir: Path) -> None:
    system_config = {
        "system": {
            "name": "ncOS",
            "version": "21.7.0",
            "environment": "production",
            "log_level": "INFO",
        },
        "orchestration": {
            "max_parallel_agents": 5,
            "default_timeout": 300,
            "retry_policy": {"max_retries": 3, "backoff_factor": 2, "max_backoff": 60},
        },
        "data": {
            "journal_path": "logs/trade_journal.jsonl",
            "backup_interval": 3600,
            "max_journal_size": 104857600,
            "archive_old_journals": True,
        },
        "voice": {
            "enabled": True,
            "engine": "whisper",
            "model": "base",
            "wake_word": "ncos",
            "language": "en",
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "cors_origins": ["http://localhost:8501"],
            "api_key_required": False,
        },
        "dashboard": {
            "host": "localhost",
            "port": 8501,
            "auto_refresh": True,
            "refresh_interval": 5,
        },
    }
    main_config = config_dir / "ncos_config.yaml"
    with open(main_config, "w") as f:
        yaml.dump(system_config, f, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    print("\ud83d\udd27 Advanced Agent Configuration Generator")
    print("=" * 50)
    generate_agent_configurations()
    print("\n\u2705 Configuration generation complete!")
