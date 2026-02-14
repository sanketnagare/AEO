
import asyncio
import traceback
from typing import Optional
from datetime import datetime, timezone
from urllib.parse import urlparse
import json

from sqlalchemy.ext.asyncio import AsyncSession
import litellm

from app.logging_config import get_logger
from app.agents.base import BaseAgent
from app.streaming.event_stream import EventStream
from app.schemas.audit import AuditReport, AuditScores, PerformanceData, CheckResult
from app.services.firecrawl import firecrawl_client
from app.services.pagespeed import pagespeed_client
from app.services.llm import llm_service
from app.services.robots import robots_service
from app.checks.seo_checks import run_all_seo_checks
from app.checks.aeo_checks import run_all_aeo_checks
from app.checks.geo_checks import run_all_geo_checks
from app.checks.scoring import calculate_score, calculate_overall_score, get_critical_issues

logger = get_logger(__name__)

CHECK_DELAY = 0.04


class AuditAgent(BaseAgent):
    """Audits a single page for SEO, AEO, and GEO readiness with sequential flow."""

    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        stream: Optional[EventStream] = None,
    ):
        super().__init__(db=db, stream=stream)

    def _get_domain(self, url: str) -> str:
        parsed = urlparse(url)
        return parsed.netloc or parsed.path

    async def run(self, url: str) -> AuditReport:
        logger.info("Starting audit for %s", url)
        try:
            report = await self._run_audit(url)
            logger.info("Audit complete for %s", url)
            return report
        except Exception as e:
            logger.error("Audit failed: %s\n%s", e, traceback.format_exc())
            await self.emit_error(f"Audit failed: {str(e)}")
            raise

    async def _run_audit(self, url: str) -> AuditReport:
        domain = self._get_domain(url)

        # 1. Greeting & Robots Analysis
        await self.emit_typing(f"❯ bot: {domain} is on board", level="success")
        await asyncio.sleep(0.3)
        
        await self.emit_typing(f"❯ bot: Checking robots.txt and sitemaps...", level="info")
        robots_data = await robots_service.analyze(url)
        
        if robots_data["robots_txt_found"]:
            await self.emit(f"✓ Found robots.txt", level="success")
        else:
            await self.emit(f"⚠️ No robots.txt found", level="warning")
            
        if robots_data["sitemaps_found"] > 0:
            await self.emit(f"✓ Discovered {robots_data['sitemaps_found']} sitemap(s)", level="success")
            if robots_data["total_pages"] > 0:
                await self.emit(f"✓ Estimated {robots_data['total_pages']} pages indexed", level="success")
        else:
            await self.emit(f"⚠️ No sitemaps found", level="warning")

        await asyncio.sleep(0.5)

        # 2. Scrape & Brand Pulse
        await self.emit_typing(f"❯ bot: Scraping home page to understand your content...", level="info")
        try:
            page_data = await firecrawl_client.scrape(url, formats=["markdown", "rawHtml"], only_main_content=False)
            html = page_data.get("rawHtml", "") or page_data.get("html", "")
            markdown = page_data.get("markdown", "")
            metadata = page_data.get("metadata", {})
            word_count = len(markdown.split()) if markdown else 0
            title = metadata.get("title", domain)
            await self.emit(f"✓ Scraped: {title}", level="success")
        except Exception as e:
            await self.emit_error(f"Failed to scrape page: {str(e)}")
            raise

        await self._analyze_brand_pulse(domain, markdown, metadata)
        await asyncio.sleep(0.5)

        # 3. PageSpeed
        await self.emit_typing(f"❯ bot: Checking site performance...", level="info")
        perf = await self._check_performance(url)
        await asyncio.sleep(0.5)

        # 4. SEO Section
        await self.emit_typing("❯ bot: Running SEO Audit...", level="info")
        seo_checks = run_all_seo_checks(html, markdown, url, metadata)
        seo_score = calculate_score(seo_checks)
        await self._emit_check_issues(seo_checks)
        await self.emit(f"{self._get_score_icon(seo_score)} SEO Score: {seo_score}/100", 
                       level="success" if seo_score > 70 else "warning")
        
        await self.emit_typing("❯ bot: Analyzing SEO findings...", level="info")
        await self._analyze_section_issues("SEO", seo_checks, domain)
        await asyncio.sleep(0.5)

        # 5. AEO Section
        await self.emit_typing("❯ bot: Running AEO Audit...", level="info")
        aeo_checks = run_all_aeo_checks(html, markdown, url, metadata)
        aeo_score = calculate_score(aeo_checks)
        await self._emit_check_issues(aeo_checks)
        await self.emit(f"{self._get_score_icon(aeo_score)} AEO Score: {aeo_score}/100", 
                       level="success" if aeo_score > 70 else "warning")
        
        await self.emit_typing("❯ bot: Analyzing AEO findings...", level="info")
        await self._analyze_section_issues("AEO", aeo_checks, domain)
        await asyncio.sleep(0.5)

        # 6. GEO Section
        await self.emit_typing("❯ bot: Running GEO Audit...", level="info")
        geo_checks = run_all_geo_checks(html, markdown, url, metadata)
        geo_score = calculate_score(geo_checks)
        await self._emit_check_issues(geo_checks)
        await self.emit(f"{self._get_score_icon(geo_score)} GEO Score: {geo_score}/100", 
                       level="success" if geo_score > 70 else "warning")
        
        await self.emit_typing("❯ bot: Analyzing GEO findings...", level="info")
        await self._analyze_section_issues("GEO", geo_checks, domain)
        await asyncio.sleep(0.5)

        # 7. Final Summary
        overall_score = calculate_overall_score(seo_score, aeo_score, geo_score)
        total_critical = len(get_critical_issues(seo_checks + aeo_checks + geo_checks))
        await self.emit(f"$ audit complete! {total_critical} critical issues found.",
                        level="success" if total_critical == 0 else "warning")
        
        await self.emit_typing("❯ bot: Generating final report...", level="info")
        await self._generate_final_summary(domain, seo_score, aeo_score, geo_score, 
                                          seo_checks, aeo_checks, geo_checks)

        # Call to Action
        await asyncio.sleep(1.0)
        await self.emit("Unlock your full audit report & detailed fix guide", level="cta", 
                        data={"action": "signup", "label": "View Full Report & Fixes"})

        return AuditReport(
            url=url,
            scores=AuditScores(seo_score=seo_score, aeo_score=aeo_score, geo_score=geo_score, overall_score=overall_score),
            performance=perf,
            seo_checks=seo_checks,
            aeo_checks=aeo_checks,
            geo_checks=geo_checks,
            word_count=word_count,
            title=metadata.get("title"),
            meta_description=metadata.get("description"),
            audited_at=datetime.now(timezone.utc),
        )

    async def _check_performance(self, url: str) -> PerformanceData:
        try:
            perf = await pagespeed_client.analyze(url)
            parts = []
            if perf.lcp: parts.append(f"LCP: {perf.lcp}s")
            if perf.performance_score: parts.append(f"Score: {perf.performance_score}/100")
            await self.emit(f"✓ {' | '.join(parts)}" if parts else "✓ Data retrieved", level="success")
            return perf
        except Exception as e:
            await self.emit_warning(f"PageSpeed check failed: {e}")
            return PerformanceData()

    async def _analyze_brand_pulse(self, domain: str, markdown: str, metadata: dict):
        preview = markdown[:2000] if markdown else "No content"
        prompt = f"""
        Analyze {domain}.
        Title: {metadata.get("title")}
        Content: {preview}
        
        Output JSON:
        {{
            "summary": "1 sentence describing what the brand provides.",
            "keywords": ["kw1", "kw2", "kw3"]
        }}
        """
        try:
            data = await llm_service.complete_json(prompt, system_prompt="You are a brand strategist.")
            await self.emit_typing(f"❯ bot: I see that {domain} is {data['summary']}", level="bot")
            await asyncio.sleep(0.3)
            # Just show summary, keywords might be too noisy if shown every time, let's keep it simple
        except Exception:
            pass

    async def _analyze_section_issues(self, section: str, checks: list[CheckResult], domain: str):
        issues = [c.message for c in checks if c.severity in ("critical", "warning")]
        if not issues:
            return

        prompt = f"""
        Domain: {domain}
        Audit Section: {section}
        Issues Found:
        {chr(10).join(f"- {i}" for i in issues[:5])}
        
        Write a concise, friendly 1-2 sentence insight about these specific issues. 
        Focus on WHY it matters. No bullet points.
        """
        try:
            insight = await llm_service.complete(prompt, max_tokens=100)
            await self.emit_typing(f"❯ bot: {insight}", level="bot")
        except Exception:
            pass

    async def _generate_final_summary(self, domain, seo, aeo, geo, seo_c, aeo_c, geo_c):
        all_issues = [c.message for c in seo_c + aeo_c + geo_c if c.severity == "critical"]
        prompt = f"""
        Domain: {domain}
        Scores: SEO {seo}, AEO {aeo}, GEO {geo}
        Critical Issues: {len(all_issues)}
        Top Issues: {chr(10).join(all_issues[:5])}
        
        Write a FINAL SUMMARY.
        1. First paragraph: 2 succinct sentences summarizing the overall health.
        2. Second part: Strictly a list of 3-4 bullet points of the most urgent fixes.
        
        Tone: Professional, urgent but encouraging.
        """
        try:
            summary = await llm_service.complete(prompt, max_tokens=250)
            await self.emit_typing(f"❯ bot: {summary}", level="bot")
        except Exception:
            await self.emit_warning("Could not generate final summary.")

    async def _emit_check_issues(self, checks: list[CheckResult]):
        for check in checks:
            if check.severity == "critical":
                await self.emit(f"  ❌ {check.message}", level="error")
                await asyncio.sleep(CHECK_DELAY)
            elif check.severity == "warning":
                await self.emit(f"  ⚠️ {check.message}", level="warning")
                await asyncio.sleep(CHECK_DELAY)

    def _get_score_icon(self, score: float) -> str:
        return "✓" if score > 70 else ("⚠️" if score > 40 else "🔴")
