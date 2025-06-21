"""
NCOS Integration Bootstrap
Master script to load and initialize all 13 agents
"""

import importlib
import importlib.util
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import yaml

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NCOS_Bootstrap')


class NCOSIntegrationBootstrap:
    """
    Master bootstrap orchestrator for NCOS v21 system.
    Loads configuration, initializes agents, and manages the agent mesh.
    """

    def __init__(self, config_dir: str = './config'):
        self.config_dir = Path(config_dir)
        self.agents = {}
        self.agent_registry = {}
        self.bootstrap_config = {}
        self.initialization_order = []
        self.mesh_connections = {}

        # System state
        self.system_state = {
            'status': 'initializing',
            'start_time': datetime.now(),
            'agents_loaded': 0,
            'agents_initialized': 0,
            'errors': []
        }

    def load_configuration(self) -> bool:
        """Load bootstrap.yaml and agent_registry.yaml"""
        try:
            # Load bootstrap configuration
            bootstrap_path = self.config_dir / 'bootstrap.yaml'
            if not bootstrap_path.exists():
                logger.warning(f"bootstrap.yaml not found at {bootstrap_path}, using defaults")
                self.bootstrap_config = self._get_default_bootstrap_config()
            else:
                with open(bootstrap_path, 'r') as f:
                    self.bootstrap_config = yaml.safe_load(f)

            # Load agent registry
            registry_path = self.config_dir / 'agent_registry.yaml'
            if not registry_path.exists():
                logger.warning(f"agent_registry.yaml not found at {registry_path}, using defaults")
                self.agent_registry = self._get_default_agent_registry()
            else:
                with open(registry_path, 'r') as f:
                    self.agent_registry = yaml.safe_load(f)

            # Determine initialization order
            self._determine_init_order()

            logger.info("Configuration loaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.system_state['errors'].append(f"Config load error: {str(e)}")
            return False

    def _get_default_bootstrap_config(self) -> Dict[str, Any]:
        """Return default bootstrap configuration"""
        return {
            'version': '21.0',
            'system': {
                'name': 'NCOS',
                'mode': 'production',
                'single_session': True
            },
            'initialization': {
                'parallel': False,
                'timeout': 300,
                'retry_attempts': 3
            },
            'mesh': {
                'enable_broadcast': True,
                'heartbeat_interval': 60
            }
        }

    def _get_default_agent_registry(self) -> Dict[str, Any]:
        """Return default agent registry"""
        return {
            'agents': {
                'CoreSystemAgent': {
                    'module': 'core_system_agent',
                    'class': 'CoreSystemAgent',
                    'priority': 1,
                    'dependencies': []
                },
                'VectorMemoryBoot': {
                    'module': 'vector_memory_boot',
                    'class': 'VectorMemoryBoot',
                    'priority': 2,
                    'dependencies': []
                },
                'ParquetIngestor': {
                    'module': 'parquet_ingestor',
                    'class': 'ParquetIngestor',
                    'priority': 2,
                    'dependencies': []
                },
                'MarketDataCaptain': {
                    'module': 'market_data_captain',
                    'class': 'MarketDataCaptain',
                    'priority': 3,
                    'dependencies': ['ParquetIngestor']
                },
                'TechnicalAnalyst': {
                    'module': 'technical_analyst',
                    'class': 'TechnicalAnalyst',
                    'priority': 4,
                    'dependencies': ['MarketDataCaptain']
                },
                'SMCRouter': {
                    'module': 'smc_router',
                    'class': 'SMCRouter',
                    'priority': 5,
                    'dependencies': ['TechnicalAnalyst']
                },
                'MAZ2Executor': {
                    'module': 'maz2_executor',
                    'class': 'MAZ2Executor',
                    'priority': 6,
                    'dependencies': ['SMCRouter']
                },
                'TMCExecutor': {
                    'module': 'tmc_executor',
                    'class': 'TMCExecutor',
                    'priority': 6,
                    'dependencies': ['SMCRouter']
                },
                'RiskGuardian': {
                    'module': 'risk_guardian',
                    'class': 'RiskGuardian',
                    'priority': 7,
                    'dependencies': ['MAZ2Executor', 'TMCExecutor']
                },
                'PortfolioManager': {
                    'module': 'portfolio_manager',
                    'class': 'PortfolioManager',
                    'priority': 8,
                    'dependencies': ['RiskGuardian']
                },
                'BroadcastRelay': {
                    'module': 'broadcast_relay',
                    'class': 'BroadcastRelay',
                    'priority': 9,
                    'dependencies': []
                },
                'ReportGenerator': {
                    'module': 'report_generator',
                    'class': 'ReportGenerator',
                    'priority': 10,
                    'dependencies': ['PortfolioManager']
                },
                'SessionStateManager': {
                    'module': 'session_state_manager',
                    'class': 'SessionStateManager',
                    'priority': 11,
                    'dependencies': []
                }
            }
        }

    def _determine_init_order(self):
        """Determine agent initialization order based on dependencies"""
        agents = self.agent_registry.get('agents', {})

        # Sort by priority first
        sorted_agents = sorted(agents.items(), key=lambda x: x[1].get('priority', 99))

        # Build initialization order respecting dependencies
        initialized = set()
        self.initialization_order = []

        while len(initialized) < len(agents):
            progress_made = False

            for agent_name, agent_config in sorted_agents:
                if agent_name in initialized:
                    continue

                # Check if all dependencies are satisfied
                deps = agent_config.get('dependencies', [])
                if all(dep in initialized for dep in deps):
                    self.initialization_order.append(agent_name)
                    initialized.add(agent_name)
                    progress_made = True

            if not progress_made:
                # Circular dependency or missing dependency
                remaining = set(agents.keys()) - initialized
                logger.warning(f"Could not resolve dependencies for: {remaining}")
                # Add remaining agents anyway
                self.initialization_order.extend(remaining)
                break

        logger.info(f"Initialization order: {self.initialization_order}")

    def load_agent_module(self, agent_name: str, agent_config: Dict[str, Any]) -> Optional[Any]:
        """Dynamically load an agent module"""
        try:
            module_name = agent_config['module']
            class_name = agent_config['class']

            # Try to import the module
            try:
                # First try standard import
                module = importlib.import_module(module_name)
            except ImportError:
                # Try loading from file
                module_path = Path(f"{module_name}.py")
                if module_path.exists():
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                else:
                    raise ImportError(f"Cannot find module {module_name}")

            # Get the agent class
            agent_class = getattr(module, class_name)

            # Load agent configuration
            config_path = self.config_dir / f"{agent_name.lower()}_config.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    agent_config_data = yaml.safe_load(f)
            else:
                agent_config_data = self._get_default_agent_config(agent_name)

            # Instantiate the agent
            agent_instance = agent_class(agent_config_data)

            logger.info(f"Successfully loaded agent: {agent_name}")
            self.system_state['agents_loaded'] += 1
            return agent_instance

        except Exception as e:
            logger.error(f"Failed to load agent {agent_name}: {e}")
            logger.error(traceback.format_exc())
            self.system_state['errors'].append(f"Agent load error ({agent_name}): {str(e)}")
            return None

    def _get_default_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Return default configuration for an agent"""
        default_configs = {
            'CoreSystemAgent': {
                'heartbeat_interval': 60,
                'data_directory': './data',
                'log_level': 'INFO'
            },
            'VectorMemoryBoot': {
                'vector_dimension': 768,
                'max_entries': 10000,
                'similarity_threshold': 0.7
            },
            'ParquetIngestor': {
                'chunk_size': 10000,
                'max_memory_mb': 500,
                'schema_definitions': {}
            },
            'MarketDataCaptain': {
                'cache_size': 1000,
                'update_interval': 60,
                'supported_symbols': ['BTC/USD', 'ETH/USD']
            },
            'TechnicalAnalyst': {
                'indicators': ['sma', 'ema', 'rsi', 'macd'],
                'timeframes': ['1m', '5m', '15m', '1h']
            },
            'SMCRouter': {
                'volatility_threshold': 0.02,
                'trend_threshold': 0.01,
                'confidence_threshold': 0.7
            },
            'MAZ2Executor': {
                'lookback_period': 20,
                'zone_multiplier': 2.0,
                'max_position_size': 10000
            },
            'TMCExecutor': {
                'trend_periods': [10, 20, 50],
                'momentum_period': 14,
                'confluence_threshold': 0.7
            },
            'RiskGuardian': {
                'max_drawdown': 0.1,
                'position_limit': 5,
                'risk_per_trade': 0.02
            },
            'PortfolioManager': {
                'rebalance_threshold': 0.1,
                'max_correlation': 0.7,
                'reserve_ratio': 0.2
            },
            'BroadcastRelay': {
                'max_queue_size': 1000,
                'retry_attempts': 3,
                'timeout': 30
            },
            'ReportGenerator': {
                'report_interval': 3600,
                'formats': ['json', 'yaml', 'html'],
                'metrics': ['pnl', 'sharpe', 'drawdown']
            },
            'SessionStateManager': {
                'checkpoint_interval': 300,
                'state_directory': './state',
                'compression': True
            }
        }

        return default_configs.get(agent_name, {})

    def initialize_agent(self, agent_name: str, agent_instance: Any) -> bool:
        """Initialize a single agent"""
        try:
            # Call agent's initialize method if it exists
            if hasattr(agent_instance, 'initialize'):
                result = agent_instance.initialize()
                if result:
                    logger.info(f"Agent {agent_name} initialized successfully")
                    self.system_state['agents_initialized'] += 1
                    return True
                else:
                    logger.error(f"Agent {agent_name} initialization returned False")
                    return False
            else:
                # Agent doesn't have initialize method, assume it's ready
                logger.info(f"Agent {agent_name} ready (no initialize method)")
                self.system_state['agents_initialized'] += 1
                return True

        except Exception as e:
            logger.error(f"Failed to initialize agent {agent_name}: {e}")
            self.system_state['errors'].append(f"Agent init error ({agent_name}): {str(e)}")
            return False

    def setup_mesh_connections(self):
        """Setup inter-agent communication mesh"""
        try:
            # Get BroadcastRelay if available
            broadcast_relay = self.agents.get('BroadcastRelay')

            if broadcast_relay and hasattr(broadcast_relay, 'register_agent'):
                # Register all agents with the broadcast relay
                for agent_name, agent_instance in self.agents.items():
                    if agent_name != 'BroadcastRelay':
                        broadcast_relay.register_agent(agent_name, agent_instance)

                logger.info("Agent mesh connections established")

            # Setup direct connections based on dependencies
            for agent_name, agent_config in self.agent_registry.get('agents', {}).items():
                if agent_name not in self.agents:
                    continue

                dependencies = agent_config.get('dependencies', [])
                self.mesh_connections[agent_name] = dependencies

                # If agent has a set_dependencies method, use it
                agent_instance = self.agents[agent_name]
                if hasattr(agent_instance, 'set_dependencies'):
                    dep_instances = {dep: self.agents.get(dep) for dep in dependencies}
                    agent_instance.set_dependencies(dep_instances)

            return True

        except Exception as e:
            logger.error(f"Failed to setup mesh connections: {e}")
            self.system_state['errors'].append(f"Mesh setup error: {str(e)}")
            return False

    def bootstrap(self) -> bool:
        """Main bootstrap process"""
        logger.info("Starting NCOS Integration Bootstrap")

        # Step 1: Load configuration
        if not self.load_configuration():
            logger.error("Failed to load configuration")
            self.system_state['status'] = 'failed'
            return False

        # Step 2: Load all agents
        logger.info("Loading agents...")
        for agent_name in self.initialization_order:
            agent_config = self.agent_registry['agents'][agent_name]
            agent_instance = self.load_agent_module(agent_name, agent_config)

            if agent_instance:
                self.agents[agent_name] = agent_instance
            else:
                logger.warning(f"Skipping agent {agent_name} due to load failure")

        # Step 3: Initialize agents in order
        logger.info("Initializing agents...")
        for agent_name in self.initialization_order:
            if agent_name in self.agents:
                success = self.initialize_agent(agent_name, self.agents[agent_name])
                if not success:
                    logger.warning(f"Agent {agent_name} initialization failed")

        # Step 4: Setup mesh connections
        logger.info("Setting up agent mesh...")
        self.setup_mesh_connections()

        # Step 5: Verify system status
        total_agents = len(self.agent_registry.get('agents', {}))
        if self.system_state['agents_initialized'] == total_agents:
            self.system_state['status'] = 'running'
            logger.info(f"Bootstrap complete! All {total_agents} agents initialized.")
            success = True
        else:
            self.system_state['status'] = 'partial'
            logger.warning(
                f"Bootstrap partial: {self.system_state['agents_initialized']}/{total_agents} agents initialized")
            success = self.system_state['agents_initialized'] > 0

        # Save bootstrap report
        self.save_bootstrap_report()

        return success

    def save_bootstrap_report(self):
        """Save detailed bootstrap report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_state': self.system_state,
            'agents_loaded': list(self.agents.keys()),
            'initialization_order': self.initialization_order,
            'mesh_connections': self.mesh_connections,
            'configuration': {
                'bootstrap': self.bootstrap_config,
                'agent_count': len(self.agent_registry.get('agents', {}))
            }
        }

        # Save as JSON
        report_path = Path('bootstrap_report.json')
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Bootstrap report saved to {report_path}")

    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Get a loaded agent instance"""
        return self.agents.get(agent_name)

    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = self.system_state.copy()
        status['uptime'] = (datetime.now() - status['start_time']).total_seconds()
        status['agent_statuses'] = {}

        for agent_name, agent_instance in self.agents.items():
            if hasattr(agent_instance, 'get_status'):
                status['agent_statuses'][agent_name] = agent_instance.get_status()
            else:
                status['agent_statuses'][agent_name] = 'running'

        return status

    def shutdown(self):
        """Gracefully shutdown the system"""
        logger.info("Initiating system shutdown...")

        # Shutdown agents in reverse order
        for agent_name in reversed(self.initialization_order):
            if agent_name in self.agents:
                agent_instance = self.agents[agent_name]
                if hasattr(agent_instance, 'shutdown'):
                    try:
                        agent_instance.shutdown()
                        logger.info(f"Agent {agent_name} shutdown complete")
                    except Exception as e:
                        logger.error(f"Error shutting down {agent_name}: {e}")

        self.system_state['status'] = 'shutdown'
        logger.info("System shutdown complete")


def main():
    """Main entry point"""
    # Create bootstrap instance
    bootstrap = NCOSIntegrationBootstrap(config_dir='./config')

    try:
        # Run bootstrap process
        success = bootstrap.bootstrap()

        if success:
            print("\n" + "=" * 50)
            print("NCOS SYSTEM SUCCESSFULLY BOOTSTRAPPED")
            print("=" * 50)

            # Display system status
            status = bootstrap.get_system_status()
            print(f"Status: {status['status']}")
            print(f"Agents Initialized: {status['agents_initialized']}")
            print(f"Active Agents: {', '.join(status['agent_statuses'].keys())}")

            if status['errors']:
                print(f"\nWarnings/Errors ({len(status['errors'])}):")
                for error in status['errors']:
                    print(f"  - {error}")

            print("\nSystem is ready for operation!")

        else:
            print("\nBootstrap failed! Check logs for details.")

    except KeyboardInterrupt:
        print("\nShutdown requested...")
        bootstrap.shutdown()
    except Exception as e:
        print(f"\nFatal error: {e}")
        traceback.print_exc()
        bootstrap.shutdown()


if __name__ == '__main__':
    main()
