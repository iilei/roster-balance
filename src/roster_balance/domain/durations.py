"""Parsing and formatting of compact factoring-entity durations."""

from __future__ import annotations

import re

_DURATION_TOKEN = re.compile(r'(?P<amount>\d+)(?P<unit>[mhdw])')
_UNIT_SECONDS = {
    'w': 7 * 24 * 60 * 60,
    'd': 24 * 60 * 60,
    'h': 60 * 60,
    'm': 60,
}


class DurationParseError(ValueError):
    """Raised when a compact duration is invalid or exceeds its limit."""


def parse_duration(value: object, *, max_seconds: int | None = None) -> int:
    """Parse a compact duration into whole seconds."""
    if not isinstance(value, str):
        raise DurationParseError('duration must be a compact duration string')
    if not value.strip():
        raise DurationParseError('duration must not be empty')

    total_seconds = 0
    for token in value.split():
        match = _DURATION_TOKEN.fullmatch(token)
        if match is None:
            raise DurationParseError(
                f'invalid duration token {token!r}; use values such as 24h or 1d 12h'
            )
        total_seconds += int(match['amount']) * _UNIT_SECONDS[match['unit']]

    if total_seconds == 0:
        raise DurationParseError('duration must be greater than zero')
    if max_seconds is not None and total_seconds > max_seconds:
        raise DurationParseError(
            f'duration exceeds the maximum of {format_duration(max_seconds)}'
        )
    return total_seconds


def format_duration(total_seconds: int) -> str:
    """Format whole seconds as a canonical compact duration."""
    if not isinstance(total_seconds, int) or total_seconds <= 0:
        raise DurationParseError('duration must be a positive whole number of seconds')

    remaining = total_seconds
    parts: list[str] = []
    for unit, unit_seconds in _UNIT_SECONDS.items():
        amount, remaining = divmod(remaining, unit_seconds)
        if amount:
            parts.append(f'{amount}{unit}')
    if remaining:
        raise DurationParseError('duration must contain whole minutes')
    return ' '.join(parts)
