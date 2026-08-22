from datetime import UTC, datetime

import pytest

from roster_balance.application.services.team_ownership_service import (
    LastOwnerError,
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)


def test_owner_can_add_another_owner() -> None:
    repository = InMemoryTeamOwnershipRepository()
    repository.add(TeamOwnership('team', 'local:alice', 'owner', datetime.now(UTC)))
    service = TeamOwnershipService(repository)

    added = service.add_owner('team', 'local:bob', Principal('local', 'alice'))

    assert added.user_id == 'local:bob'
    assert [owner.user_id for owner in service.list_owners('team')] == [
        'local:alice',
        'local:bob',
    ]


def test_non_owner_cannot_add_owner() -> None:
    repository = InMemoryTeamOwnershipRepository()
    repository.add(TeamOwnership('team', 'local:alice', 'owner', datetime.now(UTC)))
    service = TeamOwnershipService(repository)

    with pytest.raises(OwnershipAuthorizationError):
        service.add_owner('team', 'local:bob', Principal('local', 'bob'))


def test_last_owner_cannot_be_removed() -> None:
    repository = InMemoryTeamOwnershipRepository()
    repository.add(TeamOwnership('team', 'local:alice', 'owner', datetime.now(UTC)))
    service = TeamOwnershipService(repository)

    with pytest.raises(LastOwnerError):
        service.remove_owner('team', 'local:alice', Principal('local', 'alice'))


def test_require_member_rejects_users_outside_the_team() -> None:
    repository = InMemoryTeamOwnershipRepository()
    repository.add(TeamOwnership('team', 'local:alice', 'member', datetime.now(UTC)))
    service = TeamOwnershipService(repository)

    service.require_member('team', 'local:alice')
    with pytest.raises(OwnershipAuthorizationError):
        service.require_member('team', 'local:bob')
