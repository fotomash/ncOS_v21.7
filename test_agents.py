#!/usr/bin/env python3
"""Test NCOS agent loading"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "agents"))

print("Testing agent imports...")
print("=" * 40)

agents_to_test = [
    "master_orchestrator",
    "vector_memory_boot",
    "parquet_ingestor",
    "dimensional_fold",
    "market_conditioner",
    "signal_processor",
    "strategy_evaluator",
    "position_manager",
    "risk_analyzer",
    "metrics_aggregator",
    "smc_router",
    "maz2_executor",
    "tmc_executor"
]

success_count = 0
for agent in agents_to_test:
    try:
        module = __import__(agent)
        print(f"✓ {agent}")
        success_count += 1
    except Exception as e:
        print(f"✗ {agent}: {str(e)}")

print("=" * 40)
print(f"Successfully imported: {success_count}/{len(agents_to_test)} agents")
