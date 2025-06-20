import sys
from unittest.mock import MagicMock, patch
import unittest

# Stub dependencies not available in the test environment
sys.modules['spacy'] = MagicMock()
sys.modules['yaml'] = MagicMock()
sys.modules['requests'] = MagicMock()

sys.path.append('_21.7.2_verify')
from menu_voice_integration import VoiceEnabledMenuSystem


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
            with patch("requests.post") as mock_post:
                mock_post.return_value.status_code = 200
                result = self.menu._voice_mark_setup()

        self.assertEqual(result["status"], "success")

        mock_post.assert_called()
        sent_payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(sent_payload["symbol"], "XAUUSD")
        self.assertEqual(sent_payload["timeframe"], "H4")
        self.assertEqual(sent_payload["bias"], "bullish")
        self.assertEqual(sent_payload["notes"], "swept lows 2358")


if __name__ == "__main__":
    unittest.main()
