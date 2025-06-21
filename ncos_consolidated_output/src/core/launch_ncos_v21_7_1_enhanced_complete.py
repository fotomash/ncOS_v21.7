#!/usr/bin/env python3
"""
NCOS v21.7.1 Enhanced Complete System Launch Script
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

from ncos_v21_7_1_enhanced_master_orchestrator import NCOSEnhancedMasterOrchestrator


async def launch_ncos_enhanced_complete(config_path=None):
    """Launch NCOS v21.7.1 Enhanced Complete System"""
    logger.info("🚀 LAUNCHING NCOS v21.7.1 ENHANCED COMPLETE SYSTEM")
    logger.info("=" * 60)

    try:
        # Initialize orchestrator
        orchestrator = NCOSEnhancedMasterOrchestrator(config_path)

        # Initialize complete system
        await orchestrator.initialize_complete_system()

        # Display system status
        status = orchestrator.get_complete_system_status()
        logger.info("\n✅ SYSTEM READY!")
        logger.info("   Session ID: %s", status['system']['session_id'])
        logger.info("   Version: %s", status['system']['version'])
        logger.info("   Active Agents: %s", status['system']['active_agents'])
        logger.info(
            "   Trading Features: %s",
            len([f for f in status['capabilities'].values() if f]),
        )

        # Generate initial menu
        menu = orchestrator.generate_complete_enhanced_menu()
        logger.info("\n🎛️ ENHANCED TRADING SYSTEM READY")
        logger.info("   %s", menu['title'])
        logger.info("   Categories: %s", len(menu['categories']))

        return orchestrator

    except Exception as e:
        logger.error("❌ LAUNCH FAILED: %s", e)
        raise


def main():
    parser = argparse.ArgumentParser(description="Launch NCOS v21.7.1 Enhanced Complete System")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--mode", default="complete", help="Launch mode")

    args = parser.parse_args()

    # Launch system
    orchestrator = asyncio.run(launch_ncos_enhanced_complete(args.config))

    logger.info("\n🎯 NCOS v21.7.1 Enhanced Complete System is now running!")
    logger.info("   Use the orchestrator object to interact with the system")

    return orchestrator


if __name__ == "__main__":
    main()
