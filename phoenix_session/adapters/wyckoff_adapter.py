# phoenix_session/adapters/wyckoff_adapter.py
from typing import Dict, Any

class WyckoffAdapter:
    def __init__(self, phoenix_controller, legacy_wyckoff_engine=None):
        self.phoenix = phoenix_controller
        self.legacy_wyckoff = legacy_wyckoff_engine
        self.config = phoenix_controller.config

    async def analyze(self, data, use_legacy=False) -> Dict[str, Any]:
        """Analyze data using either Phoenix or legacy engine."""
        if self.config.fast_mode and not use_legacy:
            analysis = self.phoenix.analyze(data)
            return {
                "phase": analysis.get("wyckoff", {}).get("phase", "Unknown"),
                "engine": "phoenix_fast",
            }
        elif self.legacy_wyckoff:
            print("Legacy Wyckoff analysis not implemented in this adapter.")
            return {"phase": "Legacy Undetermined", "confidence": 0.0}
        else:
            raise ValueError("No valid Wyckoff engine available.")
