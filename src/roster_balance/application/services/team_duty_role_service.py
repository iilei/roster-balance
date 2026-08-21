"""Application services for team duty roles."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.team_duty_role import TeamDutyRole

if TYPE_CHECKING:
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.repositories.team_duty_role_repository import (
        TeamDutyRoleRepository,
    )


class DutyRoleNotFoundError(LookupError):
    """Raised when a duty role does not exist."""


class DutyRoleConflictError(ValueError):
    """Raised when a duty role slug is already configured."""


class TeamDutyRoleService:
    def __init__(
        self,
        repository: TeamDutyRoleRepository,
        ownership_service: TeamOwnershipService,
    ) -> None:
        self._repository = repository
        self._ownership_service = ownership_service

    def list_roles(self, team_id: str) -> list[TeamDutyRole]:
        return self._repository.list_for_team(team_id)

    def get_role(self, team_id: str, role_id: str) -> TeamDutyRole:
        role = self._repository.get(role_id)
        if role is None or role.team_id != team_id:
            raise DutyRoleNotFoundError(role_id)
        return role

    def get_role_by_slug(self, team_id: str, slug: str) -> TeamDutyRole:
        role = self._repository.get_by_slug(team_id, slug.strip().casefold())
        if role is None:
            raise DutyRoleNotFoundError(slug)
        return role

    def create_role(
        self,
        team_id: str,
        slug: str,
        display_name: str,
        description: str | None,
        principal: Principal,
    ) -> TeamDutyRole:
        self._authorize(team_id, principal)
        normalized_slug = slug.strip().casefold()
        if self._repository.get_by_slug(team_id, normalized_slug) is not None:
            raise DutyRoleConflictError(normalized_slug)
        now = datetime.now(UTC)
        return self._repository.add(
            TeamDutyRole(
                str(uuid4()),
                team_id,
                normalized_slug,
                display_name.strip(),
                description,
                True,
                now,
                now,
            )
        )

    def deactivate_role(
        self, team_id: str, role_id: str, principal: Principal
    ) -> TeamDutyRole:
        self._authorize(team_id, principal)
        role = self.get_role(team_id, role_id)
        role.active = False
        role.updated_at = datetime.now(UTC)
        return self._repository.save(role)

    def _authorize(self, team_id: str, principal: Principal) -> None:
        if not self._ownership_service.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
