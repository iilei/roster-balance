"""Application services for roster eligibility."""

from datetime import UTC, datetime

from roster_balance.application.services.team_duty_role_service import (
    TeamDutyRoleService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_eligibility import TeamEligibility
from roster_balance.domain.repositories.team_eligibility_repository import (
    TeamEligibilityRepository,
)


class EligibilityConflictError(ValueError):
    """Raised when a member is already roster eligible."""


class EligibilityNotFoundError(LookupError):
    """Raised when a member is not roster eligible."""


class TeamMemberNotFoundError(LookupError):
    """Raised when eligibility targets a non-member."""


class DutyRoleInactiveError(ValueError):
    """Raised when eligibility targets an inactive role."""


class TeamEligibilityService:
    def __init__(
        self,
        repository: TeamEligibilityRepository,
        ownership_service: TeamOwnershipService,
        duty_role_service: TeamDutyRoleService,
    ) -> None:
        self._repository = repository
        self._ownership_service = ownership_service
        self._duty_role_service = duty_role_service

    def list_eligible(
        self, team_id: str, duty_role: str | None = None
    ) -> list[TeamEligibility]:
        if duty_role is None:
            return self._repository.list_for_team(team_id)
        role = self._duty_role_service.get_role_by_slug(team_id, duty_role)
        return self._repository.list_for_role(team_id, role.id)

    def add_eligible(
        self,
        team_id: str,
        member_id: str,
        duty_role: str,
        principal: Principal,
    ) -> TeamEligibility:
        self._authorize(team_id, principal)
        role = self._duty_role_service.get_role_by_slug(team_id, duty_role)
        if not role.active:
            raise DutyRoleInactiveError(role.slug)
        if not any(
            member.user_id == member_id
            for member in self._ownership_service.list_members(team_id)
        ):
            raise TeamMemberNotFoundError(member_id)
        if self._repository.get(team_id, member_id, role.id) is not None:
            raise EligibilityConflictError(member_id)
        return self._repository.add(
            TeamEligibility(team_id, member_id, role.id, role.slug, datetime.now(UTC)),
        )

    def remove_eligible(
        self,
        team_id: str,
        member_id: str,
        duty_role: str,
        principal: Principal,
    ) -> None:
        self._authorize(team_id, principal)
        role = self._duty_role_service.get_role_by_slug(team_id, duty_role)
        if self._repository.get(team_id, member_id, role.id) is None:
            raise EligibilityNotFoundError(member_id)
        self._repository.delete(team_id, member_id, role.id)

    def _authorize(self, team_id: str, principal: Principal) -> None:
        if not self._ownership_service.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
