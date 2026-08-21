"""Repository boundary for team invitations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.team_invitation import TeamInvitation


class TeamInvitationRepository(Protocol):
    def get(self, invitation_id: str) -> TeamInvitation | None: ...

    def list_for_team(self, team_id: str) -> builtins.list[TeamInvitation]: ...

    def add(self, invitation: TeamInvitation) -> TeamInvitation: ...

    def save(self, invitation: TeamInvitation) -> TeamInvitation: ...
