"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    # App
    app_env: str = "development"
    app_version: str = "0.1.0"
    app_name: str = "AIVisibilityBot"
    frontend_url: str = "http://localhost:3000"

    # Database (Supabase PostgreSQL)
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/aivisibilitybot"

    # Firecrawl API
    firecrawl_api_key: str = ""
    firecrawl_base_url: str = "https://api.firecrawl.dev/v1"

    # Google PageSpeed Insights
    pagespeed_api_key: str = ""

    # LLM APIs (via LiteLLM)
    openai_api_key: str = ""
    gemini_api_key: str = ""
    anthropic_api_key: str = ""

    # Default LLM model for different tasks
    llm_model_fast: str = "gemini/gemini-2.0-flash"
    llm_model_quality: str = "gpt-4o"
    llm_model_cheap: str = "gpt-4o-mini"

    # Auth (Phase 8)
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
