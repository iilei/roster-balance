"""Normalized application user."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    id: str
    provider: str
    subject: str
    email: str | None
    display_name: str | None
    active: bool
    created_at: datetime
    updated_at: datetime
