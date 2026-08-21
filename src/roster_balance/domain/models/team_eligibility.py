"""Roster eligibility relation for a team member."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TeamEligibility:
    team_id: str
    member_id: str
    created_at: datetime
