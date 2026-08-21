from datetime import UTC, datetime

import pytest

from roster_balance.application.services.team_duty_role_service import (
    DutyRoleConflictError,
    TeamDutyRoleService,
)
from roster_balance.application.services.team_ownership_service import (
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_team_duty_role_repository import (
    InMemoryTeamDutyRoleRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)


def make_service() -> TeamDutyRoleService:
    ownership_repository = InMemoryTeamOwnershipRepository()
    ownership_repository.add(
        TeamOwnership('team', 'local:dev', 'owner', datetime.now(UTC))
    )
    return TeamDutyRoleService(
        InMemoryTeamDutyRoleRepository(), TeamOwnershipService(ownership_repository)
    )


def test_role_slugs_are_normalized_and_unique_per_team() -> None:
    service = make_service()
    principal = Principal('local', 'dev')

    role = service.create_role('team', ' On-Call ', 'On-call', None, principal)

    assert role.slug == 'on-call'
    with pytest.raises(DutyRoleConflictError):
        service.create_role('team', 'ON-CALL', 'Other', None, principal)
