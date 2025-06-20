"""Aggregator package for NCOS API modules.

This module exposes the key FastAPI backends used by the NCOS system so
applications can simply import them from :mod:`ncos_api`.
"""

from importlib import util
from pathlib import Path

# Export the live market data API backend
from ncos_plugin import plugin_api_backend

# Dynamically load the ZBAR API module located in the deployment folder
_zbar_path = Path(__file__).resolve().parent.parent / "_21.7.2_to_deploy" / "ncos_zbar_api.py"
if _zbar_path.exists():
    spec = util.spec_from_file_location("ncos_zbar_api", _zbar_path)
    ncos_zbar_api = util.module_from_spec(spec)
    spec.loader.exec_module(ncos_zbar_api)
else:
    ncos_zbar_api = None

__all__ = ["plugin_api_backend", "ncos_zbar_api"]
