"""Repository boundaries for availability calendars and entries."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.availability import (
        AvailabilityCalendar,
        AvailabilityEntry,
    )


class AvailabilityCalendarRepository(Protocol):
    def list_for_team(self, team_id: str) -> builtins.list[AvailabilityCalendar]: ...

    def get(self, calendar_id: str) -> AvailabilityCalendar | None: ...

    def add(self, calendar: AvailabilityCalendar) -> AvailabilityCalendar: ...

    def save(self, calendar: AvailabilityCalendar) -> AvailabilityCalendar: ...

    def delete(self, calendar_id: str) -> None: ...


class AvailabilityEntryRepository(Protocol):
    def list_for_calendar(
        self, calendar_id: str
    ) -> builtins.list[AvailabilityEntry]: ...

    def get(self, entry_id: str) -> AvailabilityEntry | None: ...

    def add(self, entry: AvailabilityEntry) -> AvailabilityEntry: ...

    def add_many(self, entries: list[AvailabilityEntry]) -> list[AvailabilityEntry]: ...

    def save(self, entry: AvailabilityEntry) -> AvailabilityEntry: ...

    def delete(self, entry_id: str) -> None: ...
