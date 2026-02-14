"""GEO (Generative Engine Optimization) audit check functions — 12 checks.

Checks how well a page is optimized for citation by AI models
(ChatGPT, Perplexity, Gemini, Google AI Overviews).
"""

import json
import re
from typing import Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from app.schemas.audit import CheckResult
from app.logging_config import get_logger

logger = get_logger(__name__)


def run_all_geo_checks(
    html: str,
    markdown: str,
    url: str,
    metadata: Optional[dict] = None,
    robots_txt: Optional[str] = None,
) -> list[CheckResult]:
    """Run all 12 GEO checks on a page."""
    soup = BeautifulSoup(html, "lxml") if html else BeautifulSoup("", "lxml")
    results = []
    logger.info("Starting GEO checks for URL")

    # AI Crawler Access (3 checks)
    results.append(check_gptbot_access(robots_txt))
    results.append(check_claudebot_access(robots_txt))
    results.append(check_other_ai_bots(robots_txt))

    # Content AI-Parsability (4 checks)
    results.append(check_js_rendering_dependency(soup))
    results.append(check_semantic_html(soup))
    results.append(check_url_slug_quality(url))
    results.append(check_tldr_section(soup, markdown))

    # Citation-Worthiness (3 checks)
    results.append(check_statistics_data(markdown))
    results.append(check_authoritative_sources(soup, url))
    results.append(check_original_insights(markdown))

    # Entity Clarity (2 checks)
    results.append(check_entity_definition(soup, markdown))
    results.append(check_organization_schema(soup))

    logger.info("GEO checks complete: %d results (%d pass, %d warn, %d critical)",
                len(results),
                sum(1 for r in results if r.severity == "pass"),
                sum(1 for r in results if r.severity == "warning"),
                sum(1 for r in results if r.severity == "critical"))
    return results


# ──────────────────────────────────────────────
# AI Crawler Access (3 checks)
# ──────────────────────────────────────────────

def _check_bot_in_robots(robots_txt: Optional[str], bot_name: str) -> tuple[bool, bool]:
    """Check if a bot is allowed or blocked in robots.txt.

    Returns:
        (is_mentioned, is_allowed)
    """
    if not robots_txt:
        return False, True  # No robots.txt = allowed by default

    lines = robots_txt.lower().split("\n")
    current_agent = None
    bot_lower = bot_name.lower()

    for line in lines:
        line = line.strip()
        if line.startswith("user-agent:"):
            agent = line.split(":", 1)[1].strip()
            current_agent = agent
        elif current_agent in (bot_lower, "*"):
            if line.startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                if path == "/" or path == "":
                    if current_agent == bot_lower:
                        return True, False  # Explicitly blocked
                    elif current_agent == "*" and bot_lower not in robots_txt.lower():
                        return False, False  # Blocked by wildcard
            elif line.startswith("allow:"):
                path = line.split(":", 1)[1].strip()
                if path == "/" and current_agent == bot_lower:
                    return True, True

    return False, True  # Not mentioned = allowed


def check_gptbot_access(robots_txt: Optional[str]) -> CheckResult:
    """Check 1: GPTBot allowed in robots.txt."""
    mentioned, allowed = _check_bot_in_robots(robots_txt, "GPTBot")

    if not robots_txt:
        return CheckResult(
            check_name="gptbot_access",
            audit_type="geo",
            severity="info",
            message="No robots.txt available — GPTBot allowed by default",
            recommendation="Consider explicitly allowing GPTBot in robots.txt.",
        )
    if not allowed:
        return CheckResult(
            check_name="gptbot_access",
            audit_type="geo",
            severity="critical",
            message="GPTBot is BLOCKED in robots.txt ❌",
            recommendation="Remove 'Disallow: /' for GPTBot to allow ChatGPT to crawl and cite your content.",
        )
    if mentioned:
        return CheckResult(
            check_name="gptbot_access",
            audit_type="geo",
            severity="pass",
            message="GPTBot is explicitly allowed ✓",
        )
    return CheckResult(
        check_name="gptbot_access",
        audit_type="geo",
        severity="pass",
        message="GPTBot allowed (not blocked in robots.txt)",
    )


def check_claudebot_access(robots_txt: Optional[str]) -> CheckResult:
    """Check 2: ClaudeBot/anthropic-ai allowed in robots.txt."""
    _, claude_allowed = _check_bot_in_robots(robots_txt, "ClaudeBot")
    _, anthropic_allowed = _check_bot_in_robots(robots_txt, "anthropic-ai")

    if not robots_txt:
        return CheckResult(
            check_name="claudebot_access",
            audit_type="geo",
            severity="info",
            message="No robots.txt available — ClaudeBot allowed by default",
        )
    if not claude_allowed or not anthropic_allowed:
        return CheckResult(
            check_name="claudebot_access",
            audit_type="geo",
            severity="warning",
            message="ClaudeBot/anthropic-ai is BLOCKED in robots.txt",
            recommendation="Allow ClaudeBot to enable Anthropic's AI to cite your content.",
        )
    return CheckResult(
        check_name="claudebot_access",
        audit_type="geo",
        severity="pass",
        message="ClaudeBot/anthropic-ai allowed ✓",
    )


def check_other_ai_bots(robots_txt: Optional[str]) -> CheckResult:
    """Check 3: PerplexityBot / Google-Extended allowed."""
    bots_to_check = {
        "PerplexityBot": _check_bot_in_robots(robots_txt, "PerplexityBot"),
        "Google-Extended": _check_bot_in_robots(robots_txt, "Google-Extended"),
    }

    if not robots_txt:
        return CheckResult(
            check_name="other_ai_bots",
            audit_type="geo",
            severity="info",
            message="No robots.txt — all AI bots allowed by default",
        )

    blocked = [bot for bot, (_, allowed) in bots_to_check.items() if not allowed]
    if blocked:
        return CheckResult(
            check_name="other_ai_bots",
            audit_type="geo",
            severity="warning",
            message=f"Blocked AI bots: {', '.join(blocked)}",
            recommendation="Allow these AI bots for maximum AI search visibility.",
        )
    return CheckResult(
        check_name="other_ai_bots",
        audit_type="geo",
        severity="pass",
        message="PerplexityBot & Google-Extended allowed ✓",
    )


# ──────────────────────────────────────────────
# Content AI-Parsability (4 checks)
# ──────────────────────────────────────────────

def check_js_rendering_dependency(soup: BeautifulSoup) -> CheckResult:
    """Check 4: Content renders without JavaScript."""
    # Check for common SPA indicators
    body = soup.find("body")
    if not body:
        return CheckResult(
            check_name="js_dependency",
            audit_type="geo",
            severity="warning",
            message="No body element found — possible rendering issue",
        )

    body_text = body.get_text(strip=True)
    noscript = soup.find("noscript")

    # Check for empty body with JS mount point
    spa_indicators = [
        soup.find("div", id="root"),
        soup.find("div", id="app"),
        soup.find("div", id="__next"),
    ]

    if len(body_text) < 100 and any(spa_indicators):
        return CheckResult(
            check_name="js_dependency",
            audit_type="geo",
            severity="warning",
            message="Content may depend on JavaScript rendering (SPA detected)",
            recommendation="Ensure server-side rendering (SSR) so AI crawlers can parse your content.",
        )
    return CheckResult(
        check_name="js_dependency",
        audit_type="geo",
        severity="pass",
        message="Content appears to render without JavaScript dependency ✓",
    )


def check_semantic_html(soup: BeautifulSoup) -> CheckResult:
    """Check 5: Semantic HTML5 elements used."""
    semantic_tags = ["article", "section", "aside", "nav", "main", "header", "footer", "figure"]
    found = [tag for tag in semantic_tags if soup.find(tag)]

    if not found:
        return CheckResult(
            check_name="semantic_html",
            audit_type="geo",
            severity="warning",
            message="No semantic HTML5 elements found",
            recommendation="Use <article>, <section>, <main>, <aside> for better content structure. "
                          "AI models use semantic HTML to understand content boundaries.",
        )
    if len(found) < 3:
        return CheckResult(
            check_name="semantic_html",
            audit_type="geo",
            severity="info",
            message=f"Some semantic HTML found: {', '.join(found)}",
            recommendation="Consider using more semantic elements for clearer content structure.",
            current_value=", ".join(found),
        )
    return CheckResult(
        check_name="semantic_html",
        audit_type="geo",
        severity="pass",
        message=f"Good semantic HTML: {', '.join(found)}",
        current_value=", ".join(found),
    )


