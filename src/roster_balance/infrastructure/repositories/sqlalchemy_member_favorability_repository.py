"""SQLAlchemy-backed member favorability repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, select

from roster_balance.domain.models.member_favorability import MemberFavorability
from roster_balance.infrastructure.db.models import MemberFavorabilityModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker
    from sqlalchemy.sql import Select


class SQLAlchemyMemberFavorabilityRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list_for_team(self, team_id: str) -> builtins.list[MemberFavorability]:
        return self._list(
            select(MemberFavorabilityModel)
            .where(MemberFavorabilityModel.team_id == team_id)
            .order_by(MemberFavorabilityModel.created_at)
        )

    def list_for_member(
        self, team_id: str, member_id: str
    ) -> builtins.list[MemberFavorability]:
        return self._list(
            select(MemberFavorabilityModel)
            .where(
                MemberFavorabilityModel.team_id == team_id,
                MemberFavorabilityModel.member_id == member_id,
            )
            .order_by(MemberFavorabilityModel.created_at)
        )

    def get(
        self, team_id: str, member_id: str, duty_role_id: str
    ) -> MemberFavorability | None:
        with self._session_factory.begin() as session:
            row = session.scalar(
                select(MemberFavorabilityModel).where(
                    MemberFavorabilityModel.team_id == team_id,
                    MemberFavorabilityModel.member_id == member_id,
                    MemberFavorabilityModel.duty_role_id == duty_role_id,
                )
            )
            return None if row is None else self._to_domain(row)

    def add(self, favorability: MemberFavorability) -> MemberFavorability:
        with self._session_factory.begin() as session:
            row = MemberFavorabilityModel(
                id=favorability.id,
                team_id=favorability.team_id,
                member_id=favorability.member_id,
                duty_role_id=favorability.duty_role_id,
                effect=favorability.effect,
                blocking_level=favorability.blocking_level,
                favorability=favorability.favorability,
                constraint_strength=favorability.constraint_strength,
                source=favorability.source,
                created_at=favorability.created_at,
                updated_at=favorability.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    def save(self, favorability: MemberFavorability) -> MemberFavorability:
        with self._session_factory.begin() as session:
            row = session.get(MemberFavorabilityModel, favorability.id)
            if row is None:
                raise LookupError(favorability.id)
            for field in (
                'team_id',
                'member_id',
                'duty_role_id',
                'effect',
                'blocking_level',
                'favorability',
                'constraint_strength',
                'source',
                'created_at',
                'updated_at',
            ):
                setattr(row, field, getattr(favorability, field))
            session.flush()
            return self._to_domain(row)

    def delete(self, team_id: str, member_id: str, duty_role_id: str) -> None:
        with self._session_factory.begin() as session:
            session.execute(
                delete(MemberFavorabilityModel).where(
                    MemberFavorabilityModel.team_id == team_id,
                    MemberFavorabilityModel.member_id == member_id,
                    MemberFavorabilityModel.duty_role_id == duty_role_id,
                )
            )

    def _list(
        self, query: Select[tuple[MemberFavorabilityModel]]
    ) -> builtins.list[MemberFavorability]:
        with self._session_factory.begin() as session:
            rows = session.scalars(query).all()
            return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row: MemberFavorabilityModel) -> MemberFavorability:
        return MemberFavorability(
            id=row.id,
            team_id=row.team_id,
            member_id=row.member_id,
            duty_role_id=row.duty_role_id,
            effect=row.effect,
            blocking_level=row.blocking_level,
            favorability=row.favorability,
            constraint_strength=row.constraint_strength,
            source=row.source,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
