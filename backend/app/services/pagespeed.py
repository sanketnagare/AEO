"""Google PageSpeed Insights API async client."""

from typing import Optional
import httpx

from app.config import get_settings
from app.schemas.audit import PerformanceData
from app.logging_config import get_logger

logger = get_logger(__name__)


class PageSpeedClient:
    """Async wrapper for Google PageSpeed Insights API.

    Returns Core Web Vitals: LCP, CLS, INP, FCP, TTFB, and overall score.
    """

    BASE_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.pagespeed_api_key
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def analyze(self, url: str, strategy: str = "mobile") -> PerformanceData:
        """Analyze a URL's performance via PageSpeed Insights.

        Args:
            url: The page URL to analyze.
            strategy: "mobile" or "desktop".

        Returns:
            PerformanceData with Core Web Vitals.
        """
        params = {
            "url": url,
            "strategy": strategy,
            "category": "performance",
        }
        if self.api_key:
            params["key"] = self.api_key

        logger.info("PageSpeed analyze: %s (strategy=%s)", url, strategy)
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        result = self._parse_response(data)
        logger.info("PageSpeed result: score=%s, LCP=%s, CLS=%s, INP=%s",
                    result.performance_score, result.lcp, result.cls, result.inp)
        return result

    def _parse_response(self, data: dict) -> PerformanceData:
        """Extract Core Web Vitals from PageSpeed API response."""
        lighthouse = data.get("lighthouseResult", {})
        audits = lighthouse.get("audits", {})
        categories = lighthouse.get("categories", {})

        # Performance score (0-100)
        perf_category = categories.get("performance", {})
        performance_score = None
        if perf_category.get("score") is not None:
            performance_score = int(perf_category["score"] * 100)

        # LCP - Largest Contentful Paint (seconds)
        lcp = None
        lcp_audit = audits.get("largest-contentful-paint", {})
        if lcp_audit.get("numericValue") is not None:
            lcp = round(lcp_audit["numericValue"] / 1000, 2)

        # CLS - Cumulative Layout Shift
        cls_val = None
        cls_audit = audits.get("cumulative-layout-shift", {})
        if cls_audit.get("numericValue") is not None:
            cls_val = round(cls_audit["numericValue"], 3)

        # INP - Interaction to Next Paint (ms) — may be in experimental audits
        inp = None
        inp_audit = audits.get("interaction-to-next-paint", {})
        if inp_audit.get("numericValue") is not None:
            inp = int(inp_audit["numericValue"])

        # FCP - First Contentful Paint (seconds)
        fcp = None
        fcp_audit = audits.get("first-contentful-paint", {})
        if fcp_audit.get("numericValue") is not None:
            fcp = round(fcp_audit["numericValue"] / 1000, 2)

        # TTFB - Time to First Byte (ms)
        ttfb = None
        ttfb_audit = audits.get("server-response-time", {})
        if ttfb_audit.get("numericValue") is not None:
            ttfb = round(ttfb_audit["numericValue"], 0)

        # Speed Index (seconds)
        speed_index = None
        si_audit = audits.get("speed-index", {})
        if si_audit.get("numericValue") is not None:
            speed_index = round(si_audit["numericValue"] / 1000, 2)

        return PerformanceData(
            lcp=lcp,
            cls=cls_val,
            inp=inp,
            fcp=fcp,
            ttfb=ttfb,
            performance_score=performance_score,
            speed_index=speed_index,
        )


# Singleton instance
pagespeed_client = PageSpeedClient()
