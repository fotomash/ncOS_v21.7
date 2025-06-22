"""Phoenix controller compatibility layer."""

from .ncos_session_optimized import PhoenixSessionController


class NCOSPhoenixController(PhoenixSessionController):
    """Alias for backward compatibility."""
    pass
