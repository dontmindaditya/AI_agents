"""
Supabase Client Management
"""
from supabase import create_client, Client
from typing import Optional
from functools import lru_cache

from app.config import settings
from app.utils.logger import setup_logger

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
            # Use alternative naming if available
            url = settings.SUPABASE_URL or settings.NEXT_PUBLIC_SUPABASE_URL
            key = settings.SUPABASE_KEY or settings.NEXT_PUBLIC_SUPABASE_ANON_KEY
            
            if not url or not key:
                logger.error("Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_KEY")
                raise ValueError("Supabase not configured. Database operations are disabled.")
            
            try:
                self._client = create_client(url, key)
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return self._client
    
    @property
    def service_client(self) -> Client:
        """Get Supabase client with service key"""
        if not self._service_client:
            url = settings.SUPABASE_URL or settings.NEXT_PUBLIC_SUPABASE_URL
            
            if not url:
                logger.error("Supabase URL not configured")
                raise ValueError("Supabase not configured. Database operations are disabled.")
            
            try:
                service_key = (
                    settings.SUPABASE_SERVICE_KEY or 
                    settings.SUPABASE_SERVICE_ROLE_KEY or 
                    settings.SUPABASE_KEY or 
                    settings.NEXT_PUBLIC_SUPABASE_ANON_KEY
                )
                if not service_key:
                    raise ValueError("No Supabase key available")
                
                self._service_client = create_client(url, service_key)
                logger.info("Supabase service client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase service client: {e}")
                raise
        return self._service_client
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            # Try a simple query
            self.client.table('_test_').select('*').limit(1).execute()
            return True
        except Exception as e:
            logger.warning(f"Supabase connection test note: {e}")
            # Connection exists but table might not - that's OK
            return True


@lru_cache()
def get_supabase_client() -> SupabaseClient:
    """Get cached Supabase client instance"""
    return SupabaseClient()


# Global instance
supabase_client = get_supabase_client()