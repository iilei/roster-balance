"""Application services for owner-managed availability calendars."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.availability import (
    AvailabilityCalendar,
    AvailabilityEntry,
)
from roster_balance.domain.vcard import parse_icalendar_entries

if TYPE_CHECKING:
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.repositories.availability_repository import (
        AvailabilityCalendarRepository,
        AvailabilityEntryRepository,
    )


class AvailabilityCalendarNotFoundError(LookupError):
    """Raised when a calendar is missing or outside the requested team."""


class AvailabilityEntryNotFoundError(LookupError):
    """Raised when an entry is missing from a calendar."""


class AvailabilityCalendarConflictError(ValueError):
    """Raised when a member already has a calendar of this type."""


class AvailabilityService:
    def __init__(
        self,
        calendars: AvailabilityCalendarRepository,
        entries: AvailabilityEntryRepository,
        ownership: TeamOwnershipService,
    ) -> None:
        self._calendars = calendars
        self._entries = entries
        self._ownership = ownership

    def list_calendars(
        self, team_id: str, principal: Principal
    ) -> list[AvailabilityCalendar]:
        self._authorize(team_id, principal)
        return self._calendars.list_for_team(team_id)

    def get_calendar(
        self, team_id: str, calendar_id: str, principal: Principal
    ) -> AvailabilityCalendar:
        self._authorize(team_id, principal)
        calendar = self._calendars.get(calendar_id)
        if calendar is None or calendar.team_id != team_id:
            raise AvailabilityCalendarNotFoundError(calendar_id)
        return calendar

    def create_calendar(
        self,
        team_id: str,
        member_id: str,
        calendar_type: str,
        custom_type: str | None,
        name: str,
        timezone: str,
        principal: Principal,
    ) -> AvailabilityCalendar:
        self._authorize(team_id, principal)
        if not self._ownership.is_member(team_id, member_id):
            raise AvailabilityCalendarNotFoundError(member_id)
        normalized_type = calendar_type.strip().casefold()
        if normalized_type not in {'holiday', 'vacation', 'custom'}:
            raise ValueError('type must be holiday, vacation, or custom')
        if normalized_type == 'custom' and not custom_type:
            raise ValueError('custom_type is required for custom calendars')
        if normalized_type != 'custom' and custom_type is not None:
            raise ValueError('custom_type is only valid for custom calendars')
        if any(
            calendar.member_id == member_id and calendar.type == normalized_type
            for calendar in self._calendars.list_for_team(team_id)
        ):
            raise AvailabilityCalendarConflictError(member_id)
        now = datetime.now(UTC)
        return self._calendars.add(
            AvailabilityCalendar(
                str(uuid4()),
                team_id,
                member_id,
                normalized_type,
                custom_type.strip() if custom_type else None,
                name.strip(),
                timezone.strip(),
                now,
                now,
            )
        )

    def update_calendar(
        self,
        team_id: str,
        calendar_id: str,
        name: str,
        timezone: str,
        principal: Principal,
    ) -> AvailabilityCalendar:
        calendar = self.get_calendar(team_id, calendar_id, principal)
        return self._calendars.save(
            replace(
                calendar,
                name=name.strip(),
                timezone=timezone.strip(),
                updated_at=datetime.now(UTC),
            )
        )

    def list_entries(
        self, team_id: str, calendar_id: str, principal: Principal
    ) -> list[AvailabilityEntry]:
        self.get_calendar(team_id, calendar_id, principal)
        return self._entries.list_for_calendar(calendar_id)

    def add_entry(
        self,
        team_id: str,
        calendar_id: str,
        starts_at: datetime,
        ends_at: datetime,
        availability: str,
        reason: str | None,
        principal: Principal,
    ) -> AvailabilityEntry:
        self.get_calendar(team_id, calendar_id, principal)
        if ends_at <= starts_at:
            raise ValueError('ends_at must be after starts_at')
        if starts_at.tzinfo is None or ends_at.tzinfo is None:
            raise ValueError('availability intervals must be timezone-aware')
        normalized = availability.strip().casefold()
        if normalized == 'blocked':
            normalized = 'unavailable'
        if normalized not in {'available', 'unavailable'}:
            raise ValueError('availability must be available or unavailable')
        now = datetime.now(UTC)
        return self._entries.add(
            AvailabilityEntry(
                str(uuid4()),
                calendar_id,
                starts_at,
                ends_at,
                normalized,
                reason.strip() if reason else None,
                now,
                now,
            )
        )

    def add_icalendar_source(
        self,
        team_id: str,
        calendar_id: str,
        content: bytes,
        effect: str,
        source_format: str,
        principal: Principal,
    ) -> list[AvailabilityEntry]:
        self.get_calendar(team_id, calendar_id, principal)
        if source_format.strip().casefold() != 'icalendar':
            raise ValueError('source_format must be icalendar')
        entries = parse_icalendar_entries(
            content, calendar_id=calendar_id, effect=effect
        )
        return self._entries.add_many(entries)

    def delete_calendar(
        self, team_id: str, calendar_id: str, principal: Principal
    ) -> None:
        self.get_calendar(team_id, calendar_id, principal)
        self._calendars.delete(calendar_id)

    def delete_entry(
        self, team_id: str, calendar_id: str, entry_id: str, principal: Principal
    ) -> None:
        self.get_calendar(team_id, calendar_id, principal)
        entry = self._entries.get(entry_id)
        if entry is None or entry.calendar_id != calendar_id:
            raise AvailabilityEntryNotFoundError(entry_id)
        self._entries.delete(entry_id)

    def update_entry(
        self,
        team_id: str,
        calendar_id: str,
        entry_id: str,
        starts_at: datetime,
        ends_at: datetime,
        availability: str,
        reason: str | None,
        principal: Principal,
    ) -> AvailabilityEntry:
        self.get_calendar(team_id, calendar_id, principal)
        entry = self._entries.get(entry_id)
        if entry is None or entry.calendar_id != calendar_id:
            raise AvailabilityEntryNotFoundError(entry_id)
        if ends_at <= starts_at:
            raise ValueError('ends_at must be after starts_at')
        if starts_at.tzinfo is None or ends_at.tzinfo is None:
            raise ValueError('availability intervals must be timezone-aware')
        normalized = availability.strip().casefold()
        if normalized == 'blocked':
            normalized = 'unavailable'
        if normalized not in {'available', 'unavailable'}:
            raise ValueError('availability must be available or unavailable')
        return self._entries.save(
            replace(
                entry,
                starts_at=starts_at,
                ends_at=ends_at,
                availability=normalized,
                reason=reason.strip() if reason else None,
                updated_at=datetime.now(UTC),
            )
        )

    def _authorize(self, team_id: str, principal: Principal) -> None:
        if not self._ownership.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
