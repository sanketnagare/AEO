"""Pydantic schemas for content endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ContentItemResponse(BaseModel):
    """Content item returned to client."""
    id: uuid.UUID
    title: str
    slug: Optional[str] = None
    content_type: str
    optimization_type: str
    status: str
    published_url: Optional[str] = None
    published_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ContentGenerateRequest(BaseModel):
    """Request to generate a new content item."""
    topic: Optional[str] = None  # Let agent choose if not specified
    content_type: Optional[str] = None
    optimization_type: Optional[str] = None  # aeo, geo, seo
