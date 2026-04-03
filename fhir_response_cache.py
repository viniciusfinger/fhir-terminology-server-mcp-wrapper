"""In-memory TTL + LRU cache for deterministic FHIR GET responses."""

from __future__ import annotations

import copy
import threading
import time
from collections import OrderedDict
from typing import Any

_CACHEABLE_PATHS = frozenset(
    {
        "/CodeSystem/$lookup",
        "/CodeSystem/$validate-code",
        "/ValueSet/$validate-code",
        "/CodeSystem/$subsumes",
        "/ConceptMap/$translate",
    }
)


def is_cacheable_path(path: str) -> bool:
    if not path.startswith("/"):
        path = "/" + path
    return path in _CACHEABLE_PATHS


class TTLRUCache:
    """Leas recently used ordered in-memory cache with per-entry TTL (monotonic clock)."""

    def __init__(self, *, max_entries: int, ttl_seconds: float) -> None:
        if max_entries < 1:
            raise ValueError("max_entries must be >= 1")
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be > 0")
        self._max = max_entries
        self._ttl = ttl_seconds
        self._data: OrderedDict[tuple[Any, ...], tuple[Any, float]] = OrderedDict()
        self._lock = threading.Lock()

    def get(self, key: tuple[Any, ...]) -> Any | None:
        now = time.monotonic()
        with self._lock:
            item = self._data.get(key)
            if item is None:
                return None
            value, expires_at = item
            if now >= expires_at:
                del self._data[key]
                return None
            self._data.move_to_end(key)
            return copy.deepcopy(value)

    def set(self, key: tuple[Any, ...], value: Any) -> None:
        now = time.monotonic()
        expires_at = now + self._ttl
        with self._lock:
            if key in self._data:
                del self._data[key]
            self._data[key] = (copy.deepcopy(value), expires_at)
            self._data.move_to_end(key)
            while len(self._data) > self._max:
                self._data.popitem(last=False)
