"""Bounded, human-readable team identifiers."""

from hashlib import blake2b
from math import ceil

from roster_balance.domain.proquint import decode as decode_proquint
from roster_balance.domain.proquint import encode as encode_proquint


class TeamIdSpace:
    def __init__(self, maximum_teams: int, seed: str) -> None:
        if maximum_teams < 1:
            raise ValueError('maximum_teams must be positive')
        self.maximum_teams = maximum_teams
        self._seed = seed.encode()
        self._groups = max(1, ceil((maximum_teams - 1).bit_length() / 16))
        self._width = max(2, ((maximum_teams - 1).bit_length() + 1) // 2 * 2)
        self._half_width = self._width // 2
        self._mask = (1 << self._half_width) - 1
        self._domain = 1 << self._width

    @property
    def encoded_length(self) -> int:
        return self._groups * 5 + max(0, self._groups - 1)

    def encode_slot(self, slot: int) -> str:
        if not 0 <= slot < self.maximum_teams:
            raise ValueError('team slot is outside the configured maximum')
        value = slot
        while True:
            value = self._permute(value)
            if value < self.maximum_teams:
                return encode_proquint(value, self._groups)

    def decode_slot(self, encoded: str) -> int:
        decoded = decode_proquint(encoded, self._groups)
        if not 0 <= decoded < self.maximum_teams:
            raise ValueError('encoded team id does not map to a valid slot')
        value = self._inverse_permute(decoded)
        if not 0 <= value < self.maximum_teams:
            raise ValueError('decoded team id is outside the configured maximum')
        return value

    def _permute(self, value: int) -> int:
        if not 0 <= value < self._domain:
            raise ValueError('value is outside the configured team-id domain')
        left = value >> self._half_width
        right = value & self._mask
        for round_number in range(8):
            digest = blake2b(
                self._seed + round_number.to_bytes(1, 'big') + right.to_bytes(8, 'big'),
                digest_size=8,
            ).digest()
            left, right = (
                right,
                (left ^ (int.from_bytes(digest, 'big') & self._mask)) & self._mask,
            )
        return (left << self._half_width) | right

    def _inverse_permute(self, value: int) -> int:
        if not 0 <= value < self._domain:
            raise ValueError('value is outside the configured team-id domain')
        left = value >> self._half_width
        right = value & self._mask
        for round_number in range(7, -1, -1):
            digest = blake2b(
                self._seed + round_number.to_bytes(1, 'big') + left.to_bytes(8, 'big'),
                digest_size=8,
            ).digest()
            left, right = (
                right ^ (int.from_bytes(digest, 'big') & self._mask),
                left,
            )
        return (left << self._half_width) | right
