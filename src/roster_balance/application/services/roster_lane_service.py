"""Application services for team-owned roster lanes."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from roster_balance.application.services.rest_rule_service import (
    RestRuleNotFoundError,
    RestRuleService,
)
from roster_balance.application.services.team_ownership_service import (
    OwnershipAuthorizationError,
    TeamOwnershipService,
)
from roster_balance.domain.models.roster_lane import RosterLane

if TYPE_CHECKING:
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.repositories.roster_lane_repository import (
        RosterLaneRepository,
    )


class RosterLaneNotFoundError(LookupError):
    """Raised when a roster lane does not exist."""


class RosterLaneService:
    def __init__(
        self,
        repository: RosterLaneRepository,
        ownership_service: TeamOwnershipService,
        rest_rule_service: RestRuleService,
    ) -> None:
        self._repository = repository
        self._ownership_service = ownership_service
        self._rest_rule_service = rest_rule_service

    def list_lanes(self, team_id: str, principal: Principal) -> list[RosterLane]:
        self._authorize(team_id, principal)
        return self._repository.list_for_team(team_id)

    def get_lane(self, team_id: str, lane_id: str, principal: Principal) -> RosterLane:
        self._authorize(team_id, principal)
        lane = self._repository.get(lane_id)
        if lane is None or lane.team_id != team_id:
            raise RosterLaneNotFoundError(lane_id)
        return lane

    def create_lane(
        self,
        team_id: str,
        name: str,
        duration: int,
        rest_rule_id: str,
        principal: Principal,
    ) -> RosterLane:
        self._authorize(team_id, principal)
        try:
            self._rest_rule_service.get_rule(team_id, rest_rule_id, principal)
        except RestRuleNotFoundError as error:
            raise ValueError('rest rule does not belong to team') from error
        now = datetime.now(UTC)
        return self._repository.add(
            RosterLane(
                id=str(uuid4()),
                team_id=team_id,
                name=name.strip(),
                duration=duration,
                rest_rule_id=rest_rule_id,
                active=True,
                created_at=now,
                updated_at=now,
            )
        )

    def deactivate_lane(self, team_id: str, lane_id: str, principal: Principal) -> None:
        self._authorize(team_id, principal)
        lane = self.get_lane(team_id, lane_id, principal)
        self._repository.save(replace(lane, active=False, updated_at=datetime.now(UTC)))

    def _authorize(self, team_id: str, principal: Principal) -> None:
        if not self._ownership_service.is_owner(team_id, principal.user_id):
            raise OwnershipAuthorizationError(principal.user_id)
