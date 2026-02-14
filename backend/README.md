# AIVisibilityBot — Backend

FastAPI backend for the AEO + GEO + SEO audit platform. Runs 51 checks across SEO (27), AEO (12), and GEO (12), with real-time SSE streaming to the frontend terminal UI.

## Tech Stack

- **Framework:** FastAPI + Uvicorn
- **Database:** SQLAlchemy (async) + Supabase PostgreSQL
- **Scraping:** Firecrawl API
- **Performance:** Google PageSpeed Insights API
- **AI/LLM:** LiteLLM (Gemini, OpenAI)
- **Streaming:** Server-Sent Events (SSE)

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
# .venv\Scripts\activate    # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your actual keys:

| Variable | Source | Required |
|---|---|---|
| `DATABASE_URL` | [Supabase](https://supabase.com) → Project Settings → Database → Connection String (URI) | Yes |
| `FIRECRAWL_API_KEY` | [firecrawl.dev](https://firecrawl.dev) → Dashboard → API Keys | Yes |
| `PAGESPEED_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) → Credentials → Create API Key | Yes |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) | Optional |
| `GEMINI_API_KEY` | [AI Studio](https://aistudio.google.com/apikey) | Optional |

### 4. Run the Server

```bash
uvicorn app.main:app --reload
```

The server starts at **http://localhost:8000**.

### 5. Verify

- **Health check:** http://localhost:8000/api/health
- **Swagger docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check — returns app status |
| `GET` | `/api/audit/stream?url=<URL>` | SSE stream — real-time audit progress |
| `POST` | `/api/audit/single` | REST — full audit result as JSON |

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # Pydantic Settings (env vars)
│   ├── database.py              # Async SQLAlchemy engine
│   ├── logging_config.py        # Centralized logging
│   ├── agents/
│   │   ├── base.py              # BaseAgent with SSE streaming
│   │   └── audit_agent.py       # Orchestrates full audit
│   ├── api/
│   │   ├── dependencies.py      # FastAPI deps (get_db)
│   │   └── routes/
│   │       ├── health.py        # Health check route
│   │       └── audit.py         # SSE + REST audit routes
│   ├── checks/
│   │   ├── seo_checks.py        # 27 SEO checks
│   │   ├── aeo_checks.py        # 12 AEO checks
│   │   ├── geo_checks.py        # 12 GEO checks
│   │   └── scoring.py           # Score calculation
│   ├── models/                  # SQLAlchemy models
│   ├── schemas/
│   │   └── audit.py             # Pydantic schemas
│   ├── services/
│   │   ├── firecrawl.py         # Firecrawl API client
│   │   ├── pagespeed.py         # PageSpeed API client
│   │   └── llm.py               # LiteLLM wrapper
│   └── streaming/
│       └── event_stream.py      # SSE event queue
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Production container
└── railway.json                 # Railway deployment config
```

## Logging

All modules use structured logging via `app/logging_config.py`:

```
09:42:24 | INFO     | app.services.firecrawl    | Scraping URL: https://example.com
09:42:27 | INFO     | app.checks.seo_checks     | SEO checks complete: 27 results (12 pass, 6 warn, 5 critical)
09:42:28 | INFO     | app.agents.audit_agent    | Audit complete — overall score: 63.5
```

To change log level, modify `setup_logging()` in `main.py`:
```python
setup_logging(level="DEBUG")  # DEBUG, INFO, WARNING, ERROR
```

## Deployment (Railway)

```bash
# Push to Railway
railway up
```

Set environment variables in Railway dashboard. The `Dockerfile` and `railway.json` handle the rest.
