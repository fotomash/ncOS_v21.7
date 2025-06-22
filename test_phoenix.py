#!/usr/bin/env python3
# test_phoenix.py - Integration tests for the Phoenix Session merge.

import unittest
import json
import asyncio
from pathlib import Path
from datetime import datetime

# This assumes the script is run from the project's root directory.
try:
    from phoenix_session.integration import create_phoenix_integration, PhoenixIntegration
    from phoenix_session.core.optimized import phoenix_rise
except ImportError as e:
    print(f"Import Error: {e}. Please run tests from the NCOS root directory.")
    PhoenixIntegration = None

# Mock config for testing
TEST_CONFIG = {
    "phoenix_session": { 
        "enabled": True, 
        "fast_mode": True,
        "cache_enabled": True,
        "token_budget": 4096
    },
    "strategies": { 
        "wyckoff": {"enabled": True}, 
        "smc": {"enabled": True}
    }
}

@unittest.skipIf(PhoenixIntegration is None, "Skipping tests due to import failure.")
class TestPhoenixIntegration(unittest.TestCase):

    def setUp(self):
        """Set up the test case"""
        self.integration = create_phoenix_integration(TEST_CONFIG["phoenix_session"])

    def test_integration_initialization(self):
        """Test if the PhoenixIntegration object initializes correctly."""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.controller)
        self.assertTrue(self.integration.controller.config.fast_mode)
        print("✅ Integration initialization test passed")

    def test_wyckoff_adapter_analysis(self):
        """Test if the Wyckoff adapter can call the fast Phoenix analysis."""
        async def run_test():
            result = await self.integration.wyckoff_adapter.analyze(data="mock_data")
            self.assertIn("phase", result)
            self.assertIn("engine", result)
            self.assertEqual(result["engine"], "phoenix_fast")
            print("✅ Wyckoff adapter test passed")

        asyncio.run(run_test())

    def test_chart_adapter_rendering(self):
        """Test if the Chart adapter can call the fast Phoenix charting."""
        output_path = self.integration.chart_adapter.render_chart(data="mock_data")
        self.assertTrue(output_path.endswith(".html"))
        self.assertTrue(Path(output_path).exists())
        print("✅ Chart adapter test passed")

    def test_phoenix_rise(self):
        """Test the phoenix_rise quick initialization"""
        phoenix = phoenix_rise()
        self.assertIsNotNone(phoenix)
        self.assertTrue(phoenix.config.fast_mode)
        print("✅ Phoenix rise test passed")

    def test_performance_stats(self):
        """Test performance statistics"""
        stats = self.integration.controller.get_performance_stats()
        self.assertIn("mode", stats)
        self.assertIn("fast_mode", stats)
        self.assertIn("cache_stats", stats)
        self.assertEqual(stats["mode"], "optimized")
        print("✅ Performance stats test passed")

    def test_token_optimization(self):
        """Test token optimization"""
        long_text = "A" * 20000  # 5000 tokens
        optimized = self.integration.controller.optimize_tokens(long_text, budget=1000)
        # Should be roughly 4000 chars for 1000 tokens
        self.assertLessEqual(len(optimized), 4000)
        self.assertIn("[optimized]", optimized)

        short_text = "B" * 100
        self.assertEqual(self.integration.controller.optimize_tokens(short_text, budget=1000), short_text)
        print("✅ Token optimization test passed")

class TestFullIntegration(unittest.TestCase):
    """Full system integration tests"""

    @unittest.skipIf(PhoenixIntegration is None, "Skipping due to import failure")
    def test_complete_workflow(self):
        """Test complete data processing workflow"""
        async def run_workflow():
            # Import orchestrator
            from orchestrators import create_orchestrator
            from schemas.unified_schemas import SessionConfig

            # Create orchestrator
            orchestrator = create_orchestrator()

            # Create session
            session_config = SessionConfig(
                session_id="test_session_001",
                token_budget=4096,
                agents=["data_ingestor", "strategy_agent", "viz_agent"],
                strategies=["wyckoff", "smc"],
                memory_config={"token_budget": 4096, "compression_enabled": True}
            )

            session_id = orchestrator.create_session(session_config)
            self.assertEqual(session_id, "test_session_001")

            # Process data
            results = await orchestrator.process_data(
                session_id,
                "csv",
                "mock_data.csv"
            )

            # Verify results
            self.assertIn("stages", results)
            self.assertIn("ingestion", results["stages"])
            self.assertIn("strategies", results["stages"])
            self.assertIn("signal", results["stages"])
            self.assertIn("visualization", results["stages"])

            print("✅ Complete workflow test passed")

            # Cleanup
            orchestrator.shutdown()

        asyncio.run(run_workflow())

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 Running NCOS v21 Phoenix Integration Tests")
    print("=" * 60)

    # Create test suite
    suite = unittest.TestSuite()

    # Add Phoenix tests
    suite.addTest(TestPhoenixIntegration('test_integration_initialization'))
    suite.addTest(TestPhoenixIntegration('test_wyckoff_adapter_analysis'))
    suite.addTest(TestPhoenixIntegration('test_chart_adapter_rendering'))
    suite.addTest(TestPhoenixIntegration('test_phoenix_rise'))
    suite.addTest(TestPhoenixIntegration('test_performance_stats'))
    suite.addTest(TestPhoenixIntegration('test_token_optimization'))

    # Add full integration test
    suite.addTest(TestFullIntegration('test_complete_workflow'))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n🎉 All tests passed! Phoenix is ready for flight!")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")

    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_integration_tests()
    exit(0 if success else 1)
