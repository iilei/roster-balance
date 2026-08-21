"""Application-level orchestration for team operations."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from roster_balance.domain.models.team import Team

if TYPE_CHECKING:
    from roster_balance.application.services.team_ownership_service import (
        TeamOwnershipService,
    )
    from roster_balance.application.services.user_service import UserService
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.repositories.team_repository import TeamRepository

_UNSET = object()


class TeamNotFoundError(LookupError):
    """Raised when a requested team does not exist."""


class TeamNameConflictError(ValueError):
    """Raised when a team name is already in use."""

    def __init__(self, name: str) -> None:
        super().__init__(f'team name already in use: {name}')


class TeamService:
    def __init__(
        self,
        repository: TeamRepository,
        user_service: UserService | None = None,
        ownership_service: TeamOwnershipService | None = None,
    ) -> None:
        self._repository = repository
        self._user_service = user_service
        self._ownership_service = ownership_service

    def list_teams(self) -> list[Team]:
        return self._repository.list()

    def search_teams(self, query: str) -> list[Team]:
        return self._repository.search(query)

    def get_team(self, team_id: str) -> Team:
        team = self._repository.get(team_id)
        if team is None:
            raise TeamNotFoundError(team_id)
        return team

    def create_team(
        self,
        name: str,
        description: str | None,
        principal: Principal | None = None,
    ) -> Team:
        if any(
            team.name.casefold() == name.casefold() for team in self._repository.list()
        ):
            raise TeamNameConflictError(name)
        team_id = str(uuid4())
        now = datetime.now(UTC)
        team = self._repository.add(Team(team_id, name, description, True, now, now))
        if principal is not None:
            if self._user_service is None or self._ownership_service is None:
                raise RuntimeError('team ownership services are not configured')
            user = self._user_service.resolve(principal)
            self._ownership_service.add_initial_owner(team.id, user.id)
        return team

    def update_team(
        self,
        team_id: str,
        *,
        name: str | None = None,
        description: str | object | None = _UNSET,
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
                description=cast('str | None', description)
                if description is not _UNSET
                else team.description,
                active=active if active is not None else team.active,
                updated_at=datetime.now(UTC),
            ),
        )

    def delete_team(self, team_id: str) -> None:
        self.get_team(team_id)
        self._repository.delete(team_id)
