"""Page model."""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Page(Base):
    __tablename__ = "pages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=True)
    meta_description: Mapped[str] = mapped_column(Text, nullable=True)
    h1_text: Mapped[str] = mapped_column(String(512), nullable=True)

    # Content
    headings_json: Mapped[dict] = mapped_column(JSONB, nullable=True)  # [{level, text}]
    word_count: Mapped[int] = mapped_column(Integer, nullable=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=True)
    content_html: Mapped[str] = mapped_column(Text, nullable=True)
    schema_markup_json: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Links & media
    internal_links_count: Mapped[int] = mapped_column(Integer, default=0)
    external_links_count: Mapped[int] = mapped_column(Integer, default=0)
    images_json: Mapped[dict] = mapped_column(JSONB, nullable=True)  # [{src, alt, ...}]
    og_tags_json: Mapped[dict] = mapped_column(JSONB, nullable=True)
    canonical_url: Mapped[str] = mapped_column(String(2048), nullable=True)

    # Scores (0-100)
    seo_score: Mapped[float] = mapped_column(Float, nullable=True)
    aeo_score: Mapped[float] = mapped_column(Float, nullable=True)
    geo_score: Mapped[float] = mapped_column(Float, nullable=True)

    last_audited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    site = relationship("Site", back_populates="pages")
    audit_results = relationship("AuditResult", back_populates="page", cascade="all, delete-orphan")
