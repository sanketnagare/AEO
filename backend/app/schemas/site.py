"""Pydantic schemas for site endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SiteCreate(BaseModel):
    """Request to add a new site."""
    url: str
    name: Optional[str] = None


class SiteResponse(BaseModel):
    """Site data returned to client."""
    id: uuid.UUID
    url: str
    name: Optional[str] = None
    business_summary: Optional[str] = None
    industry: Optional[str] = None
    seo_score: Optional[float] = None
    aeo_score: Optional[float] = None
    geo_score: Optional[float] = None
    last_crawl_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CrawlStatusResponse(BaseModel):
    """Crawl job status."""
    job_id: uuid.UUID
    status: str
    pages_found: int = 0
    pages_crawled: int = 0
    error_message: Optional[str] = None
