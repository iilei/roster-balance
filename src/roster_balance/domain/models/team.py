"""Team domain model."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Team:
    id: str
    name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime
