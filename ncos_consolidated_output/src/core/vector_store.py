"""Simple persistent vector store for ncOS."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class VectorStore:
    """A lightweight vector store with disk persistence."""

    def __init__(self, store_path: str | Path = "vector_store.json") -> None:
        self.path = Path(store_path)
        self.vectors: Dict[str, List[float]] = {}
        self.stats: Dict[str, Any] = {
            "total_vectors": 0,
            "last_loaded": None,
            "last_saved": None,
        }
        self.load()

    def add_vector(self, key: str, vector: List[float]) -> None:
        """Add or update a vector."""
        self.vectors[key] = vector
        self.stats["total_vectors"] = len(self.vectors)

    def get_vector(self, key: str) -> List[float] | None:
        """Retrieve a vector by key."""
        return self.vectors.get(key)

    def get_stats(self) -> Dict[str, Any]:
        """Return store statistics."""
        disk_size = self.path.stat().st_size if self.path.exists() else 0
        stats = dict(self.stats)
        stats["disk_usage_bytes"] = disk_size
        return stats

    def load(self) -> None:
        """Load vectors from disk if available."""
        if self.path.exists():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.vectors = data.get("vectors", {})
                self.stats.update(data.get("stats", {}))
            except Exception as exc:  # pragma: no cover - safeguard
                logger.error("Error loading vector store: %s", exc, exc_info=True)
        self.stats["total_vectors"] = len(self.vectors)
        self.stats["last_loaded"] = datetime.now().isoformat()

    def save(self) -> None:
        """Persist vectors to disk."""
        try:
            data = {"vectors": self.vectors, "stats": self.stats}
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.stats["last_saved"] = datetime.now().isoformat()
        except Exception as exc:  # pragma: no cover - safeguard
            logger.error("Error saving vector store: %s", exc, exc_info=True)
