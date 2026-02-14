"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.logging_config import setup_logging, get_logger
from app.api.routes import health, audit, auth

# Initialize logging before anything else
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown events."""
    settings = get_settings()
    logger.info("🚀 %s v%s starting... [env=%s]", settings.app_name, settings.app_version, settings.app_env)

    yield

    # Cleanup: close HTTP clients
    from app.services.firecrawl import firecrawl_client
    from app.services.pagespeed import pagespeed_client
    await firecrawl_client.close()
    await pagespeed_client.close()
    logger.info("👋 Shutdown complete.")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="AEO & GEO Autopilot Platform — Get cited by AI. On autopilot.",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount routers ──
app.include_router(health.router, prefix="/api")
app.include_router(audit.router, prefix="/api")
app.include_router(auth.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint — redirect to docs."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }
