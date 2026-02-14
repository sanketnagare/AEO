"""AEO (Answer Engine Optimization) audit check functions — 12 checks.

Checks how well a page is optimized for featured snippets,
answer boxes, and AI-powered answer engines.
"""

import json
import re
from typing import Optional
from bs4 import BeautifulSoup

from app.schemas.audit import CheckResult
from app.logging_config import get_logger

logger = get_logger(__name__)


QUESTION_WORDS = ["what", "how", "why", "when", "where", "who", "which",
                  "can", "does", "is", "are", "should", "will", "do"]


def run_all_aeo_checks(
    html: str,
    markdown: str,
    url: str,
    metadata: Optional[dict] = None,
) -> list[CheckResult]:
    """Run all 12 AEO checks on a page."""
    soup = BeautifulSoup(html, "lxml") if html else BeautifulSoup("", "lxml")
    results = []
    logger.info("Starting AEO checks for URL")

    # Snippet Readiness (4 checks)
    results.append(check_question_headings(soup))
    results.append(check_direct_answers(soup, markdown))
    results.append(check_structured_lists(soup))
    results.append(check_comparison_tables(soup))

    # Schema for Answers (4 checks)
    results.append(check_faq_schema(soup))
    results.append(check_howto_schema(soup))
    results.append(check_speakable_schema(soup))
    results.append(check_article_schema(soup))

    # E-E-A-T Signals (3 checks)
    results.append(check_author_info(soup, markdown))
    results.append(check_author_credentials(soup, markdown))
    results.append(check_external_citations(soup, url))

    # Freshness (1 check)
    results.append(check_date_modified(soup))

    logger.info("AEO checks complete: %d results (%d pass, %d warn, %d critical)",
                len(results),
                sum(1 for r in results if r.severity == "pass"),
                sum(1 for r in results if r.severity == "warning"),
                sum(1 for r in results if r.severity == "critical"))
    return results


# ──────────────────────────────────────────────
# Snippet Readiness (4 checks)
# ──────────────────────────────────────────────

def check_question_headings(soup: BeautifulSoup) -> CheckResult:
    """Check 1: Question-based headings (H2/H3 starting with who/what/how/why/etc)."""
    headings = soup.find_all(["h2", "h3"])
    question_headings = []
    for h in headings:
        text = h.get_text(strip=True).lower()
        if text.endswith("?") or any(text.startswith(w) for w in QUESTION_WORDS):
            question_headings.append(h.get_text(strip=True))

    if not question_headings:
        return CheckResult(
            check_name="question_headings",
            audit_type="aeo",
            severity="critical",
            message="No question-based headings found",
            recommendation="Add H2/H3 headings phrased as questions (e.g., 'What is...', 'How to...'). "
                          "These match how users query AI assistants and search engines.",
            current_value="0",
            expected_value="2+",
        )
    if len(question_headings) < 2:
        return CheckResult(
            check_name="question_headings",
            audit_type="aeo",
            severity="warning",
            message=f"Only {len(question_headings)} question heading found",
            recommendation="Add more question-based H2/H3 headings to capture featured snippets.",
            current_value=str(len(question_headings)),
            expected_value="2+",
        )
    return CheckResult(
        check_name="question_headings",
        audit_type="aeo",
        severity="pass",
        message=f"{len(question_headings)} question-based headings found",
        current_value=str(len(question_headings)),
    )


def check_direct_answers(soup: BeautifulSoup, markdown: str) -> CheckResult:
    """Check 2: Direct answer within first 40-60 words after question heading."""
    headings = soup.find_all(["h2", "h3"])
    question_headings = [h for h in headings
                         if h.get_text(strip=True).endswith("?")
                         or any(h.get_text(strip=True).lower().startswith(w) for w in QUESTION_WORDS)]

    if not question_headings:
        return CheckResult(
            check_name="direct_answers",
            audit_type="aeo",
            severity="warning",
            message="No question headings to check for direct answers",
            recommendation="Add question headings followed by concise 40-60 word answers.",
        )

    has_direct_answer = False
    for h in question_headings:
        next_elem = h.find_next_sibling()
        if next_elem and next_elem.name == "p":
            words = len(next_elem.get_text(strip=True).split())
            if 20 <= words <= 80:
                has_direct_answer = True
                break

    if not has_direct_answer:
        return CheckResult(
            check_name="direct_answers",
            audit_type="aeo",
            severity="warning",
            message="No direct answer format detected after question headings",
            recommendation="After each question heading, provide a concise 40-60 word answer paragraph "
                          "before expanding into detail. This format matches featured snippet requirements.",
        )
    return CheckResult(
        check_name="direct_answers",
        audit_type="aeo",
        severity="pass",
        message="Direct answer format detected after question headings ✓",
    )


