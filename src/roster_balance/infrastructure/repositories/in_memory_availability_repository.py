"""In-memory availability repositories."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.availability import (
        AvailabilityCalendar,
        AvailabilityEntry,
    )


class InMemoryAvailabilityCalendarRepository:
    def __init__(self) -> None:
        self._calendars: dict[str, AvailabilityCalendar] = {}

    def list_for_team(self, team_id: str) -> list[AvailabilityCalendar]:
        return [item for item in self._calendars.values() if item.team_id == team_id]

    def get(self, calendar_id: str) -> AvailabilityCalendar | None:
        return self._calendars.get(calendar_id)

    def list_for_member(
        self, team_id: str, member_id: str
    ) -> list[AvailabilityCalendar]:
        return [
            item
            for item in self._calendars.values()
            if item.team_id == team_id and item.member_id == member_id
        ]

    def add(self, calendar: AvailabilityCalendar) -> AvailabilityCalendar:
        self._calendars[calendar.id] = calendar
        return calendar

    def save(self, calendar: AvailabilityCalendar) -> AvailabilityCalendar:
        self._calendars[calendar.id] = calendar
        return calendar

    def delete(self, calendar_id: str) -> None:
        self._calendars.pop(calendar_id, None)


class InMemoryAvailabilityEntryRepository:
    def __init__(self) -> None:
        self._entries: dict[str, AvailabilityEntry] = {}

    def list_for_calendar(self, calendar_id: str) -> list[AvailabilityEntry]:
        return [
            item for item in self._entries.values() if item.calendar_id == calendar_id
        ]

    def get(self, entry_id: str) -> AvailabilityEntry | None:
        return self._entries.get(entry_id)

    def add(self, entry: AvailabilityEntry) -> AvailabilityEntry:
        self._entries[entry.id] = entry
        return entry

    def add_many(self, entries: list[AvailabilityEntry]) -> list[AvailabilityEntry]:
        for entry in entries:
            self.add(entry)
        return entries

    def save(self, entry: AvailabilityEntry) -> AvailabilityEntry:
        self._entries[entry.id] = entry
        return entry

    def delete(self, entry_id: str) -> None:
        self._entries.pop(entry_id, None)
