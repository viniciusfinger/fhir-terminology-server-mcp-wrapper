"""Unit tests for fhir_response_cache.TTLRUCache."""

from __future__ import annotations

import time

import pytest

from fhir_response_cache import TTLRUCache, is_cacheable_path


def test_is_cacheable_path_known_operations() -> None:
    """Test that the is_cacheable_path function returns True for known cacheable paths and False for unknown paths."""
    assert is_cacheable_path("/CodeSystem/$lookup")
    assert is_cacheable_path("CodeSystem/$lookup")
    assert is_cacheable_path("/ValueSet/$validate-code")
    assert not is_cacheable_path("/ValueSet/$expand")
    assert not is_cacheable_path("/metadata")


def test_cache_miss_then_hit() -> None:
    """First get returns None for an unknown key (miss); after set, the same key returns the stored value (hit)."""
    cache = TTLRUCache(max_entries=8, ttl_seconds=60.0)
    key = ("https://tx.fhir.org/r4", "/CodeSystem/$lookup", (("code", "x"), ("system", "y")))
    assert cache.get(key) is None

    cache.set(key, {"a": 1})
    assert cache.get(key) == {"a": 1}


def test_cache_returned_value_is_copy() -> None:
    """Test that the returned value is a copy of the stored value, so modifying it does not modify the stored value."""
    cache = TTLRUCache(max_entries=8, ttl_seconds=60.0)
    key = ("u", "/p", ())
    payload = {"nested": {"x": 1}}
    cache.set(key, payload)

    got = cache.get(key)
    assert got is not None

    got["nested"]["x"] = 99
    got2 = cache.get(key)
    assert got2 is not None

    assert got2["nested"]["x"] == 1


def test_cache_lru_eviction() -> None:
    """Test that the least recently used item is evicted when the cache is full."""
    cache = TTLRUCache(max_entries=2, ttl_seconds=60.0)
    cache.set(("b", "1", ()), 1)
    cache.set(("b", "2", ()), 2)
    cache.get(("b", "1", ()))  # refresh 1
    cache.set(("b", "3", ()), 3)  # evict LRU among full set → 2 out
    assert cache.get(("b", "1", ())) == 1
    assert cache.get(("b", "2", ())) is None
    assert cache.get(("b", "3", ())) == 3


def test_cache_ttl_expiry() -> None:
    """Test that the cache expires items after the TTL."""
    cache = TTLRUCache(max_entries=8, ttl_seconds=0.05)
    key = ("u", "/p", ())
    cache.set(key, {"v": 1})
    assert cache.get(key) == {"v": 1}
    
    time.sleep(0.08)
    assert cache.get(key) is None


def test_cache_invalid_config() -> None:
    """Test that the cache raises an error for invalid configuration."""
    with pytest.raises(ValueError):
        TTLRUCache(max_entries=0, ttl_seconds=10.0)
        
    with pytest.raises(ValueError):
        TTLRUCache(max_entries=4, ttl_seconds=0.0)
