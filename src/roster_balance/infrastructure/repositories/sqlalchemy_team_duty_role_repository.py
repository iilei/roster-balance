"""SQLAlchemy-backed team duty role repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from roster_balance.domain.models.team_duty_role import TeamDutyRole
from roster_balance.infrastructure.db.models import TeamDutyRoleModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyTeamDutyRoleRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[TeamDutyRole]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(TeamDutyRoleModel)
                .where(TeamDutyRoleModel.team_id == team_id)
                .order_by(TeamDutyRoleModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, role_id: str) -> TeamDutyRole | None:
        with self._session_factory.begin() as session:
            row = session.get(TeamDutyRoleModel, role_id)
            return None if row is None else self._to_domain(row)

    def get_by_slug(self, team_id: str, slug: str) -> TeamDutyRole | None:
        with self._session_factory.begin() as session:
            row = session.scalar(
                select(TeamDutyRoleModel).where(
                    TeamDutyRoleModel.team_id == team_id,
                    TeamDutyRoleModel.slug == slug,
                )
            )
            return None if row is None else self._to_domain(row)

    def add(self, role: TeamDutyRole) -> TeamDutyRole:
        with self._session_factory.begin() as session:
            row = TeamDutyRoleModel(
                id=role.id,
                team_id=role.team_id,
                slug=role.slug,
                display_name=role.display_name,
                description=role.description,
                active=role.active,
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def save(self, role: TeamDutyRole) -> TeamDutyRole:
        with self._session_factory.begin() as session:
            row = session.get(TeamDutyRoleModel, role.id)
            if row is None:
                raise LookupError(role.id)
            row.team_id = role.team_id
            row.slug = role.slug
            row.display_name = role.display_name
            row.description = role.description
            row.active = role.active
            row.updated_at = role.updated_at
            session.flush()
            return self._to_domain(row)

    @staticmethod
    def _to_domain(row: TeamDutyRoleModel) -> TeamDutyRole:
        return TeamDutyRole(
            id=row.id,
            team_id=row.team_id,
            slug=row.slug,
            display_name=row.display_name,
            description=row.description,
            active=row.active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
