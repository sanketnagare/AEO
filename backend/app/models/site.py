"""Site model."""

import uuid
from datetime import datetime

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    business_summary: Mapped[str] = mapped_column(Text, nullable=True)
    industry: Mapped[str] = mapped_column(String(255), nullable=True)

    # CMS integration
    cms_type: Mapped[str] = mapped_column(String(50), nullable=True)  # wordpress, ghost, webflow
    cms_credentials: Mapped[str] = mapped_column(Text, nullable=True)  # encrypted JSON

    # Crawl data
    robots_txt_content: Mapped[str] = mapped_column(Text, nullable=True)
    sitemap_url: Mapped[str] = mapped_column(String(2048), nullable=True)

    # Aggregate scores (0-100)
    seo_score: Mapped[float] = mapped_column(Float, nullable=True)
    aeo_score: Mapped[float] = mapped_column(Float, nullable=True)
    geo_score: Mapped[float] = mapped_column(Float, nullable=True)

    last_crawl_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="sites")
    pages = relationship("Page", back_populates="site", cascade="all, delete-orphan")
    audit_results = relationship("AuditResult", back_populates="site", cascade="all, delete-orphan")
    content_items = relationship("ContentItem", back_populates="site", cascade="all, delete-orphan")
    visibility_snapshots = relationship("VisibilitySnapshot", back_populates="site", cascade="all, delete-orphan")
    crawl_jobs = relationship("CrawlJob", back_populates="site", cascade="all, delete-orphan")
