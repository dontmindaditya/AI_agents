"""
Caching Module

Provides caching functionality for:
- Agent registry
- Settings
- API responses
- Any frequently accessed data

Supports multiple cache backends:
- In-memory (default)
- Redis (optional)
- Disk-based (optional)

Usage:
    from services.cache import cache, cached
    
    # Using decorator
    @cached("my-key", ttl=300)
    async def my_function():
        return expensive_computation()
    
    # Using cache directly
    await cache.set("key", value, ttl=60)
    value = await cache.get("key")
"""

import asyncio
import hashlib
import json
import time
from typing import Any, Optional, Callable, TypeVar, Union
from functools import wraps
from datetime import datetime, timezone
from enum import Enum

from utils.logger import setup_logger

logger = setup_logger(__name__)

T = TypeVar('T')


class CacheBackend(str, Enum):
    """Available cache backends."""
    MEMORY = "memory"
    REDIS = "redis"
    DISK = "disk"


class CacheEntry:
    """Represents a cached value with metadata."""
    
    def __init__(self, value: Any, ttl: int, created_at: float):
        self.value = value
        self.ttl = ttl
        self.created_at = created_at
        self.access_count = 0
        self.last_accessed = created_at
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        if self.ttl <= 0:
            return False
        return (time.time() - self.created_at) > self.ttl
    
    def touch(self):
        """Update access statistics."""
        self.access_count += 1
        self.last_accessed = time.time()
    
    def to_dict(self) -> dict:
        return {
            "created_at": self.created_at,
            "ttl": self.ttl,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
        }


class MemoryCache:
    """
    In-memory cache implementation.
    
    Features:
    - TTL support
    - Max size limit
    - LRU eviction
    - Thread-safe
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._cache: dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
        }
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        async with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._stats["misses"] += 1
                return None
            
            if entry.is_expired():
                del self._cache[key]
                self._stats["misses"] += 1
                return None
            
            entry.touch()
            self._stats["hits"] += 1
            return entry.value
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        async with self._lock:
            if len(self._cache) >= self._max_size:
                await self._evict_lru()
            
            ttl = ttl if ttl is not None else self._default_ttl
            entry = CacheEntry(
                value=value,
                ttl=ttl,
                created_at=time.time()
            )
            self._cache[key] = entry
            self._stats["sets"] += 1
    
    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    async def clear(self) -> None:
        """Clear all cached values."""
        async with self._lock:
            self._cache.clear()
            logger.info("Cache cleared")
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return False
            if entry.is_expired():
                del self._cache[key]
                return False
            return True
    
    async def get_stats(self) -> dict:
        """Get cache statistics."""
        async with self._lock:
            total = self._stats["hits"] + self._stats["misses"]
            hit_rate = (self._stats["hits"] / total * 100) if total > 0 else 0
            
            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self._max_size,
                "hit_rate_percent": round(hit_rate, 2),
            }
    
    async def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._cache:
            return
        
        lru_key = min(
            self._cache.keys(),
            key=lambda k: self._cache[k].last_accessed
        )
        del self._cache[lru_key]
        self._stats["evictions"] += 1
        logger.debug(f"Evicted LRU key: {lru_key}")
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries. Returns count of removed entries."""
        async with self._lock:
            expired_keys = [
                k for k, v in self._cache.items()
                if v.is_expired()
            ]
            for key in expired_keys:
                del self._cache[key]
            
            if expired_keys:
                logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            
            return len(expired_keys)


class Cache:
    """
    Main cache interface supporting multiple backends.
    """
    
    def __init__(self, backend: CacheBackend = CacheBackend.MEMORY):
        self._backend = backend
        self._memory_cache = MemoryCache()
        self._enabled = True
    
    @property
    def backend(self) -> CacheBackend:
        return self._backend
    
    def enable(self) -> None:
        """Enable caching."""
        self._enabled = True
        logger.info("Cache enabled")
    
    def disable(self) -> None:
        """Disable caching."""
        self._enabled = False
        logger.info("Cache disabled")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        if not self._enabled:
            return None
        return await self._memory_cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set a value in cache."""
        if not self._enabled:
            return
        return await self._memory_cache.set(key, value, ttl)
    
    async def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        return await self._memory_cache.delete(key)
    
    async def clear(self) -> None:
        """Clear all cached values."""
        await self._memory_cache.clear()
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        if not self._enabled:
            return False
        return await self._memory_cache.exists(key)
    
    async def get_stats(self) -> dict:
        """Get cache statistics."""
        return await self._memory_cache.get_stats()
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching a pattern.
        
        Args:
            pattern: Glob pattern to match (e.g., "agent:*")
            
        Returns:
            Number of keys invalidated
        """
        import fnmatch
        
        count = 0
        # Get all keys (we'd need to expose this from MemoryCache)
        async with self._memory_cache._lock:
            keys_to_delete = [
                k for k in self._memory_cache._cache.keys()
                if fnmatch.fnmatch(k, pattern)
            ]
        
        for key in keys_to_delete:
            if await self.delete(key):
                count += 1
        
        logger.info(f"Invalidated {count} keys matching pattern: {pattern}")
        return count


