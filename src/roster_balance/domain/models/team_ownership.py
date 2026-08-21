"""Team ownership relation."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class TeamOwnership:
    team_id: str
    user_id: str
    created_at: datetime
