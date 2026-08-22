"""Scheduling configuration for a roster lane."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime, timedelta


@dataclass(frozen=True, slots=True)
class RosterLane:
    id: str
    team_id: str
    name: str
    duration: timedelta
    cooldown_after: timedelta
    active: bool
    created_at: datetime
    updated_at: datetime
