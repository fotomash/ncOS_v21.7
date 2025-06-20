from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class MemoryEntry:
    """Single memory entry stored by ``EnhancedMemoryManager``."""

    data: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class EnhancedMemoryManager:
    """Manage context aware memories with TTL and namespaces."""

    def __init__(self, ttl_seconds: int = 3600, default_window: int = 5) -> None:
        self.ttl_seconds = ttl_seconds
        self.default_window = default_window
        self._namespaces: Dict[str, List[MemoryEntry]] = {}

    # ------------------------------------------------------------------
    def store_memory(self, namespace: str, data: Any, metadata: Optional[Dict[str, Any]] = None) -> MemoryEntry:
        """Store a memory entry under a namespace."""
        entry = MemoryEntry(data=data, metadata=metadata or {})
        self._namespaces.setdefault(namespace, []).append(entry)
        self._cleanup_namespace(namespace)
        return entry

    # ------------------------------------------------------------------
    def get_context_window(self, namespace: str, window_size: Optional[int] = None) -> List[MemoryEntry]:
        """Retrieve the most recent ``window_size`` entries for ``namespace``."""
        size = window_size or self.default_window
        self._cleanup_namespace(namespace)
        return self._namespaces.get(namespace, [])[-size:]

    # ------------------------------------------------------------------
    def namespaces(self) -> List[str]:
        """Return a list of all namespaces with stored memories."""
        self._cleanup_expired()
        return list(self._namespaces.keys())

    # ------------------------------------------------------------------
    def _cleanup_namespace(self, namespace: str) -> None:
        now = datetime.utcnow()
        ttl = timedelta(seconds=self.ttl_seconds)
        entries = self._namespaces.get(namespace, [])
        self._namespaces[namespace] = [e for e in entries if now - e.timestamp <= ttl]
        if not self._namespaces[namespace]:
            self._namespaces.pop(namespace, None)

    # ------------------------------------------------------------------
    def _cleanup_expired(self) -> None:
        for ns in list(self._namespaces.keys()):
            self._cleanup_namespace(ns)

