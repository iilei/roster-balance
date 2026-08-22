"""SQLAlchemy-backed team duty role repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from roster_balance.domain.models.team_duty_role import TeamDutyRole
from roster_balance.infrastructure.db.models import DutyRoleModel, TeamDutyRoleModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker


class SQLAlchemyTeamDutyRoleRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[TeamDutyRole]:
        with self._session_factory.begin() as session:
            rows = session.execute(
                select(DutyRoleModel, TeamDutyRoleModel.team_id)
                .join(
                    TeamDutyRoleModel,
                    TeamDutyRoleModel.duty_role_id == DutyRoleModel.id,
                )
                .where(TeamDutyRoleModel.team_id == team_id)
                .order_by(DutyRoleModel.created_at)
            ).all()
            return [self._to_domain(role, team_id) for role, team_id in rows]

    def get(self, role_id: str) -> TeamDutyRole | None:
        with self._session_factory.begin() as session:
            row = session.execute(
                select(DutyRoleModel, TeamDutyRoleModel.team_id)
                .join(
                    TeamDutyRoleModel,
                    TeamDutyRoleModel.duty_role_id == DutyRoleModel.id,
                )
                .where(DutyRoleModel.id == role_id)
            ).first()
            return None if row is None else self._to_domain(row[0], row[1])

    def get_by_slug(self, team_id: str, slug: str) -> TeamDutyRole | None:
        with self._session_factory.begin() as session:
            row = session.execute(
                select(DutyRoleModel, TeamDutyRoleModel.team_id)
                .join(
                    TeamDutyRoleModel,
                    TeamDutyRoleModel.duty_role_id == DutyRoleModel.id,
                )
                .where(
                    TeamDutyRoleModel.team_id == team_id,
                    DutyRoleModel.slug == slug,
                )
            ).first()
            return None if row is None else self._to_domain(row[0], row[1])

    def add(self, role: TeamDutyRole) -> TeamDutyRole:
        with self._session_factory.begin() as session:
            duty_role_row = DutyRoleModel(
                id=role.id,
                slug=role.slug,
                display_name=role.display_name,
                description=role.description,
                active=role.active,
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
            session.add(duty_role_row)
            session.add(
                TeamDutyRoleModel(
                    team_id=role.team_id,
                    duty_role_id=role.id,
                    created_at=role.created_at,
                )
            )
            session.flush()
            return self._to_domain(duty_role_row, role.team_id)

    def save(self, role: TeamDutyRole) -> TeamDutyRole:
        with self._session_factory.begin() as session:
            row = session.get(DutyRoleModel, role.id)
            if row is None:
                raise LookupError(role.id)
            row.slug = role.slug
            row.display_name = role.display_name
            row.description = role.description
            row.active = role.active
            row.updated_at = role.updated_at
            session.flush()
            return self._to_domain(row, role.team_id)

    @staticmethod
    def _to_domain(row: DutyRoleModel, team_id: str) -> TeamDutyRole:
        return TeamDutyRole(
            id=row.id,
            team_id=team_id,
            slug=row.slug,
            display_name=row.display_name,
            description=row.description,
            active=row.active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
