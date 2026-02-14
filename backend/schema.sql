-- ============================================
-- AIVisibilityBot Schema
-- Run this in Supabase SQL Editor
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Sites ──
CREATE TABLE IF NOT EXISTS sites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT NOT NULL,
    name TEXT,
    business_summary TEXT,
    industry TEXT,

    -- Crawl data
    robots_txt_content TEXT,
    sitemap_url TEXT,

    -- Aggregate scores (0-100)
    seo_score REAL,
    aeo_score REAL,
    geo_score REAL,

    last_crawl_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ── Pages ──
CREATE TABLE IF NOT EXISTS pages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    meta_description TEXT,
    h1_text TEXT,

    -- Content
    headings_json JSONB,
    word_count INTEGER,
    content_markdown TEXT,
    content_html TEXT,
    schema_markup_json JSONB,

    -- Links & media
    internal_links_count INTEGER DEFAULT 0,
    external_links_count INTEGER DEFAULT 0,
    images_json JSONB,
    og_tags_json JSONB,
    canonical_url TEXT,

    -- Scores (0-100)
    seo_score REAL,
    aeo_score REAL,
    geo_score REAL,

    last_audited_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- ── Crawl Jobs ──
CREATE TABLE IF NOT EXISTS crawl_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_id UUID REFERENCES sites(id) ON DELETE CASCADE NOT NULL,
    status TEXT DEFAULT 'pending',          -- pending, crawling, completed, failed
    total_pages INTEGER DEFAULT 0,
    crawled_pages INTEGER DEFAULT 0,
    firecrawl_job_id TEXT,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_pages_site_id ON pages(site_id);
CREATE INDEX IF NOT EXISTS idx_crawl_jobs_site_id ON crawl_jobs(site_id);
