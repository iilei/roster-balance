import pytest

from roster_balance.domain.proquint import encode
from roster_balance.domain.team_ids import TeamIdSpace


def test_proquint_matches_upstream_example() -> None:
    assert encode(42) == "babop"


def test_team_ids_are_deterministic_for_a_seed() -> None:
    first = TeamIdSpace(1000, "test-seed")
    second = TeamIdSpace(1000, "test-seed")

    assert [first.encode_slot(slot) for slot in range(100)] == [
        second.encode_slot(slot) for slot in range(100)
    ]


def test_team_ids_are_distinct_and_have_length_based_on_maximum() -> None:
    space = TeamIdSpace(1000, "test-seed")
    identifiers = {space.encode_slot(slot) for slot in range(1000)}

    assert len(identifiers) == 1000
    assert all(len(identifier) == space.encoded_length for identifier in identifiers)


def test_team_id_space_rejects_out_of_range_slots() -> None:
    with pytest.raises(ValueError, match="outside"):
        TeamIdSpace(10, "test-seed").encode_slot(10)

    with pytest.raises(ValueError, match="positive"):
        TeamIdSpace(0, "test-seed")
