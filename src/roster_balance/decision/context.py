"""Database-independent inputs for decision evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, timedelta


@dataclass(frozen=True, slots=True)
class PlanningPeriod:
    id: str
    starts_at: datetime
    ends_at: datetime
    duty_role_id: str


@dataclass(frozen=True, slots=True)
class AssignmentCandidate:
    member_id: str
    period_id: str


@dataclass(frozen=True, slots=True)
class AssignmentEvent:
    member_id: str
    lane_id: str
    starts_at: datetime
    ends_at: datetime
    cooldown_after: timedelta


@dataclass(frozen=True, slots=True)
class DecisionContext:
    periods: tuple[PlanningPeriod, ...]
    historical_events: tuple[AssignmentEvent, ...] = ()
    committed_events: tuple[AssignmentEvent, ...] = ()
    suggested_events: tuple[AssignmentEvent, ...] = ()
