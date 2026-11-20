"""OpenRouter client with streaming and model fallback.

Free OpenRouter models are rate-limited and change often. The client tries the
configured models in order; if none answers, it fetches OpenRouter's current list
of free models and tries a few of those. When streaming, it only switches model
before the first token arrives, so the user never sees two answers mixed.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from collections.abc import AsyncIterator

import httpx

log = logging.getLogger("llm")

API_BASE = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)
PREFERRED_HINTS = ("llama", "qwen", "gemma", "mistral", "deepseek", "nemotron", "gpt-oss", "glm", "kimi")


class LLMError(RuntimeError):
    pass


class LLMAuthError(LLMError):
    pass


class ThinkFilter:
    """Removes <think>...</think> blocks from streamed text, even when tags are split across chunks."""

    OPEN, CLOSE = "<think>", "</think>"

    def __init__(self):
        self.buf = ""
        self.in_think = False
        self.started = False

    def feed(self, text: str) -> str:
        self.buf += text
        out = ""
        while self.buf:
            if self.in_think:
                end = self.buf.find(self.CLOSE)
                if end == -1:
                    self.buf = self.buf[-(len(self.CLOSE) - 1):]
                    break
                self.buf = self.buf[end + len(self.CLOSE):]
                self.in_think = False
                continue
            start = self.buf.find(self.OPEN)
            if start == -1:
                keep = self._partial_tag(self.buf)
                out += self.buf[: len(self.buf) - keep]
                self.buf = self.buf[len(self.buf) - keep:]
                break
            out += self.buf[:start]
            self.buf = self.buf[start + len(self.OPEN):]
            self.in_think = True
        return self._trim_start(out)

    def flush(self) -> str:
        rest = "" if self.in_think else self.buf
        self.buf = ""
        return self._trim_start(rest)

    def _partial_tag(self, text: str) -> int:
        for k in range(len(self.OPEN) - 1, 0, -1):
            if text.endswith(self.OPEN[:k]):
                return k
        return 0

    def _trim_start(self, text: str) -> str:
        if not self.started:
            text = text.lstrip()
            self.started = bool(text)
        return text


class OpenRouterClient:
    def __init__(
        self,
        api_key: str | None,
        models: list[str],
        app_url: str = "",
        app_name: str = "Property Assistant",
        timeout: float = 45.0,
        max_tokens: int = 700,
    ):
        self.api_key = (api_key or "").strip()
        self.models = [m.strip() for m in models if m.strip()]
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": app_name,
        }
        if app_url:
            self.headers["HTTP-Referer"] = app_url
        self._free_models: list[str] = []
        self._free_models_at = 0.0
        self._last_good: str | None = None

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self.headers, timeout=httpx.Timeout(self.timeout, connect=10))

    def _payload(self, model: str, messages: list[dict], stream: bool) -> dict:
        return {"model": model, "messages": messages, "temperature": 0.2,
                "max_tokens": self.max_tokens, "stream": stream}

    async def discover_free_models(self, client: httpx.AsyncClient) -> list[str]:
        if self._free_models and time.time() - self._free_models_at < 3600:
            return self._free_models
        try:
            resp = await client.get(f"{API_BASE}/models", timeout=20)
            resp.raise_for_status()
            found = []
            for m in resp.json().get("data", []):
                mid = m.get("id", "")
                pricing = m.get("pricing") or {}
                free = mid.endswith(":free") or (
                    str(pricing.get("prompt")) in ("0", "0.0") and str(pricing.get("completion")) in ("0", "0.0")
                )
                outputs = (m.get("architecture") or {}).get("output_modalities") or ["text"]
                if free and "text" in outputs and (m.get("context_length") or 0) >= 16000:
                    found.append(mid)
            found.sort(key=lambda mid: (not any(h in mid.lower() for h in PREFERRED_HINTS), mid))
            self._free_models, self._free_models_at = found, time.time()
        except Exception as exc:
            log.warning("Free-model discovery failed: %s", exc)
        return self._free_models

    async def _candidates(self, client: httpx.AsyncClient):
        """Yield models to try: last working model, configured models, then discovered free models."""
        seen: set[str] = set()
        for model in ([self._last_good] if self._last_good else []) + self.models:
            if model not in seen:
                seen.add(model)
                yield model
        for model in (await self.discover_free_models(client))[:4]:
            if model not in seen:
                seen.add(model)
                yield model

    # ---- non-streaming ---------------------------------------------------

    async def chat(self, messages: list[dict]) -> tuple[str, str]:
        """Return (answer, model). Raises LLMError if no model answers."""
        if not self.enabled:
            raise LLMError("OPENROUTER_API_KEY is not set")
        errors: list[str] = []
        async with self._client() as client:
            async for model in self._candidates(client):
                text = await self._complete(client, model, messages, errors)
                if text:
                    self._last_good = model
                    return text, model
        raise LLMError("; ".join(errors[-4:]) or "no model available")

    async def _complete(self, client, model, messages, errors) -> str | None:
        try:
            resp = await client.post(f"{API_BASE}/chat/completions", json=self._payload(model, messages, False))
        except httpx.HTTPError as exc:
            errors.append(f"{model}: {type(exc).__name__}")
            return None
        if resp.status_code == 401:
            raise LLMAuthError("OpenRouter rejected the API key (401)")
        if resp.status_code != 200:
            errors.append(f"{model}: HTTP {resp.status_code} {resp.text[:160]}")
            return None
        try:
            data = resp.json()
            if "error" in data:
                errors.append(f"{model}: {data['error'].get('message', 'error')}")
                return None
            content = data["choices"][0]["message"].get("content") or ""
        except (ValueError, KeyError, IndexError, TypeError):
            errors.append(f"{model}: malformed response")
            return None
        content = THINK_RE.sub("", content).strip()
        if not content:
            errors.append(f"{model}: empty answer")
        return content or None

    # ---- streaming -------------------------------------------------------

    async def stream(self, messages: list[dict]) -> AsyncIterator[tuple[str, str]]:
        """Yield ("model", id) once, then ("delta", text) pieces. Raises LLMError if no model answers."""
        if not self.enabled:
            raise LLMError("OPENROUTER_API_KEY is not set")
        errors: list[str] = []
        async with self._client() as client:
            async for model in self._candidates(client):
                started = False
                async for piece in self._stream_one(client, model, messages, errors):
                    if not started:
                        started = True
                        yield "model", model
                    yield "delta", piece
                if started:
                    self._last_good = model
                    return
        raise LLMError("; ".join(errors[-4:]) or "no model available")

    async def _stream_one(self, client, model, messages, errors) -> AsyncIterator[str]:
        url = f"{API_BASE}/chat/completions"
        try:
            async with client.stream("POST", url, json=self._payload(model, messages, True)) as resp:
                if resp.status_code == 401:
                    raise LLMAuthError("OpenRouter rejected the API key (401)")
                if resp.status_code != 200:
                    body = (await resp.aread()).decode("utf-8", "replace")[:160]
                    errors.append(f"{model}: HTTP {resp.status_code} {body}")
                    return
                think = ThinkFilter()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue  # keep-alive comments
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        event = json.loads(data)
                    except ValueError:
                        continue
                    if "error" in event:
                        errors.append(f"{model}: {event['error'].get('message', 'stream error')}")
                        break
                    choices = event.get("choices") or []
                    if not choices:
                        continue
                    text = think.feed((choices[0].get("delta") or {}).get("content") or "")
                    if text:
                        yield text
                tail = think.flush()
                if tail:
                    yield tail
        except httpx.HTTPError as exc:
            errors.append(f"{model}: {type(exc).__name__}")
