"""Base agent class with SSE streaming support."""

import asyncio
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.streaming.event_stream import EventStream


class BaseAgent:
    """Base class for all AIVisibilityBot agents.

    Provides:
    - Database session injection
    - SSE event streaming (emit → terminal UI)
    - Standard run() interface

    All agents follow the same pattern:
    1. Accept input parameters
    2. Emit progress events to terminal
    3. Execute steps (API calls, checks, LLM calls)
    4. Return structured results
    """

    def __init__(
        self,
        db: Optional[AsyncSession] = None,
        stream: Optional[EventStream] = None,
    ):
        self.db = db
        self.stream = stream

    async def emit(self, message: str, level: str = "info", data: Optional[dict] = None,
                   stream_type: str = "instant"):
        """Send a message to the terminal UI via SSE.

        Args:
            message: Human-readable message.
            level: info, success, warning, error, progress.
            data: Optional structured data.
            stream_type: "instant" or "typing" for char-by-char rendering.
        """
        if self.stream:
            await self.stream.send(message, level=level, data=data, stream_type=stream_type)

    async def emit_typing(self, message: str, level: str = "info", data: Optional[dict] = None):
        """Emit a message with typewriter rendering hint + small delay for visual pacing."""
        await self.emit(message, level=level, data=data, stream_type="typing")
        await asyncio.sleep(0.05)

    async def emit_success(self, message: str, data: Optional[dict] = None):
        """Shorthand for success-level emit."""
        await self.emit(message, level="success", data=data)

    async def emit_warning(self, message: str, data: Optional[dict] = None):
        """Shorthand for warning-level emit."""
        await self.emit(message, level="warning", data=data)

    async def emit_error(self, message: str, data: Optional[dict] = None):
        """Shorthand for error-level emit."""
        await self.emit(message, level="error", data=data)

    async def run(self, **kwargs) -> dict:
        """Main agent logic — override in subclass.

        Returns:
            Dict with agent results.
        """
        raise NotImplementedError("Subclasses must implement run()")
