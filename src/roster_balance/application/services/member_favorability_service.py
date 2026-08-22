"""Application services for manual member favorability and blocking."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
)
from roster_balance.domain.models.member_favorability import MemberFavorability

if TYPE_CHECKING:
    from roster_balance.application.services.team_duty_role_service import (
        TeamDutyRoleService,
    )
    from roster_balance.application.services.team_ownership_service import (
        TeamOwnershipService,
    )
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.repositories.member_favorability_repository import (
        MemberFavorabilityRepository,
    )


class MemberFavorabilityConflictError(ValueError):
    """Raised when a member already has an explicit favorability for the role."""


class MemberFavorabilityNotFoundError(LookupError):
    """Raised when a member favorability record is missing."""


class MemberFavorabilityService:
    def __init__(
        self,
        repository: MemberFavorabilityRepository,
        ownership_service: TeamOwnershipService,
        duty_role_service: TeamDutyRoleService,
    ) -> None:
        self._repository = repository
        self._ownership_service = ownership_service
        self._duty_role_service = duty_role_service

    def list_for_team(self, team_id: str) -> list[MemberFavorability]:
        return self._repository.list_for_team(team_id)

    def list_for_member(
        self, team_id: str, member_id: str, principal: Principal
    ) -> list[MemberFavorability]:
        self._authorize(team_id, principal)
        return self._repository.list_for_member(team_id, member_id)

    def create_favorability(
        self,
        team_id: str,
        member_id: str,
        duty_role_id: str,
        effect: str,
        blocking_level: str | None,
        favorability: float | None,
        constraint_strength: float | None,
        principal: Principal,
    ) -> MemberFavorability:
        self._authorize(team_id, principal)
        self._duty_role_service.get_role(team_id, duty_role_id)
        if self._repository.get(team_id, member_id, duty_role_id) is not None:
            raise MemberFavorabilityConflictError(duty_role_id)

        effect_value = effect.strip().casefold()
        if effect_value not in {'preferred', 'blocked'}:
            raise ValueError('effect must be preferred or blocked')
        if blocking_level is not None:
            blocking_level_value = blocking_level.strip().casefold()
            if blocking_level_value not in {'soft', 'hard'}:
                raise ValueError('blocking_level must be soft or hard')
        else:
            blocking_level_value = None

        if effect_value == 'blocked':
            if favorability is not None:
                raise ValueError('favorability must be null when effect is blocked')
        elif favorability is not None and not 0.0 <= float(favorability) <= 1.0:
            raise ValueError('favorability must be between 0 and 1')

        if constraint_strength is not None:
            constraint_strength_value = float(constraint_strength)
            if not 0.0 <= constraint_strength_value <= 1.0:
                raise ValueError('constraint_strength must be between 0 and 1')
        else:
            constraint_strength_value = None

        now = datetime.now(UTC)
        return self._repository.add(
            MemberFavorability(
                id=str(uuid4()),
                team_id=team_id,
                member_id=member_id,
                duty_role_id=duty_role_id,
                effect=effect_value,
                blocking_level=blocking_level_value,
                favorability=None if favorability is None else float(favorability),
                constraint_strength=constraint_strength_value,
                source='manual',
                created_at=now,
                updated_at=now,
            )
        )

    def delete_favorability(
        self,
        team_id: str,
        member_id: str,
        duty_role_id: str,
        principal: Principal,
    ) -> None:
        self._authorize(team_id, principal)
        if self._repository.get(team_id, member_id, duty_role_id) is None:
            raise MemberFavorabilityNotFoundError(duty_role_id)
        self._repository.delete(team_id, member_id, duty_role_id)

    def _authorize(self, team_id: str, principal: Principal) -> None:
        if not self._ownership_service.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
