"""In-memory team ownership repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.team_ownership import TeamOwnership


class InMemoryTeamOwnershipRepository:
    def __init__(self) -> None:
        self._ownership: dict[tuple[str, str], TeamOwnership] = {}

    def list_for_team(self, team_id: str) -> list[TeamOwnership]:
        return [
            relation
            for relation in self._ownership.values()
            if relation.team_id == team_id
        ]

    def get(self, team_id: str, user_id: str) -> TeamOwnership | None:
        return self._ownership.get((team_id, user_id))

    def add(self, ownership: TeamOwnership) -> TeamOwnership:
        self._ownership[(ownership.team_id, ownership.user_id)] = ownership
        return ownership

    def delete(self, team_id: str, user_id: str) -> None:
        self._ownership.pop((team_id, user_id), None)
