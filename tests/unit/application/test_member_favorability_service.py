from datetime import UTC, datetime

import pytest

from roster_balance.application.services.member_favorability_service import (
    MemberFavorabilityConflictError,
    MemberFavorabilityService,
)
from roster_balance.application.services.team_duty_role_service import (
    TeamDutyRoleService,
)
from roster_balance.application.services.team_ownership_service import (
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_duty_role import TeamDutyRole
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_member_favorability_repository import (
    InMemoryMemberFavorabilityRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_duty_role_repository import (
    InMemoryTeamDutyRoleRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)


def make_service() -> MemberFavorabilityService:
    ownership_repository = InMemoryTeamOwnershipRepository()
    now = datetime.now(UTC)
    ownership_repository.add(
        TeamOwnership('team', 'local:member-user', 'member', now),
    )
    ownership_repository.add(
        TeamOwnership('team', 'local:owner-user', 'owner', now),
    )
    ownership_service = TeamOwnershipService(ownership_repository)
    duty_role_repository = InMemoryTeamDutyRoleRepository()
    duty_role_repository.add(
        TeamDutyRole(
            'role-1',
            'team',
            'on-call',
            'On-call',
            None,
            True,
            now,
            now,
        ),
    )
    duty_role_service = TeamDutyRoleService(
        duty_role_repository,
        ownership_service,
    )
    return MemberFavorabilityService(
        InMemoryMemberFavorabilityRepository(),
        ownership_service,
        duty_role_service,
    )


def test_manual_favorability_is_unique_per_member_and_role() -> None:
    service = make_service()
    principal = Principal('local', 'owner-user')

    created = service.create_favorability(
        team_id='team',
        member_id='local:member-user',
        duty_role_id='role-1',
        effect='preferred',
        blocking_level='soft',
        favorability=0.8,
        constraint_strength=0.4,
        principal=principal,
    )

    assert created.effect == 'preferred'
    assert created.source == 'manual'

    with pytest.raises(MemberFavorabilityConflictError):
        service.create_favorability(
            team_id='team',
            member_id='local:member-user',
            duty_role_id='role-1',
            effect='preferred',
            blocking_level='soft',
            favorability=0.9,
            constraint_strength=0.5,
            principal=principal,
        )
