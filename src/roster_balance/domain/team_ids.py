"""Short, database-backed team aliases."""

from __future__ import annotations

from roster_balance.domain.proquint import decode, encode, normalize_alias

_MAX_ALIAS_LENGTH = 11


class TeamIdSpace:
    """Validate and generate short human-friendly team aliases.

    The domain should not implement Feistel or proquint shuffling. Uniqueness is
    enforced by the database layer.
    """

    def __init__(self, maximum_teams: int, seed: str | None = None) -> None:
        if maximum_teams < 1:
            raise ValueError('maximum_teams must be positive')
        if maximum_teams > 36**_MAX_ALIAS_LENGTH:
            raise ValueError('maximum_teams exceeds the supported alias capacity')
        self.maximum_teams = maximum_teams
        self.seed = seed or 'default'

    @property
    def encoded_length(self) -> int:
        return _MAX_ALIAS_LENGTH

    def encode_slot(self, slot: int) -> str:
        if not 0 <= slot < self.maximum_teams:
            raise ValueError('team slot is outside the configured maximum')
        return encode(slot)

    def decode_slot(self, encoded: str) -> int:
        return decode(encoded)

    def validate_alias(self, alias: str) -> str:
        return normalize_alias(alias)

    def is_valid_alias(self, alias: str) -> bool:
        try:
            self.validate_alias(alias)
        except ValueError:
            return False
        return True
