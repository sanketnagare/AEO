"""SEO audit check functions — 27 checks.

Each check function takes parsed HTML (BeautifulSoup) and/or page metadata,
and returns a CheckResult with severity and recommendation.

Phase 1 will implement all 27 checks. This module provides the structure.
"""

from typing import Optional
from bs4 import BeautifulSoup

from app.schemas.audit import CheckResult
from app.logging_config import get_logger

logger = get_logger(__name__)


def run_all_seo_checks(
    html: str,
    markdown: str,
    url: str,
    metadata: Optional[dict] = None,
) -> list[CheckResult]:
    """Run all 27 SEO checks on a page.

    Args:
        html: Raw HTML string.
        markdown: Extracted markdown content.
        url: Page URL.
        metadata: Firecrawl metadata dict.

    Returns:
        List of CheckResult for each check.
    """
    soup = BeautifulSoup(html, "lxml") if html else BeautifulSoup("", "lxml")
    meta = metadata or {}
    results = []
    logger.info("Starting SEO checks for URL (html_len=%d, md_len=%d)", len(html or ""), len(markdown or ""))

    # Title & Meta (5 checks)
    results.append(check_title_exists(soup))
    results.append(check_title_length(soup))
    results.append(check_meta_description_exists(soup))
    results.append(check_meta_description_length(soup))
    results.append(check_meta_keywords(soup))

    # Headings (3 checks)
    results.append(check_h1_exists(soup))
    results.append(check_h1_count(soup))
    results.append(check_heading_hierarchy(soup))

    # Content (4 checks)
    results.append(check_word_count(markdown))
    results.append(check_content_readability(markdown))
    results.append(check_keyword_density(soup, markdown))
    results.append(check_duplicate_content(soup))

    # Links (3 checks)
    results.append(check_internal_links(soup, url))
    results.append(check_external_links(soup, url))
    results.append(check_broken_links(soup))

    # Images (2 checks)
    results.append(check_images_alt_text(soup))
    results.append(check_image_formats(soup))

    # Technical (6 checks)
    results.append(check_ssl(url))
    results.append(check_canonical_tag(soup))
    results.append(check_viewport_meta(soup))
    results.append(check_page_size(html))
    results.append(check_robots_meta(soup))
    results.append(check_lang_attribute(soup))

    # Structured Data (2 checks)
    results.append(check_schema_markup(soup))
    results.append(check_schema_validity(soup))

    # Social & Discovery (2 checks)
    results.append(check_og_tags(soup))
    results.append(check_sitemap_reference(soup))

    logger.info("SEO checks complete: %d results (%d pass, %d warn, %d critical)",
                len(results),
                sum(1 for r in results if r.severity == "pass"),
                sum(1 for r in results if r.severity == "warning"),
                sum(1 for r in results if r.severity == "critical"))
    return results


# ──────────────────────────────────────────────
# Title & Meta (5 checks)
# ──────────────────────────────────────────────

def check_title_exists(soup: BeautifulSoup) -> CheckResult:
    """Check 1: Title tag exists."""
    title = soup.find("title")
    if not title or not title.string or not title.string.strip():
        return CheckResult(
            check_name="title_exists",
            audit_type="seo",
            severity="critical",
            message="Title tag is missing",
            recommendation="Add a descriptive <title> tag between 50-60 characters.",
            current_value=None,
            expected_value="Non-empty title tag",
        )
    return CheckResult(
        check_name="title_exists",
        audit_type="seo",
        severity="pass",
        message=f"Title tag found: \"{title.string.strip()[:80]}\"",
        current_value=title.string.strip(),
    )


