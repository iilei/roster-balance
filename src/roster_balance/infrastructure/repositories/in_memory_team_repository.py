"""In-memory team repository for local development and tests."""

from roster_balance.domain.models.team import Team


class InMemoryTeamRepository:
    def __init__(self) -> None:
        self._teams: dict[str, Team] = {}

    def list(self) -> list[Team]:
        return sorted(self._teams.values(), key=lambda team: team.created_at)

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
