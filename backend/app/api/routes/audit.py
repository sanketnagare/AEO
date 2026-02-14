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

        # Yield events as they come from the agent
        # NOTE: We intentionally do NOT set the "event" field.
        # All events go through EventSource.onmessage to avoid
        # conflicts with EventSource's built-in "error" event.
        async for event in stream:
            yield {
                "data": json.dumps({
                    "type": event.type,
                    "message": event.message,
                    "timestamp": event.timestamp.isoformat(),
                    "data": event.data,
                    "stream_type": event.stream_type,
                }),
            }

        # Ensure agent task is complete
        await task

    return EventSourceResponse(event_generator())


@router.post("/single", response_model=AuditReport)
async def audit_single(request: AuditRequest):
    """REST endpoint — audit a URL and return JSON (no streaming).

    For API users or when SSE is not needed.
    """
    agent = AuditAgent()
    report = await agent.run(url=request.url)
    return report
