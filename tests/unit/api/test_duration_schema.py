import pytest
from pydantic import ValidationError

from roster_balance.api.schemas import RestRuleCreate


def test_rest_rule_schema_stores_and_serializes_canonical_seconds() -> None:
    rule = RestRuleCreate.model_validate(
        {'name': 'On-call recovery', 'cooldown_after': '24h 60m'}
    )

    assert rule.cooldown_after == 90000
    assert rule.model_dump() == {
        'name': 'On-call recovery',
        'cooldown_after': 90000,
    }


def test_rest_rule_schema_uses_configured_maximum(monkeypatch) -> None:
    monkeypatch.setenv('MAX_FACTORING_ENTITY_DURATION_SECONDS', '86400')

    with pytest.raises(ValidationError, match='maximum'):
        RestRuleCreate.model_validate({'name': 'Too long', 'cooldown_after': '1d 1m'})


def test_rest_rule_schema_rejects_non_duration_values() -> None:
    with pytest.raises(ValidationError, match='compact duration'):
        RestRuleCreate.model_validate({'name': 'Invalid', 'cooldown_after': object()})
