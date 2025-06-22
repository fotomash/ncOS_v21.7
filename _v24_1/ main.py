#!/usr/bin/env python3
"""
NCOS v24 - Main System Entry Point
Initializes and runs the comprehensive multi-agent system.
"""

import asyncio
import signal
import sys
from pathlib import Path
from typing import Optional

# Ensure the source directory is in the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ncos.core.system import NCOSSystem
from ncos.utils.helpers import ConfigHelper
from loguru import logger

class NCOSServer:
    """Main server class to manage the NCOS system lifecycle."""

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/production.yaml"
        self.system: Optional[NCOSSystem] = None
        self.shutdown_event = asyncio.Event()

    async def start(self):
        """Loads configuration, initializes, and runs the NCOS system."""
        try:
            config = self._load_and_merge_configs()
            self._configure_logging(config.get("logging", {}))

            logger.info("Initializing NCOS v24...")
            self.system = NCOSSystem(config)

            self._setup_signal_handlers()

            await self.system.initialize()
            logger.info("NCOS system started successfully. Awaiting tasks...")

            await self.shutdown_event.wait()

        except Exception as e:
            logger.critical(f"Fatal error during startup: {e}", exc_info=True)
            raise
        finally:
            await self.stop()

    async def stop(self):
        """Gracefully shuts down the NCOS system."""
        if self.system:
            logger.info("Shutting down NCOS system...")
            await self.system.cleanup()
            logger.info("NCOS system has been shut down.")

    def _load_and_merge_configs(self) -> dict:
        """Loads base, environment-specific, and environment variable configs."""
        try:
            # Load base config
            base_config = ConfigHelper.load_from_file("config/base.yaml")
            
            # Load environment-specific config
            env = os.getenv("NCOS_ENV", "production")
            env_config_path = f"config/{env}.yaml"
            env_config = {}
            if Path(env_config_path).exists():
                env_config = ConfigHelper.load_from_file(env_config_path)

            # Merge configs (env-specific overrides base)
            config = ConfigHelper.merge_configs(base_config, env_config)
            
            logger.info(f"Configuration loaded for environment: '{env}'")
            return config
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def _configure_logging(self, log_config: dict):
        """Configures the logging system using Loguru."""
        logger.remove()  # Remove default handler
        log_level = log_config.get("level", "INFO").upper()
        
        # Console sink
        if log_config.get("enable_console", True):
            logger.add(sys.stderr, level=log_level, format=log_config.get("format"))

        # File sink
        if log_config.get("file_path"):
            logger.add(
                log_config["file_path"],
                level=log_level,
                rotation=log_config.get("max_file_size", "10 MB"),
                retention=log_config.get("backup_count", 5),
                enqueue=True, # Make file logging non-blocking
                backtrace=True,
                diagnose=True,
            )
        logger.info(f"Logging configured at level: {log_level}")
        
    def _setup_signal_handlers(self):
        """Sets up signal handlers for graceful shutdown."""
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, self.shutdown_event.set)
        logger.debug("Signal handlers for graceful shutdown have been set.")


async def main():
    """Main asynchronous entry point."""
    server = NCOSServer()
    try:
        await server.start()
    except asyncio.CancelledError:
        logger.info("Main task cancelled.")
    except Exception as e:
        logger.critical(f"NCOS server encountered a fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("NCOS shut down by user.")
        sys.exit(0)
