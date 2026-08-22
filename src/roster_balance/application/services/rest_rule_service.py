"""Application services for team-owned rest rules."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.rest_rule import RestRule

if TYPE_CHECKING:
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.repositories.rest_rule_repository import (
        RestRuleRepository,
    )


class RestRuleNotFoundError(LookupError):
    """Raised when a rest rule does not exist."""


class RestRuleService:
    def __init__(
        self,
        repository: RestRuleRepository,
        ownership_service: TeamOwnershipService,
    ) -> None:
        self._repository = repository
        self._ownership_service = ownership_service

    def list_rules(self, team_id: str, principal: Principal) -> list[RestRule]:
        self._authorize(team_id, principal)
        return self._repository.list_for_team(team_id)

    def get_rule(self, team_id: str, rule_id: str, principal: Principal) -> RestRule:
        self._authorize(team_id, principal)
        rule = self._repository.get(rule_id)
        if rule is None or rule.team_id != team_id:
            raise RestRuleNotFoundError(rule_id)
        return rule

    def create_rule(
        self, team_id: str, name: str, cooldown_after: int, principal: Principal
    ) -> RestRule:
        self._authorize(team_id, principal)
        now = datetime.now(UTC)
        return self._repository.add(
            RestRule(
                id=str(uuid4()),
                team_id=team_id,
                name=name.strip(),
                cooldown_after=cooldown_after,
                active=True,
                created_at=now,
                updated_at=now,
            )
        )

    def deactivate_rule(self, team_id: str, rule_id: str, principal: Principal) -> None:
        self._authorize(team_id, principal)
        rule = self.get_rule(team_id, rule_id, principal)
        rule.active = False
        rule.updated_at = datetime.now(UTC)
        self._repository.save(rule)

    def _authorize(self, team_id: str, principal: Principal) -> None:
        if not self._ownership_service.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
