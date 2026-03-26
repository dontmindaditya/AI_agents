"""
Tests for Connection Pool Module

Tests for HTTP and database connection pooling.
"""
import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import sys
from pathlib import Path

backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))


class TestPoolConfig:
    """Tests for PoolConfig dataclass."""

    def test_pool_config_defaults(self):
        """Test default pool configuration."""
        from services.connection_pool import PoolConfig
        
        config = PoolConfig()
        
        assert config.min_size == 5
        assert config.max_size == 20
        assert config.timeout == 30.0
        assert config.max_keepalive_connections == 10
        assert config.max_connections == 100
        assert config.keepalive_expiry == 30.0

    def test_pool_config_custom(self):
        """Test custom pool configuration."""
        from services.connection_pool import PoolConfig
        
        config = PoolConfig(
            min_size=10,
            max_size=50,
            timeout=60.0,
        )
        
        assert config.min_size == 10
        assert config.max_size == 50
        assert config.timeout == 60.0


class TestHTTPConnectionPool:
    """Tests for HTTPConnectionPool class."""

    @pytest.fixture
    def pool(self):
        """Create a fresh HTTPConnectionPool instance."""
        from services.connection_pool import HTTPConnectionPool, PoolConfig
        config = PoolConfig(max_connections=10)
        return HTTPConnectionPool(config)

    @pytest.mark.asyncio
    async def test_initialize(self, pool):
        """Test pool initialization."""
        await pool.initialize()
        
        assert pool._initialized is True
        assert pool._client is not None

    @pytest.mark.asyncio
    async def test_double_initialize(self, pool):
        """Test that double initialization doesn't create new client."""
        await pool.initialize()
        first_client = pool._client
        
        await pool.initialize()
        
        assert pool._client is first_client

    @pytest.mark.asyncio
    async def test_close(self, pool):
        """Test pool close."""
        await pool.initialize()
        await pool.close()
        
        assert pool._initialized is False
        assert pool._client is None

    @pytest.mark.asyncio
    async def test_client_property_raises_when_not_initialized(self, pool):
        """Test that accessing client before init raises error."""
        with pytest.raises(RuntimeError):
            _ = pool.client

    @pytest.mark.asyncio
    async def test_get_stats(self, pool):
        """Test getting pool statistics."""
        stats = pool.get_stats()
        
        assert "initialized" in stats
        assert "config" in stats
        assert "requests" in stats
        assert stats["initialized"] is False


class TestDatabaseConnectionPool:
    """Tests for DatabaseConnectionPool class."""

    def test_init(self):
        """Test pool initialization."""
        from services.connection_pool import DatabaseConnectionPool, PoolConfig
        
        pool = DatabaseConnectionPool(
            database_url="postgresql://localhost/test",
            config=PoolConfig(min_size=2, max_size=10)
        )
        
        assert pool._database_url == "postgresql://localhost/test"
        assert pool._initialized is False

    def test_get_pool_status_not_initialized(self):
        """Test pool status when not initialized."""
        from services.connection_pool import DatabaseConnectionPool
        
        pool = DatabaseConnectionPool("postgresql://localhost/test")
        status = pool.get_pool_status()
        
        assert status["initialized"] is False


class TestConnectionPoolManager:
    """Tests for ConnectionPoolManager class."""

    @pytest.fixture
    def manager(self):
        """Create a fresh ConnectionPoolManager instance."""
        from services.connection_pool import ConnectionPoolManager
        return ConnectionPoolManager()

    @pytest.mark.asyncio
    async def test_initialize(self, manager):
        """Test manager initialization."""
        await manager.initialize()
        
        assert manager._initialized is True
        assert manager._http_pool is not None

    @pytest.mark.asyncio
    async def test_close(self, manager):
        """Test manager close."""
        await manager.initialize()
        await manager.close()
        
        assert manager._initialized is False

    def test_add_database(self, manager):
        """Test adding a database pool."""
        pool = manager.add_database(
            name="test_db",
            database_url="postgresql://localhost/test"
        )
        
        assert pool is not None
        assert manager.get_database("test_db") is pool

    def test_get_database_not_found(self, manager):
        """Test getting non-existent database."""
        result = manager.get_database("nonexistent")
        
        assert result is None

    def test_get_all_stats(self, manager):
        """Test getting all statistics."""
        stats = manager.get_all_stats()
        
        assert "http" in stats
        assert "databases" in stats
        assert "initialized" in stats


class TestGlobalHttpClient:
    """Tests for global HTTP client."""

    @pytest.mark.asyncio
    async def test_get_http_client(self):
        """Test getting the global HTTP client."""
        from services.connection_pool import get_http_client
        
        client = await get_http_client()
        
        assert client is not None
        assert client._initialized is True


class TestConnectionPoolIntegration:
    """Integration tests for connection pools."""

    @pytest.mark.asyncio
    async def test_pool_stats_tracking(self):
        """Test that pool tracks statistics."""
        from services.connection_pool import HTTPConnectionPool, PoolConfig
        
        config = PoolConfig(max_connections=5)
        pool = HTTPConnectionPool(config)
        
        await pool.initialize()
        
        stats = pool.get_stats()
        
        assert stats["requests"] == 0
        assert stats["errors"] == 0

    @pytest.mark.asyncio
    async def test_pool_config_in_stats(self):
        """Test that pool config is included in stats."""
        from services.connection_pool import HTTPConnectionPool, PoolConfig
        
        config = PoolConfig(
            max_connections=50,
            max_keepalive_connections=20,
            timeout=60.0
        )
        pool = HTTPConnectionPool(config)
        
        stats = pool.get_stats()
        
        assert stats["config"]["max_connections"] == 50
        assert stats["config"]["max_keepalive"] == 20
        assert stats["config"]["timeout"] == 60.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
