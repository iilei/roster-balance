"""Normalized application user."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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