def check_title_length(soup: BeautifulSoup) -> CheckResult:
    """Check 2: Title tag is optimal length (50-60 chars)."""
    title = soup.find("title")
    if not title or not title.string:
        return CheckResult(
            check_name="title_length",
            audit_type="seo",
            severity="critical",
            message="No title tag to check length",
            current_value="N/A",
            expected_value="50-60 characters",
        )
    length = len(title.string.strip())
    if length < 30:
        return CheckResult(
            check_name="title_length",
            audit_type="seo",
            severity="warning",
            message=f"Title too short ({length} chars)",
            recommendation="Lengthen title to 50-60 characters for best SERP display.",
            current_value=str(length),
            expected_value="50-60 characters",
        )
    if length > 60:
        return CheckResult(
            check_name="title_length",
            audit_type="seo",
            severity="warning",
            message=f"Title too long ({length} chars) — may be truncated",
            recommendation="Shorten title to 60 characters or less.",
            current_value=str(length),
            expected_value="50-60 characters",
        )
    return CheckResult(
        check_name="title_length",
        audit_type="seo",
        severity="pass",
        message=f"Title length OK ({length} chars)",
        current_value=str(length),
    )


def check_meta_description_exists(soup: BeautifulSoup) -> CheckResult:
    """Check 3: Meta description exists."""
    meta = soup.find("meta", attrs={"name": "description"})
    if not meta or not meta.get("content", "").strip():
        return CheckResult(
            check_name="meta_description_exists",
            audit_type="seo",
            severity="critical",
            message="Meta description is missing",
            recommendation="Add a meta description between 150-160 characters with target keywords.",
        )
    desc = meta["content"].strip()
    return CheckResult(
        check_name="meta_description_exists",
        audit_type="seo",
        severity="pass",
        message=f"Meta description found ({len(desc)} chars)",
        current_value=desc[:100] + ("..." if len(desc) > 100 else ""),
    )


def check_meta_description_length(soup: BeautifulSoup) -> CheckResult:
    """Check 4: Meta description optimal length (150-160 chars)."""
    meta = soup.find("meta", attrs={"name": "description"})
    if not meta or not meta.get("content", "").strip():
        return CheckResult(
            check_name="meta_description_length",
            audit_type="seo",
            severity="critical",
            message="No meta description to check length",
            current_value="N/A",
            expected_value="150-160 characters",
        )
    length = len(meta["content"].strip())
    if length < 120:
        return CheckResult(
            check_name="meta_description_length",
            audit_type="seo",
            severity="warning",
            message=f"Meta description too short ({length} chars)",
            recommendation="Expand to 150-160 characters for best SERP display.",
            current_value=str(length),
            expected_value="150-160 characters",
        )
    if length > 160:
        return CheckResult(
            check_name="meta_description_length",
            audit_type="seo",
            severity="warning",
            message=f"Meta description too long ({length} chars)",
            recommendation="Shorten to 160 characters or less.",
            current_value=str(length),
            expected_value="150-160 characters",
        )
    return CheckResult(
        check_name="meta_description_length",
        audit_type="seo",
        severity="pass",
        message=f"Meta description length OK ({length} chars)",
        current_value=str(length),
    )


def check_meta_keywords(soup: BeautifulSoup) -> CheckResult:
    """Check 5: Meta keywords tag (informational — not a ranking factor)."""
    meta = soup.find("meta", attrs={"name": "keywords"})
    if not meta or not meta.get("content", "").strip():
        return CheckResult(
            check_name="meta_keywords",
            audit_type="seo",
            severity="info",
            message="No meta keywords tag (not a ranking factor, informational only)",
        )
    return CheckResult(
        check_name="meta_keywords",
        audit_type="seo",
        severity="pass",
        message="Meta keywords tag present",
        current_value=meta["content"].strip()[:100],
    )


# ──────────────────────────────────────────────
# Headings (3 checks)
# ──────────────────────────────────────────────

def check_h1_exists(soup: BeautifulSoup) -> CheckResult:
    """Check 6: H1 tag exists."""
    h1 = soup.find("h1")
    if not h1:
        return CheckResult(
            check_name="h1_exists",
            audit_type="seo",
            severity="critical",
            message="No H1 tag found",
            recommendation="Add exactly one H1 tag with your primary keyword.",
        )
    text = h1.get_text(strip=True)
    return CheckResult(
        check_name="h1_exists",
        audit_type="seo",
        severity="pass",
        message=f"H1 found: \"{text[:80]}\"",
        current_value=text,
    )


