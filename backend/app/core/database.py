from supabase import create_client, Client
from app.core.config import settings


class SupabaseClient:
    """Supabase client wrapper for database and auth operations."""
    
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_KEY
            )
        return cls._instance
    
    @property
    def client(self) -> Client:
        """Get Supabase client instance."""
        return self._client


def get_supabase_client() -> Client:
    """Get Supabase client for dependency injection."""
    return SupabaseClient().client
