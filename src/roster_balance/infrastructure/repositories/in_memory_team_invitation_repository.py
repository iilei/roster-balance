"""In-memory team invitation repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from datetime import datetime

    from roster_balance.domain.models.team_invitation import TeamInvitation


class InMemoryTeamInvitationRepository:
    def __init__(self) -> None:
        self._invitations: dict[str, TeamInvitation] = {}

    def get(self, invitation_id: str) -> TeamInvitation | None:
        return self._invitations.get(invitation_id)

    def find_pending(self, team_id: str, email: str) -> TeamInvitation | None:
        return next(
            (
                invitation
                for invitation in self._invitations.values()
                if invitation.team_id == team_id
                and invitation.email == email
                and invitation.status == 'pending'
            ),
            None,
        )

    def list_for_team(self, team_id: str) -> list[TeamInvitation]:
        return [
            invitation
            for invitation in self._invitations.values()
            if invitation.team_id == team_id
        ]

    def add(self, invitation: TeamInvitation) -> TeamInvitation:
        self._invitations[invitation.id] = invitation
        return invitation

    def save(self, invitation: TeamInvitation) -> TeamInvitation:
        self._invitations[invitation.id] = invitation
        return invitation

    def purge_expired(self, now: datetime) -> int:
        expired_ids = [
            invitation_id
            for invitation_id, invitation in self._invitations.items()
            if invitation.status == 'pending' and invitation.expires_at <= now
        ]
        for invitation_id in expired_ids:
            del self._invitations[invitation_id]
        return len(expired_ids)
