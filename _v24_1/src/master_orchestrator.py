"""
Master Orchestrator for NCOS v11.5 Phoenix-Mesh

This module implements the core orchestration logic for the Neural Agent Mesh,
managing agent lifecycle, token budget, and execution flow.
"""

import logging
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Set

import yaml
from pydantic import ValidationError

from .session_state import SessionState
from .kernel import NeuralMeshKernel
from .core import AgentProfile, Message, TokenBudget, SystemConfig
from .utils.vector_client import VectorClient
from .utils.memory_manager import MemoryManager
from .budget import TokenBudgetManager

logger = logging.getLogger(__name__)


class MasterOrchestrator:
    """
    Master Orchestrator for NCOS v11.5 Phoenix-Mesh

    The orchestrator is responsible for:
    1. Loading and validating the system configuration
    2. Initializing the Neural Mesh Kernel
    3. Loading and initializing agents
    4. Managing the token budget
    5. Orchestrating the execution flow
    6. Handling errors and recovery
    """

    def __init__(self, config_path: str, workdir: Path):
        """
        Initialize the Master Orchestrator.

        Args:
            config_path: Path to the main configuration file
            workdir: Working directory for the system
        """
        self.config_path = config_path
        self.workdir = workdir
        self.session_state = None
        self.kernel = None
        self.config = None
        self.token_budget_manager = None
        self.memory_manager = None
        self.vector_client = None
        self.agents = {}
        self.running = False
        self.initialized = False

    def initialize(self) -> None:
        """Initialize the system components."""
        logger.info("Initializing Master Orchestrator")

        # Load and validate configuration
        self._load_config()

        # Initialize token budget
        self.token_budget_manager = TokenBudgetManager(
            total_budget=self.config.token_budget.total,
            reserve_percentage=self.config.token_budget.reserve_percentage
        )

        # Initialize session state
        self.session_state = SessionState(
            session_id=self.config.session_id or f"session_{int(time.time())}",
            token_budget=self.token_budget_manager.get_budget(),
            config=self.config
        )

        # Initialize memory systems
        self._initialize_memory()

        # Initialize Neural Mesh Kernel
        self.kernel = NeuralMeshKernel(
            session_state=self.session_state,
            token_budget_manager=self.token_budget_manager,
            memory_manager=self.memory_manager,
            config=self.config
        )

        # Load agents
        self._load_agents()

        self.initialized = True
        logger.info("Master Orchestrator initialization complete")

    def _load_config(self) -> None:
        """Load and validate the system configuration."""
        logger.info(f"Loading configuration from: {self.config_path}")

        try:
            with open(self.config_path, "r") as f:
                config_data = yaml.safe_load(f)

            self.config = SystemConfig(**config_data)
            logger.info(f"Configuration loaded successfully: {self.config.system_name} v{self.config.system_version}")

        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            raise
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            raise

    def _initialize_memory(self) -> None:
        """Initialize memory systems."""
        logger.info("Initializing memory systems")

        # Initialize vector client
        self.vector_client = VectorClient(
            vector_db_type=self.config.memory.vector_db_type,
            connection_string=self.config.memory.connection_string,
            dimension=self.config.memory.vector_dimension
        )

        # Initialize memory manager
        self.memory_manager = MemoryManager(
            vector_client=self.vector_client,
            session_id=self.session_state.session_id,
            config=self.config.memory
        )

    def _load_agents(self) -> None:
        """Load and initialize agents from profiles."""
        logger.info("Loading agent profiles")

        agent_profiles_dir = Path(self.config.agent_profiles_dir)

        # Load each agent profile and initialize the agent
        for agent_config in self.config.agents:
            try:
                profile_path = agent_profiles_dir / f"{agent_config.profile_path}"

                with open(profile_path, "r") as f:
                    profile_data = yaml.safe_load(f)

                # Create agent profile
                profile = AgentProfile(**profile_data)

                # Register agent with kernel
                self.kernel.register_agent(profile)
                logger.info(f"Loaded agent: {profile.name} ({profile.id})")

            except FileNotFoundError:
                logger.error(f"Agent profile not found: {profile_path}")
                continue
            except ValidationError as e:
                logger.error(f"Agent profile validation error: {e}")
                continue
            except Exception as e:
                logger.error(f"Error loading agent: {e}")
                continue

    def run(self) -> None:
        """Run the system main loop."""
        if not self.initialized:
            logger.error("Cannot run: system not initialized")
            return

        logger.info("Starting Master Orchestrator main loop")
        self.running = True

        try:
            # Main execution loop
            while self.running:
                self._execute_cycle()

                # Check system health
                if not self._check_health():
                    logger.warning("System health check failed, attempting recovery")
                    self._attempt_recovery()

                # Throttle execution if needed
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            self.shutdown()

    def _execute_cycle(self) -> None:
        """Execute a single orchestration cycle."""
        # Get next action from kernel
        action = self.kernel.get_next_action()

        if action:
            # Execute the action
            result = self.kernel.execute_action(action)

            # Process the result
            self.kernel.process_result(action, result)

        # Create snapshot if needed
        self._create_snapshot_if_needed()

    def _check_health(self) -> bool:
        """Check system health."""
        # Check token budget
        if self.token_budget_manager.is_budget_critical():
            logger.warning("Token budget is critical")
            return False

        # Check agent health
        for agent_id, agent_state in self.kernel.get_agent_states().items():
            if not agent_state.healthy:
                logger.warning(f"Agent {agent_id} is unhealthy")
                return False

        return True

    def _attempt_recovery(self) -> None:
        """Attempt system recovery."""
        logger.info("Attempting system recovery")

        # Try to restore from latest snapshot
        latest_snapshot = self.memory_manager.get_latest_snapshot()
        if latest_snapshot:
            logger.info(f"Restoring from snapshot: {latest_snapshot.id}")
            self.session_state = latest_snapshot.session_state
            self.token_budget_manager.reset(self.session_state.token_budget)

            # Reinitialize kernel with restored state
            self.kernel = NeuralMeshKernel(
                session_state=self.session_state,
                token_budget_manager=self.token_budget_manager,
                memory_manager=self.memory_manager,
                config=self.config
            )

            # Reload agents
            self._load_agents()
        else:
            logger.warning("No snapshot available for recovery")

    def _create_snapshot_if_needed(self) -> None:
        """Create a session snapshot if needed."""
        # Check if it's time to create a snapshot
        current_time = time.time()
        last_snapshot_time = self.session_state.last_snapshot_time or 0

        if (current_time - last_snapshot_time) > self.config.snapshot_interval_seconds:
            logger.info("Creating session snapshot")

            # Create snapshot
            snapshot_id = self.memory_manager.create_snapshot(self.session_state)

            # Update last snapshot time
            self.session_state.last_snapshot_time = current_time

            logger.info(f"Snapshot created: {snapshot_id}")

    def shutdown(self) -> None:
        """Shut down the system gracefully."""
        logger.info("Shutting down Master Orchestrator")

        self.running = False

        # Create final snapshot
        if self.memory_manager:
            logger.info("Creating final session snapshot")
            self.memory_manager.create_snapshot(self.session_state)

        # Shutdown kernel
        if self.kernel:
            self.kernel.shutdown()

        # Close vector client
        if self.vector_client:
            self.vector_client.close()

        logger.info("Master Orchestrator shutdown complete")
