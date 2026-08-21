"""Team domain model."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class Team:
    id: UUID
    name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime
