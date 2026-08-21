"""In-memory team repository for local development and tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.team import Team


class InMemoryTeamRepository:
    def __init__(self) -> None:
        self._teams: dict[str, Team] = {}

    def list(self) -> builtins.list[Team]:
        return sorted(self._teams.values(), key=lambda team: team.created_at)

    def search(self, query: str) -> builtins.list[Team]:
        normalized_query = query.casefold()
        return [
            team
            for team in self.list()
            if normalized_query in team.name.casefold()
            or normalized_query in (team.description or '').casefold()
        ]

    def get(self, team_id: str) -> Team | None:
        return self._teams.get(team_id)

    def add(self, team: Team) -> Team:
        self._teams[team.id] = team
        return team

    def save(self, team: Team) -> Team:
        self._teams[team.id] = team
        return team

    def delete(self, team_id: str) -> None:
        self._teams.pop(team_id, None)
