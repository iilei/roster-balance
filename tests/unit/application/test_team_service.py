from datetime import UTC, datetime
from uuid import UUID

import pytest

from roster_balance.api import dependencies
from roster_balance.application.services.team_ownership_service import (
    TeamOwnershipService,
)
from roster_balance.application.services.team_service import (
    TeamNotFoundError,
    TeamService,
)
from roster_balance.domain.models.team import Team
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_repository import (
    InMemoryTeamRepository,
)


def test_team_service_allocates_distinct_uuid_ids() -> None:
    service = TeamService(InMemoryTeamRepository())

    first = service.create_team('First', None)
    second = service.create_team('Second', None)

    assert first.id != second.id
    assert UUID(first.id)
    assert UUID(second.id)
    assert service.get_team(first.id).id == first.id


def test_team_service_rejects_duplicate_team_names() -> None:
    service = TeamService(InMemoryTeamRepository())

    service.create_team('Duplicate', None)

    with pytest.raises(ValueError, match='already in use'):
        service.create_team('duplicate', None)


def test_team_service_lists_active_teams_for_a_user_by_role() -> None:
    team_repository = InMemoryTeamRepository()
    ownership_repository = InMemoryTeamOwnershipRepository()
    service = TeamService(
        team_repository,
        ownership_service=TeamOwnershipService(ownership_repository),
    )
    active_owned = Team(
        'owned', 'Owned', None, True, datetime.now(UTC), datetime.now(UTC)
    )
    active_member = Team(
        'member', 'Member', None, True, datetime.now(UTC), datetime.now(UTC)
    )
    inactive_owned = Team(
        'inactive', 'Inactive', None, False, datetime.now(UTC), datetime.now(UTC)
    )
    for team in (active_owned, active_member, inactive_owned):
        team_repository.add(team)
    ownership_repository.add(
        TeamOwnership('owned', 'local:dev', 'owner', datetime.now(UTC)),
    )
    ownership_repository.add(
        TeamOwnership('member', 'local:dev', 'member', datetime.now(UTC)),
    )
    ownership_repository.add(
        TeamOwnership('inactive', 'local:dev', 'owner', datetime.now(UTC)),
    )

    teams = service.list_teams_for_user('local:dev')
    owned = service.list_teams_for_user('local:dev', 'owner')

    assert [team.name for team, _ in teams] == ['Owned', 'Member']
    assert [team.name for team, _ in owned] == ['Owned']


def test_team_service_requires_membership_for_details_and_ownership_for_changes() -> (
    None
):
    team_repository = InMemoryTeamRepository()
    ownership_repository = InMemoryTeamOwnershipRepository()

    service = TeamService(
        team_repository,
        ownership_service=TeamOwnershipService(ownership_repository),
    )
    team = service.create_team('Owned', None)
    ownership_repository.add(
        TeamOwnership(team.id, 'local:dev', 'owner', datetime.now(UTC)),
    )

    assert service.get_team_for_member(team.id, 'local:dev').id == team.id
    with pytest.raises(TeamNotFoundError):
        service.get_team_for_member(team.id, 'local:other')
    with pytest.raises(PermissionError):
        service.delete_team_for_owner(team.id, 'local:other')


def test_application_dependencies_use_sqlalchemy_repositories() -> None:
    assert dependencies.user_repository.__class__.__name__ == 'SQLAlchemyUserRepository'
    assert (
        dependencies.team_service._repository.__class__.__name__
        == 'SQLAlchemyTeamRepository'
    )
    assert (
        dependencies.team_ownership_service._repository.__class__.__name__
        == 'SQLAlchemyTeamOwnershipRepository'
    )
