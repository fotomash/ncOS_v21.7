# phoenix_session/adapters/wyckoff_adapter.py
from typing import Dict, Any

class WyckoffAdapter:
    def __init__(self, phoenix_controller, legacy_wyckoff_engine=None):
        self.phoenix = phoenix_controller
        self.legacy_wyckoff = legacy_wyckoff_engine
        self.config = phoenix_controller.config

    def analyze(self, data, use_legacy=False) -> Dict[str, Any]:
        """
        Analyze data using either Phoenix or legacy engine.
        """
        if self.config.fast_mode and not use_legacy:
            # Use the high-speed Phoenix engine
            return self.phoenix.analyze(data)
        elif self.legacy_wyckoff:
            # Fallback to the original, deep-analysis engine
            print("Legacy Wyckoff analysis not implemented in this adapter.")
            return {"phase": "Legacy Undetermined", "confidence": 0.0}
        else:
            raise ValueError("No valid Wyckoff engine available.")