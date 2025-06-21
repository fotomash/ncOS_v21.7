"""Compatibility wrapper for the unified voice system.

All functionality is provided by :mod:`core.ncos_voice_unified`.
"""

import sys as _sys

from core import menu_voice_integration as _menu_impl
from core import voice_tag_parser as _voice_impl
from core import zbar_voice_integration as _zbar_impl

_sys.modules.setdefault("voice_tag_parser", _voice_impl)
_sys.modules.setdefault("menu_voice_integration", _menu_impl)
_sys.modules.setdefault("zbar_voice_integration", _zbar_impl)
from core import ncos_voice_unified as _impl
_sys.modules.setdefault("ncos_voice_unified", _impl)

NCOSVoiceSystem = _impl.NCOSVoiceSystem
quick_start = _impl.quick_start

__all__ = ["NCOSVoiceSystem", "quick_start"]