def check_structured_lists(soup: BeautifulSoup) -> CheckResult:
    """Check 3: HTML lists for step-by-step content (ol/ul)."""
    ordered = soup.find_all("ol")
    unordered = soup.find_all("ul")
    total = len(ordered) + len(unordered)

    if total == 0:
        return CheckResult(
            check_name="structured_lists",
            audit_type="aeo",
            severity="warning",
            message="No HTML lists found",
            recommendation="Add ordered lists (for steps) or unordered lists (for features/benefits). "
                          "Lists are a primary format for featured snippets.",
        )
    return CheckResult(
        check_name="structured_lists",
        audit_type="aeo",
        severity="pass",
        message=f"Lists found: {len(ordered)} ordered, {len(unordered)} unordered",
        current_value=str(total),
    )


def check_comparison_tables(soup: BeautifulSoup) -> CheckResult:
    """Check 4: HTML tables for comparison data."""
    tables = soup.find_all("table")
    if not tables:
        return CheckResult(
            check_name="comparison_tables",
            audit_type="aeo",
            severity="info",
            message="No comparison tables found",
            recommendation="Add tables for comparisons, pricing, or feature matrices. "
                          "32.5% of AI citations use tabular data.",
        )
    return CheckResult(
        check_name="comparison_tables",
        audit_type="aeo",
        severity="pass",
        message=f"{len(tables)} table(s) found",
        current_value=str(len(tables)),
    )


# ──────────────────────────────────────────────
# Schema for Answers (4 checks)
# ──────────────────────────────────────────────

def _get_schema_types(soup: BeautifulSoup) -> list[str]:
    """Extract all @type values from JSON-LD scripts."""
    types = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                t = data.get("@type", "")
                types.append(t if isinstance(t, str) else str(t))
                # Check @graph
                for item in data.get("@graph", []):
                    t = item.get("@type", "")
                    types.append(t if isinstance(t, str) else str(t))
            elif isinstance(data, list):
                for item in data:
                    t = item.get("@type", "")
                    types.append(t if isinstance(t, str) else str(t))
        except (json.JSONDecodeError, TypeError, AttributeError):
            pass
    return types


def check_faq_schema(soup: BeautifulSoup) -> CheckResult:
    """Check 5: FAQPage schema markup."""
    types = _get_schema_types(soup)
    if "FAQPage" in types:
        return CheckResult(
            check_name="faq_schema",
            audit_type="aeo",
            severity="pass",
            message="FAQPage schema markup found ✓",
        )
    return CheckResult(
        check_name="faq_schema",
        audit_type="aeo",
        severity="critical",
        message="No FAQPage schema markup",
        recommendation="Add FAQPage JSON-LD schema with Q&A pairs. "
                      "This enables rich FAQ results in Google and helps AI engines parse your content.",
    )


def check_howto_schema(soup: BeautifulSoup) -> CheckResult:
    """Check 6: HowTo schema markup."""
    types = _get_schema_types(soup)
    if "HowTo" in types:
        return CheckResult(
            check_name="howto_schema",
            audit_type="aeo",
            severity="pass",
            message="HowTo schema markup found ✓",
        )
    return CheckResult(
        check_name="howto_schema",
        audit_type="aeo",
        severity="info",
        message="No HowTo schema markup",
        recommendation="Add HowTo schema if your page contains step-by-step instructions.",
    )


def check_speakable_schema(soup: BeautifulSoup) -> CheckResult:
    """Check 7: Speakable schema markup."""
    types = _get_schema_types(soup)
    # Speakable can be a property, not always a @type
    has_speakable = "Speakable" in types
    if not has_speakable:
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "speakable" in json.dumps(data).lower():
                    has_speakable = True
                    break
            except (json.JSONDecodeError, TypeError):
                pass

    if has_speakable:
        return CheckResult(
            check_name="speakable_schema",
            audit_type="aeo",
            severity="pass",
            message="Speakable schema found ✓",
        )
    return CheckResult(
        check_name="speakable_schema",
        audit_type="aeo",
        severity="info",
        message="No Speakable schema markup",
        recommendation="Add Speakable schema to indicate which sections are suitable for voice assistants.",
    )


def check_article_schema(soup: BeautifulSoup) -> CheckResult:
    """Check 8: Article schema with author + dateModified."""
    types = _get_schema_types(soup)
    article_types = {"Article", "NewsArticle", "BlogPosting", "WebPage"}
    has_article = any(t in article_types for t in types)

    if not has_article:
        return CheckResult(
            check_name="article_schema",
            audit_type="aeo",
            severity="warning",
            message="No Article/BlogPosting schema markup",
            recommendation="Add Article schema with author and dateModified for E-E-A-T signals.",
        )
    return CheckResult(
        check_name="article_schema",
        audit_type="aeo",
        severity="pass",
        message="Article schema markup found ✓",
    )


