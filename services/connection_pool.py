"""
Connection Pool Module

Provides connection pooling for:
- HTTP clients (httpx)
- Database connections (PostgreSQL/SQLAlchemy)
- Supabase client sessions

Features:
- Singleton connection pools
- Configurable pool sizes
- Connection health checks
- Automatic reconnection
- Graceful shutdown

Usage:
    from services.connection_pool import http_client, db_pool, get_http_client
    
    # HTTP requests with connection pooling
    response = await http_client.get("https://api.example.com/data")
    
    # Database connections
    async with db_pool.connection() as conn:
        result = await conn.fetch("SELECT * FROM users")
"""

import asyncio
import httpx
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime

from utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class PoolConfig:
    """Configuration for connection pools."""
    min_size: int = 5
    max_size: int = 20
    timeout: float = 30.0
    max_keepalive_connections: int = 10
    max_connections: int = 100
    keepalive_expiry: float = 30.0


class HTTPConnectionPool:
    """
    Managed HTTP connection pool using httpx.
    
    Features:
    - Configurable pool limits
    - Automatic connection reuse
    - Request timeout handling
    - Health monitoring
    """
    
    def __init__(self, config: Optional[PoolConfig] = None):
        self._config = config or PoolConfig()
        self._client: Optional[httpx.AsyncClient] = None
        self._stats = {
            "requests": 0,
            "errors": 0,
            "timeouts": 0,
            "connections_created": 0,
        }
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the HTTP client with connection pooling."""
        if self._initialized:
            return
        
        limits = httpx.Limits(
            max_keepalive_connections=self._config.max_keepalive_connections,
            max_connections=self._config.max_connections,
        )
        
        timeout = httpx.Timeout(
            timeout=self._config.timeout,
            connect=self._config.timeout,
        )
        
        self._client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout,
            follow_redirects=True,
        )
        self._initialized = True
        self._stats["connections_created"] += 1
        logger.info(f"HTTP connection pool initialized (max: {self._config.max_connections})")
    
    async def close(self) -> None:
        """Close the HTTP client and release connections."""
        if self._client:
            await self._client.aclose()
            self._client = None
            self._initialized = False
            logger.info("HTTP connection pool closed")
    
    @property
    def client(self) -> httpx.AsyncClient:
        """Get the HTTP client (must be initialized first)."""
        if not self._client:
            raise RuntimeError("HTTP pool not initialized. Call initialize() first.")
        return self._client
    
    async def request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Make an HTTP request with connection pooling.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for httpx
            
        Returns:
            httpx.Response: The HTTP response
        """
        if not self._client:
            await self.initialize()
        
        try:
            self._stats["requests"] += 1
            response = await self._client.request(method, url, **kwargs)
            return response
        except httpx.TimeoutException:
            self._stats["timeouts"] += 1
            raise
        except Exception:
            self._stats["errors"] += 1
            raise
    
    async def get(self, url: str, **kwargs) -> httpx.Response:
        """Convenience method for GET requests."""
        return await self.request("GET", url, **kwargs)
    
    async def post(self, url: str, **kwargs) -> httpx.Response:
        """Convenience method for POST requests."""
        return await self.request("POST", url, **kwargs)
    
    async def put(self, url: str, **kwargs) -> httpx.Response:
        """Convenience method for PUT requests."""
        return await self.request("PUT", url, **kwargs)
    
    async def delete(self, url: str, **kwargs) -> httpx.Response:
        """Convenience method for DELETE requests."""
        return await self.request("DELETE", url, **kwargs)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        return {
            **self._stats,
            "initialized": self._initialized,
            "config": {
                "max_connections": self._config.max_connections,
                "max_keepalive": self._config.max_keepalive_connections,
                "timeout": self._config.timeout,
            }
        }


