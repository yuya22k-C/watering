"""Claude API client for basil-ai.

Builds the prompt per docs/claude-api-prompt.md, sends a multimodal request to
claude-opus-4-7 (via the Anthropic SDK), and parses the JSON response.

The response is always a *suggestion*. Final decision belongs to safety.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ClaudeSuggestion:
    """Parsed response from Claude. All fields mirror docs/claude-api-prompt.md."""

    water: bool
    ml: int
    confidence: float
    reason: str
    observations: list[str]
    warnings: list[str]
    raw_text: str


@dataclass
class ClaudeCallResult:
    """Bundled result so main.py can persist it into api_logs in one shot."""

    suggestion: ClaudeSuggestion | None  # None if parse failed
    model: str
    latency_ms: int
    input_tokens: int | None
    output_tokens: int | None
    cache_read: int | None
    cache_creation: int | None
    prompt_text: str
    response_text: str
    error: str | None  # parse error or HTTP error


def build_prompt(
    latest: dict[str, Any],
    recent_24h_summary: dict[str, Any],
    last_decision: dict[str, Any] | None,
) -> tuple[str, str]:
    """Assemble (system_text, user_text).

    Keep the system message stable across calls (cacheable). Put dynamic
    per-call details (current instantaneous values, last decision) at the
    tail of the user message where they do not invalidate the cache prefix.
    """
    raise NotImplementedError


def call_claude(
    api_key: str,
    model: str,
    system_text: str,
    user_text: str,
    image_jpeg_base64: str,
    *,
    max_tokens: int = 600,
    timeout_s: float = 20.0,
) -> ClaudeCallResult:
    """Call the Anthropic API with multimodal input and parse the JSON reply.

    TODO:
    - Use anthropic.Anthropic(api_key=...).messages.create
    - Attach cache_control={"type":"ephemeral"} to the system block and the
      stable portion of the user message
    - 2-step exponential backoff on transient errors (2s, 4s); give up after
      the 3rd failure and return ClaudeCallResult(suggestion=None, error=...)
    - Strip stray markdown fences, parse JSON, validate required fields
    """
    raise NotImplementedError
