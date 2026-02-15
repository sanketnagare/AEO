"""Audit API routes — SSE streaming and REST endpoints."""

import json
import asyncio
import traceback
from fastapi import APIRouter, Query
from sse_starlette.sse import EventSourceResponse

from app.logging_config import get_logger
from app.agents.audit_agent import AuditAgent
from app.streaming.event_stream import EventStream
from app.schemas.audit import AuditRequest, AuditReport

logger = get_logger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/stream")
async def audit_stream(url: str = Query(..., description="URL to audit")):
    """SSE endpoint — streams real-time audit progress to terminal UI.

    Connects to the AuditAgent, which emits events as it runs each check.
    Frontend connects via EventSource and renders each event as a terminal line.
    """
    logger.info("SSE audit stream started for: %s", url)

    async def event_generator():
        stream = EventStream()
        agent = AuditAgent(stream=stream)

        # Run agent in background task
        async def run_agent():
            try:
                report = await agent.run(url=url)
                await stream.complete(data=report.model_dump(mode="json"))
            except Exception as e:
                logger.error("SSE agent task failed: %s\n%s", e, traceback.format_exc())
                await stream.error(f"Audit failed: {str(e)}")

        task = asyncio.create_task(run_agent())

        try:
            # Yield events as they come from the agent
            # We use a timeout to yield a "ping" if no events occur, 
            # keeping the connection alive through proxies.
            while True:
                try:
                    # Wait for an event with a timeout for keep-alive
                    event = await asyncio.wait_for(stream.__anext__(), timeout=15.0)
                    
                    yield {
                        "data": json.dumps({
                            "type": event.type,
                            "message": event.message,
                            "timestamp": event.timestamp.isoformat(),
                            "data": event.data,
                            "stream_type": event.stream_type,
                        }),
                    }
                except asyncio.TimeoutError:
                    # Send a comment-based ping (standard SSE keep-alive)
                    # or a structured ping event. Here we do both for maximum compatibility.
                    yield ": ping\n\n" 
                    yield {
                        "data": json.dumps({
                            "type": "ping",
                            "message": "keep-alive",
                            "timestamp": asyncio.get_event_loop().time(),
                        }),
                    }
                except StopAsyncIteration:
                    break
        finally:
            # Ensure agent task is complete
            if not task.done():
                await task

    return EventSourceResponse(
        event_generator(),
        ping=20,  # Built-in sse-starlette ping every 20s
        send_timeout=3600,  # Allow stream to stay open for up to 1 hour
    )


@router.post("/single", response_model=AuditReport)
async def audit_single(request: AuditRequest):
    """REST endpoint — audit a URL and return JSON (no streaming).

    For API users or when SSE is not needed.
    """
    agent = AuditAgent()
    report = await agent.run(url=request.url)
    return report
