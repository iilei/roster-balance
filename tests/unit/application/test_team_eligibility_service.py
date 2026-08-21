from datetime import UTC, datetime

import pytest

from roster_balance.application.services.team_duty_role_service import (
    TeamDutyRoleService,
)
from roster_balance.application.services.team_eligibility_service import (
    EligibilityConflictError,
    TeamEligibilityService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_team_duty_role_repository import (
    InMemoryTeamDutyRoleRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_eligibility_repository import (
    InMemoryTeamEligibilityRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)


def make_service() -> TeamEligibilityService:
    ownership_repository = InMemoryTeamOwnershipRepository()
    ownership_repository.add(
        TeamOwnership('team', 'local:dev', 'owner', datetime.now(UTC))
    )
    ownership_service = TeamOwnershipService(ownership_repository)
    duty_role_service = TeamDutyRoleService(
        InMemoryTeamDutyRoleRepository(), ownership_service
    )
    duty_role_service.create_role(
        'team', 'on-call', 'On-call', None, Principal('local', 'dev')
    )
    return TeamEligibilityService(
        InMemoryTeamEligibilityRepository(),
        ownership_service,
        duty_role_service,
    )


def test_owner_can_add_eligible_member_without_changing_team_membership() -> None:
    service = make_service()

    added = service.add_eligible(
        'team', 'local:dev', 'on-call', Principal('local', 'dev')
    )

    assert added.member_id == 'local:dev'


def test_duplicate_eligibility_is_rejected() -> None:
    service = make_service()
    principal = Principal('local', 'dev')
    service.add_eligible('team', 'local:dev', 'on-call', principal)

    with pytest.raises(EligibilityConflictError):
        service.add_eligible('team', 'local:dev', 'on-call', principal)


def test_non_owner_cannot_change_eligibility() -> None:
    service = make_service()

    with pytest.raises(OwnershipAuthorizationError):
        service.add_eligible(
            'team', 'local:dev', 'on-call', Principal('local', 'other')
        )
