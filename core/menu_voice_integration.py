"""Compatibility wrapper for menu voice integration.

This module forwards imports to :mod:`core.menu_voice_integration` so that
existing references to :mod:`ncOS.menu_voice_integration` continue to work.
"""

import sys as _sys

from core import voice_tag_parser as _voice_impl

_sys.modules.setdefault("voice_tag_parser", _voice_impl)
from core import menu_voice_integration as _impl

_sys.modules.setdefault("menu_voice_integration", _impl)

VoiceEnabledMenuSystem = _impl.VoiceEnabledMenuSystem
integrate_voice_menu = _impl.integrate_voice_menu
demo_voice_menu = _impl.demo_voice_menu

__all__ = ["VoiceEnabledMenuSystem", "integrate_voice_menu", "demo_voice_menu"]
