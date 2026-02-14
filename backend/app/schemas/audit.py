"""Pydantic schemas for audit endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class AuditRequest(BaseModel):
    """Request to audit a single URL."""
    url: str


class CheckResult(BaseModel):
    """Result of a single audit check."""
    check_name: str
    audit_type: str  # seo, aeo, geo
    severity: str  # critical, warning, info, pass
    message: str
    recommendation: Optional[str] = None
    current_value: Optional[str] = None
    expected_value: Optional[str] = None


class PerformanceData(BaseModel):
    """Core Web Vitals from PageSpeed Insights."""
    lcp: Optional[float] = None  # Largest Contentful Paint (seconds)
    cls: Optional[float] = None  # Cumulative Layout Shift
    inp: Optional[int] = None    # Interaction to Next Paint (ms)
    fcp: Optional[float] = None  # First Contentful Paint (seconds)
    ttfb: Optional[float] = None # Time to First Byte (ms)
    performance_score: Optional[int] = None  # 0-100
    speed_index: Optional[float] = None


class AuditScores(BaseModel):
    """Scores for SEO, AEO, and GEO."""
    seo_score: float = 0.0
    aeo_score: float = 0.0
    geo_score: float = 0.0
    overall_score: float = 0.0


class AuditReport(BaseModel):
    """Full audit report for a single page."""
    url: str
    scores: AuditScores
    performance: Optional[PerformanceData] = None
    seo_checks: list[CheckResult] = []
    aeo_checks: list[CheckResult] = []
    geo_checks: list[CheckResult] = []
    word_count: Optional[int] = None
    title: Optional[str] = None
    meta_description: Optional[str] = None
    audited_at: datetime


class StreamEvent(BaseModel):
    """SSE event sent from agent to terminal UI."""
    type: str  # info, success, warning, error, progress, complete
    message: str
    timestamp: datetime
    data: Optional[dict] = None
    stream_type: str = "instant"  # "instant" = appears immediately, "typing" = char-by-char typewriter
