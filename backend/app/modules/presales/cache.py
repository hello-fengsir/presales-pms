"""Redis cache integration — dashboard stats, rate limiting, session."""
import redis
import json
import os
from functools import wraps
from typing import Optional, Any, Callable

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

_pool: Optional[redis.ConnectionPool] = None
_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """Lazy-init Redis client with connection pooling."""
    global _pool, _client
    if _client is None:
        try:
            _pool = redis.ConnectionPool.from_url(
                REDIS_URL,
                max_connections=20,
                socket_timeout=3,
                socket_connect_timeout=3,
                retry_on_timeout=True,
            )
            _client = redis.Redis(connection_pool=_pool)
            _client.ping()  # Verify connection
        except Exception:
            # Redis unavailable — return a null client, cache calls become no-ops
            _pool = None
            _client = None
    return _client


def cache_result(ttl: int = 300, prefix: str = "cache"):
    """Decorator: cache function return value in Redis.
    
    Usage:
        @cache_result(ttl=300, prefix="dashboard")
        def get_dashboard_stats(db, params):
            ...
    
    If Redis is unavailable, the function runs normally (no caching).
    """
    def decorator(fn: Callable):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            r = get_redis()
            if r is None:
                return await fn(*args, **kwargs)
            
            # Build cache key from function args
            key_parts = [prefix, fn.__name__]
            for a in args:
                if hasattr(a, '__dict__'):
                    continue  # Skip DB session objects
                key_parts.append(str(a)[:50])
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={str(v)[:50]}")
            cache_key = ":".join(key_parts)
            
            # Try cache
            try:
                cached = r.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass
            
            # Compute and cache
            result = await fn(*args, **kwargs)
            try:
                r.setex(cache_key, ttl, json.dumps(result, default=str))
            except Exception:
                pass
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str = "dashboard:*"):
    """Invalidate all cache keys matching pattern."""
    r = get_redis()
    if r is None:
        return
    try:
        keys = r.keys(pattern)
        if keys:
            r.delete(*keys)
    except Exception:
        pass
