"""Team domain model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True)
class Team:
    id: str
    name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime
