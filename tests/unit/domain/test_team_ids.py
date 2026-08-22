import pytest

from roster_balance.domain.proquint import decode, encode
from roster_balance.domain.team_ids import TeamIdSpace


def test_short_aliases_are_normalized_and_validated() -> None:
    assert encode(42) == '16'
    assert decode('16') == 42

    assert TeamIdSpace(maximum_teams=100).validate_alias('demo-team') == 'demo-team'


def test_short_aliases_reject_invalid_values() -> None:
    with pytest.raises(ValueError, match='must not be empty'):
        TeamIdSpace(maximum_teams=100).validate_alias('')
    with pytest.raises(ValueError, match='may contain only lowercase letters'):
        TeamIdSpace(maximum_teams=100).validate_alias('-invalid')
    with pytest.raises(ValueError, match='11 characters or fewer'):
        TeamIdSpace(maximum_teams=100).validate_alias('a' * 12)


def test_team_id_space_round_trips_within_bounds() -> None:
    space = TeamIdSpace(maximum_teams=100, seed='demo-seed')

    for slot in range(space.maximum_teams):
        encoded = space.encode_slot(slot)
        assert space.decode_slot(encoded) == slot