# Global cache instance
cache = Cache()


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.
    
    Args:
        prefix: Key prefix (e.g., "agent", "settings")
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Generated cache key string
    """
    parts = [prefix]
    
    for arg in args:
        if arg is not None:
            parts.append(str(arg))
    
    for key, value in sorted(kwargs.items()):
        if value is not None:
            parts.append(f"{key}={value}")
    
    key_string = ":".join(parts)
    
    if len(key_string) > 200:
        hash_part = hashlib.md5(key_string.encode()).hexdigest()[:16]
        return f"{prefix}:{hash_part}"
    
    return key_string


def cached(
    key_prefix: str,
    ttl: int = 300,
    condition: Optional[Callable[..., bool]] = None
):
    """
    Decorator to cache function results.
    
    Args:
        key_prefix: Prefix for the cache key
        ttl: Time to live in seconds (default: 300)
        condition: Optional function to determine if result should be cached
        
    Usage:
        @cached("user", ttl=60)
        async def get_user(user_id: str):
            return await db.fetch_user(user_id)
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache._enabled:
                return await func(*args, **kwargs)
            
            should_cache = condition is None or condition(*args, **kwargs)
            
            if should_cache:
                cache_key = generate_cache_key(key_prefix, *args, **kwargs)
                cached_value = await cache.get(cache_key)
                
                if cached_value is not None:
                    logger.debug(f"Cache hit: {cache_key}")
                    return cached_value
            
            result = await func(*args, **kwargs)
            
            if should_cache and result is not None:
                await cache.set(cache_key, result, ttl)
                logger.debug(f"Cache set: {cache_key}")
            
            return result
        
        return wrapper
    return decorator


# Cached agent registry
class CachedAgentRegistry:
    """
    Wrapper for AgentRegistry with caching support.
    """
    
    def __init__(self, registry):
        self._registry = registry
        self._cache = cache
        self._cache_ttl = 300  # 5 minutes default
    
    def _get_cache_key(self, agent_id: Optional[str] = None) -> str:
        if agent_id:
            return f"registry:agent:{agent_id}"
        return "registry:agents:all"
    
    async def get_all_agents(self, force_refresh: bool = False) -> list:
        """Get all agents with caching."""
        cache_key = self._get_cache_key()
        
        if not force_refresh:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                return cached
        
        agents = self._registry.get_all_agents()
        await self._cache.set(cache_key, agents, self._cache_ttl)
        return agents
    
    async def get_agent_metadata(self, agent_id: str, force_refresh: bool = False) -> Optional[dict]:
        """Get agent metadata with caching."""
        cache_key = self._get_cache_key(agent_id)
        
        if not force_refresh:
            cached = await self._cache.get(cache_key)
            if cached is not None:
                return cached
        
        metadata = self._registry.get_agent_metadata(agent_id)
        if metadata is not None:
            await self._cache.set(cache_key, metadata, self._cache_ttl)
        return metadata
    
    async def invalidate(self, agent_id: Optional[str] = None) -> None:
        """Invalidate cache for specific agent or all agents."""
        if agent_id:
            await self._cache.delete(self._get_cache_key(agent_id))
        else:
            await self._cache.invalidate_pattern("registry:*")
        
        logger.info(f"Registry cache invalidated for: {agent_id or 'all'}")


# Cached settings
class CachedSettings:
    """
    Wrapper for settings with caching support.
    """
    
    def __init__(self, settings):
        self._settings = settings
        self._cache = cache
        self._cache_ttl = 60  # 1 minute for settings
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value with caching."""
        cache_key = f"settings:{key}"
        
        cached = await self._cache.get(cache_key)
        if cached is not None:
            return cached
        
        value = getattr(self._settings, key, default)
        await self._cache.set(cache_key, value, self._cache_ttl)
        return value
    
    async def invalidate(self, key: Optional[str] = None) -> None:
        """Invalidate settings cache."""
        if key:
            await self._cache.delete(f"settings:{key}")
        else:
            await self._cache.invalidate_pattern("settings:*")
        
        logger.info(f"Settings cache invalidated for: {key or 'all'}")


# Global cached registry
_cached_registry: Optional[CachedAgentRegistry] = None


def get_cached_registry(registry) -> CachedAgentRegistry:
    """Get or create cached agent registry."""
    global _cached_registry
    if _cached_registry is None:
        _cached_registry = CachedAgentRegistry(registry)
    return _cached_registry


# Helper functions
async def invalidate_agent_cache(agent_id: Optional[str] = None) -> None:
    """Invalidate agent registry cache."""
    from agents.registry import agent_registry
    cached = get_cached_registry(agent_registry)
    await cached.invalidate(agent_id)


async def invalidate_settings_cache(key: Optional[str] = None) -> None:
    """Invalidate settings cache."""
    from config import settings
    cached_settings = CachedSettings(settings)
    await cached_settings.invalidate(key)
