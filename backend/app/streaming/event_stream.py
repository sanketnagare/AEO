"""EventStream — async bridge between agent emit() calls and SSE responses."""

import asyncio
from datetime import datetime, timezone
from typing import Optional, AsyncIterator

from app.schemas.audit import StreamEvent
from app.logging_config import get_logger

logger = get_logger(__name__)


class EventStream:
    """Async queue that bridges agent events to SSE responses.

    Usage:
        stream = EventStream()
        # Agent sends events:
        await stream.send("Crawling page...", level="info")
        # SSE endpoint iterates:
        async for event in stream:
            yield event
    """

    def __init__(self):
        self._queue: asyncio.Queue[Optional[StreamEvent]] = asyncio.Queue()
        self._closed = False

    async def send(
        self,
        message: str,
        level: str = "info",
        data: Optional[dict] = None,
        stream_type: str = "instant",
    ):
        """Send an event to the stream.

        Args:
            message: Human-readable message for terminal display.
            level: Event type — info, success, warning, error, progress, complete.
            data: Optional structured data payload.
            stream_type: "instant" for immediate display, "typing" for char-by-char typewriter.
        """
        if self._closed:
            return

        event = StreamEvent(
            type=level,
            message=message,
            timestamp=datetime.now(timezone.utc),
            data=data,
            stream_type=stream_type,
        )
        await self._queue.put(event)

    async def complete(self, data: Optional[dict] = None):
        """Send a completion event and close the stream."""
        await self.send("", level="complete", data=data)
        self._closed = True
        await self._queue.put(None)  # Sentinel to stop iteration

    async def error(self, message: str, data: Optional[dict] = None):
        """Send an error event and close the stream."""
        await self.send(message, level="error", data=data)
        self._closed = True
        await self._queue.put(None)

    def __aiter__(self) -> AsyncIterator[StreamEvent]:
        return self

    async def __anext__(self) -> StreamEvent:
        event = await self._queue.get()
        if event is None:
            raise StopAsyncIteration
        return event
