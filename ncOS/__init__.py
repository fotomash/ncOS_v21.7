"""ncOS package"""

from .semantic_utils import (
    extract_and_validate_uploaded_archive,
    summarize_workspace_memory,
    intelligently_route_user_request_to_best_agent,
    automatically_optimize_memory_and_consolidate_session_data,
    detect_and_recover_from_system_errors_automatically,
)
from .voice_tag_parser import VoiceTagParser, VoiceTag
from .menu_voice_integration import VoiceEnabledMenuSystem

# Optional heavy modules are imported lazily to avoid requiring their
# dependencies during lightweight usage such as unit tests.
def _lazy_import(module_name, attr):
    try:
        module = __import__(module_name, fromlist=[attr])
        return getattr(module, attr)
    except Exception:
        return None

EnhancedLLMCLI = _lazy_import("ncOS.enhanced_cli", "EnhancedLLMCLI")
NCOSPredictiveEngine = _lazy_import("ncOS.ncos_predictive_engine", "NCOSPredictiveEngine")
FeatureExtractor = _lazy_import("ncOS.ncos_feature_extractor", "FeatureExtractor")
DataEnricher = _lazy_import("ncOS.ncos_data_enricher", "DataEnricher")
NCOSVoiceSystem = _lazy_import("ncOS.ncos_voice_unified", "NCOSVoiceSystem")

__all__ = [
    "extract_and_validate_uploaded_archive",
    "summarize_workspace_memory",
    "intelligently_route_user_request_to_best_agent",
    "automatically_optimize_memory_and_consolidate_session_data",
    "detect_and_recover_from_system_errors_automatically",
    "EnhancedLLMCLI",
    "NCOSPredictiveEngine",
    "FeatureExtractor",
    "DataEnricher",
    "VoiceTagParser",
    "VoiceTag",
    "VoiceEnabledMenuSystem",
    "NCOSVoiceSystem",
]
