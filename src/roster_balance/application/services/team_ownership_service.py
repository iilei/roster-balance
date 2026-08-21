"""Application services for team ownership."""

from datetime import UTC, datetime

from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.domain.repositories.team_ownership_repository import (
    TeamOwnershipRepository,
)


class OwnershipNotFoundError(LookupError):
    """Raised when a requested ownership relation does not exist."""


class OwnershipConflictError(ValueError):
    """Raised when a user already owns a team."""


class LastOwnerError(ValueError):
    """Raised when removing the final team owner."""


class OwnershipAuthorizationError(PermissionError):
    """Raised when a non-owner changes team ownership."""


class TeamOwnershipService:
    def __init__(self, repository: TeamOwnershipRepository) -> None:
        self._repository = repository

    def list_owners(self, team_id: str) -> list[TeamOwnership]:
        return self._repository.list_for_team(team_id)

    def is_owner(self, team_id: str, user_id: str) -> bool:
        return self._repository.get(team_id, user_id) is not None

    def add_initial_owner(self, team_id: str, user_id: str) -> TeamOwnership:
        if self._repository.list_for_team(team_id):
            raise OwnershipConflictError(team_id)
        return self._repository.add(TeamOwnership(team_id, user_id, datetime.now(UTC)))

    def add_owner(
        self, team_id: str, user_id: str, principal: Principal
    ) -> TeamOwnership:
        if not self.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
        if self._repository.get(team_id, user_id) is not None:
            raise OwnershipConflictError(user_id)
        return self._repository.add(TeamOwnership(team_id, user_id, datetime.now(UTC)))

    def remove_owner(self, team_id: str, user_id: str, principal: Principal) -> None:
        if not self.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
        if self._repository.get(team_id, user_id) is None:
            raise OwnershipNotFoundError(user_id)
        if len(self._repository.list_for_team(team_id)) == 1:
            raise LastOwnerError(team_id)
        self._repository.delete(team_id, user_id)
