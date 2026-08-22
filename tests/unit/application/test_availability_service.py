from datetime import UTC, datetime

import pytest

from roster_balance.application.services.availability_service import (
    AvailabilityCalendarConflictError,
    AvailabilityCalendarNotFoundError,
    AvailabilityService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_availability_repository import (
    InMemoryAvailabilityCalendarRepository,
    InMemoryAvailabilityEntryRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)


def make_service() -> AvailabilityService:
    ownership_repository = InMemoryTeamOwnershipRepository()
    now = datetime.now(UTC)
    ownership_repository.add(TeamOwnership('team', 'local:owner', 'owner', now))
    ownership_repository.add(TeamOwnership('team', 'local:member', 'member', now))
    ownership = TeamOwnershipService(ownership_repository)
    return AvailabilityService(
        InMemoryAvailabilityCalendarRepository(),
        InMemoryAvailabilityEntryRepository(),
        ownership,
    )


def test_owner_can_file_member_calendar_and_entry() -> None:
    service = make_service()
    owner = Principal('local', 'owner')
    calendar = service.create_calendar(
        'team', 'local:member', 'vacation', None, 'Vacation', 'UTC', owner
    )

    entry = service.add_entry(
        'team',
        calendar.id,
        datetime(2026, 9, 1, tzinfo=UTC),
        datetime(2026, 9, 2, tzinfo=UTC),
        'unavailable',
        'Holiday',
        owner,
    )

    assert calendar.member_id == 'local:member'
    assert entry.availability == 'unavailable'
    assert service.list_entries('team', calendar.id, owner) == [entry]


def test_calendar_type_is_unique_per_member_and_team() -> None:
    service = make_service()
    owner = Principal('local', 'owner')
    service.create_calendar(
        'team', 'local:member', 'vacation', None, 'One', 'UTC', owner
    )

    with pytest.raises(AvailabilityCalendarConflictError):
        service.create_calendar(
            'team', 'local:member', 'VACATION', None, 'Two', 'UTC', owner
        )


def test_owner_cannot_file_calendar_for_non_member() -> None:
    service = make_service()

    with pytest.raises(AvailabilityCalendarNotFoundError):
        service.create_calendar(
            'team',
            'local:unknown',
            'vacation',
            None,
            'Vacation',
            'UTC',
            Principal('local', 'owner'),
        )


def test_non_owner_cannot_manage_calendars() -> None:
    service = make_service()

    with pytest.raises(OwnershipAuthorizationError):
        service.list_calendars('team', Principal('local', 'member'))


def test_entry_requires_positive_timezone_aware_interval() -> None:
    service = make_service()
    owner = Principal('local', 'owner')
    calendar = service.create_calendar(
        'team', 'local:member', 'vacation', None, 'Vacation', 'UTC', owner
    )

    with pytest.raises(ValueError, match='ends_at must be after starts_at'):
        service.add_entry(
            'team',
            calendar.id,
            datetime(2026, 9, 2, tzinfo=UTC),
            datetime(2026, 9, 1, tzinfo=UTC),
            'unavailable',
            None,
            owner,
        )


def test_owner_can_update_calendar_metadata_and_entry() -> None:
    service = make_service()
    owner = Principal('local', 'owner')
    calendar = service.create_calendar(
        'team', 'local:member', 'vacation', None, 'Vacation', 'UTC', owner
    )
    entry = service.add_entry(
        'team',
        calendar.id,
        datetime(2026, 9, 1, tzinfo=UTC),
        datetime(2026, 9, 2, tzinfo=UTC),
        'unavailable',
        'Holiday',
        owner,
    )

    updated_calendar = service.update_calendar(
        'team', calendar.id, 'Updated vacation', 'Europe/Amsterdam', owner
    )
    updated_entry = service.update_entry(
        'team',
        calendar.id,
        entry.id,
        datetime(2026, 9, 3, tzinfo=UTC),
        datetime(2026, 9, 4, tzinfo=UTC),
        'available',
        'Changed plan',
        owner,
    )

    assert updated_calendar.id == calendar.id
    assert updated_calendar.name == 'Updated vacation'
    assert updated_calendar.timezone == 'Europe/Amsterdam'
    assert updated_entry.id == entry.id
    assert updated_entry.availability == 'available'
    assert updated_entry.reason == 'Changed plan'
