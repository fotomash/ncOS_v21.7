#!/usr/bin/env python3
# test_phoenix.py - Integration tests for the Phoenix Session merge.

import unittest
from pathlib import Path
import json

# Before tests can run, we need to ensure the integration module is importable
# This assumes the script is run from the project's root directory.
try:
    from phoenix_session.integration import create_phoenix_integration, PhoenixIntegration
except ImportError as e:
    print(f"Import Error: {e}")
    print("Please ensure you have run the merge process and are running tests from the NCOS root directory.")
    PhoenixIntegration = None  # Prevent further errors

# Mock configuration for testing purposes
TEST_CONFIG = {
    "phoenix_session": {
        "enabled": True,
        "mode": "integrated",
        "fast_mode": True,
        "cache_enabled": True,
        "performance": {
            "max_workers": 1,
            "token_budget": 4096
        }
    },
    "strategies": {
        "wyckoff": {"enabled": True}
    }
}

@unittest.skipIf(PhoenixIntegration is None, "Skipping tests due to import failure.")
class TestPhoenixIntegration(unittest.TestCase):

    def setUp(self):
        """Set up the test case"""
        self.integration = create_phoenix_integration(TEST_CONFIG)

    def test_01_integration_initialization(self):
        """Test if the PhoenixIntegration object initializes correctly."""
        self.assertIsNotNone(self.integration)
        self.assertIsNotNone(self.integration.phoenix)
        self.assertIsNotNone(self.integration.wyckoff_adapter)
        self.assertTrue(self.integration.phoenix.config.fast_mode)

    def test_02_wyckoff_adapter_analysis(self):
        """Test if the Wyckoff adapter can call the fast Phoenix analysis."""
        result = self.integration.wyckoff_adapter.analyze(data="mock_data")
        self.assertIn("phase", result)
        self.assertEqual(result["phase"], "Accumulation")
        self.assertIn("confidence", result)

    def test_03_chart_adapter_rendering(self):
        """Test if the Chart adapter can call the fast Phoenix charting."""
        output_path = self.integration.chart_adapter.render_chart(data="mock_data")
        # The fast chart engine returns a mock path
        self.assertIsInstance(output_path, str)
        self.assertTrue(output_path.endswith(".html"))

    def test_04_get_status(self):
        """Test the status reporting of the integration."""
        status = self.integration.get_status()
        self.assertIn("phoenix_controller_status", status)
        self.assertIn("adapters_connected", status)
        self.assertEqual(status["phoenix_controller_status"]["phoenix_session"], "active")

if __name__ == '__main__':
    unittest.main()
