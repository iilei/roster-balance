"""Roster eligibility relation for a team member."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class TeamEligibility:
    team_id: str
    member_id: str
    duty_role_id: str
    duty_role: str
    created_at: datetime
