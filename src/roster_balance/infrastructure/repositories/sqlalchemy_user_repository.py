"""SQLAlchemy-backed user repository."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from roster_balance.domain.models.user import User
from roster_balance.infrastructure.db.models import UserModel

if TYPE_CHECKING:
    import builtins

    from sqlalchemy.orm import Session, sessionmaker

    from roster_balance.domain.models.principal import Principal


class SQLAlchemyUserRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def list(self) -> builtins.list[User]:
        with self._session_factory.begin() as session:
            rows = session.scalars(
                select(UserModel).order_by(UserModel.created_at)
            ).all()
            return [self._to_domain(row) for row in rows]

    def get(self, user_id: str) -> User | None:
        with self._session_factory.begin() as session:
            row = session.get(UserModel, user_id)
            return None if row is None else self._to_domain(row)

    def get_by_principal(self, principal: Principal) -> User | None:
        with self._session_factory.begin() as session:
            row = session.scalar(
                select(UserModel).where(
                    UserModel.provider == principal.provider,
                    UserModel.subject == principal.subject,
                )
            )
            return None if row is None else self._to_domain(row)

    def add(self, user: User) -> User:
        with self._session_factory.begin() as session:
            row = UserModel(
                id=user.id,
                provider=user.provider,
                subject=user.subject,
                email=user.email,
                display_name=user.display_name,
                active=user.active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
            session.add(row)
            session.flush()
            return self._to_domain(row)

    @staticmethod
    def _to_domain(row: UserModel) -> User:
        return User(
            id=row.id,
            provider=row.provider,
            subject=row.subject,
            email=row.email,
            display_name=row.display_name,
            active=row.active,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
