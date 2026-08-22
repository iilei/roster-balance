"""Explainable decision result structures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class ConstraintResult:
    step_id: str
    passed: bool
    hard: bool
    reason: str


@dataclass(frozen=True, slots=True)
class HopResult:
    step_id: str
    kind: str
    passed: bool
    reason: str
    value: float | None = None


@dataclass(frozen=True, slots=True)
class ScoreContribution:
    step_id: str
    raw_value: float
    weight: float
    contribution: float


@dataclass(frozen=True, slots=True)
class CandidateRecommendation:
    member_id: str
    score: float
    rank: int
    factors: tuple[ScoreContribution, ...]
    hops: tuple[HopResult, ...]


@dataclass(frozen=True, slots=True)
class CandidateRejection:
    member_id: str
    rejected_by: tuple[str, ...]
    hops: tuple[HopResult, ...]


@dataclass(frozen=True, slots=True)
class CandidateBoard:
    period_id: str
    starts_at: datetime
    ends_at: datetime
    duty_role_id: str
    ranked: tuple[CandidateRecommendation, ...]
    ruled_out: tuple[CandidateRejection, ...]
    selected_member_id: str | None


@dataclass(frozen=True, slots=True)
class DecisionResult:
    policy_id: str
    policy_version: int
    boards: tuple[CandidateBoard, ...]