def check_h1_count(soup: BeautifulSoup) -> CheckResult:
    """Check 7: Exactly one H1 tag."""
    h1s = soup.find_all("h1")
    count = len(h1s)
    if count == 0:
        return CheckResult(
            check_name="h1_count",
            audit_type="seo",
            severity="critical",
            message="No H1 tag found",
            recommendation="Add exactly one H1 tag.",
            current_value="0",
            expected_value="1",
        )
    if count > 1:
        return CheckResult(
            check_name="h1_count",
            audit_type="seo",
            severity="warning",
            message=f"Multiple H1 tags found ({count})",
            recommendation="Use exactly one H1 per page. Use H2/H3 for sub-headings.",
            current_value=str(count),
            expected_value="1",
        )
    return CheckResult(
        check_name="h1_count",
        audit_type="seo",
        severity="pass",
        message="Exactly one H1 tag ✓",
        current_value="1",
    )


def check_heading_hierarchy(soup: BeautifulSoup) -> CheckResult:
    """Check 8: Proper H1→H2→H3 hierarchy (no skipping levels)."""
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    if not headings:
        return CheckResult(
            check_name="heading_hierarchy",
            audit_type="seo",
            severity="warning",
            message="No headings found on page",
            recommendation="Add headings (H1, H2, H3) to structure your content.",
        )

    levels = [int(h.name[1]) for h in headings]
    skipped = False
    for i in range(1, len(levels)):
        if levels[i] > levels[i - 1] + 1:
            skipped = True
            break

    if skipped:
        return CheckResult(
            check_name="heading_hierarchy",
            audit_type="seo",
            severity="warning",
            message="Heading hierarchy skips levels (e.g. H1 → H3)",
            recommendation="Maintain proper hierarchy: H1 → H2 → H3 without skipping.",
            current_value=" → ".join(f"H{l}" for l in levels[:10]),
        )
    return CheckResult(
        check_name="heading_hierarchy",
        audit_type="seo",
        severity="pass",
        message="Heading hierarchy is correct",
        current_value=" → ".join(f"H{l}" for l in levels[:10]),
    )


# ──────────────────────────────────────────────
# Content (4 checks)
# ──────────────────────────────────────────────

def check_word_count(markdown: str) -> CheckResult:
    """Check 9: Adequate word count."""
    words = len(markdown.split()) if markdown else 0
    if words < 300:
        return CheckResult(
            check_name="word_count",
            audit_type="seo",
            severity="warning",
            message=f"Thin content ({words} words)",
            recommendation="Aim for 1000+ words for articles, 300+ for pages.",
            current_value=str(words),
            expected_value="300+ words",
        )
    if words < 1000:
        return CheckResult(
            check_name="word_count",
            audit_type="seo",
            severity="info",
            message=f"Content length: {words} words (adequate for a page)",
            current_value=str(words),
        )
    return CheckResult(
        check_name="word_count",
        audit_type="seo",
        severity="pass",
        message=f"Good content length: {words} words",
        current_value=str(words),
    )


def check_content_readability(markdown: str) -> CheckResult:
    """Check 10: Readability score (Flesch-Kincaid)."""
    try:
        import textstat
        if not markdown or len(markdown.split()) < 20:
            return CheckResult(
                check_name="readability",
                audit_type="seo",
                severity="info",
                message="Not enough content to assess readability",
            )
        score = textstat.flesch_reading_ease(markdown)
        if score < 30:
            level = "Very difficult to read"
            severity = "warning"
        elif score < 50:
            level = "Difficult to read"
            severity = "info"
        elif score < 60:
            level = "Fairly difficult"
            severity = "info"
        elif score < 70:
            level = "Standard"
            severity = "pass"
        else:
            level = "Easy to read"
            severity = "pass"

        return CheckResult(
            check_name="readability",
            audit_type="seo",
            severity=severity,
            message=f"Readability: {level} (Flesch score: {score:.0f})",
            recommendation="Aim for a score of 60+ for general audiences." if score < 60 else None,
            current_value=f"{score:.0f}",
            expected_value="60+",
        )
    except Exception:
        return CheckResult(
            check_name="readability",
            audit_type="seo",
            severity="info",
            message="Could not calculate readability score",
        )


