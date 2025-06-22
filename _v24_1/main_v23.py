#!/usr/bin/env python
"""
NCOS v11.5 Phoenix-Mesh Main Entry Point
"""

import os
import sys
import argparse
import logging
from pathlib import Path

from src.master_orchestrator import MasterOrchestrator
from src.logger import setup_logging

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="NCOS v11.5 Phoenix-Mesh")
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/phoenix.yaml",
        help="Path to the main configuration file"
    )
    parser.add_argument(
        "--log-level", a
        type=str, 
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Logging level"
    )
    parser.add_argument(
        "--workdir", 
        type=str, 
        default="./workspace",
        help="Working directory for the system"
    )
    return parser.parse_args()

def main():
    """Main entry point for the NCOS Phoenix system."""
    args = parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Ensure the working directory exists
    workdir = Path(args.workdir)
    workdir.mkdir(exist_ok=True, parents=True)
    
    logger.info(f"Starting NCOS v11.5 Phoenix-Mesh with config: {args.config}")
    logger.info(f"Working directory: {workdir}")
    
    try:
        # Initialize the Master Orchestrator
        orchestrator = MasterOrchestrator(
            config_path=args.config,
            workdir=workdir
        )
        
        # Start the system
        orchestrator.initialize()
        orchestrator.run()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down gracefully...")
        if 'orchestrator' in locals():
            orchestrator.shutdown()
    except Exception as e:
        logger.error(f"Error in main execution: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("NCOS v11.5 Phoenix-Mesh shutdown complete")

if __name__ == "__main__":
    main()
