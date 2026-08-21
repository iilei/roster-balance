"""In-memory team invitation repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.team_invitation import TeamInvitation


class InMemoryTeamInvitationRepository:
    def __init__(self) -> None:
        self._invitations: dict[str, TeamInvitation] = {}

    def get(self, invitation_id: str) -> TeamInvitation | None:
        return self._invitations.get(invitation_id)

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
