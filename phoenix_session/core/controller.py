"""Phoenix controller used by :class:`PhoenixIntegration`."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from .ncos_session_optimized import PhoenixSessionController


class NCOSPhoenixController:
    """Lightweight controller that wraps :class:`PhoenixSessionController`.

    This layer keeps a small registry of adapters and exposes a subset of the
    methods that ``PhoenixIntegration`` relies on.  It delegates the heavy work
    to :class:`PhoenixSessionController` but adds a thin compatibility API for
    adapter management and status reporting.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        # Underlying optimized controller with all core functionality
        self._controller = PhoenixSessionController(config)
        # Local registry of connected adapters
        self._adapters: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Basic proxy attributes
    # ------------------------------------------------------------------
    @property
    def config(self):
        """Expose the underlying configuration."""
        return self._controller.config

    # ------------------------------------------------------------------
    # Adapter management
    # ------------------------------------------------------------------
    def connect_adapter(self, name: str, adapter: Any) -> None:
        """Register an adapter for later use."""
        self._adapters[name] = adapter

    # ``register_adapter`` is an alias used in some legacy code
    register_adapter = connect_adapter

    def get_registered_adapters(self) -> Iterable[str]:
        """Return an iterable of registered adapter names."""
        return self._adapters.keys()

    # ------------------------------------------------------------------
    # Delegated methods from ``PhoenixSessionController``
    # ------------------------------------------------------------------
    def analyze(self, data: Any = None) -> Dict[str, Any]:
        return self._controller.analyze(data)

    def chart(self, data: Any = None, chart_type: Optional[str] = None) -> str:
        return self._controller.chart(data, chart_type)

    def quick_start(self, data_path: Optional[str] = None) -> Dict[str, Any]:
        return self._controller.quick_start(data_path)

    def get_performance_stats(self) -> Dict[str, Any]:
        return self._controller.get_performance_stats()

    def optimize_tokens(self, text: str, budget: int) -> str:
        return self._controller.optimize_tokens(text, budget)

    def shutdown(self) -> None:
        self._controller.shutdown()

    # ------------------------------------------------------------------
    # Enhanced status reporting
    # ------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """Return status information including adapter registry."""
        status = self._controller.get_status()
        status["adapters"] = list(self.get_registered_adapters())
        return status


# Backwards compatibility export
PhoenixController = NCOSPhoenixController

