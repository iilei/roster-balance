"""SQLAlchemy-backed team ownership repository."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from sqlalchemy import select

from roster_balance.domain.models.team_ownership import TeamOwnership
from roster_balance.infrastructure.db.models import TeamMembershipModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker

    from roster_balance.domain.models.team_ownership import TeamMemberRole


class SQLAlchemyTeamOwnershipRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[TeamOwnership]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamMembershipModel)
                .where(TeamMembershipModel.team_id == team_id)
                .order_by(TeamMembershipModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def list_for_user(
        self, user_id: str, role: str | None = None
    ) -> builtins.list[TeamOwnership]:
        with self._session_factory.begin() as session:
            statement = select(TeamMembershipModel).where(
                TeamMembershipModel.user_id == user_id
            )
            if role is not None:
                statement = statement.where(TeamMembershipModel.role == role)
            rows = session.scalars(
                statement.order_by(TeamMembershipModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, team_id: str, user_id: str) -> TeamOwnership | None:
        with self._session_factory.begin() as session:
            row = session.get(TeamMembershipModel, (team_id, user_id))
            return None if row is None else self._to_domain(row)

    def add(self, ownership: TeamOwnership) -> TeamOwnership:
        with self._session_factory.begin() as session:
            row = TeamMembershipModel(
                team_id=ownership.team_id,
                user_id=ownership.user_id,
                role=ownership.role,
                created_at=ownership.created_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def delete(self, team_id: str, user_id: str) -> None:
        with self._session_factory.begin() as session:
            row = session.get(TeamMembershipModel, (team_id, user_id))
            if row is not None:
                session.delete(row)

    @staticmethod
    def _to_domain(row: TeamMembershipModel) -> TeamOwnership:
        return TeamOwnership(
            team_id=row.team_id,
            user_id=row.user_id,
            role=cast('TeamMemberRole', row.role),
            created_at=row.created_at,
        )
