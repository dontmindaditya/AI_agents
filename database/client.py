"""
Supabase Client for Main Backend

This module provides a singleton wrapper for Supabase client connections.
It supports both anonymous (anon) and service-level connections for
different access levels to the database.

Features:
- Connection pooling
- Lazy initialization
- Health monitoring
- Thread-safe operations

Usage:
    from database.client import supabase_client
    
    # For regular user operations (uses anon key)
    result = supabase_client.client.table("users").select("*").execute()
    
    # For admin operations (uses service key)
    result = supabase_client.service_client.table("users").insert(data).execute()

Environment Variables:
    - SUPABASE_URL: Your Supabase project URL
    - SUPABASE_KEY: Your Supabase anon key
    - SUPABASE_SERVICE_KEY: Your Supabase service role key
"""

from typing import Optional, Dict, Any
from functools import lru_cache
import httpx
from services.connection_pool import HTTPConnectionPool, get_http_client, PoolConfig
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SupabaseClient:
    """
    Supabase client wrapper providing lazy initialization of connections.
    
    This class provides two types of connections:
    - client: Uses anon key for public-facing operations
    - service_client: Uses service key for admin operations
    
    Features:
    - Connection pooling via shared HTTP client
    - Lazy initialization
    - Health monitoring
    - Error handling
    
    Attributes:
        _client: Cached anonymous client instance
        _service_client: Cached service client instance
        _http_pool: Shared HTTP connection pool
    """
    
    def __init__(self):
        self._client: Optional[Any] = None
        self._service_client: Optional[Any] = None
        self._http_pool: Optional[HTTPConnectionPool] = None
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the Supabase client with connection pooling."""
        if self._initialized:
            return
        
        try:
            from supabase import create_client, Client
            
            url = settings.SUPABASE_URL or settings.NEXT_PUBLIC_SUPABASE_URL
            key = settings.SUPABASE_KEY or settings.NEXT_PUBLIC_SUPABASE_ANON_KEY
            
            if not url or not key:
                logger.warning("Supabase configuration missing. Client will be unavailable.")
                return
            
            self._http_pool = await get_http_client()
            
            self._client = create_client(url, key)
            
            service_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY or settings.NEXT_PUBLIC_SUPABASE_ANON_KEY
            self._service_client = create_client(url, service_key)
            
            self._initialized = True
            logger.info("Supabase client initialized with connection pooling")
            
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise
    
    async def close(self) -> None:
        """Close the Supabase client."""
        self._client = None
        self._service_client = None
        self._initialized = False
        logger.info("Supabase client closed")
    
    @property
    def client(self) -> Any:
        """
        Get Supabase client with anon key.
        
        Returns:
            Client: Supabase client instance authenticated with anon key.
            
        Raises:
            RuntimeError: If Supabase is not configured or initialized.
        """
        if not self._initialized:
            raise RuntimeError(
                "Supabase client not initialized. Call initialize() first, "
                "or use supabase_client which auto-initializes."
            )
        if not self._client:
            raise RuntimeError("Supabase not configured.")
        return self._client
    
    @property
    def service_client(self) -> Any:
        """
        Get Supabase client with service key.
        
        Returns:
            Client: Supabase client instance authenticated with service key.
            
        Raises:
            RuntimeError: If Supabase is not configured or initialized.
        """
        if not self._initialized:
            raise RuntimeError(
                "Supabase client not initialized. Call initialize() first, "
                "or use supabase_client which auto-initializes."
            )
        if not self._service_client:
            raise RuntimeError("Supabase not configured.")
        return self._service_client
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status information."""
        return {
            "initialized": self._initialized,
            "has_client": self._client is not None,
            "has_service_client": self._service_client is not None,
            "http_pool": self._http_pool.get_stats() if self._http_pool else None,
        }


