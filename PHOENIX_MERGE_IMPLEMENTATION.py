# PHOENIX_MERGE_IMPLEMENTATION.py - Complete merge implementation
"""
This file contains the complete implementation for merging Phoenix Session into NCOS.
Copy the relevant sections into your project as needed.
"""

# ============== SECTION 1: Phoenix Core Controller ==============
PHOENIX_CORE_CONTROLLER = """
# phoenix_session/core/controller.py
from typing import Dict, Any, Optional
import asyncio
import pandas as pd
import time
from pathlib import Path

# Import the optimized Phoenix implementation
try:
    from ncos_session_optimized import PhoenixSessionController, OptimizedConfig
except ImportError:
    # Fallback if not found
    class PhoenixSessionController:
        def __init__(self, config=None):
            self.config = config or {}

    class OptimizedConfig:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

class NCOSPhoenixController(PhoenixSessionController):
    def __init__(self, ncos_config: Optional[Dict[str, Any]] = None):
        # Convert NCOS config to Phoenix config
        phoenix_config = self._convert_config(ncos_config)
        super().__init__(phoenix_config)

        # NCOS-specific extensions
        self.ncos_mode = True
        self.integration_adapters = {}

    def _convert_config(self, ncos_config: Optional[Dict[str, Any]]) -> OptimizedConfig:
        if not ncos_config:
            return OptimizedConfig()

        return OptimizedConfig(
            token_budget=ncos_config.get('memory', {}).get('token_budget', 4096),
            wyckoff_enabled=ncos_config.get('strategies', {}).get('wyckoff', {}).get('enabled', True),
            fast_mode=ncos_config.get('phoenix', {}).get('fast_mode', True),
            cache_enabled=ncos_config.get('phoenix', {}).get('cache', True)
        )

    async def async_analyze(self, data):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.analyze, data)

    def integrate_with_ncos(self, orchestrator):
        self.orchestrator = orchestrator
        print("✅ Phoenix integrated with NCOS orchestrator")
"""

# ============== SECTION 2: Wyckoff Adapter ==============
WYCKOFF_ADAPTER = """
# phoenix_session/adapters/wyckoff_adapter.py
from typing import Dict, Any
import pandas as pd

class PhoenixWyckoffAdapter:
    def __init__(self, phoenix_controller):
        self.phoenix = phoenix_controller
        self.legacy_wyckoff = None

    def analyze_with_fallback(self, data: pd.DataFrame) -> Dict[str, Any]:
        # Quick Phoenix analysis
        quick_result = self.phoenix.wyckoff.quick_analysis(data)

        # If confidence is low, use legacy system
        if quick_result['confidence'] < 0.7 and self.legacy_wyckoff:
            return self.legacy_wyckoff.detailed_analysis(data)

        return quick_result

    def connect_legacy(self, legacy_module):
        self.legacy_wyckoff = legacy_module
        print("✅ Phoenix Wyckoff adapter connected to legacy system")
"""

# ============== SECTION 3: Chart Adapter ==============
CHART_ADAPTER = """
# phoenix_session/adapters/chart_adapter.py
from typing import Dict, Any, Optional
import pandas as pd

class PhoenixChartAdapter:
    def __init__(self, phoenix_controller):
        self.phoenix = phoenix_controller
        self.native_engine = None

    def render_chart(self, data: pd.DataFrame, 
                    chart_type: str = 'candlestick',
                    use_native: bool = False) -> str:
        if use_native and self.native_engine:
            return self.native_engine.create_advanced_chart(data, chart_type)

        # Use Phoenix for speed
        return self.phoenix.chart(data, chart_type)

    def connect_native(self, native_engine):
        self.native_engine = native_engine
        print("✅ Phoenix Chart adapter connected to native engine")
"""