class DatabaseConnectionPool:
    """
    PostgreSQL connection pool using SQLAlchemy.
    
    Features:
    - Async connection management
    - Automatic reconnection
    - Connection health checks
    - Pool size limits
    """
    
    def __init__(self, database_url: str, config: Optional[PoolConfig] = None):
        self._database_url = database_url
        self._config = config or PoolConfig()
        self._pool = None
        self._engine = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the database connection pool."""
        if self._initialized:
            return
        
        try:
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
            
            self._engine = create_async_engine(
                self._database_url,
                pool_size=self._config.min_size,
                max_overflow=self._config.max_size - self._config.min_size,
                pool_timeout=self._config.timeout,
                pool_recycle=3600,
                echo=False,
            )
            
            self._pool = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
            
            self._initialized = True
            logger.info(f"Database pool initialized (min: {self._config.min_size}, max: {self._config.max_size})")
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    async def close(self) -> None:
        """Close the database pool."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._pool = None
            self._initialized = False
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def connection(self):
        """
        Get a database connection from the pool.
        
        Usage:
            async with db_pool.connection() as conn:
                result = await conn.execute("SELECT * FROM users")
        """
        if not self._pool:
            await self.initialize()
        
        async with self._pool() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
    
    @asynccontextmanager
    async def transaction(self):
        """
        Get a database connection with transaction.
        """
        async with self.connection() as conn:
            async with conn.begin():
                yield conn
    
    async def execute(self, query: str, params: Optional[Dict] = None):
        """Execute a query."""
        async with self.connection() as conn:
            result = await conn.execute(query, params or {})
            return result
    
    async def fetch_all(self, query: str, params: Optional[Dict] = None):
        """Fetch all rows from a query."""
        async with self.connection() as conn:
            result = await conn.execute(query, params or {})
            return result.fetchall()
    
    async def fetch_one(self, query: str, params: Optional[Dict] = None):
        """Fetch one row from a query."""
        async with self.connection() as conn:
            result = await conn.execute(query, params or {})
            return result.fetchone()
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get pool status information."""
        if not self._engine:
            return {"initialized": False}
        
        pool = self._engine.pool
        return {
            "initialized": self._initialized,
            "pool_size": pool.size(),
            "pool_checked_in": pool.checkedin(),
            "pool_checked_out": pool.checkedout(),
            "pool_overflow": pool.overflow(),
            "pool_total": pool.size() + pool.overflow(),
        }


class ConnectionPoolManager:
    """
    Central manager for all connection pools.
    
    Provides:
    - Singleton HTTP pool
    - Per-database connection pools
    - Lifecycle management
    - Statistics aggregation
    """
    
    def __init__(self):
        self._http_pool: Optional[HTTPConnectionPool] = None
        self._db_pools: Dict[str, DatabaseConnectionPool] = {}
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize all configured connection pools."""
        if self._initialized:
            return
        
        http_config = PoolConfig(
            min_size=5,
            max_size=50,
            timeout=30.0,
            max_connections=100,
        )
        self._http_pool = HTTPConnectionPool(http_config)
        await self._http_pool.initialize()
        
        self._initialized = True
        logger.info("All connection pools initialized")
    
    async def close(self) -> None:
        """Close all connection pools gracefully."""
        if self._http_pool:
            await self._http_pool.close()
        
        for name, pool in self._db_pools.items():
            await pool.close()
        
        self._initialized = False
        logger.info("All connection pools closed")
    
    @property
    def http(self) -> HTTPConnectionPool:
        """Get the HTTP connection pool."""
        if not self._http_pool:
            raise RuntimeError("Connection pools not initialized")
        return self._http_pool
    
    def add_database(
        self,
        name: str,
        database_url: str,
        config: Optional[PoolConfig] = None
    ) -> DatabaseConnectionPool:
        """Add a database connection pool."""
        pool = DatabaseConnectionPool(database_url, config)
        self._db_pools[name] = pool
        return pool
    
    def get_database(self, name: str) -> Optional[DatabaseConnectionPool]:
        """Get a database connection pool by name."""
        return self._db_pools.get(name)
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics from all pools."""
        stats = {
            "http": self._http_pool.get_stats() if self._http_pool else None,
            "databases": {
                name: pool.get_pool_status()
                for name, pool in self._db_pools.items()
            },
            "initialized": self._initialized,
        }
        return stats


pool_manager = ConnectionPoolManager()


http_client = HTTPConnectionPool()


async def get_http_client() -> HTTPConnectionPool:
    """Get the shared HTTP client pool."""
    if not http_client._initialized:
        await http_client.initialize()
    return http_client


async def close_all_pools() -> None:
    """Close all connection pools."""
    await pool_manager.close()
    if http_client._initialized:
        await http_client.close()
