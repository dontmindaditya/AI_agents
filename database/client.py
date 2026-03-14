"""
Supabase Client for Main Backend

This module provides a singleton wrapper for Supabase client connections.
It supports both anonymous (anon) and service-level connections for
different access levels to the database.

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

from supabase import create_client, Client
from typing import Optional
from functools import lru_cache
import os
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)


class SupabaseClient:
    """
    Supabase client wrapper providing lazy initialization of connections.
    
    This class provides two types of connections:
    - client: Uses anon key for public-facing operations
    - service_client: Uses service key for admin operations
    
    Attributes:
        _client: Cached anonymous client instance
        _service_client: Cached service client instance
    """
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """
        Get Supabase client with anon key.
        
        Returns:
            Client: Supabase client instance authenticated with anon key.
            
        Raises:
            ValueError: If SUPABASE_URL or SUPABASE_KEY is not configured.
        """
        if not self._client:
            url = settings.SUPABASE_URL or settings.NEXT_PUBLIC_SUPABASE_URL
            key = settings.SUPABASE_KEY or settings.NEXT_PUBLIC_SUPABASE_ANON_KEY
            
            if not url or not key:
                logger.error("Supabase configuration missing.")
                raise ValueError("Supabase not configured.")
            
            try:
                self._client = create_client(url, key)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return self._client
    
    @property
    def service_client(self) -> Client:
        """
        Get Supabase client with service key.
        
        Returns:
            Client: Supabase client instance authenticated with service key.
            
        Raises:
            ValueError: If SUPABASE_URL or SUPABASE_SERVICE_KEY is not configured.
        """
        if not self._service_client:
            url = settings.SUPABASE_URL or settings.NEXT_PUBLIC_SUPABASE_URL
            key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY or settings.NEXT_PUBLIC_SUPABASE_ANON_KEY
            
            if not url or not key:
                logger.error("Supabase configuration missing.")
                raise ValueError("Supabase not configured.")
            
            try:
                self._service_client = create_client(url, key)
            except Exception as e:
                logger.error(f"Failed to initialize Supabase service client: {e}")
                raise
        return self._service_client


@lru_cache()
def get_supabase_client() -> SupabaseClient:
    """
    Get a cached Supabase client instance.
    
    Returns:
        SupabaseClient: Singleton instance of the Supabase client wrapper.
    """
    return SupabaseClient()


# Global instance
supabase_client = get_supabase_client()
