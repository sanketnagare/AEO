"""Visibility snapshot model."""

import uuid
from datetime import datetime, date

from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class VisibilitySnapshot(Base):
    __tablename__ = "visibility_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(
        String(50), nullable=False  # chatgpt, perplexity, gemini, google_aio
    )
    query_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    brand_mentioned: Mapped[bool] = mapped_column(Boolean, default=False)
    brand_cited_as_source: Mapped[bool] = mapped_column(Boolean, default=False)
    competitor_mentions: Mapped[dict] = mapped_column(JSONB, nullable=True)
    raw_response_excerpt: Mapped[str] = mapped_column(Text, nullable=True)

    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    site = relationship("Site", back_populates="visibility_snapshots")
