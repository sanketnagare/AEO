"""Content item model."""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ContentItem(Base):
    __tablename__ = "content_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    site_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(String(512), nullable=True)
    content_markdown: Mapped[str] = mapped_column(Text, nullable=True)
    content_html: Mapped[str] = mapped_column(Text, nullable=True)
    schema_markup_json: Mapped[dict] = mapped_column(JSONB, nullable=True)

    # Targeting
    target_questions: Mapped[dict] = mapped_column(JSONB, nullable=True)  # ["what is...", "how to..."]
    target_keywords: Mapped[dict] = mapped_column(JSONB, nullable=True)  # ["keyword1", "keyword2"]

    # Type & optimization
    content_type: Mapped[str] = mapped_column(
        String(50), nullable=False  # qa_article, comparison, guide, faq_page, how_to
    )
    optimization_type: Mapped[str] = mapped_column(
        String(10), nullable=False  # aeo, geo, seo
    )

    # Workflow status
    status: Mapped[str] = mapped_column(
        String(20), default="draft"  # draft, in_review, approved, published, declined
    )
    published_url: Mapped[str] = mapped_column(String(2048), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    site = relationship("Site", back_populates="content_items")
