from datetime import UTC, datetime

import pytest

from roster_balance.application.services.rest_rule_service import RestRuleService
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_rest_rule_repository import (
    InMemoryRestRuleRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)


def make_service() -> RestRuleService:
    ownership_repository = InMemoryTeamOwnershipRepository()
    now = datetime.now(UTC)
    ownership_repository.add(TeamOwnership('team', 'local:owner', 'owner', now))
    ownership_repository.add(TeamOwnership('team', 'local:member', 'member', now))
    return RestRuleService(
        InMemoryRestRuleRepository(), TeamOwnershipService(ownership_repository)
    )


def test_owner_can_create_and_deactivate_rest_rule() -> None:
    service = make_service()
    principal = Principal('local', 'owner')

    rule = service.create_rule('team', 'On-call recovery', 86400, principal)

    assert rule.cooldown_after == 86400
    assert service.list_rules('team', principal) == [rule]
    service.deactivate_rule('team', rule.id, principal)
    assert service.get_rule('team', rule.id, principal).active is False


def test_non_owner_cannot_manage_rest_rules() -> None:
    service = make_service()

    with pytest.raises(OwnershipAuthorizationError):
        service.list_rules('team', Principal('local', 'member'))
