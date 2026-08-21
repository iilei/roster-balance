"""PostgreSQL / SQLAlchemy team repository implementation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from roster_balance.domain.models.team import Team
from roster_balance.infrastructure.db.models import TeamModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyTeamRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list(self) -> builtins.list[Team]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamModel).order_by(TeamModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def search(self, query: str) -> builtins.list[Team]:
        normalized_query = f'%{query.casefold()}%'
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamModel)
                .where(
                    TeamModel.name.ilike(normalized_query)
                    | TeamModel.description.ilike(normalized_query)
                )
                .order_by(TeamModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, team_id: str) -> Team | None:
        with self._session_factory.begin() as session:
            row = session.get(TeamModel, team_id)
            return None if row is None else self._to_domain(row)

    def add(self, team: Team) -> Team:
        with self._session_factory.begin() as session:
            row = TeamModel(
                id=team.id,
                name=team.name,
                description=team.description,
                active=team.active,
                created_at=team.created_at,
                updated_at=team.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def save(self, team: Team) -> Team:
        with self._session_factory.begin() as session:
            row = session.get(TeamModel, team.id)
            if row is None:
                raise LookupError(team.id)
            row.name = team.name
            row.description = team.description
            row.active = team.active
            row.updated_at = team.updated_at
            session.flush()
            return self._to_domain(row)

    def delete(self, team_id: str) -> None:
        with self._session_factory.begin() as session:
            row = session.get(TeamModel, team_id)
            if row is not None:
                session.delete(row)

    @staticmethod
    def _to_domain(row: TeamModel) -> Team:
        return Team(
            id=row.id,
            name=row.name,
            description=row.description,
            active=row.active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
