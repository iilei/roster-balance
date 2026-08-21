"""Application services for roster eligibility."""

from datetime import UTC, datetime

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


class TeamEligibilityService:
    def __init__(
        self,
        repository: TeamEligibilityRepository,
        ownership_service: TeamOwnershipService,
    ) -> None:
        self._repository = repository
        self._ownership_service = ownership_service

    def list_eligible(self, team_id: str) -> list[TeamEligibility]:
        return self._repository.list_for_team(team_id)

    def add_eligible(
        self, team_id: str, member_id: str, principal: Principal
    ) -> TeamEligibility:
        self._authorize(team_id, principal)
        if self._repository.get(team_id, member_id) is not None:
            raise EligibilityConflictError(member_id)
        return self._repository.add(
            TeamEligibility(team_id, member_id, datetime.now(UTC))
        )

    def remove_eligible(
        self, team_id: str, member_id: str, principal: Principal
    ) -> None:
        self._authorize(team_id, principal)
        if self._repository.get(team_id, member_id) is None:
            raise EligibilityNotFoundError(member_id)
        self._repository.delete(team_id, member_id)

    def _authorize(self, team_id: str, principal: Principal) -> None:
        if not self._ownership_service.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
