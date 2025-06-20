"""Aggregator package for NCOS API modules.

This module exposes the key FastAPI backends used by the NCOS system so
applications can simply import them from :mod:`ncos_api`.
"""

# Export the live market data API backend
from ncos_plugin import plugin_api_backend

# Import integrated ZBAR strategy API
from . import ncos_zbar_api

# Data retrieval API for serving bar data
from . import data_retrieval_api

__all__ = [
    "plugin_api_backend",
    "ncos_zbar_api",
    "data_retrieval_api",
]