# ──────────────────────────────────────────────
# E-E-A-T Signals (3 checks)
# ──────────────────────────────────────────────

def check_author_info(soup: BeautifulSoup, markdown: str) -> CheckResult:
    """Check 9: Author name and bio on page."""
    # Check for common author patterns in HTML
    author_patterns = [
        soup.find(class_=re.compile(r"author", re.I)),
        soup.find("meta", attrs={"name": "author"}),
        soup.find(attrs={"rel": "author"}),
        soup.find(attrs={"itemprop": "author"}),
    ]
    has_author = any(p for p in author_patterns)

    if not has_author and markdown:
        # Check markdown for author mentions
        lower_md = markdown.lower()
        if any(phrase in lower_md for phrase in ["written by", "by ", "author:", "about the author"]):
            has_author = True

    if not has_author:
        return CheckResult(
            check_name="author_info",
            audit_type="aeo",
            severity="warning",
            message="No author information found",
            recommendation="Add author name, bio, and photo. E-E-A-T signals boost AI trust.",
        )
    return CheckResult(
        check_name="author_info",
        audit_type="aeo",
        severity="pass",
        message="Author information found ✓",
    )


def check_author_credentials(soup: BeautifulSoup, markdown: str) -> CheckResult:
    """Check 10: Author credentials mentioned."""
    cred_patterns = [
        r"\b(phd|md|mba|cpa|jd|rn)\b",
        r"\b(certified|expert|specialist|professor|dr\.)\b",
        r"\b(years? of experience|experienced)\b",
        r"\b(founder|ceo|cto|director)\b",
    ]
    text = markdown.lower() if markdown else ""
    has_creds = any(re.search(p, text, re.I) for p in cred_patterns)

    if not has_creds:
        return CheckResult(
            check_name="author_credentials",
            audit_type="aeo",
            severity="info",
            message="No author credentials detected",
            recommendation="Include author credentials, title, or experience to build E-E-A-T.",
        )
    return CheckResult(
        check_name="author_credentials",
        audit_type="aeo",
        severity="pass",
        message="Author credentials found ✓",
    )


def check_external_citations(soup: BeautifulSoup, url: str) -> CheckResult:
    """Check 11: Authoritative external citations."""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    links = soup.find_all("a", href=True)
    external = [l for l in links if l["href"].startswith("http")
                and domain not in urlparse(l["href"]).netloc]

    if len(external) == 0:
        return CheckResult(
            check_name="external_citations",
            audit_type="aeo",
            severity="warning",
            message="No external citations/references",
            recommendation="Add references to authoritative sources (research, .gov, .edu sites). "
                          "Statistics with citations increase AI visibility by 15-30%.",
        )
    return CheckResult(
        check_name="external_citations",
        audit_type="aeo",
        severity="pass",
        message=f"{len(external)} external citations found",
        current_value=str(len(external)),
    )


# ──────────────────────────────────────────────
# Freshness (1 check)
# ──────────────────────────────────────────────

def check_date_modified(soup: BeautifulSoup) -> CheckResult:
    """Check 12: dateModified within last 6 months."""
    from datetime import datetime, timezone, timedelta

    # Check meta tags
    modified = soup.find("meta", attrs={"property": "article:modified_time"})
    if not modified:
        modified = soup.find("meta", attrs={"name": "last-modified"})

    # Check JSON-LD
    if not modified:
        for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and "dateModified" in data:
                    date_str = data["dateModified"]
                    try:
                        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                        six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)
                        if dt > six_months_ago:
                            return CheckResult(
                                check_name="date_modified",
                                audit_type="aeo",
                                severity="pass",
                                message=f"Content recently updated: {date_str[:10]}",
                                current_value=date_str[:10],
                            )
                        else:
                            return CheckResult(
                                check_name="date_modified",
                                audit_type="aeo",
                                severity="warning",
                                message=f"Content last updated: {date_str[:10]} (over 6 months ago)",
                                recommendation="Update content regularly. Fresh content ranks better in AI responses.",
                                current_value=date_str[:10],
                            )
                    except (ValueError, TypeError):
                        pass
            except (json.JSONDecodeError, TypeError):
                pass

    if modified and modified.get("content"):
        return CheckResult(
            check_name="date_modified",
            audit_type="aeo",
            severity="pass",
            message=f"Date modified: {modified['content'][:10]}",
            current_value=modified["content"],
        )

    return CheckResult(
        check_name="date_modified",
        audit_type="aeo",
        severity="warning",
        message="No dateModified found",
        recommendation="Add dateModified in schema markup and meta tags to signal content freshness.",
    )
