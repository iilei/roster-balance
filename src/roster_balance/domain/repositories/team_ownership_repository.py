"""Repository boundary for team ownership."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.team_ownership import TeamOwnership


class TeamOwnershipRepository(Protocol):
    def list_for_team(self, team_id: str) -> builtins.list[TeamOwnership]: ...

    def list_for_user(
        self, user_id: str, role: str | None = None
    ) -> builtins.list[TeamOwnership]: ...

    def get(self, team_id: str, user_id: str) -> TeamOwnership | None: ...

    def add(self, ownership: TeamOwnership) -> TeamOwnership: ...

    def delete(self, team_id: str, user_id: str) -> None: ...
