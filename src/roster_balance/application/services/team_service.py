"""Application-level orchestration for team operations."""

from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from roster_balance.domain.models.team import Team
from roster_balance.domain.repositories.team_repository import TeamRepository

_UNSET = object()


class TeamNotFoundError(LookupError):
	"""Raised when a requested team does not exist."""


class TeamNameConflictError(ValueError):
	"""Raised when a team name is already in use."""


class TeamService:
	def __init__(self, repository: TeamRepository) -> None:
		self._repository = repository

	def list_teams(self) -> list[Team]:
		return self._repository.list()

	def get_team(self, team_id: UUID) -> Team:
		team = self._repository.get(team_id)
		if team is None:
			raise TeamNotFoundError(team_id)
		return team

	def create_team(self, name: str, description: str | None) -> Team:
		if any(team.name.casefold() == name.casefold() for team in self._repository.list()):
			raise TeamNameConflictError(name)
		now = datetime.now(UTC)
		return self._repository.add(
			Team(uuid4(), name, description, True, now, now)
		)

	def update_team(
		self,
		team_id: UUID,
		*,
		name: str | None = None,
		description: str | None | object = _UNSET,
		active: bool | None = None,
	) -> Team:
		team = self.get_team(team_id)
		if name is not None and any(
			other.id != team_id and other.name.casefold() == name.casefold()
			for other in self._repository.list()
		):
			raise TeamNameConflictError(name)
		return self._repository.save(
			replace(
				team,
				name=name if name is not None else team.name,
				description=description if description is not _UNSET else team.description,
				active=active if active is not None else team.active,
				updated_at=datetime.now(UTC),
			)
		)

	def delete_team(self, team_id: UUID) -> None:
		self.get_team(team_id)
		self._repository.delete(team_id)
