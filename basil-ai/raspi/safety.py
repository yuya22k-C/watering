"""Safety guards for basil-ai.

Holds the final decision. A Claude suggestion must pass every guard before any
water is dispensed. See docs/safety-guards.md for the authoritative spec.

Guards must never raise: on unexpected input they fail safe (no watering).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class GuardConfig:
    max_water_ml_per_shot: int = 40
    min_cooldown_minutes: int = 180
    max_water_ml_per_day: int = 120
    sensor_stale_minutes: int = 10
    tank_empty_shutdown: bool = True


@dataclass
class GuardDecision:
    """Final decision after all guards."""

    water: bool
    ml: int
    clipped: bool
    source: str  # 'claude_guarded' | 'rule_based' | 'manual'
    guard_reason: str | None  # why clipped/denied, None on plain approve


def decide(
    suggestion: dict[str, Any] | None,
    latest: dict[str, Any],
    recent_24h: dict[str, Any],
    last_watering: dict[str, Any] | None,
    config: GuardConfig,
) -> GuardDecision:
    """Run all guards against a Claude suggestion (or None for rule-based).

    Order of guards (short-circuit; see docs/safety-guards.md):
      1. tank empty          -> deny
      2. sensor stale/missing -> deny
      3. abnormal readings    -> deny
      4. cooldown not elapsed -> deny
      5. daily ml exceeded    -> deny
      6. per-shot ml over cap -> clip (not deny)
      7. sudden weight drop   -> deny (leak suspected)

    When `suggestion` is None, build one via rule_based_decide() first.
    """
    raise NotImplementedError


def rule_based_decide(
    latest: dict[str, Any],
    recent_24h: dict[str, Any],
) -> dict[str, Any]:
    """Local fallback when Claude is unavailable or returns unparseable output.

    Returns the same shape as a parsed ClaudeSuggestion dict. Numbers are
    intentionally conservative; they are tuned during phase 5 (long-run test).
    """
    raise NotImplementedError
