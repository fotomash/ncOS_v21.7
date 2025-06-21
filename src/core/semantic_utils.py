"""Utility functions for advanced semantic operations in ncOS."""

from __future__ import annotations

import asyncio
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, Optional


async def extract_and_validate_uploaded_archive(
        archive_path: str,
        extract_to: str | None = None,
        allowed_formats: Iterable[str] | None = None,
) -> Dict[str, Any]:
    """Extract an uploaded archive and perform basic validation.

    Parameters
    ----------
    archive_path:
        Path to the uploaded archive file.
    extract_to:
        Destination directory for extracted files. If not provided, a
        temporary directory will be created.
    allowed_formats:
        Iterable of allowed archive formats. Defaults to {"zip", "tar", "gztar"}.

    Returns
    -------
    Dict[str, Any]
        Information about the extraction and validation process. The
        dictionary contains ``status`` (``"success"`` or ``"error"``), the
        ``extracted_to`` path, ``file_count`` of extracted files and the
        original ``archive`` path.
    """
    allowed = set(allowed_formats or {"zip", "tar", "gztar"})
    archive_file = Path(archive_path)

    if archive_file.suffix.replace(".", "") not in allowed:
        return {
            "status": "error",
            "error": "unsupported_format",
            "archive": archive_path,
        }

    if not archive_file.exists():
        return {"status": "error", "error": "file_not_found", "archive": archive_path}

    dest_dir = Path(extract_to) if extract_to else Path(tempfile.mkdtemp())
    dest_dir.mkdir(parents=True, exist_ok=True)

    try:
        shutil.unpack_archive(str(archive_file), str(dest_dir))
        file_count = sum(1 for _ in dest_dir.rglob("*") if _.is_file())
        return {
            "status": "success",
            "archive": str(archive_file),
            "extracted_to": str(dest_dir),
            "file_count": file_count,
        }
    except Exception as exc:  # pragma: no cover - sanity wrapper
        return {"status": "error", "error": str(exc), "archive": archive_path}


async def summarize_workspace_memory(session_state: Any) -> Dict[str, Any]:
    """Create a summary of workspace memory usage.

    The function expects an object or mapping with attributes similar to
    ``memory_usage_mb`` and ``processed_files``. It returns a summary
    dictionary with the amount of memory used and basic counts for session
    analysis.
    """

    memory_mb = getattr(session_state, "memory_usage_mb", 0.0)
    processed_files = getattr(session_state, "processed_files", [])
    active_agents = getattr(session_state, "active_agents", [])
    trading_signals = getattr(session_state, "trading_signals", [])

    summary = {
        "memory_usage_mb": float(memory_mb),
        "processed_files": len(processed_files),
        "active_agents": len(active_agents),
        "trading_signals": len(trading_signals),
    }

    return summary


async def intelligently_route_user_request_to_best_agent(
        request: Dict[str, Any],
        agent_registry: Dict[str, Any],
) -> Dict[str, Any]:
    """Determine the best agent for a given user request.

    Parameters
    ----------
    request:
        Incoming request payload. It may contain a ``type`` or ``intent``
        field used for routing.
    agent_registry:
        Mapping of agent names to metadata. Each entry should at least
        contain an ``id`` field.

    Returns
    -------
    Dict[str, Any]
        A routing decision including the ``selected_agent`` and a ``reason``
        string.
    """

    req_type = request.get("type") or request.get("intent")
    selected_agent = None
    reason = "no_match"

    if req_type and req_type in agent_registry:
        selected_agent = req_type
        reason = "matched_by_type"
    elif "default" in agent_registry:
        selected_agent = "default"
        reason = "fallback_default"
    else:
        if agent_registry:
            selected_agent = next(iter(agent_registry))
            reason = "first_available"

    return {
        "status": "routed" if selected_agent else "error",
        "request_type": req_type,
        "selected_agent": selected_agent,
        "reason": reason,
    }


async def automatically_optimize_memory_and_consolidate_session_data(
        session_state: Any,
        max_files: int | None = None,
        max_memory_mb: float | None = None,
) -> Dict[str, Any]:
    """Perform light-weight memory optimization on the session state.

    Parameters
    ----------
    session_state:
        Object or mapping representing the current session state.
    max_files:
        Optional maximum number of ``processed_files`` to retain.
    max_memory_mb:
        If provided, clamp ``memory_usage_mb`` to this value.

    Returns
    -------
    Dict[str, Any]
        Summary of the optimization including ``files_consolidated`` and the
        resulting ``memory_usage_mb``.
    """

    files = getattr(session_state, "processed_files", [])
    before_count = len(files)

    if max_files is not None and before_count > max_files:
        excess = before_count - max_files
        del files[:excess]

    memory_mb = getattr(session_state, "memory_usage_mb", 0.0)
    freed = 0.0
    if max_memory_mb is not None and memory_mb > max_memory_mb:
        freed = memory_mb - max_memory_mb
        memory_mb = max_memory_mb

    if hasattr(session_state, "memory_usage_mb"):
        session_state.memory_usage_mb = memory_mb

    return {
        "status": "optimized",
        "files_consolidated": before_count - len(files),
        "memory_freed_mb": float(freed),
        "memory_usage_mb": float(memory_mb),
    }


async def detect_and_recover_from_system_errors_automatically(
        error: Exception | str,
        context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Attempt automatic recovery from system errors.

    Parameters
    ----------
    error:
        The caught exception or error message.
    context:
        Optional context information related to the error.

    Returns
    -------
    Dict[str, Any]
        The recovery result with ``status`` and ``recovery_action``.
    """

    err_msg = str(error)
    recovery_action = "logged"

    if isinstance(error, asyncio.TimeoutError):
        recovery_action = "retry"  # transient timeout
    elif "disk" in err_msg.lower() and context:
        # Example of handling disk related issues by freeing workspace
        workspace = context.get("workspace")
        if workspace:
            try:
                for path in Path(workspace).glob("*.tmp"):
                    path.unlink(missing_ok=True)
                recovery_action = "cleared_temp_files"
            except Exception:  # pragma: no cover - best effort
                recovery_action = "cleanup_failed"

    status = "recovered" if recovery_action != "cleanup_failed" else "error"
    return {
        "status": status,
        "error": err_msg,
        "recovery_action": recovery_action,
    }


__all__ = [
    "extract_and_validate_uploaded_archive",
    "summarize_workspace_memory",
    "intelligently_route_user_request_to_best_agent",
    "automatically_optimize_memory_and_consolidate_session_data",
    "detect_and_recover_from_system_errors_automatically",
]
