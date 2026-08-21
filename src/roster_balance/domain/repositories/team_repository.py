"""Repository boundary for teams."""

from typing import Protocol

from roster_balance.domain.models.team import Team


class TeamRepository(Protocol):
    def list(self) -> list[Team]: ...

    def get(self, team_id: str) -> Team | None: ...

    def add(self, team: Team) -> Team: ...

    def save(self, team: Team) -> Team: ...

    def delete(self, team_id: str) -> None: ...
