"""In-memory roster-lane repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.roster_lane import RosterLane


class InMemoryRosterLaneRepository:
    def __init__(self) -> None:
        self._lanes: dict[str, RosterLane] = {}

    def list_for_team(self, team_id: str) -> list[RosterLane]:
        return [lane for lane in self._lanes.values() if lane.team_id == team_id]

    def get(self, lane_id: str) -> RosterLane | None:
        return self._lanes.get(lane_id)

    def add(self, lane: RosterLane) -> RosterLane:
        self._lanes[lane.id] = lane
        return lane

    def save(self, lane: RosterLane) -> RosterLane:
        self._lanes[lane.id] = lane
        return lane
