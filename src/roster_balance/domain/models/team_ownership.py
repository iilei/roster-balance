"""Team ownership relation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from datetime import datetime

TeamMemberRole = Literal['owner', 'member']


@dataclass(slots=True)
class TeamOwnership:
    team_id: str
    user_id: str
    role: TeamMemberRole
    created_at: datetime
