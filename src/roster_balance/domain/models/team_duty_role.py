"""Configured duty role for a team."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TeamDutyRole:
    id: str
    team_id: str
    slug: str
    display_name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime
