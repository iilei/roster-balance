"""In-memory member favorability repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.member_favorability import MemberFavorability


class InMemoryMemberFavorabilityRepository:
    def __init__(self) -> None:
        self._favorability: dict[tuple[str, str, str], MemberFavorability] = {}

    def list_for_team(self, team_id: str) -> list[MemberFavorability]:
        return [item for item in self._favorability.values() if item.team_id == team_id]

    def list_for_member(self, team_id: str, member_id: str) -> list[MemberFavorability]:
        return [
            item
            for item in self._favorability.values()
            if item.team_id == team_id and item.member_id == member_id
        ]

    def get(
        self, team_id: str, member_id: str, duty_role_id: str
    ) -> MemberFavorability | None:
        return self._favorability.get((team_id, member_id, duty_role_id))

    def add(self, favorability: MemberFavorability) -> MemberFavorability:
        self._favorability[
            (favorability.team_id, favorability.member_id, favorability.duty_role_id)
        ] = favorability
        return favorability

    def save(self, favorability: MemberFavorability) -> MemberFavorability:
        self._favorability[
            (favorability.team_id, favorability.member_id, favorability.duty_role_id)
        ] = favorability
        return favorability

    def delete(self, team_id: str, member_id: str, duty_role_id: str) -> None:
        self._favorability.pop((team_id, member_id, duty_role_id), None)
