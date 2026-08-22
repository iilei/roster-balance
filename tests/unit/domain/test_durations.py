import pytest

from roster_balance.domain.durations import (
    DurationParseError,
    format_duration,
    parse_duration,
)


def test_parse_duration_returns_seconds() -> None:
    assert parse_duration('1d 12h') == 129600


def test_parse_duration_accepts_only_complete_supported_tokens() -> None:
    assert parse_duration(' 2w 3d 4h 5m ') == 1483500

    for value in ('', '1day', '1h30m', '1.5h', '-1h', '1s', '1m 0x'):
        with pytest.raises(DurationParseError):
            parse_duration(value)


def test_parse_duration_enforces_limit_after_summing_tokens() -> None:
    with pytest.raises(DurationParseError, match='maximum'):
        parse_duration('1d 1h', max_seconds=86400)


def test_format_duration_returns_canonical_form() -> None:
    assert format_duration(60 * 60 * 24 + 60 * 60) == '1d 1h'
    assert format_duration(7 * 24 * 60 * 60) == '1w'


def test_format_duration_rejects_subminute_values() -> None:
    with pytest.raises(DurationParseError):
        format_duration(61)
