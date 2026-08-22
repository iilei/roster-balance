from datetime import UTC, datetime

import pytest

from roster_balance.application.services.rest_rule_service import RestRuleService
from roster_balance.application.services.roster_lane_service import RosterLaneService
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.principal import Principal
from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.repositories.in_memory_rest_rule_repository import (
    InMemoryRestRuleRepository,
)
from roster_balance.infrastructure.repositories.in_memory_roster_lane_repository import (
    InMemoryRosterLaneRepository,
)
from roster_balance.infrastructure.repositories.in_memory_team_ownership_repository import (
    InMemoryTeamOwnershipRepository,
)


def make_service() -> tuple[RosterLaneService, RestRuleService]:
    ownership_repository = InMemoryTeamOwnershipRepository()
    now = datetime.now(UTC)
    ownership_repository.add(TeamOwnership('team', 'local:owner', 'owner', now))
    ownership_repository.add(TeamOwnership('other', 'local:owner', 'owner', now))
    ownership_service = TeamOwnershipService(ownership_repository)
    rest_rule_service = RestRuleService(InMemoryRestRuleRepository(), ownership_service)
    return (
        RosterLaneService(
            InMemoryRosterLaneRepository(), ownership_service, rest_rule_service
        ),
        rest_rule_service,
    )


def test_owner_can_create_and_deactivate_lane_with_team_rest_rule() -> None:
    service, rest_rules = make_service()
    principal = Principal('local', 'owner')
    rule = rest_rules.create_rule('team', 'On-call recovery', 86400, principal)

    lane = service.create_lane('team', '24-hour on-call', 86400, rule.id, principal)

    assert lane.duration == 86400
    assert lane.rest_rule_id == rule.id
    service.deactivate_lane('team', lane.id, principal)
    assert service.get_lane('team', lane.id, principal).active is False


def test_lane_rejects_rest_rule_from_another_team() -> None:
    service, rest_rules = make_service()
    principal = Principal('local', 'owner')
    rule = rest_rules.create_rule('other', 'Other recovery', 3600, principal)

    with pytest.raises(ValueError, match='does not belong'):
        service.create_lane('team', 'On-call', 86400, rule.id, principal)


def test_non_owner_cannot_manage_lanes() -> None:
    service, _ = make_service()

    with pytest.raises(OwnershipAuthorizationError):
        service.list_lanes('team', Principal('local', 'member'))
