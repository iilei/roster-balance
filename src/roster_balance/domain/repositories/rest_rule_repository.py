"""Repository boundary for team-owned rest rules."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.rest_rule import RestRule


class RestRuleRepository(Protocol):
    def list_for_team(self, team_id: str) -> builtins.list[RestRule]: ...

    def get(self, rule_id: str) -> RestRule | None: ...

    def add(self, rule: RestRule) -> RestRule: ...

    def save(self, rule: RestRule) -> RestRule: ...

    def delete(self, rule_id: str) -> None: ...
