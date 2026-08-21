from uuid import UUID

import pytest

from roster_balance.api import dependencies
from roster_balance.application.services.team_service import TeamService
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
