"""Firecrawl API async client for web scraping and crawling."""

from typing import Optional
import httpx

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class FirecrawlClient:
    """Async wrapper for the Firecrawl API.

    Supports:
    - scrape: Extract content from a single page
    - crawl_start: Start a full site crawl
    - crawl_status: Check crawl progress
    - map: Discover all URLs on a site
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.firecrawl_api_key
        self.base_url = settings.firecrawl_base_url
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def scrape(
        self,
        url: str,
        formats: list[str] | None = None,
        only_main_content: bool = True,
    ) -> dict:
        """Scrape a single page.

        Args:
            url: The URL to scrape.
            formats: Output formats, e.g. ["markdown", "html"]. Defaults to both.
            only_main_content: If True, extract only the main content area.

        Returns:
            Dict with keys: markdown, html, metadata, etc.
        """
        payload = {
            "url": url,
            "formats": formats or ["markdown", "html"],
            "onlyMainContent": only_main_content,
        }
        logger.info("Scraping URL: %s", url)
        response = await self.client.post("/scrape", json=payload)
        response.raise_for_status()
        data = response.json()
        result = data.get("data", data)
        logger.info("Scrape complete: html_len=%d, md_len=%d, metadata_keys=%s",
                    len(result.get("html", "")),
                    len(result.get("markdown", "")),
                    list(result.get("metadata", {}).keys()))
        return result

    async def crawl_start(
        self,
        url: str,
        max_pages: int = 50,
        exclude_patterns: list[str] | None = None,
    ) -> dict:
        """Start a full site crawl (async — returns job ID).

        Args:
            url: The root URL to crawl.
            max_pages: Maximum number of pages to crawl.
            exclude_patterns: URL patterns to exclude.

        Returns:
            Dict with crawl job details including job_id.
        """
        payload = {
            "url": url,
            "limit": max_pages,
            "scrapeOptions": {
                "formats": ["markdown", "html"],
                "onlyMainContent": True,
            },
        }
        if exclude_patterns:
            payload["excludePatterns"] = exclude_patterns

        logger.info("Starting crawl: %s (max_pages=%d)", url, max_pages)
        response = await self.client.post("/crawl", json=payload)
        response.raise_for_status()
        result = response.json()
        logger.info("Crawl started: job_id=%s", result.get("id", "unknown"))
        return result

    async def crawl_status(self, job_id: str) -> dict:
        """Check the status of a crawl job.

        Args:
            job_id: The crawl job ID returned by crawl_start.

        Returns:
            Dict with status, completed count, total count, and page data.
        """
        response = await self.client.get(f"/crawl/{job_id}")
        response.raise_for_status()
        return response.json()

    async def map(self, url: str) -> dict:
        """Discover all URLs on a website (without scraping content).

        Args:
            url: The root URL to map.

        Returns:
            Dict with list of discovered URLs.
        """
        payload = {"url": url}
        response = await self.client.post("/map", json=payload)
        response.raise_for_status()
        return response.json()


# Singleton instance
firecrawl_client = FirecrawlClient()
