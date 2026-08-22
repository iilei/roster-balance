from datetime import UTC, datetime

import pytest

from roster_balance.domain.vcard import (
    ICalendarParseError,
    parse_icalendar_entries,
)


def test_parse_vcard_entries_requires_explicit_effect() -> None:
    with pytest.raises(ICalendarParseError, match='effect must be'):
        parse_icalendar_entries(
            'BEGIN:VCALENDAR\nEND:VCALENDAR', calendar_id='cal', effect='blocked'
        )


def test_parse_vcard_entries_parses_utc_and_folded_summary() -> None:
    entries = parse_icalendar_entries(
        'BEGIN:VCALENDAR\r\n'
        'BEGIN:VEVENT\r\n'
        'DTSTART:20260901T090000Z\r\n'
        'DTEND:20260901T170000Z\r\n'
        'SUMMARY:Team availability with a very long\r\n'
        ' folded description\r\n'
        'END:VEVENT\r\n'
        'END:VCALENDAR\r\n',
        calendar_id='cal',
        effect='unavailable',
        now=datetime(2026, 8, 22, tzinfo=UTC),
    )

    assert len(entries) == 1
    assert entries[0].id == 'cal:0'
    assert entries[0].starts_at == datetime(2026, 9, 1, 9, tzinfo=UTC)
    assert entries[0].ends_at == datetime(2026, 9, 1, 17, tzinfo=UTC)
    assert entries[0].availability == 'unavailable'
    assert entries[0].reason == 'Team availability with a very longfolded description'


def test_parse_vcard_entries_supports_tzid_and_all_day_dates() -> None:
    entries = parse_icalendar_entries(
        'BEGIN:VEVENT\n'
        'DTSTART;TZID=Europe/Amsterdam:20260901T090000\n'
        'DTEND;TZID=Europe/Amsterdam:20260901T170000\n'
        'END:VEVENT\n'
        'BEGIN:VEVENT\n'
        'DTSTART;VALUE=DATE:20260902\n'
        'DTEND;VALUE=DATE:20260904\n'
        'END:VEVENT\n',
        calendar_id='cal',
        effect='available',
    )

    assert entries[0].starts_at.isoformat() == '2026-09-01T09:00:00+02:00'
    assert entries[1].starts_at.isoformat() == '2026-09-02T00:00:00+00:00'
    assert entries[1].ends_at.isoformat() == '2026-09-04T00:00:00+00:00'


def test_parse_vcard_entries_rejects_invalid_event() -> None:
    with pytest.raises(ICalendarParseError, match='requires valid DTSTART and DTEND'):
        parse_icalendar_entries(
            'BEGIN:VEVENT\nDTSTART:20260901T090000Z\nEND:VEVENT\n',
            calendar_id='cal',
            effect='available',
        )
