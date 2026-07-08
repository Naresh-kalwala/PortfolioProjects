"""Thin abstraction over multiple LLM providers so the rest of the app never
imports openai/anthropic/google.generativeai directly. Swap providers with
the AI_PROVIDER env var without touching any calling code.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings


class AIProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
        max_tokens: int = 2000,
    ) -> str:
        """Return the raw text completion for `prompt`."""

    async def complete_json(
        self, prompt: str, system: str | None = None, max_tokens: int = 2000
    ) -> dict[str, Any]:
        raw = await self.complete(prompt, system=system, json_mode=True, max_tokens=max_tokens)
        return _parse_json_response(raw)


def _parse_json_response(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


class OpenAIProvider(AIProvider):
    def __init__(self) -> None:
        from openai import AsyncOpenAI

        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = "gpt-4o"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
        max_tokens: int = 2000,
    ) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.4,
            response_format={"type": "json_object"} if json_mode else None,
        )
        return response.choices[0].message.content or ""


class AnthropicProvider(AIProvider):
    def __init__(self) -> None:
        from anthropic import AsyncAnthropic

        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = "claude-sonnet-5"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
        max_tokens: int = 2000,
    ) -> str:
        if json_mode:
            prompt = f"{prompt}\n\nRespond with ONLY valid JSON, no prose, no markdown fences."

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            system=system or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


class GeminiProvider(AIProvider):
    def __init__(self) -> None:
        import google.generativeai as genai

        genai.configure(api_key=settings.gemini_api_key)
        self._genai = genai
        self._model_name = "gemini-1.5-pro"

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=20))
    async def complete(
        self,
        prompt: str,
        system: str | None = None,
        json_mode: bool = False,
        max_tokens: int = 2000,
    ) -> str:
        model = self._genai.GenerativeModel(
            self._model_name, system_instruction=system or None
        )
        generation_config = {"max_output_tokens": max_tokens, "temperature": 0.4}
        if json_mode:
            generation_config["response_mime_type"] = "application/json"

        response = await model.generate_content_async(
            prompt, generation_config=generation_config
        )
        return response.text


_PROVIDERS: dict[str, type[AIProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
}

_instance_cache: dict[str, AIProvider] = {}


def get_ai_provider() -> AIProvider:
    name = settings.ai_provider
    if name not in _instance_cache:
        _instance_cache[name] = _PROVIDERS[name]()
    return _instance_cache[name]
