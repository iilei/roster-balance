"""Team ownership relation."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

TeamMemberRole = Literal['owner', 'member']


@dataclass(slots=True)
class TeamOwnership:
    team_id: str
    user_id: str
    role: TeamMemberRole
    created_at: datetime
