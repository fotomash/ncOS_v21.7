"""Compatibility wrapper for the voice tag parser.

This module now re-exports :class:`VoiceTagParser` and :class:`VoiceTag` from
:mod:`core.voice_tag_parser` to avoid duplicating the implementation.
"""

from core import voice_tag_parser as _impl
import sys as _sys

# Provide unqualified module name expected by some core modules
_sys.modules.setdefault("voice_tag_parser", _impl)

VoiceTagParser = _impl.VoiceTagParser
VoiceTag = _impl.VoiceTag

__all__ = ["VoiceTagParser", "VoiceTag"]
