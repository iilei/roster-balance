"""Short team-alias helpers.

This project does not use proquint or Feistel-style shuffling for team aliases.
Aliases are simply short strings with a DB-level uniqueness constraint.
"""

from __future__ import annotations

import re

_MAX_ALIAS_LENGTH = 11
_ALIAS_PATTERN = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def normalize_alias(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError('team alias must be a string')

    normalized = value.strip().lower()
    if not normalized:
        raise ValueError('team alias must not be empty')
    if len(normalized) > _MAX_ALIAS_LENGTH:
        raise ValueError('team alias must be 11 characters or fewer')
    if not _ALIAS_PATTERN.fullmatch(normalized):
        raise ValueError(
            'team alias may contain only lowercase letters, digits, and hyphens'
        )
    return normalized


def encode(value: int, groups: int = 1) -> str:
    if value < 0:
        raise ValueError('value must be non-negative')
    if groups < 1:
        raise ValueError('groups must be positive')

    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    if value == 0:
        encoded_value = '0'
    else:
        chunks: list[str] = []
        current_value = value
        while current_value:
            current_value, remainder = divmod(current_value, 36)
            chunks.append(digits[remainder])
        encoded_value = ''.join(reversed(chunks))
    return normalize_alias(encoded_value)


def decode(value: str, groups: int | None = None) -> int:
    normalized = normalize_alias(value)
    if '-' in normalized:
        raise ValueError(
            'team alias must not include hyphens when decoding to an integer'
        )
    if groups is not None and groups < 1:
        raise ValueError('groups must be positive')
    return int(normalized, 36)
