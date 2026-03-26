"""
Tests for Cache Module

Tests for the caching system including:
- MemoryCache
- Cache interface
- Cached decorator
- Cache statistics
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock
import time
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))


class TestMemoryCache:
    """Tests for MemoryCache class."""

    @pytest.fixture
    def cache(self):
        """Create a fresh MemoryCache instance."""
        from services.cache import MemoryCache
        return MemoryCache(max_size=100, default_ttl=60)

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        """Test basic set and get operations."""
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self, cache):
        """Test getting a key that doesn't exist."""
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete(self, cache):
        """Test deleting a key."""
        await cache.set("key1", "value1")
        deleted = await cache.delete("key1")
        assert deleted is True
        
        result = await cache.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, cache):
        """Test deleting a nonexistent key."""
        deleted = await cache.delete("nonexistent")
        assert deleted is False

    @pytest.mark.asyncio
    async def test_clear(self, cache):
        """Test clearing the cache."""
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        
        await cache.clear()
        
        assert await cache.get("key1") is None
        assert await cache.get("key2") is None

    @pytest.mark.asyncio
    async def test_exists(self, cache):
        """Test checking if a key exists."""
        await cache.set("key1", "value1")
        
        assert await cache.exists("key1") is True
        assert await cache.exists("nonexistent") is False

    @pytest.mark.asyncio
    async def test_ttl_expiration(self):
        """Test that TTL expiration works."""
        from services.cache import MemoryCache
        cache = MemoryCache(default_ttl=1)
        
        await cache.set("key1", "value1")
        assert await cache.get("key1") == "value1"
        
        # Wait for TTL to expire
        await asyncio.sleep(1.5)
        
        assert await cache.get("key1") is None

    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        from services.cache import MemoryCache
        cache = MemoryCache(max_size=3, default_ttl=3600)
        
        await cache.set("key1", "value1")
        await cache.set("key2", "value2")
        await cache.set("key3", "value3")
        
        # Access key1 to make it recently used
        await cache.get("key1")
        
        # Add new key, should evict key2 (LRU)
        await cache.set("key4", "value4")
        
        assert await cache.get("key1") == "value1"  # Should exist
        assert await cache.get("key2") is None  # Should be evicted
        assert await cache.get("key3") == "value3"  # Should exist

    @pytest.mark.asyncio
    async def test_get_stats(self, cache):
        """Test cache statistics."""
        await cache.set("key1", "value1")
        await cache.get("key1")
        await cache.get("nonexistent")
        
        stats = await cache.get_stats()
        
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["sets"] == 1
        assert stats["size"] == 1

    @pytest.mark.asyncio
    async def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        from services.cache import MemoryCache
        cache = MemoryCache(default_ttl=1)
        
        await cache.set("key1", "value1")
        await asyncio.sleep(1.5)
        
        count = await cache.cleanup_expired()
        assert count == 1
        assert await cache.get("key1") is None


class TestCacheInterface:
    """Tests for the main Cache interface."""

    @pytest.fixture
    def cache(self):
        """Create a fresh Cache instance."""
        from services.cache import Cache
        return Cache()

    @pytest.mark.asyncio
    async def test_set_and_get(self, cache):
        """Test set and get operations."""
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_disable_cache(self, cache):
        """Test that disabled cache returns None."""
        cache.disable()
        
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        
        assert result is None
        
        cache.enable()
        
        await cache.set("key1", "value1")
        result = await cache.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_invalidate_pattern(self, cache):
        """Test pattern-based invalidation."""
        await cache.set("agent:frontend", "data1")
        await cache.set("agent:backend", "data2")
        await cache.set("settings:name", "data3")
        
        count = await cache.invalidate_pattern("agent:*")
        
        assert count == 2
        assert await cache.get("agent:frontend") is None
        assert await cache.get("agent:backend") is None
        assert await cache.get("settings:name") == "data3"


