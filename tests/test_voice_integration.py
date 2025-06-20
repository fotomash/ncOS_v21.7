import sys
import types
import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
VOICE_DIR = ROOT / "_21.7.2_to_deploy"


def load_module(path: Path, name: str):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


def load_voice_tag_parser():
    sys.modules.setdefault("spacy", types.SimpleNamespace(load=lambda name: None))
    return load_module(VOICE_DIR / "voice_tag_parser.py", "voice_tag_parser")


def load_enhanced_menu_system(vp_mod):
    sys.modules["voice_tag_parser"] = vp_mod
    sys.modules.setdefault(
        "menu_system",
        types.SimpleNamespace(MenuSystem=type("MenuSystem", (), {"__init__": lambda self, cfg: None})),
    )
    return load_module(VOICE_DIR / "enhanced_menu_system.py", "enhanced_menu_system")


class TestVoiceTagParser(unittest.TestCase):
    def setUp(self):
        self.vp_mod = load_voice_tag_parser()
        self.parser = self.vp_mod.VoiceTagParser()

    def test_basic_parsing(self):
        tag = self.parser.parse("mark gold bullish on 4 hour chart at support")
        self.assertEqual(tag.symbol, "XAUUSD")
        self.assertEqual(tag.timeframe, "H4")
        self.assertEqual(tag.bias, "bullish")
        self.assertEqual(tag.action, "mark")
        self.assertIn("support", tag.notes)
        self.assertGreaterEqual(tag.confidence, 0.99)


class TestEnhancedMenuSystem(unittest.TestCase):
    def setUp(self):
        vp_mod = load_voice_tag_parser()
        ems_mod = load_enhanced_menu_system(vp_mod)

        class DummyEMS(ems_mod.EnhancedMenuSystem):
            def __init__(self):
                super().__init__({})
                self.called_action = None

            def _execute_action(self, action):
                self.called_action = action
                return {"ok": True}

        self.ems = DummyEMS()

    def test_process_voice_command_executed(self):
        result = self.ems.process_voice_command("mark gold bullish on 4 hour chart")
        self.assertEqual(result["status"], "executed")
        self.assertEqual(self.ems.called_action["action"], "append_journal")

    def test_process_voice_command_confirm_needed(self):
        result = self.ems.process_voice_command("mark gold")
        self.assertEqual(result["status"], "confirm_needed")

    def test_process_voice_command_clarification(self):
        result = self.ems.process_voice_command("hello world")
        self.assertEqual(result["status"], "clarification_needed")


if __name__ == "__main__":
    unittest.main()
