#!/usr/bin/env python3
"""
NCOS v21.7.1 Enhanced Complete System Launch Script
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from ncos_v21_7_1_enhanced_master_orchestrator import NCOSEnhancedMasterOrchestrator

async def launch_ncos_enhanced_complete(config_path=None):
    """Launch NCOS v21.7.1 Enhanced Complete System"""
    print("🚀 LAUNCHING NCOS v21.7.1 ENHANCED COMPLETE SYSTEM")
    print("=" * 60)

    try:
        # Initialize orchestrator
        orchestrator = NCOSEnhancedMasterOrchestrator(config_path)

        # Initialize complete system
        await orchestrator.initialize_complete_system()

        # Display system status
        status = orchestrator.get_complete_system_status()
        print("\n✅ SYSTEM READY!")
        print(f"   Session ID: {status['system']['session_id']}")
        print(f"   Version: {status['system']['version']}")
        print(f"   Active Agents: {status['system']['active_agents']}")
        print(f"   Trading Features: {len([f for f in status['capabilities'].values() if f])}")

        # Generate initial menu
        menu = orchestrator.generate_complete_enhanced_menu()
        print("\n🎛️ ENHANCED TRADING SYSTEM READY")
        print(f"   {menu['title']}")
        print(f"   Categories: {len(menu['categories'])}")

        return orchestrator

    except Exception as e:
        print(f"❌ LAUNCH FAILED: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Launch NCOS v21.7.1 Enhanced Complete System")
    parser.add_argument("--config", help="Configuration file path")
    parser.add_argument("--mode", default="complete", help="Launch mode")

    args = parser.parse_args()

    # Launch system
    orchestrator = asyncio.run(launch_ncos_enhanced_complete(args.config))

    print("\n🎯 NCOS v21.7.1 Enhanced Complete System is now running!")
    print("   Use the orchestrator object to interact with the system")

    return orchestrator

if __name__ == "__main__":
    main()
