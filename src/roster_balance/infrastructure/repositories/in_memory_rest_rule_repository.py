"""In-memory rest-rule repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.rest_rule import RestRule


class InMemoryRestRuleRepository:
    def __init__(self) -> None:
        self._rules: dict[str, RestRule] = {}

    def list_for_team(self, team_id: str) -> list[RestRule]:
        return [rule for rule in self._rules.values() if rule.team_id == team_id]

    def get(self, rule_id: str) -> RestRule | None:
        return self._rules.get(rule_id)

    def add(self, rule: RestRule) -> RestRule:
        self._rules[rule.id] = rule
        return rule

    def save(self, rule: RestRule) -> RestRule:
        self._rules[rule.id] = rule
        return rule

    def delete(self, rule_id: str) -> None:
        self._rules.pop(rule_id, None)