def check_keyword_density(soup: BeautifulSoup, markdown: str) -> CheckResult:
    """Check 11: Placeholder — keyword density requires knowing the target keyword."""
    return CheckResult(
        check_name="keyword_density",
        audit_type="seo",
        severity="info",
        message="Keyword density check requires target keyword (available in full site audit)",
    )


def check_duplicate_content(soup: BeautifulSoup) -> CheckResult:
    """Check 12: Placeholder — duplicate content detection (requires multi-page comparison)."""
    return CheckResult(
        check_name="duplicate_content",
        audit_type="seo",
        severity="info",
        message="Duplicate content check available in full site audit mode",
    )


# ──────────────────────────────────────────────
# Links (3 checks)
# ──────────────────────────────────────────────

def check_internal_links(soup: BeautifulSoup, url: str) -> CheckResult:
    """Check 13: Internal links present."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    links = soup.find_all("a", href=True)
    internal = []
    for l in links:
        href = l["href"]
        try:
            if href.startswith("/") or href.startswith("#"):
                internal.append(l)
            elif href.startswith("http") and domain in urlparse(href).netloc:
                internal.append(l)
        except Exception:
            pass  # Skip malformed URLs
    count = len(internal)
    if count < 3:
        return CheckResult(
            check_name="internal_links",
            audit_type="seo",
            severity="warning",
            message=f"Only {count} internal links found",
            recommendation="Add at least 3 internal links to related pages.",
            current_value=str(count),
            expected_value="3+",
        )
    return CheckResult(
        check_name="internal_links",
        audit_type="seo",
        severity="pass",
        message=f"{count} internal links found",
        current_value=str(count),
    )


def check_external_links(soup: BeautifulSoup, url: str) -> CheckResult:
    """Check 14: External links to authority sites."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    links = soup.find_all("a", href=True)
    external = []
    for l in links:
        href = l["href"]
        try:
            if href.startswith("http") and domain not in urlparse(href).netloc:
                external.append(l)
        except Exception:
            pass  # Skip malformed URLs
    count = len(external)
    if count == 0:
        return CheckResult(
            check_name="external_links",
            audit_type="seo",
            severity="info",
            message="No external links found",
            recommendation="Add links to authoritative sources for credibility.",
            current_value="0",
        )
    return CheckResult(
        check_name="external_links",
        audit_type="seo",
        severity="pass",
        message=f"{count} external links found",
        current_value=str(count),
    )


def check_broken_links(soup: BeautifulSoup) -> CheckResult:
    """Check 15: Placeholder — broken link detection (requires HTTP requests)."""
    return CheckResult(
        check_name="broken_links",
        audit_type="seo",
        severity="info",
        message="Broken link check available in full site audit mode",
    )


# ──────────────────────────────────────────────
# Images (2 checks)
# ──────────────────────────────────────────────

def check_images_alt_text(soup: BeautifulSoup) -> CheckResult:
    """Check 16: All images have alt text."""
    images = soup.find_all("img")
    if not images:
        return CheckResult(
            check_name="images_alt_text",
            audit_type="seo",
            severity="pass",
            message="No images found on page",
        )
    missing = [img for img in images if not img.get("alt", "").strip()]
    if missing:
        return CheckResult(
            check_name="images_alt_text",
            audit_type="seo",
            severity="warning",
            message=f"{len(missing)}/{len(images)} images missing alt text",
            recommendation="Add descriptive alt text to all images for accessibility and SEO.",
            current_value=f"{len(missing)} missing",
            expected_value="0 missing",
        )
    return CheckResult(
        check_name="images_alt_text",
        audit_type="seo",
        severity="pass",
        message=f"All {len(images)} images have alt text",
        current_value=str(len(images)),
    )


