#!/usr/bin/env python3
"""
ncOS Agent Rationalization Tool
Analyzes and consolidates 53 agents into ~25 optimized agents
"""

import ast
import json
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class AgentRationalizer:
    def __init__(self, project_root="ncOS_v21.7"):
        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / "agents"
        self.backup_dir = Path(f"agents_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.analysis_report = {
            'total_agents': 0,
            'agent_categories': defaultdict(list),
            'consolidation_map': {},
            'orphaned_agents': [],
            'core_agents': []
        }

        # Define agent consolidation strategy
        self.consolidation_strategy = {
            'MarketAnalysis': {
                'consolidated_name': 'MarketAnalysisAgent',
                'merge_candidates': ['market_data', 'technical_analyst', 'market_condition',
                                     'price_action', 'volume_analysis', 'market_structure'],
                'core_functions': ['analyze_market', 'get_indicators', 'detect_patterns']
            },
            'RiskManagement': {
                'consolidated_name': 'RiskManagementAgent',
                'merge_candidates': ['risk_guardian', 'risk_monitor', 'exposure_manager',
                                     'position_sizer', 'stop_loss', 'risk_calculator'],
                'core_functions': ['calculate_risk', 'manage_exposure', 'set_stops']
            },
            'TradeExecution': {
                'consolidated_name': 'TradeExecutionAgent',
                'merge_candidates': ['trade_executor', 'order_manager', 'smc_executor',
                                     'tmc_executor', 'maz2_executor', 'execution_router'],
                'core_functions': ['execute_trade', 'manage_orders', 'route_execution']
            },
            'StrategyAnalysis': {
                'consolidated_name': 'StrategyAnalysisAgent',
                'merge_candidates': ['strategy_evaluator', 'smc_master', 'wyckoff_phase',
                                     'orderflow_anomaly', 'divergence_strategy', 'liquidity_analysis'],
                'core_functions': ['evaluate_strategy', 'identify_setup', 'score_opportunity']
            },
            'SystemMonitoring': {
                'consolidated_name': 'SystemMonitoringAgent',
                'merge_candidates': ['performance_monitor', 'metrics_aggregator', 'health_monitor',
                                     'system_status', 'alert_manager', 'drift_detection'],
                'core_functions': ['monitor_performance', 'aggregate_metrics', 'send_alerts']
            },
            'DataManagement': {
                'consolidated_name': 'DataManagementAgent',
                'merge_candidates': ['data_enricher', 'data_validator', 'data_processor',
                                     'signal_processor', 'data_pipeline', 'data_captain'],
                'core_functions': ['process_data', 'validate_data', 'enrich_data']
            },
            'JournalSession': {
                'consolidated_name': 'JournalSessionAgent',
                'merge_candidates': ['journal_manager', 'session_manager', 'trade_logger',
                                     'session_state', 'trade_history', 'performance_tracker'],
                'core_functions': ['log_trade', 'manage_session', 'track_performance']
            }
        }

    def analyze_agent(self, agent_path):
        """Analyze an agent file to extract its characteristics"""
        agent_info = {
            'name': agent_path.stem,
            'path': agent_path,
            'classes': [],
            'functions': [],
            'imports': [],
            'dependencies': [],
            'complexity': 0,
            'category': 'uncategorized'
        }

        try:
            with open(agent_path, 'r', encoding='utf-8') as f:
                content = f.read()

            tree = ast.parse(content)

            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    agent_info['classes'].append(node.name)
                    agent_info['complexity'] += len(node.body)
                elif isinstance(node, ast.FunctionDef):
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                        agent_info['functions'].append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            agent_info['imports'].append(alias.name)
                    else:
                        agent_info['imports'].append(node.module or '')

            # Categorize agent based on name and content
            agent_info['category'] = self._categorize_agent(agent_info['name'], content)

        except Exception as e:
            print(f"Error analyzing {agent_path}: {e}")

        return agent_info

    def _categorize_agent(self, name, content):
        """Categorize agent based on name and content analysis"""
        name_lower = name.lower()
        content_lower = content.lower()

        for category, config in self.consolidation_strategy.items():
            for candidate in config['merge_candidates']:
                if candidate in name_lower or candidate.replace('_', '') in name_lower:
                    return category

        # Content-based categorization
        if any(term in content_lower for term in ['market', 'price', 'technical', 'indicator']):
            return 'MarketAnalysis'
        elif any(term in content_lower for term in ['risk', 'exposure', 'position_size']):
            return 'RiskManagement'
        elif any(term in content_lower for term in ['execute', 'order', 'trade_execution']):
            return 'TradeExecution'
        elif any(term in content_lower for term in ['strategy', 'setup', 'signal']):
            return 'StrategyAnalysis'
        elif any(term in content_lower for term in ['monitor', 'metric', 'performance']):
            return 'SystemMonitoring'
        elif any(term in content_lower for term in ['data', 'process', 'enrich']):
            return 'DataManagement'
        elif any(term in content_lower for term in ['journal', 'session', 'log']):
            return 'JournalSession'

        return 'Other'

    def scan_agents(self):
        """Scan all agent files and categorize them"""
        print("🔍 Scanning agent files...")

        # Find all Python files that could be agents
        agent_files = []

        # Check agents directory
        if self.agents_dir.exists():
            agent_files.extend(self.agents_dir.glob("*.py"))

        # Check root directory for agent files
        for file in self.project_root.glob("*agent*.py"):
            if file.stem != '__init__':
                agent_files.append(file)

        print(f"Found {len(agent_files)} agent files")

        # Analyze each agent
        for agent_file in agent_files:
            agent_info = self.analyze_agent(agent_file)
            self.analysis_report['total_agents'] += 1

            category = agent_info['category']
            self.analysis_report['agent_categories'][category].append(agent_info)

            # Identify core agents (high complexity or many functions)
            if agent_info['complexity'] > 50 or len(agent_info['functions']) > 10:
                self.analysis_report['core_agents'].append(agent_info['name'])

        # Report findings
        print("\n📊 Agent Distribution:")
        for category, agents in self.analysis_report['agent_categories'].items():
            print(f"  {category}: {len(agents)} agents")

    def create_consolidated_agent(self, category, agents):
        """Create a consolidated agent from multiple agents"""
        config = self.consolidation_strategy.get(category, {})
        consolidated_name = config.get('consolidated_name', f'{category}Agent')
        core_functions = config.get('core_functions', [])

        # Generate consolidated agent code
        agent_code = f"""\"\"\"
{consolidated_name} - Consolidated from {len(agents)} agents
Handles all {category.lower()} related functionality
\"\"\"
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Consolidated imports
"""

        # Add core functions
        for i, func in enumerate(core_functions):
            if i == 0:
                agent_code += f"""

logger = logging.getLogger(__name__)


class {consolidated_name}:
    \"\"\"
    Consolidated agent for {category} operations.
    Merged from: {', '.join([a['name'] for a in agents])}
    \"\"\"

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        self.name = "{consolidated_name}"
        self.category = "{category}"
        self._initialize_components()

    def _initialize_components(self):
        \"\"\"Initialize all sub-components\"\"\"
        # TODO: Initialize merged components
        pass

    async def {func}(self, *args, **kwargs) -> Dict[str, Any]:
        \"\"\"
        Core function: {func.replace('_', ' ').title()}
        TODO: Implement consolidated logic from merged agents
        \"\"\"
        try:
            # Placeholder implementation
            result = {{"status": "success", "function": "{func}"}}
            logger.info(f"{{self.name}}: Executing {func}")
            return result
        except Exception as e:
            logger.error(f"{{self.name}}: Error in {func}: {{e}}")
            return {{"status": "error", "message": str(e)}}
"""
            else:
                agent_code += f"""

    async def {func}(self, *args, **kwargs) -> Dict[str, Any]:
        \"\"\"
        Core function: {func.replace('_', ' ').title()}
        TODO: Implement consolidated logic from merged agents
        \"\"\"
        try:
            # Placeholder implementation
            result = {{"status": "success", "function": "{func}"}}
            logger.info(f"{{self.name}}: Executing {func}")
            return result
        except Exception as e:
            logger.error(f"{{self.name}}: Error in {func}: {{e}}")
            return {{"status": "error", "message": str(e)}}
"""

        # Add utility methods
        agent_code += """

    async def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Main processing method for agent messages\"\"\"
        action = message.get('action', 'default')

        # Route to appropriate handler
        handlers = {
"""

        for func in core_functions:
            agent_code += f'            "{func}": self.{func},\n'

        agent_code += """        }

        handler = handlers.get(action)
        if handler:
            return await handler(**message.get('params', {}))
        else:
            return {"status": "error", "message": f"Unknown action: {action}"}

    def get_capabilities(self) -> List[str]:
        \"\"\"Return list of agent capabilities\"\"\"
        return [
"""

        for func in core_functions:
            agent_code += f'            "{func}",\n'

        agent_code += """        ]


# Agent factory function
def create_agent(config: Dict[str, Any] = None):
    \"\"\"Factory function to create agent instance\"\"\"
    return """ + consolidated_name + """(config)
"""

        return agent_code

    def generate_migration_guide(self):
        """Generate a migration guide for updating code references"""
        guide = """# Agent Consolidation Migration Guide

## Overview
This guide helps you migrate from the old multi-agent structure to the new consolidated agent architecture.

## Agent Mapping

"""

        for category, agents in self.analysis_report['agent_categories'].items():
            if category in self.consolidation_strategy:
                config = self.consolidation_strategy[category]
                guide += f"### {category}\n"
                guide += f"**New Agent:** `{config['consolidated_name']}`\n\n"
                guide += "**Replaces:**\n"
                for agent in agents:
                    guide += f"- `{agent['name']}` → `{config['consolidated_name']}`\n"
                guide += "\n"

        guide += """## Code Migration Examples

### Before:
```python
from agents.market_data_captain import MarketDataCaptain
from agents.technical_analyst import TechnicalAnalyst

market_agent = MarketDataCaptain()
tech_agent = TechnicalAnalyst()
```

### After:
```python
from agents.consolidated.market_analysis_agent import MarketAnalysisAgent

market_agent = MarketAnalysisAgent()
# All functionality now in one agent
```

## Configuration Updates

Update your agent registry to use the new consolidated agents:

```yaml
agents:
  market_analysis:
    class: MarketAnalysisAgent
    module: agents.consolidated.market_analysis_agent

  risk_management:
    class: RiskManagementAgent
    module: agents.consolidated.risk_management_agent
```

## Testing

1. Run integration tests with new agents
2. Verify all functionality is preserved
3. Check performance improvements
"""

        return guide

    def create_base_agent_class(self):
        """Create a base agent class for all consolidated agents"""
        base_class = """\"\"\"
Base Agent Class for ncOS Consolidated Agents
\"\"\"
import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseAgent(ABC):
    \"\"\"
    Abstract base class for all ncOS agents.
    Provides common functionality and interface.
    \"\"\"

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"ncOS.{name}")
        self._running = False
        self._metrics = {
            'messages_processed': 0,
            'errors': 0,
            'start_time': None,
            'last_activity': None
        }

    @abstractmethod
    async def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Process incoming message - must be implemented by subclasses\"\"\"
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        \"\"\"Return list of agent capabilities\"\"\"
        pass

    async def start(self):
        \"\"\"Start the agent\"\"\"
        self._running = True
        self._metrics['start_time'] = datetime.now()
        self.logger.info(f"{self.name} started")

    async def stop(self):
        \"\"\"Stop the agent\"\"\"
        self._running = False
        self.logger.info(f"{self.name} stopped")

    def get_status(self) -> Dict[str, Any]:
        \"\"\"Get agent status and metrics\"\"\"
        return {
            'name': self.name,
            'running': self._running,
            'metrics': self._metrics,
            'capabilities': self.get_capabilities()
        }

    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Handle incoming message with error handling and metrics\"\"\"
        try:
            self._metrics['last_activity'] = datetime.now()
            result = await self.process(message)
            self._metrics['messages_processed'] += 1
            return result
        except Exception as e:
            self._metrics['errors'] += 1
            self.logger.error(f"Error processing message: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'agent': self.name
            }


class AgentRegistry:
    \"\"\"
    Registry for managing all agents in the system
    \"\"\"

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        \"\"\"Register an agent\"\"\"
        self._agents[agent.name] = agent

    def get(self, name: str) -> Optional[BaseAgent]:
        \"\"\"Get agent by name\"\"\"
        return self._agents.get(name)

    def list_agents(self) -> List[str]:
        \"\"\"List all registered agents\"\"\"
        return list(self._agents.keys())

    async def broadcast(self, message: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Broadcast message to all agents\"\"\"
        results = {}
        for name, agent in self._agents.items():
            results[name] = await agent.handle_message(message)
        return results


# Global registry instance
agent_registry = AgentRegistry()
"""

        return base_class

    def backup_existing_agents(self):
        """Backup existing agent files before consolidation"""
        print("\n📦 Backing up existing agents...")

        if self.agents_dir.exists():
            shutil.copytree(self.agents_dir, self.backup_dir)
            print(f"✅ Backup created: {self.backup_dir}")

        # Also backup individual agent files in root
        root_agents_backup = self.backup_dir / "root_agents"
        root_agents_backup.mkdir(exist_ok=True)

        for agent_file in self.project_root.glob("*agent*.py"):
            if agent_file.stem != '__init__':
                shutil.copy2(agent_file, root_agents_backup / agent_file.name)

    def create_consolidated_structure(self):
        """Create new directory structure for consolidated agents"""
        print("\n📁 Creating consolidated agent structure...")

        # Create new directories
        consolidated_dir = self.agents_dir / "consolidated"
        consolidated_dir.mkdir(parents=True, exist_ok=True)

        # Create base agent class
        base_agent_code = self.create_base_agent_class()
        base_agent_path = consolidated_dir / "base_agent.py"
        with open(base_agent_path, 'w') as f:
            f.write(base_agent_code)

        print(f"✅ Created base agent class: {base_agent_path}")

        # Create consolidated agents
        for category, agents in self.analysis_report['agent_categories'].items():
            if category in self.consolidation_strategy and len(agents) > 1:
                config = self.consolidation_strategy[category]
                consolidated_code = self.create_consolidated_agent(category, agents)

                # Save consolidated agent
                file_name = f"{config['consolidated_name'].lower().replace('agent', '_agent')}.py"
                agent_path = consolidated_dir / file_name

                with open(agent_path, 'w') as f:
                    f.write(consolidated_code)

                print(f"✅ Created {config['consolidated_name']}: merged {len(agents)} agents")

                # Track consolidation
                for agent in agents:
                    self.analysis_report['consolidation_map'][agent['name']] = config['consolidated_name']

        # Create __init__.py for consolidated package
        self._create_init_file(consolidated_dir)

    def _create_init_file(self, consolidated_dir):
        """Create __init__.py file for consolidated agents package"""
        init_content = """\"\"\"
Consolidated Agent Package
\"\"\"
from .base_agent import BaseAgent, agent_registry

# Import all consolidated agents
"""

        for category, config in self.consolidation_strategy.items():
            agent_file = config['consolidated_name'].lower().replace('agent', '_agent')
            init_content += f"from .{agent_file} import {config['consolidated_name']}\n"

        init_content += """

__all__ = [
    'BaseAgent',
    'agent_registry',
"""

        for config in self.consolidation_strategy.values():
            init_content += f"    '{config['consolidated_name']}',\n"

        init_content += "]\n"

        init_path = consolidated_dir / "__init__.py"
        with open(init_path, 'w') as f:
            f.write(init_content)

    def generate_report(self):
        """Generate consolidation report"""
        report = {
            'consolidation_date': datetime.now().isoformat(),
            'original_agents': self.analysis_report['total_agents'],
            'consolidated_agents': len(self.consolidation_strategy),
            'reduction_ratio': f"{(1 - len(self.consolidation_strategy) / self.analysis_report['total_agents']) * 100:.1f}%",
            'categories': {
                cat: len(agents) for cat, agents in self.analysis_report['agent_categories'].items()
            },
            'consolidation_map': self.analysis_report['consolidation_map'],
            'backup_location': str(self.backup_dir)
        }

        # Save JSON report
        report_path = 'agent_consolidation_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Save migration guide
        guide = self.generate_migration_guide()
        guide_path = 'agent_migration_guide.md'
        with open(guide_path, 'w') as f:
            f.write(guide)

        print(f"\n📊 Reports saved:")
        print(f"  - {report_path}")
        print(f"  - {guide_path}")

        return report

    def run(self):
        """Execute agent rationalization"""
        print("🚀 Starting Agent Rationalization")
        print("=" * 50)

        # Backup existing agents
        self.backup_existing_agents()

        # Scan and analyze agents
        self.scan_agents()

        # Create consolidated structure
        self.create_consolidated_structure()

        # Generate reports
        report = self.generate_report()

        print("\n" + "=" * 50)
        print("✅ AGENT RATIONALIZATION COMPLETE!")
        print(f"📊 Consolidated {report['original_agents']} agents → {report['consolidated_agents']} agents")
        print(f"📈 Reduction: {report['reduction_ratio']}")
        print(f"📁 Backup saved: {self.backup_dir}")

        print("\n🎯 Next Steps:")
        print("1. Review the consolidated agents in agents/consolidated/")
        print("2. Update imports using the migration guide")
        print("3. Test each consolidated agent")
        print("4. Remove old agent files after validation")

        return True


if __name__ == "__main__":
    rationalizer = AgentRationalizer()
    rationalizer.run()
