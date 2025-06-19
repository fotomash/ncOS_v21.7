"""
NCOS v21.7.1 Phoenix Mesh Version Information
"""

__version__ = "21.7.1"
__version_info__ = (21, 7, 1)
__title__ = "NCOS Phoenix Mesh"
__description__ = "Neural Cognitive Operating System - Complete AI Trading Ecosystem"
__author__ = "NCOS Team"
__author_email__ = "team@ncos.ai"
__license__ = "MIT"
__copyright__ = "Copyright 2025 NCOS Team"
__url__ = "https://github.com/ncos/phoenix-mesh"

# Build information
BUILD_DATE = "2025-06-19"
BUILD_VERSION = "21.7.1"
BUILD_COMMIT = "phoenix-mesh-complete"

# System information
SYSTEM_NAME = "NCOS Phoenix Mesh"
SYSTEM_VERSION = "21.7.1"
SYSTEM_CODENAME = "Phoenix Mesh Complete"
SYSTEM_DESCRIPTION = "Complete AI Trading Ecosystem with Multi-Agent Orchestration"

# Component versions
COMPONENTS = {
    "core_system": "21.7.1",
    "agent_framework": "21.7.1", 
    "trading_strategies": "21.7.1",
    "vector_processing": "21.7.1",
    "zanflow_orchestration": "21.7.1",
    "knowledge_intelligence": "21.7.1",
    "interaction_system": "21.7.1",
    "risk_management": "21.7.1",
    "trigger_system": "21.7.1",
    "memory_system": "21.7.1"
}

# Feature flags
FEATURES = {
    "multi_agent_orchestration": True,
    "native_vector_processing": True,
    "zanflow_workflows": True,
    "knowledge_intelligence": True,
    "enhanced_interaction": True,
    "advanced_trading_strategies": True,
    "comprehensive_risk_management": True,
    "intelligent_triggers": True,
    "multi_tier_memory": True,
    "real_time_monitoring": True
}

def get_version():
    """Get the current version string."""
    return __version__

def get_version_info():
    """Get the version info tuple."""
    return __version_info__

def get_build_info():
    """Get build information."""
    return {
        "version": __version__,
        "build_date": BUILD_DATE,
        "build_version": BUILD_VERSION,
        "build_commit": BUILD_COMMIT,
        "system_name": SYSTEM_NAME,
        "system_codename": SYSTEM_CODENAME
    }

def get_system_info():
    """Get complete system information."""
    return {
        "system": {
            "name": SYSTEM_NAME,
            "version": SYSTEM_VERSION,
            "codename": SYSTEM_CODENAME,
            "description": SYSTEM_DESCRIPTION
        },
        "build": {
            "date": BUILD_DATE,
            "version": BUILD_VERSION,
            "commit": BUILD_COMMIT
        },
        "components": COMPONENTS,
        "features": FEATURES
    }

# Version validation
def validate_version():
    """Validate version consistency."""
    assert __version__ == SYSTEM_VERSION, "Version mismatch detected"
    assert __version__ == BUILD_VERSION, "Build version mismatch detected"
    return True

# Initialize validation on import
validate_version()
