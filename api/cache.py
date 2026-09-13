"""Caching helpers with Redis support and an in-memory fallback.

Set REDIS_URL to use Redis. If Redis is unavailable, the application remains
usable and falls back to process-local TTL caching instead of failing startup.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json
import os

try:
    import redis
except Exception:  # keeps lightweight/offline demo usable
    redis = None

_CACHE = {}
_REDIS_CLIENT = None
_REDIS_CHECKED = False
_NAMESPACE = "ai_social_media"


def _redis_client():
    global _REDIS_CLIENT, _REDIS_CHECKED
    if _REDIS_CHECKED:
        return _REDIS_CLIENT
    _REDIS_CHECKED = True
    if redis is None:
        return None
    url = os.getenv("REDIS_URL", "").strip()
    if not url:
        return None
    try:
        client = redis.from_url(url, socket_connect_timeout=1, socket_timeout=1, decode_responses=True)
        client.ping()
        _REDIS_CLIENT = client
    except Exception:
        _REDIS_CLIENT = None
    return _REDIS_CLIENT


def _key(func_name, args, kwargs):
    payload = repr((func_name, args, sorted(kwargs.items()))).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    return f"{_NAMESPACE}:{func_name}:{digest}"


def cached(seconds=300):
    """Cache JSON-compatible function results for the requested TTL."""
    ttl = max(1, int(seconds))

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _key(func.__name__, args, kwargs)
            client = _redis_client()

            if client is not None:
                try:
                    value = client.get(key)
                    if value is not None:
                        return json.loads(value)
                except Exception:
                    pass

            now = datetime.now()
            entry = _CACHE.get(key)
            if entry and entry["expires_at"] > now:
                return entry["value"]

            value = func(*args, **kwargs)
            _CACHE[key] = {"value": value, "expires_at": now + timedelta(seconds=ttl)}

            if client is not None:
                try:
                    client.setex(key, ttl, json.dumps(value, default=str))
                except Exception:
                    pass
            return value

        return wrapper

    return decorator


def clear_cache():
    memory_items = len(_CACHE)
    _CACHE.clear()
    redis_items = 0
    client = _redis_client()
    if client is not None:
        try:
            keys = list(client.scan_iter(match=f"{_NAMESPACE}:*"))
            if keys:
                redis_items = int(client.delete(*keys))
        except Exception:
            redis_items = 0
    return {"status": "cleared", "memory_items": memory_items, "redis_items": redis_items}


def cache_status():
    client = _redis_client()
    return {
        "backend": "redis+memory-fallback" if client is not None else "memory-fallback",
        "redis_configured": bool(os.getenv("REDIS_URL", "").strip()),
        "redis_reachable": client is not None,
        "memory_items": len(_CACHE),
    }
