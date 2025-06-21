#!/usr/bin/env python3
# main.py - Main execution script for NCOS v21 Phoenix Mesh

import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path

from orchestrators import create_orchestrator
from phoenix_session import create_phoenix_integration
from schemas.unified_schemas import SessionConfig

class NCOSPhoenixMesh:
    """Main application class for NCOS v21 Phoenix Mesh"""

    def __init__(self, config_path: str = "config/workspace_config.yaml"):
        print("🚀 Initializing NCOS v21 Phoenix Mesh...")
        self.orchestrator = create_orchestrator(config_path)
        self.phoenix = create_phoenix_integration()
        self.active_session = None

    async def start_session(self, session_name: str = None) -> str:
        """Start a new analysis session"""
        session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session_config = SessionConfig(
            session_id=session_name,
            token_budget=4096,
            agents=["data_ingestor", "strategy_agent", "viz_agent", "memory_agent"],
            strategies=["wyckoff", "smc"],
            memory_config={
                "token_budget": 4096,
                "compression_enabled": True,
                "vector_dimensions": 768,
                "retention_hours": 24
            }
        )

        self.active_session = self.orchestrator.create_session(session_config)
        print(f"✅ Started session: {self.active_session}")
        return self.active_session

    async def analyze_data(self, data_source: str, data_path: str = None):
        """Analyze market data"""
        if not self.active_session:
            await self.start_session()

        print(f"\n📊 Analyzing data from {data_source}...")
        results = await self.orchestrator.process_data(
            self.active_session,
            data_source,
            data_path
        )

        # Display results
        self._display_results(results)

        return results

    def _display_results(self, results: dict):
        """Display analysis results"""
        print("\n" + "=" * 60)
        print("📈 Analysis Results")
        print("=" * 60)

        # Data ingestion status
        if "ingestion" in results["stages"]:
            ing = results["stages"]["ingestion"]
            print(f"\n✅ Data Ingestion: {ing['status']}")

        # Strategy results
        if "strategies" in results["stages"]:
            print("\n📊 Strategy Analysis:")
            for strategy, result in results["stages"]["strategies"].items():
                if result["status"] == "success":
                    analysis = result["result"]
                    print(f"\n  {strategy.upper()}:")

                    if hasattr(analysis, 'phase'):
                        print(f"    Phase: {analysis.phase.value}")
                        print(f"    Confidence: {analysis.confidence:.2%}")
                        print(f"    Events: {', '.join(analysis.events)}")
                    elif hasattr(analysis, 'bias'):
                        print(f"    Bias: {analysis.bias}")
                        print(f"    Confidence: {analysis.confidence:.2%}")

        # Signal
        if "signal" in results["stages"]:
            signal = results["stages"]["signal"]
            print(f"\n🎯 Trading Signal: {signal['signal'].upper()}")
            print(f"   Confidence: {signal['confidence']:.2%}")

        # Visualization
        if "visualization" in results["stages"]:
            viz = results["stages"]["visualization"]
            print(f"\n📊 Chart saved to: {viz['chart']}")

        print("\n" + "=" * 60)

    async def optimize_system(self):
        """Run system optimization"""
        print("\n🔧 Running system optimization...")
        opt_results = self.orchestrator.optimize_system()

        print("\nOptimization Results:")
        if "memory" in opt_results["optimizations"]:
            mem_opt = opt_results["optimizations"]["memory"]
            print(f"  Memory: Freed {mem_opt['tokens_freed']} tokens")
            print(f"  Removed {mem_opt['removed_contexts']} old contexts")

        if "memory_stats" in opt_results:
            stats = opt_results["memory_stats"]
            print(f"\nMemory Stats:")
            print(f"  Total contexts: {stats['total_contexts']}")
            print(f"  Token usage: {stats['usage_percentage']:.1f}%")

    def shutdown(self):
        """Shutdown the system"""
        print("\n🛑 Shutting down NCOS Phoenix Mesh...")
        self.orchestrator.shutdown()
        print("✅ Shutdown complete")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="NCOS v21 Phoenix Mesh")
    parser.add_argument("--analyze", type=str, help="Analyze data from file")
    parser.add_argument("--source", type=str, default="csv", help="Data source type")
    parser.add_argument("--optimize", action="store_true", help="Run optimization")
    parser.add_argument("--test", action="store_true", help="Run tests")

    args = parser.parse_args()

    if args.test:
        # Run tests
        import test_phoenix
        test_phoenix.run_integration_tests()
        return

    # Initialize NCOS
    ncos = NCOSPhoenixMesh()

    try:
        # Start session
        await ncos.start_session()

        # Analyze data if provided
        if args.analyze:
            await ncos.analyze_data(args.source, args.analyze)
        else:
            # Demo analysis
            print("\n📊 Running demo analysis...")
            await ncos.analyze_data("csv", "demo_data.csv")

        # Optimize if requested
        if args.optimize:
            await ncos.optimize_system()

        # Phoenix status
        print("\n🔥 Phoenix Status:")
        phoenix_status = ncos.phoenix.get_status()
        print(json.dumps(phoenix_status, indent=2))

    finally:
        ncos.shutdown()

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║          NCOS v21 Phoenix Mesh - Production Ready     ║
    ║                                                       ║
    ║  🔥 Phoenix Rising: Optimized Financial Analysis      ║
    ║  📊 38 Wyckoff Components | 56 Pydantic Models       ║
    ║  ⚡ Fast Mode | Token Optimization | Native Charts    ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    asyncio.run(main())
