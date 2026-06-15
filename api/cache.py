from datetime import datetime, timedelta
from functools import wraps

_CACHE = {}


def cached(seconds=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            now = datetime.now()
            entry = _CACHE.get(key)
            if entry and entry["expires_at"] > now:
                return entry["value"]
            value = func(*args, **kwargs)
            _CACHE[key] = {"value": value, "expires_at": now + timedelta(seconds=seconds)}
            return value

        return wrapper

    return decorator


def clear_cache():
    _CACHE.clear()
    return {"status": "cleared", "items": 0}