class TestGenerateCacheKey:
    """Tests for cache key generation."""

    def test_simple_key(self):
        """Test simple key generation."""
        from services.cache import generate_cache_key
        
        key = generate_cache_key("prefix")
        assert key == "prefix"

    def test_key_with_args(self):
        """Test key generation with arguments."""
        from services.cache import generate_cache_key
        
        key = generate_cache_key("prefix", "arg1", "arg2")
        assert key == "prefix:arg1:arg2"

    def test_key_with_kwargs(self):
        """Test key generation with keyword arguments."""
        from services.cache import generate_cache_key
        
        key = generate_cache_key("prefix", name="test", id=123)
        assert "name=test" in key
        assert "id=123" in key

    def test_key_with_none(self):
        """Test that None values are skipped."""
        from services.cache import generate_cache_key
        
        key = generate_cache_key("prefix", None, "arg2")
        assert key == "prefix:arg2"

    def test_key_truncation(self):
        """Test that long keys are truncated."""
        from services.cache import generate_cache_key
        
        long_arg = "a" * 300
        key = generate_cache_key("prefix", long_arg)
        
        assert len(key) <= 200


class TestCachedDecorator:
    """Tests for the cached decorator."""

    @pytest.mark.asyncio
    async def test_cached_function(self):
        """Test that cached decorator caches results."""
        from services.cache import cached, cache
        
        cache_instance = cache
        await cache_instance.clear()
        
        call_count = 0
        
        @cached("test", ttl=60)
        async def expensive_function():
            nonlocal call_count
            call_count += 1
            return {"result": "data"}
        
        # First call
        result1 = await expensive_function()
        assert result1 == {"result": "data"}
        assert call_count == 1
        
        # Second call should be cached
        result2 = await expensive_function()
        assert result2 == {"result": "data"}
        assert call_count == 1  # Still 1, not called again

    @pytest.mark.asyncio
    async def test_cache_disabled(self):
        """Test that cached decorator respects disabled cache."""
        from services.cache import cached, cache
        
        call_count = 0
        cache.disable()
        
        @cached("test", ttl=60)
        async def expensive_function():
            nonlocal call_count
            call_count += 1
            return {"result": "data"}
        
        await expensive_function()
        await expensive_function()
        
        assert call_count == 2  # Called twice because cache is disabled
        
        cache.enable()


class TestCachedAgentRegistry:
    """Tests for CachedAgentRegistry."""

    @pytest.mark.asyncio
    async def test_get_all_agents_caches(self):
        """Test that get_all_agents caches results."""
        from services.cache import get_cached_registry, cache
        
        await cache.clear()
        
        mock_registry = MagicMock()
        mock_registry.get_all_agents.return_value = [{"name": "Agent1"}]
        
        cached_registry = get_cached_registry(mock_registry)
        
        # First call
        result1 = await cached_registry.get_all_agents()
        assert result1 == [{"name": "Agent1"}]
        
        # Second call should be cached
        result2 = await cached_registry.get_all_agents()
        assert result2 == [{"name": "Agent1"}]
        
        # Registry should only be called once
        assert mock_registry.get_all_agents.call_count == 1

    @pytest.mark.asyncio
    async def test_force_refresh(self):
        """Test force_refresh bypasses cache."""
        from services.cache import MemoryCache, CachedAgentRegistry
        
        # Create a fresh cache for this test
        test_cache = MemoryCache()
        
        mock_registry = MagicMock()
        mock_registry.get_all_agents.side_effect = [
            [{"Name": "Agent1"}],
            [{"Name": "Agent2"}]
        ]
        
        cached_registry = CachedAgentRegistry(mock_registry)
        cached_registry._cache = test_cache
        
        result1 = await cached_registry.get_all_agents()
        
        # Clear the cache
        await test_cache.clear()
        
        result2 = await cached_registry.get_all_agents(force_refresh=True)
        
        assert result1 == [{"Name": "Agent1"}]
        assert result2 == [{"Name": "Agent2"}]
        assert mock_registry.get_all_agents.call_count == 2


class TestCacheStats:
    """Tests for cache statistics."""

    @pytest.mark.asyncio
    async def test_hit_rate_calculation(self):
        """Test that hit rate is calculated correctly."""
        from services.cache import MemoryCache
        
        cache = MemoryCache()
        
        await cache.set("key1", "value1")
        await cache.get("key1")  # hit
        await cache.get("key1")  # hit
        await cache.get("nonexistent")  # miss
        
        stats = await cache.get_stats()
        
        assert stats["hits"] == 2
        assert stats["misses"] == 1
        assert stats["hit_rate_percent"] == pytest.approx(66.67, 0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
