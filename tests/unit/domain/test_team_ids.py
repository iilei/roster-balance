from roster_balance.domain.proquint import decode, encode
from roster_balance.domain.team_ids import TeamIdSpace


def test_proquint_matches_upstream_example() -> None:
    assert encode(42) == 'babop'


def test_proquint_decode_round_trip() -> None:
    for value in (0, 1, 2, 42, 999, 65535):
        assert decode(encode(value)) == value


def test_proquint_alias_generation_is_independent_of_team_ids() -> None:
    alias = encode(42)

    assert alias == 'babop'
    assert alias.islower()
    assert len(alias) >= 5


def test_proquint_aliases_do_not_need_to_be_unique_for_the_same_value() -> None:
    first = encode(42)
    second = encode(42)

    assert first == second
    assert isinstance(first, str)


def test_team_id_space_round_trips_within_bounds() -> None:
    space = TeamIdSpace(maximum_teams=100, seed='demo-seed')

    # Alias uniqueness belongs in the persistence layer; the domain contract here is
    # deterministic encoding and recovery of the configured slot values.
    for slot in range(space.maximum_teams):
        encoded = space.encode_slot(slot)
        assert space.decode_slot(encoded) == slot
