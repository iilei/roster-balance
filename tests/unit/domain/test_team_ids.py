from roster_balance.domain.proquint import encode


def test_proquint_matches_upstream_example() -> None:
    assert encode(42) == 'babop'


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