def check_image_formats(soup: BeautifulSoup) -> CheckResult:
    """Check 17: Modern image formats (WebP/AVIF)."""
    images = soup.find_all("img", src=True)
    if not images:
        return CheckResult(
            check_name="image_formats",
            audit_type="seo",
            severity="pass",
            message="No images to check format",
        )
    modern = [img for img in images if any(img["src"].lower().endswith(ext)
              for ext in [".webp", ".avif", ".svg"])]
    legacy = len(images) - len(modern)
    if legacy > 0:
        return CheckResult(
            check_name="image_formats",
            audit_type="seo",
            severity="info",
            message=f"{legacy}/{len(images)} images use legacy formats (JPG/PNG/GIF)",
            recommendation="Consider converting to WebP/AVIF for smaller file sizes.",
            current_value=f"{legacy} legacy",
        )
    return CheckResult(
        check_name="image_formats",
        audit_type="seo",
        severity="pass",
        message=f"All {len(images)} images use modern formats",
    )


# ──────────────────────────────────────────────
# Technical (6 checks)
# ──────────────────────────────────────────────

def check_ssl(url: str) -> CheckResult:
    """Check 18: HTTPS."""
    if url.startswith("https://"):
        return CheckResult(
            check_name="ssl",
            audit_type="seo",
            severity="pass",
            message="SSL/HTTPS enabled ✓",
        )
    return CheckResult(
        check_name="ssl",
        audit_type="seo",
        severity="critical",
        message="Site is not using HTTPS",
        recommendation="Enable SSL/HTTPS — it's a ranking factor and security requirement.",
        current_value="HTTP",
        expected_value="HTTPS",
    )


def check_canonical_tag(soup: BeautifulSoup) -> CheckResult:
    """Check 19: Canonical tag present."""
    canonical = soup.find("link", attrs={"rel": "canonical"})
    if not canonical or not canonical.get("href"):
        return CheckResult(
            check_name="canonical_tag",
            audit_type="seo",
            severity="warning",
            message="No canonical tag found",
            recommendation="Add a <link rel='canonical'> tag to prevent duplicate content issues.",
        )
    return CheckResult(
        check_name="canonical_tag",
        audit_type="seo",
        severity="pass",
        message=f"Canonical tag found: {canonical['href'][:80]}",
        current_value=canonical["href"],
    )


def check_viewport_meta(soup: BeautifulSoup) -> CheckResult:
    """Check 20: Mobile viewport meta tag."""
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        return CheckResult(
            check_name="viewport_meta",
            audit_type="seo",
            severity="critical",
            message="No viewport meta tag — page may not be mobile-friendly",
            recommendation="Add <meta name='viewport' content='width=device-width, initial-scale=1'>.",
        )
    return CheckResult(
        check_name="viewport_meta",
        audit_type="seo",
        severity="pass",
        message="Viewport meta tag present ✓",
        current_value=viewport.get("content", ""),
    )


def check_page_size(html: str) -> CheckResult:
    """Check 21: Page size under 3MB."""
    size_bytes = len(html.encode("utf-8")) if html else 0
    size_kb = size_bytes / 1024
    size_mb = size_kb / 1024
    if size_mb > 3:
        return CheckResult(
            check_name="page_size",
            audit_type="seo",
            severity="warning",
            message=f"Page is large ({size_mb:.1f}MB)",
            recommendation="Reduce page size to under 3MB for faster load times.",
            current_value=f"{size_mb:.1f}MB",
            expected_value="< 3MB",
        )
    return CheckResult(
        check_name="page_size",
        audit_type="seo",
        severity="pass",
        message=f"Page size OK ({size_kb:.0f}KB)",
        current_value=f"{size_kb:.0f}KB",
    )


def check_robots_meta(soup: BeautifulSoup) -> CheckResult:
    """Check 22: Robots meta tag — ensure page is indexable."""
    robots = soup.find("meta", attrs={"name": "robots"})
    if not robots:
        return CheckResult(
            check_name="robots_meta",
            audit_type="seo",
            severity="pass",
            message="No robots meta tag (page is indexable by default)",
        )
    content = robots.get("content", "").lower()
    if "noindex" in content:
        return CheckResult(
            check_name="robots_meta",
            audit_type="seo",
            severity="warning",
            message="Page is set to noindex",
            recommendation="Remove noindex if you want this page to appear in search results.",
            current_value=content,
        )
    return CheckResult(
        check_name="robots_meta",
        audit_type="seo",
        severity="pass",
        message="Robots meta allows indexing",
        current_value=content,
    )


