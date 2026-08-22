"""Team-owned cooldown rule for factoring entities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class RestRule:
    id: str
    team_id: str
    name: str
    cooldown_after: int
    active: bool
    created_at: datetime
    updated_at: datetime
