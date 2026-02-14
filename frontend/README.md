# AIVisibilityBot — Frontend

Next.js frontend with a hacker-style terminal UI for real-time AEO + GEO + SEO audits. Connects to the backend via Server-Sent Events (SSE) for streaming audit results.

## Tech Stack

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS (dark terminal theme)
- **Fonts:** Inter + JetBrains Mono
- **Streaming:** SSE via EventSource

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
cp .env.example .env.local
```

Edit `.env.local`:

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend API URL |

### 3. Run Dev Server

```bash
npm run dev
```

App runs at **http://localhost:3000**.

> **Note:** The backend must be running on port 8000 for audits to work.

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx           # Root layout (fonts, metadata, dark theme)
│   ├── page.tsx             # Landing page (hero, terminal, features)
│   └── globals.css          # Dark terminal theme, animations
├── components/
│   ├── Terminal.tsx          # Interactive terminal with SSE streaming
│   └── TerminalLine.tsx     # Single line with color coding
├── lib/
│   ├── sse.ts               # SSE connection helper
│   └── api.ts               # REST API client
├── .env.local               # Local env vars
├── .env.example             # Env template
├── tailwind.config.ts       # Tailwind config
└── package.json
```

## How It Works

1. User types a URL in the terminal
2. Frontend connects to `GET /api/audit/stream?url=<URL>` via SSE
3. Backend streams events: `info`, `success`, `warning`, `error`, `complete`
4. Terminal renders each event with color-coded output
5. On completion, a score summary box appears (SEO / AEO / GEO / Overall)

## Terminal Commands

| Command | Action |
|---|---|
| `https://example.com` | Run a full audit on the URL |
| `clear` | Reset the terminal |

## Deployment (Vercel)

```bash
npm run build
vercel --prod
```

Set `NEXT_PUBLIC_API_URL` to your deployed backend URL in Vercel environment settings.
