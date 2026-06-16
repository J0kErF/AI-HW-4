"""LLM client — OpenAI-compatible chat, routed through the Gatekeeper.

Every completion goes through :meth:`ApiGatekeeper.execute`, so rate limits,
retries, the token ledger and the budget cap apply uniformly to the Graphify
semantic layer, the debugging agent, and the benchmark. The underlying client
is injected, so tests pass a fake and never hit the network.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from graphquest.shared.gatekeeper import ApiGatekeeper


@dataclass
class LLMResponse:
    """A completion plus its token usage."""

    text: str
    input_tokens: int
    output_tokens: int


def build_chat_client(api_key: str, base_url: str | None = None) -> Any:
    """Construct an OpenAI-compatible client (DeepSeek via ``base_url``)."""
    import openai

    return openai.OpenAI(api_key=api_key, base_url=base_url)


def _usage(resp: Any) -> tuple[int, int]:
    """Extract (prompt, completion) tokens from an OpenAI-style response."""
    usage = getattr(resp, "usage", None)
    if usage is None:
        return (0, 0)
    return (int(getattr(usage, "prompt_tokens", 0)), int(getattr(usage, "completion_tokens", 0)))


class LLMClient:
    """Thin chat wrapper that bills every call through the Gatekeeper.

    Args:
        gatekeeper: The single chokepoint (rate limit, budget, ledger).
        model: Model id (from config/env, never hardcoded).
        client: An object exposing ``chat.completions.create(...)`` (the openai
            SDK client, or a fake in tests).
        service: Gatekeeper service bucket name.
    """

    def __init__(
        self, gatekeeper: ApiGatekeeper, model: str, client: Any, service: str = "llm"
    ) -> None:
        self._gk = gatekeeper
        self._model = model
        self._client = client
        self._service = service

    def complete(self, system: str, user: str, temperature: float = 0.0) -> LLMResponse:
        """Run one chat completion through the gatekeeper and return text+usage."""
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]

        def call() -> Any:
            return self._client.chat.completions.create(
                model=self._model, messages=messages, temperature=temperature
            )

        resp = self._gk.execute(
            self._service, call, token_extractor=_usage, model=self._model
        )
        in_tok, out_tok = _usage(resp)
        return LLMResponse(text=resp.choices[0].message.content, input_tokens=in_tok,
                           output_tokens=out_tok)
