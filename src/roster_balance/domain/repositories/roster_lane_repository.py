"""Repository boundary for team-owned roster lanes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    import builtins

    from roster_balance.domain.models.roster_lane import RosterLane


class RosterLaneRepository(Protocol):
    def list_for_team(self, team_id: str) -> builtins.list[RosterLane]: ...

    def get(self, lane_id: str) -> RosterLane | None: ...

    def add(self, lane: RosterLane) -> RosterLane: ...

    def save(self, lane: RosterLane) -> RosterLane: ...