# ============== SECTION 4: Main Integration Module ==============
INTEGRATION_MODULE = """
# phoenix_session/integration.py
from typing import Dict, Any, Optional
import asyncio

# Import from local modules
from .core.controller import NCOSPhoenixController
from .adapters.wyckoff_adapter import PhoenixWyckoffAdapter
from .adapters.chart_adapter import PhoenixChartAdapter

class PhoenixIntegration:
    def __init__(self, ncos_config: Optional[Dict[str, Any]] = None):
        # Initialize Phoenix controller
        self.phoenix = NCOSPhoenixController(ncos_config)

        # Initialize adapters
        self.wyckoff_adapter = PhoenixWyckoffAdapter(self.phoenix)
        self.chart_adapter = PhoenixChartAdapter(self.phoenix)

        # Integration state
        self.integrated = False
        self.legacy_modules = {}

    def integrate_with_orchestrator(self, orchestrator):
        # Connect Phoenix to orchestrator
        self.phoenix.integrate_with_ncos(orchestrator)

        # Register Phoenix handlers
        orchestrator.register_handler('phoenix_analyze', self.phoenix.analyze)
        orchestrator.register_handler('phoenix_chart', self.phoenix.chart)

        # Set integration flag
        self.integrated = True

        return self

    def connect_legacy_modules(self, modules: Dict[str, Any]):
        self.legacy_modules = modules

        # Connect Wyckoff
        if 'wyckoff' in modules:
            self.wyckoff_adapter.connect_legacy(modules['wyckoff'])

        # Connect charting
        if 'native_chart_engine' in modules:
            self.chart_adapter.connect_native(modules['native_chart_engine'])

    async def run_analysis_pipeline(self, data_source: str) -> Dict[str, Any]:
        # Phase 1: Quick Phoenix analysis
        quick_analysis = await self.phoenix.async_analyze(data_source)

        # Phase 2: Enhanced analysis if needed
        if quick_analysis['wyckoff']['confidence'] < 0.8:
            detailed = self.wyckoff_adapter.analyze_with_fallback(data_source)
            quick_analysis['wyckoff_detailed'] = detailed

        # Phase 3: Generate chart
        chart = self.chart_adapter.render_chart(
            data_source, 
            use_native=not self.phoenix.config.fast_mode
        )
        quick_analysis['chart'] = chart

        return quick_analysis

    def get_performance_metrics(self) -> Dict[str, Any]:
        return {
            "phoenix_status": self.phoenix.get_status(),
            "integrated": self.integrated,
            "adapters_connected": {
                "wyckoff": self.wyckoff_adapter.legacy_wyckoff is not None,
                "charting": self.chart_adapter.native_engine is not None
            }
        }

def create_phoenix_integration(config: Optional[Dict[str, Any]] = None) -> PhoenixIntegration:
    return PhoenixIntegration(config)
"""

# ============== SECTION 5: Phoenix Configuration ==============
PHOENIX_CONFIG = {
    "phoenix_session": {
        "enabled": True,
        "mode": "integrated",
        "fast_mode": True,
        "cache_enabled": True,
        "fallback_to_legacy": True,
        "performance": {
            "max_workers": 4,
            "token_budget": 4096,
            "analysis_timeout": 5.0
        },
        "adapters": {
            "wyckoff": "phoenix_session.adapters.wyckoff_adapter",
            "charting": "phoenix_session.adapters.chart_adapter"
        }
    }
}

# ============== SECTION 6: Installation Instructions ==============
INSTALLATION_STEPS = """
1. Copy ncos_session_optimized.py to phoenix_session/core/
2. Create the directory structure as shown
3. Copy each section to its respective file
4. Update your master configuration with PHOENIX_CONFIG
5. Run validation script to ensure proper setup
"""

if __name__ == "__main__":
    print("Phoenix Merge Implementation Reference")
    print("=" * 50)
    print("This file contains all code needed for the merge.")
    print("Copy sections as needed into your project.")
    print(INSTALLATION_STEPS)
