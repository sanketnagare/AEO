"""API dependencies — DB session, future auth and rate limiting."""

from app.database import get_db

# Re-export for convenience
__all__ = ["get_db"]
