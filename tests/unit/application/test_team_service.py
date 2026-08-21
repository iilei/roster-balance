import pytest

from roster_balance.application.services.team_service import TeamService
from roster_balance.domain.team_ids import TeamIdSpace
from roster_balance.infrastructure.repositories.in_memory_team_repository import (
    InMemoryTeamRepository,
)


def test_team_service_allocates_stable_distinct_ids_until_capacity() -> None:
    service = TeamService(InMemoryTeamRepository(), TeamIdSpace(2, 'test-seed'))

    first = service.create_team('First', None)
    second = service.create_team('Second', None)

    assert first.id != second.id
    assert service.get_team(first.id).id == first.id

    with pytest.raises(ValueError, match='maximum team count'):
        service.create_team('Third', None)


def test_same_seed_produces_same_first_team_id() -> None:
    first_service = TeamService(InMemoryTeamRepository(), TeamIdSpace(100, 'test-seed'))
    second_service = TeamService(
        InMemoryTeamRepository(),
        TeamIdSpace(100, 'test-seed'),
    )

    assert (
        first_service.create_team('Team', None).id
        == second_service.create_team('Team', None).id
    )
