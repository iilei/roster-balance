"""Repository boundary for member favorability records."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.member_favorability import MemberFavorability


class MemberFavorabilityRepository(Protocol):
    def list_for_team(self, team_id: str) -> builtins.list[MemberFavorability]: ...

    def list_for_member(
        self, team_id: str, member_id: str
    ) -> builtins.list[MemberFavorability]: ...

    def get(
        self, team_id: str, member_id: str, duty_role_id: str
    ) -> MemberFavorability | None: ...

    def add(self, favorability: MemberFavorability) -> MemberFavorability: ...

    def save(self, favorability: MemberFavorability) -> MemberFavorability: ...

    def delete(self, team_id: str, member_id: str, duty_role_id: str) -> None: ...
