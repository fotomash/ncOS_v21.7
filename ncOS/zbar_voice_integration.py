"""Compatibility wrapper for voice-enabled ZBAR agent.

The implementation lives in :mod:`core.zbar_voice_integration`.
"""

import sys as _sys

from core import voice_tag_parser as _voice_impl

_sys.modules.setdefault("voice_tag_parser", _voice_impl)
from core import zbar_voice_integration as _impl
_sys.modules.setdefault("zbar_voice_integration", _impl)

VoiceEnabledZBARAgent = _impl.VoiceEnabledZBARAgent
demo_voice_zbar_integration = _impl.demo_voice_zbar_integration

__all__ = ["VoiceEnabledZBARAgent", "demo_voice_zbar_integration"]
