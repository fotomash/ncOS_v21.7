#!/usr/bin/env python3
"""
Compatibility shim for test suite - redirects to actual orchestrator
"""
from core.enhanced_core_orchestrator import *

# Additional compatibility exports
__all__ = ['MasterOrchestrator', 'enhanced_master_orchestrator']
