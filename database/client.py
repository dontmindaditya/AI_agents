"""
Supabase Client for Main Backend
"""
from supabase import create_client, Client
from typing import Optional
from functools import lru_cache
import os
from config import settings
from utils.logger import setup_logger

logger = setup_logger(__name__)

class SupabaseClient:
    """Supabase client wrapper"""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        """Get Supabase client with anon key"""
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
        """Get Supabase client with service key"""
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
    return SupabaseClient()

# Global instance
supabase_client = get_supabase_client()
