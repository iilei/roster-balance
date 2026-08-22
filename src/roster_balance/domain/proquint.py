"""Proquint encoding for non-negative integers."""

_CONSONANTS = 'bdfghjklmnprstvz'
_VOWELS = 'aiou'


def decode(value: str, groups: int | None = None) -> int:
    """Decode a proquint string back to its integer value."""
    if not isinstance(value, str):
        raise TypeError('value must be a string')

    normalized = value.strip().lower()
    if not normalized:
        raise ValueError('value must not be empty')

    parts = normalized.split('-')
    if not all(part for part in parts):
        raise ValueError('proquint groups must not be empty')
    if groups is not None and len(parts) != groups:
        raise ValueError('value does not match the requested group count')

    decoded = 0
    for part in parts:
        if len(part) != 5:
            raise ValueError('each proquint group must have length 5')

        word = 0
        for index, char in enumerate(part):
            if index % 2 == 0:
                if char not in _CONSONANTS:
                    raise ValueError(f'invalid proquint consonant: {char!r}')
                value_bits = _CONSONANTS.index(char)
            else:
                if char not in _VOWELS:
                    raise ValueError(f'invalid proquint vowel: {char!r}')
                value_bits = _VOWELS.index(char)

            if index == 0:
                word |= value_bits << 12
            elif index == 1:
                word |= value_bits << 10
            elif index == 2:
                word |= value_bits << 6
            elif index == 3:
                word |= value_bits << 4
            else:
                word |= value_bits

        decoded = (decoded << 16) | word
    return decoded


def encode(value: int, groups: int = 1) -> str:
    """Encode an integer as one or more fixed-width Proquint groups."""
    if value < 0:
        raise ValueError('value must be non-negative')
    if groups < 1:
        raise ValueError('groups must be positive')
    if value >= 1 << (groups * 16):
        raise ValueError('value does not fit in the requested groups')

    encoded = []
    for group in range(groups - 1, -1, -1):
        word = (value >> (group * 16)) & 0xFFFF
        encoded.append(
            ''.join(
                (
                    _CONSONANTS[(word >> 12) & 0xF],
                    _VOWELS[(word >> 10) & 0x3],
                    _CONSONANTS[(word >> 6) & 0xF],
                    _VOWELS[(word >> 4) & 0x3],
                    _CONSONANTS[word & 0xF],
                ),
            ),
        )
    return '-'.join(encoded)