class AsyncSupabaseClient:
    """
    Async Supabase client with connection pooling.
    
    This client provides async methods and uses a shared
    HTTP connection pool for better performance.
    """
    
    def __init__(self, url: str, key: str, http_pool: HTTPConnectionPool):
        self._url = url
        self._key = key
        self._http_pool = http_pool
        self._rest_url = f"{url}/rest/v1"
        self._auth_url = f"{url}/auth/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for Supabase requests."""
        return {
            "apikey": self._key,
            "Authorization": f"Bearer {self._key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
    
    async def table(self, table_name: str) -> "TableQuery":
        """Get a table query builder."""
        return TableQuery(self, table_name)
    
    async def from_(self, table_name: str) -> "TableQuery":
        """Get a table query builder (alternate syntax)."""
        return await self.table(table_name)
    
    async def health_check(self) -> bool:
        """Check if Supabase is reachable."""
        try:
            response = await self._http_pool.get(
                f"{self._rest_url}/",
                headers=self._get_headers()
            )
            return response.status_code in (200, 201)
        except Exception:
            return False


class TableQuery:
    """Builder for Supabase table queries."""
    
    def __init__(self, client: AsyncSupabaseClient, table_name: str):
        self._client = client
        self._table_name = table_name
        self._url = f"{client._rest_url}/{table_name}"
        self._headers = client._get_headers()
        self._select = "*"
        self._filters = []
        self._order_by = None
        self._limit = None
        self._offset = None
    
    def select(self, columns: str = "*") -> "TableQuery":
        """Set columns to select."""
        self._select = columns
        return self
    
    def eq(self, column: str, value: Any) -> "TableQuery":
        """Add equality filter."""
        self._filters.append(f"{column}=eq.{value}")
        return self
    
    def neq(self, column: str, value: Any) -> "TableQuery":
        """Add not-equal filter."""
        self._filters.append(f"{column}=neq.{value}")
        return self
    
    def gt(self, column: str, value: Any) -> "TableQuery":
        """Add greater-than filter."""
        self._filters.append(f"{column}=gt.{value}")
        return self
    
    def lt(self, column: str, value: Any) -> "TableQuery":
        """Add less-than filter."""
        self._filters.append(f"{column}=lt.{value}")
        return self
    
    def order(self, column: str, desc: bool = False) -> "TableQuery":
        """Set ordering."""
        direction = "desc" if desc else "asc"
        self._order_by = f"{column}.order={direction}"
        return self
    
    def limit(self, count: int) -> "TableQuery":
        """Set result limit."""
        self._limit = f"limit={count}"
        return self
    
    def range(self, from_: int, to: int) -> "TableQuery":
        """Set pagination range."""
        self._offset = f"offset={from_}"
        self._limit = f"limit={to - from_ + 1}"
        return self
    
    def _build_url(self) -> str:
        """Build the query URL."""
        params = [f"select={self._select}"]
        params.extend(self._filters)
        if self._order_by:
            params.append(self._order_by)
        if self._limit:
            params.append(self._limit)
        if self._offset:
            params.append(self._offset)
        return f"{self._url}?{'&'.join(params)}"
    
    async def execute(self) -> Dict[str, Any]:
        """Execute the query."""
        url = self._build_url()
        response = await self._client._http_pool.get(url, headers=self._headers)
        return response.json()
    
    async def insert(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data."""
        url = f"{self._url}"
        response = await self._client._http_pool.post(
            url,
            headers=self._headers,
            json=data
        )
        return response.json()
    
    async def update(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update data."""
        url = self._build_url()
        response = await self._client._http_pool.patch(
            url,
            headers=self._headers,
            json=data
        )
        return response.json()
    
    async def delete(self) -> Dict[str, Any]:
        """Delete data."""
        url = self._build_url()
        response = await self._client._http_pool.delete(url, headers=self._headers)
        return response.json()


_supabase_client: Optional[SupabaseClient] = None


@lru_cache()
def get_supabase_client() -> SupabaseClient:
    """
    Get a cached Supabase client instance.
    
    Returns:
        SupabaseClient: Singleton instance of the Supabase client wrapper.
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client


async def initialize_supabase() -> None:
    """Initialize the global Supabase client."""
    client = get_supabase_client()
    await client.initialize()


async def close_supabase() -> None:
    """Close the global Supabase client."""
    global _supabase_client
    if _supabase_client:
        await _supabase_client.close()


supabase_client = get_supabase_client()
