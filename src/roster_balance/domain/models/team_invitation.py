"""Team invitation domain model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

InvitationStatus = Literal['pending', 'accepted', 'declined', 'expired']
InvitationRole = Literal['member']


@dataclass(slots=True)
class TeamInvitation:
    id: str
    team_id: str
    inviter_user_id: str
    email: str
    role: InvitationRole
    status: InvitationStatus
    token_hash: str
    created_at: datetime
    expires_at: datetime
    accepted_at: datetime | None = None
    accepted_by_user_id: str | None = None
