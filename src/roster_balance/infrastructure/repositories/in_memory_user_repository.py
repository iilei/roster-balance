"""In-memory user repository for local development and tests."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from roster_balance.domain.models.principal import Principal
    from roster_balance.domain.models.user import User


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def list(self) -> list[User]:
        return list(self._users.values())

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_by_principal(self, principal: Principal) -> User | None:
        return next(
            (
                user
                for user in self._users.values()
                if user.provider == principal.provider
                and user.subject == principal.subject
            ),
            None,
        )

    def add(self, user: User) -> User:
        self._users[user.id] = user
        return user
