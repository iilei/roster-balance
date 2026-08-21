"""Proquint encoding for non-negative integers."""

_CONSONANTS = "bdfghjklmnprstvz"
_VOWELS = "aiou"


def encode(value: int, groups: int = 1) -> str:
    """Encode an integer as one or more fixed-width Proquint groups."""
    if value < 0:
        raise ValueError("value must be non-negative")
    if groups < 1:
        raise ValueError("groups must be positive")
    if value >= 1 << (groups * 16):
        raise ValueError("value does not fit in the requested groups")

    encoded = []
    for group in range(groups - 1, -1, -1):
        word = (value >> (group * 16)) & 0xFFFF
        encoded.append(
            "".join(
                (
                    _CONSONANTS[(word >> 12) & 0xF],
                    _VOWELS[(word >> 10) & 0x3],
                    _CONSONANTS[(word >> 6) & 0xF],
                    _VOWELS[(word >> 4) & 0x3],
                    _CONSONANTS[word & 0xF],
                )
            )
        )
    return "-".join(encoded)
