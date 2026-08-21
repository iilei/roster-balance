"""Repository boundary for teams."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.team import Team


class TeamRepository(Protocol):
    def list(self) -> builtins.list[Team]: ...

    def search(self, query: str) -> builtins.list[Team]: ...

    def get(self, team_id: str) -> Team | None: ...

    def add(self, team: Team) -> Team: ...

    def save(self, team: Team) -> Team: ...

    def delete(self, team_id: str) -> None: ...
