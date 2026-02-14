
import asyncio
import httpx
from urllib.parse import urlparse, urljoin
import xml.etree.ElementTree as ET
from app.logging_config import get_logger

logger = get_logger(__name__)

class RobotsService:
    async def analyze(self, url: str) -> dict:
        """
        Fetch robots.txt, find sitemaps, and count total pages.
        Returns:
            {
                "robots_txt_found": bool,
                "sitemaps_found": int,
                "total_pages": int,
                "sitemap_urls": list[str]
            }
        """
        domain = urlparse(url).netloc
        scheme = urlparse(url).scheme
        robots_url = f"{scheme}://{domain}/robots.txt"
        
        result = {
            "robots_txt_found": False,
            "sitemaps_found": 0,
            "total_pages": 0,
            "sitemap_urls": []
        }

        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(robots_url, timeout=5.0, follow_redirects=True)
                
                if resp.status_code == 200:
                    result["robots_txt_found"] = True
                    lines = resp.text.splitlines()
                    for line in lines:
                        if line.lower().startswith("sitemap:"):
                            sitemap_url = line.split(":", 1)[1].strip()
                            result["sitemap_urls"].append(sitemap_url)
                
                # If no sitemap in robots.txt, try standard location
                if not result["sitemap_urls"]:
                    standard_sitemap = f"{scheme}://{domain}/sitemap.xml"
                    sitemap_resp = await client.head(standard_sitemap, timeout=3.0)
                    if sitemap_resp.status_code == 200:
                         result["sitemap_urls"].append(standard_sitemap)

                result["sitemaps_found"] = len(result["sitemap_urls"])
                
                # Count pages from first 3 sitemaps (to avoid timeout on huge sites)
                total_pages = 0
                for sitemap in result["sitemap_urls"][:3]:
                    try:
                        s_resp = await client.get(sitemap, timeout=5.0)
                        if s_resp.status_code == 200:
                            # Simple XML parsing
                            try:
                                root = ET.fromstring(s_resp.content)
                                # Handle standard sitemap namespaces if present, or just find all 'loc'
                                # This is a naive count, but sufficient for estimation
                                urls = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                                if not urls:
                                    urls = root.findall(".//loc")
                                total_pages += len(urls)
                            except ET.ParseError:
                                # Fallback: simple string count if XML is malformed
                                total_pages += s_resp.text.count("<loc>")
                    except Exception as e:
                        logger.warning(f"Failed to parse sitemap {sitemap}: {e}")
                
                result["total_pages"] = total_pages

        except Exception as e:
            logger.error(f"Robots.txt analysis failed for {url}: {e}")
        
        return result

robots_service = RobotsService()
