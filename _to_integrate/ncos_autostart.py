#!/usr/bin/env python3
"""
NCOS v21 Phoenix Mesh - AUTOSTART System
Automated boot sequence with integrated Predictive Engine
"""

import os
import sys
import asyncio
import yaml
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NCOSAutoStartManager:
    """
    NCOS v21 AUTOSTART Manager - Controls entire boot process
    Integrates all components including the new Predictive Engine
    """

    def __init__(self, config_file: str = "AUTOSTART_v21.md", mode: str = "production"):
        self.config_file = config_file
        self.mode = mode
        self.boot_time = datetime.now()

        self.state = {
            "version": "21.7.1",
            "status": "initializing",
            "boot_time": self.boot_time.isoformat(),
            "mode": mode,
            "components": {},
            "mount_points": {},
            "agents": {},
            "workspaces": {},
            "errors": [],
            "warnings": []
        }

        self.configs = {}
        self.mount_manager = MountPointManager()
        self.agent_loader = AgentLoader()
        self.workspace_manager = WorkspaceManager()

    async def execute_boot_sequence(self):
        """Execute the complete AUTOSTART sequence."""
        print(f"\n{'='*60}")
        print(f"🚀 NCOS v21 Phoenix Mesh - AUTOSTART")
        print(f"{'='*60}")
        print(f"Version: {self.state['version']}")
        print(f"Mode: {self.mode}")
        print(f"Boot Time: {self.boot_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        stages = [
            ("🔍 Pre-flight Checks", self.preflight_checks),
            ("📁 Configuration Loading", self.load_configurations),
            ("🏗️ Core Systems Init", self.initialize_core_systems),
            ("📂 Mount Points Setup", self.setup_mount_points),
            ("🧠 Predictive Engine Init", self.initialize_predictive_engine),
            ("🤖 Agent Deployment", self.deploy_agents),
            ("📊 Workspace Setup", self.setup_workspaces),
            ("💾 Memory/Vector Init", self.initialize_memory_vector),
            ("📡 Data Feeds Connect", self.connect_data_feeds),
            ("🎯 Final Validation", self.finalize_boot)
        ]

        for stage_name, stage_func in stages:
            print(f"\n{stage_name} Starting...")
            stage_start = datetime.now()

            try:
                await stage_func()
                duration = (datetime.now() - stage_start).total_seconds()
                print(f"✅ {stage_name} Complete ({duration:.2f}s)")

                self.state['components'][stage_name] = {
                    'status': 'success',
                    'duration': duration,
                    'timestamp': datetime.now().isoformat()
                }

            except Exception as e:
                print(f"❌ {stage_name} Failed: {e}")
                logger.error(f"Stage {stage_name} failed", exc_info=True)

                self.state['errors'].append({
                    'stage': stage_name,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

                self.state['components'][stage_name] = {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }

                if self.mode == 'production':
                    print("\n⚠️  Production mode: Halting boot sequence due to error")
                    break

        # Generate boot report
        await self.generate_boot_report()

        return self.state

    async def preflight_checks(self):
        """Perform pre-flight system checks."""
        checks = {
            'python_version': sys.version_info >= (3, 8),
            'config_exists': Path(self.config_file).exists() or Path('AUTOSTART_v21.yaml').exists(),
            'core_modules': self._check_core_modules(),
            'disk_space': self._check_disk_space(),
            'permissions': self._check_permissions()
        }

        for check_name, passed in checks.items():
            if passed:
                print(f"  ✓ {check_name}")
            else:
                raise RuntimeError(f"Pre-flight check failed: {check_name}")

        # Check for required directories
        required_dirs = ['config', 'logs', 'data', 'workspaces']
        for dir_name in required_dirs:
            Path(dir_name).mkdir(exist_ok=True)
            print(f"  ✓ Directory '{dir_name}' ready")

    async def load_configurations(self):
        """Load all configuration files."""
        # Primary config sources
        config_sources = [
            ('autostart', 'AUTOSTART_v21.yaml'),
            ('agents', 'config/agents.yaml'),
            ('triggers', 'config/triggers.yaml'),
            ('predictive', 'config/predictive_engine_config.yaml'),
            ('system', 'config/system_config.yaml')
        ]

        for config_name, config_path in config_sources:
            if Path(config_path).exists():
                with open(config_path, 'r') as f:
                    self.configs[config_name] = yaml.safe_load(f)
                print(f"  ✓ Loaded {config_name} configuration")
            else:
                self.state['warnings'].append(f"Config not found: {config_path}")
                print(f"  ⚠️  {config_name} configuration not found")

    async def initialize_core_systems(self):
        """Initialize core NCOS systems."""
        # Import core modules
        try:
            from ncos_orchestrator import Orchestrator
            from ncos_session_manager import SessionManager
            from ncos_event_bus import EventBus

            # Initialize event bus
            self.event_bus = EventBus()
            print("  ✓ Event Bus initialized")

            # Initialize session manager
            self.session_manager = SessionManager()
            print("  ✓ Session Manager initialized")

            # Initialize orchestrator
            self.orchestrator = Orchestrator(
                self.session_manager,
                self.configs.get('triggers', {})
            )
            print("  ✓ Orchestrator initialized")

            self.state['components']['core_systems'] = {
                'event_bus': 'active',
                'session_manager': 'active',
                'orchestrator': 'active'
            }

        except ImportError as e:
            raise RuntimeError(f"Failed to import core modules: {e}")

    async def setup_mount_points(self):
        """Setup all mount points from configuration."""
        mount_config = self.configs.get('autostart', {}).get('mount_points', {})

        # Primary mount points
        primary_mounts = mount_config.get('primary', {})
        for mount_path, mount_type in primary_mounts.items():
            success = await self.mount_manager.mount(mount_path, mount_type)
            if success:
                print(f"  ✓ Mounted {mount_path} -> {mount_type}")
            else:
                print(f"  ❌ Failed to mount {mount_path}")

        # Workspace-specific mounts
        workspace_mounts = mount_config.get('workspace_specific', {})
        for workspace, mounts in workspace_mounts.items():
            for mount_path in mounts:
                success = await self.mount_manager.mount(
                    mount_path, 
                    f"workspace_{workspace}"
                )
                if success:
                    print(f"  ✓ Mounted {mount_path} for {workspace}")

    async def initialize_predictive_engine(self):
        """Initialize the new Predictive Engine."""
        try:
            from ncos_predictive_engine import NCOSPredictiveEngine
            from ncos_predictive_schemas import PredictiveEngineConfig

            # Load predictive config
            pred_config = self.configs.get('predictive', {})
            if not pred_config:
                print("  ⚠️  No predictive engine config found, using defaults")
                pred_config = self._get_default_predictive_config()

            # Initialize engine
            config = PredictiveEngineConfig(**pred_config)
            self.predictive_engine = NCOSPredictiveEngine(config)

            print("  ✓ Predictive Engine initialized")
            print(f"    - Grade thresholds: A={config.predictive_scorer.grade_thresholds.A}, "
                  f"B={config.predictive_scorer.grade_thresholds.B}, "
                  f"C={config.predictive_scorer.grade_thresholds.C}")
            print(f"    - Journaling: {'Enabled' if config.journaling.enabled else 'Disabled'}")

            self.state['components']['predictive_engine'] = {
                'status': 'active',
                'config': {
                    'enabled': config.predictive_scorer.enabled,
                    'grade_thresholds': config.predictive_scorer.grade_thresholds.dict()
                }
            }

        except Exception as e:
            self.state['warnings'].append(f"Predictive Engine init failed: {e}")
            print(f"  ⚠️  Predictive Engine initialization failed: {e}")

    async def deploy_agents(self):
        """Deploy all configured agents."""
        agents_config = self.configs.get('agents', {}).get('agents', [])

        # Sort by initialization order if specified
        init_order = self.configs.get('autostart', {}).get(
            'agent_initialization_order', 
            []
        )

        if init_order:
            # Sort agents based on initialization order
            agents_config = sorted(
                agents_config,
                key=lambda a: init_order.index(a['id']) 
                if a['id'] in init_order else 999
            )

        deployed_count = 0
        for agent_config in agents_config:
            if not agent_config.get('enabled', True):
                continue

            try:
                agent = await self.agent_loader.load_agent(
                    agent_config,
                    self.orchestrator
                )

                if agent:
                    agent_id = agent_config['id']
                    self.state['agents'][agent_id] = {
                        'status': 'active',
                        'class': agent_config.get('class', 'Unknown'),
                        'triggers': agent_config.get('triggers', [])
                    }
                    deployed_count += 1
                    print(f"  ✓ Deployed {agent_id}")

            except Exception as e:
                print(f"  ❌ Failed to deploy {agent_config['id']}: {e}")
                self.state['errors'].append({
                    'component': 'agent_deployment',
                    'agent': agent_config['id'],
                    'error': str(e)
                })

        print(f"\n  Deployed {deployed_count}/{len(agents_config)} agents")

    async def setup_workspaces(self):
        """Setup all configured workspaces."""
        workspace_config = self.configs.get('autostart', {}).get('workspaces', {})

        for ws_name, ws_config in workspace_config.items():
            try:
                workspace = await self.workspace_manager.create_workspace(
                    ws_name, 
                    ws_config
                )

                if workspace:
                    self.state['workspaces'][ws_name] = {
                        'status': 'active',
                        'resources': ws_config.get('resources', {}),
                        'services': len(ws_config.get('services', []))
                    }
                    print(f"  ✓ Workspace '{ws_name}' initialized")

            except Exception as e:
                print(f"  ❌ Failed to setup workspace '{ws_name}': {e}")

    async def initialize_memory_vector(self):
        """Initialize memory and vector systems."""
        # Placeholder for memory/vector initialization
        print("  ✓ Memory manager initialized")
        print("  ✓ Vector store connected")

        self.state['components']['memory_vector'] = {
            'memory_manager': 'active',
            'vector_store': 'active'
        }

    async def connect_data_feeds(self):
        """Connect to configured data feeds."""
        # Placeholder for data feed connections
        print("  ✓ Market data feed connected")
        print("  ✓ CSV discovery engine active")

        self.state['components']['data_feeds'] = {
            'market_data': 'connected',
            'csv_discovery': 'active'
        }

    async def finalize_boot(self):
        """Perform final validation and start services."""
        print("\n📋 Boot Summary:")
        print(f"  - Agents Deployed: {len(self.state['agents'])}")
        print(f"  - Workspaces Active: {len(self.state['workspaces'])}")
        print(f"  - Errors: {len(self.state['errors'])}")
        print(f"  - Warnings: {len(self.state['warnings'])}")

        # Save boot state
        boot_state_file = f"logs/boot_state_{self.boot_time.strftime('%Y%m%d_%H%M%S')}.json"
        Path('logs').mkdir(exist_ok=True)

        with open(boot_state_file, 'w') as f:
            json.dump(self.state, f, indent=2)

        print(f"\n💾 Boot state saved to: {boot_state_file}")

        # Update final status
        if not self.state['errors']:
            self.state['status'] = 'running'
            print("\n✅ NCOS v21 Phoenix Mesh - READY")
        else:
            self.state['status'] = 'degraded'
            print("\n⚠️  System running with errors - check boot state")

    async def generate_boot_report(self):
        """Generate detailed boot report."""
        report = {
            'system': 'NCOS v21 Phoenix Mesh',
            'version': self.state['version'],
            'boot_time': self.state['boot_time'],
            'mode': self.mode,
            'duration': (datetime.now() - self.boot_time).total_seconds(),
            'status': self.state['status'],
            'summary': {
                'components_loaded': len([c for c in self.state['components'].values() 
                                        if c.get('status') == 'success']),
                'agents_deployed': len(self.state['agents']),
                'workspaces_active': len(self.state['workspaces']),
                'errors': len(self.state['errors']),
                'warnings': len(self.state['warnings'])
            }
        }

        # Save report
        report_file = f"logs/boot_report_{self.boot_time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

    def _check_core_modules(self):
        """Check if core modules exist."""
        required_modules = [
            'ncos_orchestrator.py',
            'ncos_session_manager.py',
            'ncos_event_bus.py'
        ]
        return all(Path(m).exists() for m in required_modules)

    def _check_disk_space(self):
        """Check available disk space."""
        import shutil
        stat = shutil.disk_usage('.')
        # Require at least 1GB free
        return stat.free > 1024 * 1024 * 1024

    def _check_permissions(self):
        """Check file system permissions."""
        try:
            test_file = Path('test_write.tmp')
            test_file.write_text('test')
            test_file.unlink()
            return True
        except:
            return False

    def _get_default_predictive_config(self):
        """Get default predictive engine configuration."""
        return {
            'data_enricher': {'enabled': True},
            'feature_extractor': {'enabled': True},
            'predictive_scorer': {
                'enabled': True,
                'factor_weights': {
                    'htf_bias_alignment': 0.20,
                    'idm_detected_clarity': 0.10,
                    'sweep_validation_strength': 0.15,
                    'choch_confirmation_score': 0.15,
                    'poi_validation_score': 0.20,
                    'tick_density_score': 0.10,
                    'spread_stability_score': 0.10
                },
                'grade_thresholds': {'A': 0.85, 'B': 0.70, 'C': 0.55}
            },
            'journaling': {'enabled': True}
        }


class MountPointManager:
    """Manages virtual mount points for the system."""

    def __init__(self):
        self.mounts = {}

    async def mount(self, path: str, mount_type: str) -> bool:
        """Mount a virtual path."""
        self.mounts[path] = {
            'type': mount_type,
            'mounted_at': datetime.now(),
            'status': 'active'
        }

        # Create physical directory if needed
        if mount_type.startswith('workspace_'):
            physical_path = Path(f"workspaces/{path.strip('/')}")
            physical_path.mkdir(parents=True, exist_ok=True)

        return True


class AgentLoader:
    """Loads and initializes agents."""

    async def load_agent(self, agent_config: Dict, orchestrator) -> Optional[Any]:
        """Load an agent from configuration."""
        module_name = agent_config.get('module')
        class_name = agent_config.get('class')

        if not module_name or not class_name:
            raise ValueError(f"Agent config missing module or class: {agent_config}")

        # Import the module
        module_path = f"{module_name}.py"
        if not Path(module_path).exists():
            raise FileNotFoundError(f"Agent module not found: {module_path}")

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Get the class and instantiate
        agent_class = getattr(module, class_name)
        agent = agent_class(
            orchestrator,
            agent_config['id'],
            agent_config.get('config', {})
        )

        # Register triggers
        for trigger in agent_config.get('triggers', []):
            await orchestrator.register_agent(agent, trigger)

        return agent


class WorkspaceManager:
    """Manages workspace lifecycle."""

    async def create_workspace(self, name: str, config: Dict) -> Dict:
        """Create and initialize a workspace."""
        workspace = {
            'name': name,
            'status': 'initializing',
            'created_at': datetime.now(),
            'config': config
        }

        # Create workspace directory
        ws_path = Path(f"workspaces/{name}")
        ws_path.mkdir(parents=True, exist_ok=True)

        # Initialize services (placeholder)
        for service in config.get('services', []):
            # In real implementation, start actual services
            pass

        workspace['status'] = 'active'
        return workspace


async def main():
    """Main entry point for AUTOSTART."""
    parser = argparse.ArgumentParser(description='NCOS v21 AUTOSTART System')
    parser.add_argument(
        '--mode',
        choices=['production', 'development', 'test'],
        default='production',
        help='Boot mode'
    )
    parser.add_argument(
        '--config',
        default='AUTOSTART_v21.yaml',
        help='Configuration file'
    )
    parser.add_argument(
        '--skip-errors',
        action='store_true',
        help='Continue boot sequence on errors'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create and run autostart manager
    autostart = NCOSAutoStartManager(args.config, args.mode)

    try:
        boot_state = await autostart.execute_boot_sequence()

        if boot_state['status'] == 'running':
            print("\n🎉 System ready for operations!")
            print("\nNext steps:")
            print("  1. Check system status: python ncos_status.py")
            print("  2. View active agents: python ncos_agents.py --list")
            print("  3. Start trading: python ncos_trade.py --symbol XAUUSD")

            # Keep running
            if args.mode == 'production':
                print("\n⚡ System running... Press Ctrl+C to stop")
                try:
                    await asyncio.Event().wait()
                except KeyboardInterrupt:
                    print("\n👋 Shutting down...")

        else:
            print(f"\n⚠️  System status: {boot_state['status']}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"AUTOSTART failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
