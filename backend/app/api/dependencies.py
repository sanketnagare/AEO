"""API dependencies — Supabase client and future auth/rate limiting."""

from app.supabase_client import supabase

# Re-export for convenience
__all__ = ["supabase"]
