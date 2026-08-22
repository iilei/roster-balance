"""Adapt vobject iCalendar components into availability entries."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from typing import Any

import vobject

from roster_balance.domain.models.availability import AvailabilityEntry


class ICalendarParseError(ValueError):
    """Raised when a calendar component cannot be converted to an entry."""


def parse_icalendar_entries(
    value: bytes | str,
    *,
    calendar_id: str,
    effect: str,
    now: datetime | None = None,
) -> list[AvailabilityEntry]:
    """Parse vobject VEVENT components with an explicit availability effect."""
    normalized_effect = effect.strip().casefold()
    if normalized_effect not in {'available', 'unavailable'}:
        raise ICalendarParseError('effect must be available or unavailable')
    try:
        text = value.decode('utf-8') if isinstance(value, bytes) else value
        calendars = list(vobject.readComponents(text))
        vevents = [
            event
            for calendar in calendars
            for event in (
                calendar.getChildren() if calendar.name == 'VCALENDAR' else (calendar,)
            )
            if event.name == 'VEVENT'
        ]
    except (UnicodeDecodeError, vobject.base.ParseError, AttributeError) as error:
        raise ICalendarParseError('invalid iCalendar data') from error
    if not vevents:
        raise ICalendarParseError('calendar contains no VEVENT entries')

    timestamp = now or datetime.now(UTC)
    entries: list[AvailabilityEntry] = []
    for index, event in enumerate(vevents):
        try:
            starts_at = _as_datetime(event.dtstart.value)
            ends_at = _as_datetime(event.dtend.value)
        except (AttributeError, TypeError, ValueError) as error:
            raise ICalendarParseError(
                'VEVENT requires valid DTSTART and DTEND'
            ) from error
        if ends_at <= starts_at:
            raise ICalendarParseError('VEVENT DTEND must be after DTSTART')
        reason = _component_text(event, 'summary') or _component_text(
            event, 'description'
        )
        entries.append(
            AvailabilityEntry(
                id=f'{calendar_id}:{index}',
                calendar_id=calendar_id,
                starts_at=starts_at,
                ends_at=ends_at,
                availability=normalized_effect,
                reason=reason,
                created_at=timestamp,
                updated_at=timestamp,
            )
        )
    return entries


def _as_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            raise ICalendarParseError('VEVENT datetime must be timezone-aware')
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min, UTC)
    raise ICalendarParseError('VEVENT datetime has an unsupported value')


def _component_text(event: Any, name: str) -> str | None:
    component = getattr(event, name, None)
    value = getattr(component, 'value', None)
    return value if isinstance(value, str) else None