def check_url_slug_quality(url: str) -> CheckResult:
    """Check 6: URL slug is descriptive and keyword-aligned."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if not path or path == "":
        return CheckResult(
            check_name="url_slug",
            audit_type="geo",
            severity="pass",
            message="Homepage URL (no slug needed)",
        )

    slug = path.split("/")[-1]

    # Check for non-descriptive patterns
    bad_patterns = [
        re.match(r"^\d+$", slug),  # Just a number
        re.match(r"^[a-f0-9-]{32,}$", slug),  # UUID-like
        re.match(r"^page\d+$", slug, re.I),  # page1, page2
        re.match(r"^post-\d+$", slug, re.I),  # post-123
    ]

    if any(bad_patterns):
        return CheckResult(
            check_name="url_slug",
            audit_type="geo",
            severity="warning",
            message=f"URL slug is not descriptive: /{slug}",
            recommendation="Use descriptive URL slugs with keywords (e.g., /what-is-project-management).",
            current_value=slug,
        )

    # Check slug length
    if len(slug) > 60:
        return CheckResult(
            check_name="url_slug",
            audit_type="geo",
            severity="info",
            message=f"URL slug is long ({len(slug)} chars): /{slug[:40]}...",
            recommendation="Keep URL slugs concise (3-5 words).",
            current_value=slug,
        )

    return CheckResult(
        check_name="url_slug",
        audit_type="geo",
        severity="pass",
        message=f"Good URL slug: /{slug}",
        current_value=slug,
    )


def check_tldr_section(soup: BeautifulSoup, markdown: str) -> CheckResult:
    """Check 7: TL;DR or summary section present."""
    # Check headings for TL;DR, Summary, Key Takeaways, etc.
    summary_terms = ["tl;dr", "tldr", "summary", "key takeaway", "in short",
                     "in brief", "at a glance", "overview", "executive summary"]

    headings = soup.find_all(["h1", "h2", "h3", "h4"])
    for h in headings:
        text = h.get_text(strip=True).lower()
        if any(term in text for term in summary_terms):
            return CheckResult(
                check_name="tldr_section",
                audit_type="geo",
                severity="pass",
                message=f"Summary/TL;DR section found: \"{h.get_text(strip=True)}\"",
            )

    # Check markdown for inline TL;DR
    if markdown:
        lower_md = markdown.lower()
        if any(term in lower_md for term in ["tl;dr", "**summary**", "**key takeaway"]):
            return CheckResult(
                check_name="tldr_section",
                audit_type="geo",
                severity="pass",
                message="TL;DR or summary content found in body",
            )

    return CheckResult(
        check_name="tldr_section",
        audit_type="geo",
        severity="critical",
        message="No TL;DR or summary section found",
        recommendation="Add a TL;DR or Summary section at the top/bottom. "
                      "AI models often extract these directly for user-facing answers.",
    )


# ──────────────────────────────────────────────
# Citation-Worthiness (3 checks)
# ──────────────────────────────────────────────

def check_statistics_data(markdown: str) -> CheckResult:
    """Check 8: Statistics/data points included."""
    if not markdown:
        return CheckResult(
            check_name="statistics",
            audit_type="geo",
            severity="warning",
            message="No content to check for statistics",
        )

    # Look for percentage patterns, numbers with context
    stat_patterns = [
        r"\d+(\.\d+)?%",              # 25%, 3.5%
        r"\$[\d,]+(\.\d+)?",          # $1,000, $3.5M
        r"\d+x\b",                     # 10x
        r"\d+ million|\d+ billion",    # 5 million
        r"according to",
        r"research (shows|finds|indicates)",
        r"study (shows|finds|reveals)",
        r"data (shows|suggests)",
    ]

    found = sum(1 for p in stat_patterns if re.search(p, markdown, re.I))

    if found == 0:
        return CheckResult(
            check_name="statistics",
            audit_type="geo",
            severity="warning",
            message="No statistics or data points found",
            recommendation="Add statistics with citations. Pages with data points have 15-30% higher AI citation rates.",
        )
    if found < 3:
        return CheckResult(
            check_name="statistics",
            audit_type="geo",
            severity="info",
            message=f"Some data indicators found ({found})",
            recommendation="Add more statistics and data points for stronger AI citation potential.",
            current_value=str(found),
        )
    return CheckResult(
        check_name="statistics",
        audit_type="geo",
        severity="pass",
        message=f"Good data coverage ({found} statistical indicators found)",
        current_value=str(found),
    )


def check_authoritative_sources(soup: BeautifulSoup, url: str) -> CheckResult:
    """Check 9: Authoritative external sources cited."""
    domain = urlparse(url).netloc
    links = soup.find_all("a", href=True)

    authority_domains = [".gov", ".edu", ".org", "wikipedia.org", "scholar.google",
                        "pubmed", "arxiv.org", "nature.com", "sciencedirect"]

    external_links = [l for l in links if l["href"].startswith("http")
                      and domain not in urlparse(l["href"]).netloc]
    authority_links = [l for l in external_links
                       if any(auth in l["href"].lower() for auth in authority_domains)]

    if not external_links:
        return CheckResult(
            check_name="authoritative_sources",
            audit_type="geo",
            severity="warning",
            message="No external source citations",
            recommendation="Cite authoritative sources (.gov, .edu, research papers). "
                          "Expert citations increase AI visibility by 10-20%.",
        )
    if not authority_links:
        return CheckResult(
            check_name="authoritative_sources",
            audit_type="geo",
            severity="info",
            message=f"{len(external_links)} external links, but no authoritative sources (.gov, .edu)",
            recommendation="Include links to academic, government, or research sources.",
        )
    return CheckResult(
        check_name="authoritative_sources",
        audit_type="geo",
        severity="pass",
        message=f"{len(authority_links)} authoritative source(s) cited",
        current_value=str(len(authority_links)),
    )


def check_original_insights(markdown: str) -> CheckResult:
    """Check 10: Original insights (not generic rehash)."""
    if not markdown:
        return CheckResult(
            check_name="original_insights",
            audit_type="geo",
            severity="info",
            message="No content to analyze for originality",
        )

    # Heuristic: look for first-person experience, unique phrasing
    insight_indicators = [
        r"\b(in my experience|we found|our (data|research|analysis|team))\b",
        r"\b(we (tested|built|created|developed|discovered))\b",
        r"\b(here'?s what (we|I) (learned|found|discovered))\b",
        r"\b(case study|real-world example)\b",
        r"\b(proprietary|exclusive|first-hand)\b",
    ]

    found = sum(1 for p in insight_indicators if re.search(p, markdown, re.I))

    if found == 0:
        return CheckResult(
            check_name="original_insights",
            audit_type="geo",
            severity="info",
            message="No clear original insights detected",
            recommendation="Include original analysis, case studies, or first-hand experience. "
                          "AI models prefer citing unique, non-rehashed content.",
        )
    return CheckResult(
        check_name="original_insights",
        audit_type="geo",
        severity="pass",
        message=f"Original insight indicators found ({found})",
        current_value=str(found),
    )


# ──────────────────────────────────────────────
# Entity Clarity (2 checks)
# ──────────────────────────────────────────────

def check_entity_definition(soup: BeautifulSoup, markdown: str) -> CheckResult:
    """Check 11: First paragraph clearly defines what the page/brand/product IS."""
    # Get first paragraph
    first_p = soup.find("p")
    if not first_p:
        return CheckResult(
            check_name="entity_definition",
            audit_type="geo",
            severity="warning",
            message="No paragraph content found",
            recommendation="Start with a clear paragraph defining what your product/brand/topic IS.",
        )

    text = first_p.get_text(strip=True).lower()

    # Check for definitional patterns ("X is a...", "X is the...", "X helps...", "X provides...")
    definition_patterns = [
        r"\bis (a|an|the)\b",
        r"\bprovides?\b",
        r"\bhelps?\b",
        r"\bis designed to\b",
        r"\benables?\b",
        r"\boffers?\b",
    ]

    has_definition = any(re.search(p, text) for p in definition_patterns)
    word_count = len(text.split())

    if word_count < 10:
        return CheckResult(
            check_name="entity_definition",
            audit_type="geo",
            severity="warning",
            message="First paragraph is too short for entity definition",
            recommendation="Write a clear 2-3 sentence first paragraph that defines what this page is about.",
        )

    if has_definition:
        return CheckResult(
            check_name="entity_definition",
            audit_type="geo",
            severity="pass",
            message="First paragraph contains entity-defining language ✓",
        )

    return CheckResult(
        check_name="entity_definition",
        audit_type="geo",
        severity="info",
        message="First paragraph may not clearly define the entity",
        recommendation="Start your page with 'X is...' or 'X provides...' for clear AI comprehension.",
    )


def check_organization_schema(soup: BeautifulSoup) -> CheckResult:
    """Check 12: Organization schema with sameAs links."""
    types = []
    has_same_as = False

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                t = data.get("@type", "")
                types.append(t)
                if t == "Organization" and "sameAs" in data:
                    has_same_as = True
                # Check @graph
                for item in data.get("@graph", []):
                    t = item.get("@type", "")
                    types.append(t)
                    if t == "Organization" and "sameAs" in item:
                        has_same_as = True
        except (json.JSONDecodeError, TypeError):
            pass

    if "Organization" not in types:
        return CheckResult(
            check_name="organization_schema",
            audit_type="geo",
            severity="warning",
            message="No Organization schema markup",
            recommendation="Add Organization schema with sameAs links to social profiles. "
                          "This helps AI models identify and cite your brand correctly.",
        )
    if not has_same_as:
        return CheckResult(
            check_name="organization_schema",
            audit_type="geo",
            severity="info",
            message="Organization schema found but missing sameAs links",
            recommendation="Add sameAs links to your social media profiles and Wikipedia page.",
            current_value="Organization (no sameAs)",
        )
    return CheckResult(
        check_name="organization_schema",
        audit_type="geo",
        severity="pass",
        message="Organization schema with sameAs links ✓",
    )
