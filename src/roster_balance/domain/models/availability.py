"""Availability calendar domain models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(frozen=True, slots=True)
class AvailabilityCalendar:
    id: str
    team_id: str
    member_id: str
    type: str
    custom_type: str | None
    name: str
    timezone: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class AvailabilityEntry:
    id: str
    calendar_id: str
    starts_at: datetime
    ends_at: datetime
    availability: str
    reason: str | None
    created_at: datetime
    updated_at: datetime
