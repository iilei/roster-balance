"""Manual favorability or blocking data for a team member."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class MemberFavorability:
    id: str
    team_id: str
    member_id: str
    duty_role_id: str
    effect: str
    blocking_level: str | None
    favorability: float | None
    constraint_strength: float | None
    source: str
    created_at: datetime
    updated_at: datetime
