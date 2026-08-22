"""SQLAlchemy-backed roster-lane repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from roster_balance.domain.models.roster_lane import RosterLane
from roster_balance.infrastructure.db.models import RosterLaneModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyRosterLaneRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[RosterLane]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(RosterLaneModel)
                .where(RosterLaneModel.team_id == team_id)
                .order_by(RosterLaneModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, lane_id: str) -> RosterLane | None:
        with self._session_factory.begin() as session:
            row = session.get(RosterLaneModel, lane_id)
            return None if row is None else self._to_domain(row)

    def add(self, lane: RosterLane) -> RosterLane:
        with self._session_factory.begin() as session:
            row = RosterLaneModel(
                id=lane.id,
                team_id=lane.team_id,
                name=lane.name,
                duration=lane.duration,
                rest_rule_id=lane.rest_rule_id,
                active=lane.active,
                created_at=lane.created_at,
                updated_at=lane.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def save(self, lane: RosterLane) -> RosterLane:
        with self._session_factory.begin() as session:
            row = session.get(RosterLaneModel, lane.id)
            if row is None:
                raise LookupError(lane.id)
            row.name = lane.name
            row.duration = lane.duration
            row.rest_rule_id = lane.rest_rule_id
            row.active = lane.active
            row.updated_at = lane.updated_at
            session.flush()
            return self._to_domain(row)

    @staticmethod
    def _to_domain(row: RosterLaneModel) -> RosterLane:
        return RosterLane(
            id=row.id,
            team_id=row.team_id,
            name=row.name,
            duration=row.duration,
            rest_rule_id=row.rest_rule_id,
            active=row.active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