def check_lang_attribute(soup: BeautifulSoup) -> CheckResult:
    """Check 23: HTML lang attribute."""
    html_tag = soup.find("html")
    if not html_tag or not html_tag.get("lang"):
        return CheckResult(
            check_name="lang_attribute",
            audit_type="seo",
            severity="warning",
            message="No lang attribute on <html> tag",
            recommendation="Add lang='en' (or appropriate language) to the <html> tag.",
        )
    return CheckResult(
        check_name="lang_attribute",
        audit_type="seo",
        severity="pass",
        message=f"Language set: {html_tag['lang']}",
        current_value=html_tag["lang"],
    )


# ──────────────────────────────────────────────
# Structured Data (2 checks)
# ──────────────────────────────────────────────

def check_schema_markup(soup: BeautifulSoup) -> CheckResult:
    """Check 24: JSON-LD schema markup present."""
    import json
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    if not scripts:
        return CheckResult(
            check_name="schema_markup",
            audit_type="seo",
            severity="warning",
            message="No JSON-LD schema markup found",
            recommendation="Add structured data (Article, Organization, FAQPage) for rich results.",
        )
    schema_types = []
    for script in scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                schema_types.append(data.get("@type", "Unknown"))
            elif isinstance(data, list):
                for item in data:
                    schema_types.append(item.get("@type", "Unknown"))
        except (json.JSONDecodeError, TypeError):
            pass
    return CheckResult(
        check_name="schema_markup",
        audit_type="seo",
        severity="pass",
        message=f"Schema found: {', '.join(schema_types) if schema_types else 'JSON-LD present'}",
        current_value=", ".join(schema_types),
    )


def check_schema_validity(soup: BeautifulSoup) -> CheckResult:
    """Check 25: Schema markup is valid JSON."""
    import json
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    if not scripts:
        return CheckResult(
            check_name="schema_validity",
            audit_type="seo",
            severity="info",
            message="No schema markup to validate",
        )
    for i, script in enumerate(scripts):
        try:
            json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            return CheckResult(
                check_name="schema_validity",
                audit_type="seo",
                severity="warning",
                message=f"Schema block {i + 1} has invalid JSON",
                recommendation="Fix JSON-LD syntax errors.",
            )
    return CheckResult(
        check_name="schema_validity",
        audit_type="seo",
        severity="pass",
        message=f"All {len(scripts)} schema block(s) are valid JSON",
    )


# ──────────────────────────────────────────────
# Social & Discovery (2 checks)
# ──────────────────────────────────────────────

def check_og_tags(soup: BeautifulSoup) -> CheckResult:
    """Check 26: Open Graph tags present."""
    og_title = soup.find("meta", attrs={"property": "og:title"})
    og_desc = soup.find("meta", attrs={"property": "og:description"})
    og_image = soup.find("meta", attrs={"property": "og:image"})

    missing = []
    if not og_title:
        missing.append("og:title")
    if not og_desc:
        missing.append("og:description")
    if not og_image:
        missing.append("og:image")

    if missing:
        return CheckResult(
            check_name="og_tags",
            audit_type="seo",
            severity="warning",
            message=f"Missing Open Graph tags: {', '.join(missing)}",
            recommendation="Add OG tags for better social media sharing previews.",
            current_value=f"{len(missing)} missing",
        )
    return CheckResult(
        check_name="og_tags",
        audit_type="seo",
        severity="pass",
        message="All Open Graph tags present (title, description, image)",
    )


def check_sitemap_reference(soup: BeautifulSoup) -> CheckResult:
    """Check 27: Placeholder — sitemap check (requires HTTP request to /sitemap.xml)."""
    return CheckResult(
        check_name="sitemap",
        audit_type="seo",
        severity="info",
        message="Sitemap check available in full site audit mode",
    )
