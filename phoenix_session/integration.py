# phoenix_session/integration.py
from typing import Dict, Any, Optional
from .core.controller import NCOSPhoenixController
from .adapters.wyckoff_adapter import WyckoffAdapter
from .adapters.chart_adapter import ChartAdapter


class PhoenixIntegration:
    def __init__(self, ncos_config: Optional[Dict[str, Any]] = None):
        self.phoenix = NCOSPhoenixController(ncos_config)
        self.controller = self.phoenix

        # In a real scenario, you'd pass the actual legacy engines here
        self.wyckoff_adapter = WyckoffAdapter(self.phoenix, legacy_wyckoff_engine=None)
        self.chart_adapter = ChartAdapter(self.phoenix, native_engine=None)

        self.phoenix.connect_adapter("wyckoff", self.wyckoff_adapter)
        self.phoenix.connect_adapter("charting", self.chart_adapter)

    def get_status(self) -> Dict[str, Any]:
        return {
            "phoenix_controller_status": self.phoenix.get_status(),
            "adapters_connected": {
                "wyckoff": self.wyckoff_adapter.legacy_wyckoff is not None,
                "charting": self.chart_adapter.native_engine is not None
            }
        }


def create_phoenix_integration(config: Optional[Dict[str, Any]] = None) -> PhoenixIntegration:
    return PhoenixIntegration(config)
