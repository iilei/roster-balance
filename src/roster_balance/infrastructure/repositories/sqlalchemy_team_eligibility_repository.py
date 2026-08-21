"""SQLAlchemy-backed team eligibility repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from roster_balance.domain.models.team_eligibility import TeamEligibility
from roster_balance.infrastructure.db.models import TeamEligibilityModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyTeamEligibilityRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[TeamEligibility]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamEligibilityModel)
                .where(TeamEligibilityModel.team_id == team_id)
                .order_by(TeamEligibilityModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def list_for_role(
        self, team_id: str, duty_role_id: str
    ) -> builtins.list[TeamEligibility]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamEligibilityModel)
                .where(
                    TeamEligibilityModel.team_id == team_id,
                    TeamEligibilityModel.duty_role_id == duty_role_id,
                )
                .order_by(TeamEligibilityModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(
        self, team_id: str, member_id: str, duty_role_id: str
    ) -> TeamEligibility | None:
        with self._session_factory.begin() as session:
            row = session.get(
                TeamEligibilityModel,
                (team_id, member_id, duty_role_id),
            )
            return None if row is None else self._to_domain(row)

    def add(self, eligibility: TeamEligibility) -> TeamEligibility:
        with self._session_factory.begin() as session:
            row = TeamEligibilityModel(
                team_id=eligibility.team_id,
                member_id=eligibility.member_id,
                duty_role_id=eligibility.duty_role_id,
                duty_role=eligibility.duty_role,
                created_at=eligibility.created_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def delete(self, team_id: str, member_id: str, duty_role_id: str) -> None:
        with self._session_factory.begin() as session:
            row = session.get(
                TeamEligibilityModel,
                (team_id, member_id, duty_role_id),
            )
            if row is not None:
                session.delete(row)

    @staticmethod
    def _to_domain(row: TeamEligibilityModel) -> TeamEligibility:
        return TeamEligibility(
            team_id=row.team_id,
            member_id=row.member_id,
            duty_role_id=row.duty_role_id,
            duty_role=row.duty_role,
            created_at=row.created_at,
        )
