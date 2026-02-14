"""LLM service wrapping LiteLLM for unified AI model access."""

from typing import Optional
import json
import litellm

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class LLMService:
    """Thin wrapper around LiteLLM for unified LLM access.

    Supports model routing:
    - fast: Gemini 2.0 Flash (free, fast, good for analysis)
    - quality: GPT-4o (best quality for content generation)
    - cheap: GPT-4o-mini (good quality, low cost for simple tasks)
    """

    def __init__(self):
        settings = get_settings()
        self.model_fast = "gemini/gemini-2.5-flash-lite"
        self.model_quality = settings.llm_model_quality
        self.model_cheap = settings.llm_model_cheap

        # Silence LiteLLM debug logs
        litellm.suppress_debug_info = True

    async def complete(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        models: Optional[list[str]] = None,
        tier: str = "fast",
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        """Get a text completion from an LLM.

        Args:
            prompt: User message / prompt.
            system_prompt: System message for context.
            model: Specific model override (single).
            models: List of models to try in order (fallback).
            tier: "fast", "quality", or "cheap" (used if no model/models provided).
            temperature: Sampling temperature.
            max_tokens: Maximum response tokens.

        Returns:
            Response text.
        """
        # Determine candidate models
        candidates = []
        if models:
            candidates = models
        elif model:
            candidates = [model]
        else:
            default_model = {
                "fast": self.model_fast,
                "quality": self.model_quality,
                "cheap": self.model_cheap,
            }.get(tier, self.model_fast)
            candidates = [default_model]

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        last_exception = None

        for candidate in candidates:
            try:
                logger.info("LLM call: model=%s tier=%s temp=%.1f max_tokens=%d", candidate, tier, temperature, max_tokens)
                response = await litellm.acompletion(
                    model=candidate,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                content = response.choices[0].message.content
                logger.info("LLM response from %s: %d chars", candidate, len(content or ""))
                return content
            except Exception as e:
                logger.warning("LLM call failed for model %s: %s", candidate, str(e))
                last_exception = e
                continue

        # If all fail, raise the last exception
        if last_exception:
            raise last_exception
        raise Exception("No LLM models available")

    async def complete_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        tier: str = "fast",
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> dict:
        """Get a JSON-structured completion from an LLM.

        Args:
            prompt: Should request JSON output.
            system_prompt: System prompt (will append JSON instruction).
            model: Specific model override.
            tier: "fast", "quality", or "cheap".
            temperature: Lower default for structured output.
            max_tokens: Maximum response tokens.

        Returns:
            Parsed JSON dict.
        """
        json_instruction = "\n\nRespond with valid JSON only. No markdown, no code fences."
        full_system = (system_prompt or "") + json_instruction

        text = await self.complete(
            prompt=prompt,
            system_prompt=full_system,
            model=model,
            models=None,  # json wrapper doesn't support list yet, but consistent sig
            tier=tier,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # Clean up potential markdown code fences
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        text = text.strip()

        return json.loads(text)


# Singleton instance
llm_service = LLMService()
