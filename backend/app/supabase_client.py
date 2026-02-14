"""Supabase client singleton."""

from supabase import create_client, Client, ClientOptions
from app.config import get_settings


def get_supabase() -> Client:
    """Return a Supabase client instance."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)


# Singleton for convenience
supabase: Client = get_supabase()
