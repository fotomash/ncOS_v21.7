import sys
from unittest.mock import MagicMock, patch
import unittest

# Stub dependencies not available in the test environment
sys.modules['spacy'] = MagicMock()
sys.modules['yaml'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['pandas'] = MagicMock()
sys.modules['zbar_agent'] = MagicMock()
sys.modules['zbar_logger'] = MagicMock()

from ncOS.menu_voice_integration import VoiceEnabledMenuSystem


class DummyMenu(VoiceEnabledMenuSystem):
    def _add_voice_menu(self):
        # avoid calling get_main_menu during tests
        pass


class TestVoiceMenuSystem(unittest.TestCase):
    def setUp(self):
        self.menu = DummyMenu(orchestrator=None, config={"api_base": "http://api"})
        self.menu.update_context = MagicMock()

    def test_voice_mark_setup_posts_journal(self):
        # Simulate user inputs for command, confirmation and analysis prompt
        inputs = iter([
            "Mark gold bullish on 4hour swept lows at 2358",
            "y",
            "n",
        ])
        with patch("builtins.input", lambda *_: next(inputs)):
            sys.modules['requests'].post.return_value.status_code = 200
            result = self.menu._voice_mark_setup()

        self.assertIn(result["status"], {"success", "error"})

        if sys.modules['requests'].post.called:
            sent_payload = sys.modules['requests'].post.call_args.kwargs["json"]
            self.assertEqual(sent_payload["symbol"], "XAUUSD")
            self.assertEqual(sent_payload["timeframe"], "H4")
            self.assertEqual(sent_payload["bias"], "bullish")
            self.assertEqual(sent_payload["notes"], "swept lows 2358")


if __name__ == "__main__":
    unittest.main()
